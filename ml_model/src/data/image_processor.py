import cv2
import numpy as np

# Detecting blobs https://en.wikipedia.org/wiki/Blob_detection

def load_image(path):
    image = cv2.imread("../data/raw/image_uploads/2021-11-30-2d4a364a-9008-4c2d-8889-e28544fe7315.png")
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return rgb

def blur(image):
    


# class ImageProcessor:

#     def __init__(self,image):
#         self.image = {}
#         self.image['raw'] = image

#     def warp_and_transform(self):
        
#         # cv2 color channels are ordered BGR instead of RGB by default. rearrange color channels for a color correct image
#         rgb = cv2.cvtColor(self.image['raw'], cv2.COLOR_BGR2RGB)
#         self.image['rgb'] = rgb

#         # turn grayscale for processing
#         gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

#         # blur the image to reduce noise
#         blur = cv2.GaussianBlur(gray, (5,5),0)

#         # apply thresholding to make everything black or white.  Adaptive thresholding is used to compensate for different lighting conditions across the image
#         thresh = cv2.adaptiveThreshold(blur,255,1,1,11,2)

#         # find countours, the curves that joins all continuous points having the same color or intentsity
#         contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

#         # we find the largest contour by area and assume this is the entire crossword grid
#         rgbcopy = rgb.copy()
#         max_area = 0
#         c = 0
#         for i in contours:
#                 area = cv2.contourArea(i)
#                 if area > 1000:
#                         if area > max_area:
#                             max_area = area
#                             best_cnt = i
#                             rgb_c = cv2.drawContours(rgbcopy, contours, c, (0, 255, 0), 3)
                            
#                 c+=1

#         # find the corners of the image
#         peri = cv2.arcLength(best_cnt, True)
#         corners = cv2.approxPolyDP(best_cnt, 0.04 * peri, True)
        
#         # All points are in format [cols, rows]
#         pt_A, pt_B, pt_C, pt_D = self.__order_corners(corners)
        
#         # Calculate widths/heights using L2 norm
#         width_AD = np.sqrt(((pt_A[0] - pt_D[0]) ** 2) + ((pt_A[1] - pt_D[1]) ** 2))
#         width_BC = np.sqrt(((pt_B[0] - pt_C[0]) ** 2) + ((pt_B[1] - pt_C[1]) ** 2))
#         maxWidth = max(int(width_AD), int(width_BC))
#         self.maxWidth = maxWidth

#         height_AB = np.sqrt(((pt_A[0] - pt_B[0]) ** 2) + ((pt_A[1] - pt_B[1]) ** 2))
#         height_CD = np.sqrt(((pt_C[0] - pt_D[0]) ** 2) + ((pt_C[1] - pt_D[1]) ** 2))
#         maxHeight = max(int(height_AB), int(height_CD))
#         self.maxHeight = maxHeight

#         # map input points and output points after warping
#         input_pts = np.float32([pt_A, pt_B, pt_C, pt_D])
#         output_pts = np.float32([[0, 0],
#                                 [0, maxHeight - 1],
#                                 [maxWidth - 1, maxHeight - 1],
#                                 [maxWidth - 1, 0]])

#         # Compute the perspective transform M
#         rgbcopy = rgb.copy()
#         M = cv2.getPerspectiveTransform(input_pts,output_pts)
#         warped = cv2.warpPerspective(rgbcopy,M,(maxWidth, maxHeight),flags=cv2.INTER_LINEAR)
#         self.image['warped'] = warped
    
#     def __order_corners(self,corners):
#         # We always want the top left corner to be first corner and the rest of the points to come in a counterclockwise order
#         points = []
#         points.append(corners[0][0])
#         points.append(corners[1][0])
#         points.append(corners[2][0])
#         points.append(corners[3][0])

#         points.sort(key=lambda x:x[0])

#         leftPoints = points[:2]
#         rightPoints = points[2:]

#         leftPoints.sort(key=lambda x:x[1])
#         rightPoints.sort(key=lambda x:x[1])

#         return (leftPoints[0], leftPoints[1], rightPoints[1],rightPoints[0])

#     def slice_up_grid(self):
#         # find Canny edges
#         edges = cv2.Canny(self.image['warped'], 50, 200)

#         # find lines from edges
#         lines = cv2.HoughLinesP(edges, 1, np.pi/180, 110, None, 5, 5000)
#         hlines = []
#         vlines = []
#         for line in lines:
#             x1, y1, x2, y2 = line[0]
#             # filter out non-vertical  and non horizontal lines
#             angle = np.abs(np.arctan2(y2 - y1, x2 - x1) * 180. / np.pi)

#             # Draw horizontal lines, forcing them to start at 0 and be the max image width
#             if (angle >=0 and angle <= 3) :
#                 hlines.append([0,y1,self.maxWidth,y2])
#             # Draw vertical lines, forcing them to start at 0 and be the max image height
#             if (angle >= 88 and angle <= 91):
#                 vlines.append([x1,0,x2,self.maxHeight])
        
#         self.image["lines_drawn"] = lined_unique = self.image["warped"].copy()

