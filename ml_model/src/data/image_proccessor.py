import cv2
import numpy as np

class ImageProcessor:

    def __init__(self,image):
        self.image = {}
        self.image['raw'] = image

    def warp_and_transform(self):
        
        # cv2 color channels are ordered BGR instead of RGB by default. rearrange color channels for a color correct image
        rgb = cv2.cvtColor(self.image['raw'], cv2.COLOR_BGR2RGB)
        self.image['rgb'] = rgb

        # turn grayscale for processing
        gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

        # blur the image to reduce noise
        blur = cv2.GaussianBlur(gray, (5,5),0)

        # apply thresholding to make everything black or white.  Adaptive thresholding is used to compensate for different lighting conditions across the image
        thresh = cv2.adaptiveThreshold(blur,255,1,1,11,2)

        # find countours, the curves that joins all continuous points having the same color or intentsity
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # we find the largest contour by area and assume this is the entire crossword grid
        rgbcopy = rgb.copy()
        max_area = 0
        c = 0
        for i in contours:
                area = cv2.contourArea(i)
                if area > 1000:
                        if area > max_area:
                            max_area = area
                            best_cnt = i
                            rgb_c = cv2.drawContours(rgbcopy, contours, c, (0, 255, 0), 3)
                            
                c+=1

        # find the corners of the image
        peri = cv2.arcLength(best_cnt, True)
        corners = cv2.approxPolyDP(best_cnt, 0.04 * peri, True)
        
        # All points are in format [cols, rows]
        pt_A, pt_B, pt_C, pt_D = self.__order_corners(corners)
        
        # Calculate widths/heights using L2 norm
        width_AD = np.sqrt(((pt_A[0] - pt_D[0]) ** 2) + ((pt_A[1] - pt_D[1]) ** 2))
        width_BC = np.sqrt(((pt_B[0] - pt_C[0]) ** 2) + ((pt_B[1] - pt_C[1]) ** 2))
        maxWidth = max(int(width_AD), int(width_BC))
        self.maxWidth = maxWidth

        height_AB = np.sqrt(((pt_A[0] - pt_B[0]) ** 2) + ((pt_A[1] - pt_B[1]) ** 2))
        height_CD = np.sqrt(((pt_C[0] - pt_D[0]) ** 2) + ((pt_C[1] - pt_D[1]) ** 2))
        maxHeight = max(int(height_AB), int(height_CD))
        self.maxHeight = maxHeight

        # map input points and output points after warping
        input_pts = np.float32([pt_A, pt_B, pt_C, pt_D])
        output_pts = np.float32([[0, 0],
                                [0, maxHeight - 1],
                                [maxWidth - 1, maxHeight - 1],
                                [maxWidth - 1, 0]])

        # Compute the perspective transform M
        rgbcopy = rgb.copy()
        M = cv2.getPerspectiveTransform(input_pts,output_pts)
        warped = cv2.warpPerspective(rgbcopy,M,(maxWidth, maxHeight),flags=cv2.INTER_LINEAR)
        self.image['warped'] = warped
    
    def __order_corners(self,corners):
        # We always want the top left corner to be first corner and the rest of the points to come in a counterclockwise order
        points = []
        points.append(corners[0][0])
        points.append(corners[1][0])
        points.append(corners[2][0])
        points.append(corners[3][0])

        points.sort(key=lambda x:x[0])

        leftPoints = points[:2]
        rightPoints = points[2:]

        leftPoints.sort(key=lambda x:x[1])
        rightPoints.sort(key=lambda x:x[1])

        return (leftPoints[0], leftPoints[1], rightPoints[1],rightPoints[0])

    def slice_up_grid(self):
        # find Canny edges
        edges = cv2.Canny(self.image['warped'], 50, 200)

        # find lines from edges
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 130, None, 5, 5000)
        hlines = []
        vlines = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            # filter out non-vertical  and non horizontal lines
            angle = np.abs(np.arctan2(y2 - y1, x2 - x1) * 180. / np.pi)

            # Draw horizontal lines, forcing them to start at 0 and be the max image width
            if (angle >=0 and angle <= 1) :
                hlines.append([0,y1,self.maxWidth,y2])
            # Draw vertical lines, forcing them to start at 0 and be the max image height
            if (angle >= 88 and angle <= 91):
                vlines.append([x1,0,x2,self.maxHeight])
        
        # find unique lines and draw those on the image
        hlines.sort(key=lambda x:x[1])
        hlines_unique = []
        previous_line_y1 = -1000
        for line in hlines:
            if line[1] >= previous_line_y1+20: # TODO: instead of skipping the duplicate lines, average the duplicate line's coordinates with the original to get a better fit
                hlines_unique.append(line)
                previous_line_y1 = line[1]
                #cv2.line(lined_unique, (line[0], line[1]), (line[2], line[3]), (255, 0, 255), 2)

        vlines.sort(key=lambda x:x[0])
        vlines_unique = []
        previous_line_x1 = -1000
        for line in vlines:
            if line[0] >= previous_line_x1+20:
                vlines_unique.append(line)
                previous_line_x1 = line[0]
                #cv2.line(lined_unique, (line[0], line[1]), (line[2], line[3]), (255, 255, 0), 2)

        # crop image based on line intersections
        img = self.image['warped'].copy()
        prev_hline = hlines_unique[0]
        prev_vline = vlines_unique[0]

        sliced_grid = []

        for hline in hlines_unique[1:]:
            for vline in vlines_unique[1:]:
                y=prev_hline[1]
                yheight=hline[1]
                x=prev_vline[0]
                xwidth=vline[0]
                cropped = img[y:yheight,x:xwidth].copy()

                prev_vline=vline
                #print("v:",y,yheight,x,xwidth)
                sliced_grid.append(cropped)
            
            prev_vline=vlines_unique[0]
            prev_hline=hline
        
        self.image['cells'] = sliced_grid