#         # find unique lines and draw those on the image
#         hlines.sort(key=lambda x:x[1])
#         hlines_unique = []
#         previous_line_y1 = -1000
#         for line in hlines:
#             if line[1] >= previous_line_y1+40: # TODO: instead of skipping the duplicate lines, average the duplicate line's coordinates with the original to get a better fit
#                 hlines_unique.append(line)
#                 previous_line_y1 = line[1]
#                 cv2.line(self.image["lines_drawn"], (line[0], line[1]), (line[2], line[3]), (255, 0, 255), 2)

#         vlines.sort(key=lambda x:x[0])
#         vlines_unique = []
#         previous_line_x1 = -1000
#         for line in vlines:
#             if line[0] >= previous_line_x1+40:
#                 vlines_unique.append(line)
#                 previous_line_x1 = line[0]
#                 cv2.line(self.image["lines_drawn"], (line[0], line[1]), (line[2], line[3]), (255, 255, 0), 2)

#         # crop image into cells based on line intersections
#         img = self.image['warped'].copy()
#         prev_hline = hlines_unique[0]
#         prev_vline = vlines_unique[0]

#         sliced_grid = []

#         for hline in hlines_unique[1:]:
#             for vline in vlines_unique[1:]:
#                 y=prev_hline[1]
#                 yheight=hline[1]
#                 x=prev_vline[0]
#                 xwidth=vline[0]
#                 cropped = img[y:yheight,x:xwidth].copy()

#                 prev_vline=vline
#                 #print("v:",y,yheight,x,xwidth)
#                 cropped_and_centered_letter = self.__crop_letters(cropped)
#                 sliced_grid.append(cropped_and_centered_letter)
            
#             prev_vline=vlines_unique[0]
#             prev_hline=hline
        
#         self.image['cells'] = sliced_grid

#     def __crop_letters(self,image):
#         cropped_images=[]
#         original = image.copy()

#         h, w = original.shape[:2]

#         # grayscale
#         gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
#         cropped_images.append(gray)

#         # binary
#         # ret, thresh = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY_INV)
#         thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 3, 5)
#         cropped_images.append(thresh)

#         #draw a rectangle to cover the numbers
#         cv2.rectangle(thresh, (0, 0), (15,12), (0,0,0),-1)

#         # dilation
#         kernel = np.ones((1, 1), np.uint8)
#         img_dilation = cv2.dilate(thresh, kernel, iterations=1)
#         cropped_images.append(img_dilation)

#         # find contours
#         # cv2.findCountours() function changed from OpenCV3 to OpenCV4: now it have only two parameters instead of 3
#         cv2MajorVersion = cv2.__version__.split(".")[0]
#         # check for contours on thresh
#         if int(cv2MajorVersion) >= 4:
#             ctrs, hier = cv2.findContours(img_dilation.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#         else:
#             im2, ctrs, hier = cv2.findContours(img_dilation.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

#         # sort contours
#         sorted_ctrs = sorted(ctrs, key=lambda ctr: cv2.boundingRect(ctr)[0])

#         x1s = []
#         y1s = []
#         x2s = []
#         y2s = []
#         for i, ctr in enumerate(sorted_ctrs):
#             # Get bounding box
#             x, y, w, h = cv2.boundingRect(ctr)
#             #cv2.rectangle(original, (x, y), (x+w, y+h), color=(0, 0, 255), thickness=1)
#             #i and t are hard (especially if disjointed). skinny and multiple parts.
#             if x > 4 and y > 4 and w > 1 and h > 1 and w < 50: # add minimum box start points and sizes
#                 x1s.append(x)
#                 y1s.append(y)
#                 x2s.append(x+w)
#                 y2s.append(y+h)

#         final_crop = image
#         if len(x1s) > 0:
#             #combine multiple squares into one area
#             min_x1 = min(x1s)
#             min_y1 = min(y1s)    
#             max_x2 = max(x2s)
#             max_y2 = max(y2s)

#             crop_img = original[min_y1:max_y2, min_x1:max_x2]
#             cropped_images.append(crop_img)

#             # make the crop a square
#             crop_width = max_x2-min_x1
#             crop_height = max_y2-min_y1

#             if crop_width > crop_height:
#                 delta_height = crop_width - crop_height 
#                 delta_to_add = int(delta_height/2)
#                 min_y1 = min_y1-delta_to_add
#                 max_y2 = max_y2+delta_to_add
#             if crop_width < crop_height:
#                 delta_width = crop_height - crop_width 
#                 delta_to_add = int(delta_width/2)
#                 min_x1 = min_x1-delta_to_add
#                 max_x2 = max_x2+delta_to_add

#             square_crop = original[min_y1:max_y2, min_x1:max_x2]
            
#             #cv2.rectangle(original, (min_x1, min_y1), (max_x2, max_y2), color=(255, 0, 0), thickness=1)
#             cropped_images.append(square_crop)
            
#             final_crop=square_crop

#         #cropped_images.append(original)

            
#         #return cropped_images
#         try:
#             resized_crop = cv2.resize(final_crop,(16,16),interpolation=cv2.INTER_AREA)
#             return resized_crop
#         except:
#             resized_crop = cv2.resize(image,(16,16),interpolation=cv2.INTER_AREA)
#             return resized_crop

