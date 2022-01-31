import cv2
import numpy as np
from imutils import contours

# Detecting blobs https://en.wikipedia.org/wiki/Blob_detection

def load_image(path):
    image = cv2.imread(path)
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return rgb

def crop_grid(image):
    grid_contour, _ = __find_grid(image)

    corners = __find_corners(grid_contour)

    maxWidth,maxHeight = __calculate_dimensions(corners)

    input_pts = corners
    output_pts = np.float32([[0, 0],
                        [0, maxHeight - 1],
                        [maxWidth - 1, maxHeight - 1],
                        [maxWidth - 1, 0]])

    h, status = cv2.findHomography(corners, output_pts)
    warped = cv2.warpPerspective(image.copy(), h, (maxWidth,maxHeight), flags=cv2.INTER_LINEAR)

    return warped

def __find_grid(image):
    thresh = cv2.adaptiveThreshold(image.copy(), 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 3, 10)

    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    sorted_ctrs = sorted(contours, key=lambda ctr: cv2.boundingRect(ctr)[0])

    image_contours = cv2.cvtColor(image.copy(), cv2.COLOR_GRAY2RGB)

    max_area_index = -1
    max_area = -1
    max_contour  = None

    for i, contour in enumerate(sorted_ctrs):
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(image_contours, (x, y), (x+w, y+h), color=(0, 255, 0), thickness=1)

        area = w*h
        if w*h > max_area:
            max_area=area
            max_area_index = i
            max_contour = contour
            
    # color in the max area contour, assumed to be our crossword grid
    cv2.drawContours(image_contours, sorted_ctrs, max_area_index, (255, 0, 0), 3)
    return max_contour, image_contours

def __find_corners(grid_contour):
    peri = cv2.arcLength(grid_contour, True)
    corners = cv2.approxPolyDP(grid_contour, 0.04 * peri, True)
    
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

    return np.array([leftPoints[0], leftPoints[1], rightPoints[1],rightPoints[0]])

def __calculate_dimensions(corners):
    pt_A, pt_B, pt_C, pt_D = corners

    # Calculate widths/heights using L2 norm
    width_AD = np.sqrt(((pt_A[0] - pt_D[0]) ** 2) + ((pt_A[1] - pt_D[1]) ** 2))
    width_BC = np.sqrt(((pt_B[0] - pt_C[0]) ** 2) + ((pt_B[1] - pt_C[1]) ** 2))
    maxWidth = max(int(width_AD), int(width_BC))


    height_AB = np.sqrt(((pt_A[0] - pt_B[0]) ** 2) + ((pt_A[1] - pt_B[1]) ** 2))
    height_CD = np.sqrt(((pt_C[0] - pt_D[0]) ** 2) + ((pt_C[1] - pt_D[1]) ** 2))
    maxHeight = max(int(height_AB), int(height_CD))

    return (maxWidth,maxHeight)

def crop_letters(image):

    hlines,vlines, _ = __find_grid_lines(image)
    
    cropped_cells = __crop_cells(hlines,vlines,image)

    cropped_letters = []
    for cell in cropped_cells:
        cropped_letter = __crop_letter(cell)
        cropped_letters.append(cropped_letter)

    return cropped_letters

def __find_grid_lines(image):
    image_hough=image.copy()
    height,width = image.shape[:2]

    image_canny = cv2.Canny(image,400,500)
    kernel = np.ones((3, 3), np.uint8)

    image_dilation = cv2.dilate(image_canny, kernel, iterations=2)

    threshold = 500
    image_hough = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

    lines = cv2.HoughLines(image_dilation, 1, np.pi/180, threshold)
    
    hlines = []
    vlines = []


    for i in range(0, len(lines)):
        for rho,theta in lines[i]:
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a * rho
            y0 = b * rho
            
            pt1_x = int(x0 + 1000*(-b)) 
            pt1_y = int(y0 + 1000*(a))
            pt2_x = int(x0 - 1000*(-b))
            pt2_y = int(y0 - 1000*(a))
            angle = np.degrees(theta)

        # Add horizontal lines
        if angle == 90:
            hlines.append([0,pt1_y,image.shape[1],pt2_y,angle])

        # Add vertical lines
        if angle == 0:
            vlines.append([pt1_x,0,pt2_x,image.shape[0],angle])


    hlines.sort(key=lambda x:x[1])
    vlines.sort(key=lambda x:x[0])

    hlines,vlines = __dedupe_similar_lines(hlines,vlines)


    for line in hlines:
        cv2.line(image_hough, (line[0],line[1]), (line[2],line[3]), (0,255,0), 1, cv2.LINE_AA)
    for line in vlines:
        cv2.line(image_hough, (line[0],line[1]), (line[2],line[3]), (0,0,255), 1, cv2.LINE_AA)

    return hlines,vlines,image_hough

def __dedupe_similar_lines(hlines,vlines):
    hlines_unique=[]
    vlines_unique=[]

    minimum_gap_between_lines=20

    previous_y = -1000
    previous_x = -1000

    # TODO: Split the difference for close lines in the future?
    # For now, just pad it with some pixels
    offset_padding=2
    for line in hlines:
        if line[1] >= previous_y + minimum_gap_between_lines:
            hlines_unique.append([line[0],line[1]+offset_padding,line[2],line[3]+offset_padding])
            previous_y=line[1]+offset_padding
        
    for line in vlines:
        if line[0] >= previous_x + minimum_gap_between_lines:
            vlines_unique.append([line[0]+offset_padding,line[1],line[2]+offset_padding,line[3]])
            previous_x=line[0]+offset_padding

    return hlines_unique,vlines_unique

def __crop_cells(hlines,vlines,image):

    prev_hline = hlines[0]
    prev_vline = vlines[0]
    cropped_cells = []

    for hline in hlines[1:]:
        for vline in vlines[1:]:
            y=prev_hline[1]
            yheight=hline[1]
            x=prev_vline[0]
            xwidth=vline[0]

            # validation that we aren't cropping some tiny sliver
            if yheight-y >= 20 and xwidth-x >=20:
                cropped_cell = image[y:yheight,x:xwidth].copy()
                cropped_cells.append(cropped_cell)

            prev_vline=vline
        
        prev_vline=vlines[0]
        prev_hline=hline

    return cropped_cells


def __remove_grid_lines(hlines,vlines,image):
    

    result = image.copy()

    for hline in hlines:
        cv2.rectangle(result,(hline[0],hline[1]),(hline[2],hline[3]),(255,255,255),5) 
    for vline in vlines:
        cv2.rectangle(result,(vline[0],vline[1]),(vline[2],vline[3]),(255,255,255),5)
    
    return result

def __crop_letter(image):
    result = image.copy()

    # Cover the numbers up partially, just enough so they aren't the largest recognized contour.
    coverup_x=int(image.shape[1]*.5)
    coverup_y=int(image.shape[0]*.3)
    print(coverup_x,coverup_y)
    cv2.rectangle(result, (0, 0), (coverup_x,coverup_y), (255,255,255),-1)

    ret,thresh = cv2.threshold(result, 170, 255, cv2.THRESH_BINARY_INV)
   
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    sorted_ctrs = sorted(contours, key=lambda ctr: cv2.boundingRect(ctr)[0])

    image_contours = cv2.cvtColor(image.copy(), cv2.COLOR_GRAY2RGB)

    max_area_index = -1
    max_area = -1
    max_contour  = None

    for i, contour in enumerate(sorted_ctrs):
        x, y, w, h = cv2.boundingRect(contour)

        area = w*h
        if w*h > max_area:
            max_area=area
            max_area_index = i
            max_contour = contour
            
    #draw a box around the max area contour, assumed to be our crossword grid
    x, y, w, h = cv2.boundingRect(sorted_ctrs[max_area_index])
    cv2.rectangle(image_contours, (x, y), (x+w, y+h), color=(0, 255, 0), thickness=2)

    return image_contours

    # Create a mask for only the left quadrant, the only place clue number appears
    # height,width = image.shape[:2]
    
    # mask = image.copy()
    # cv2.rectangle(mask, (0, 0), (width,height), (0,0,0),-1)
    # cv2.rectangle(mask, (3, 3), (int(width*.4),int(height*.4)), (255,255,255),-1)

    # mask_inv = cv2.bitwise_not(mask)

    # image_masked = cv2.bitwise_or(image, mask_inv)

    # ret,thresh = cv2.threshold(image_masked, 140, 255, cv2.THRESH_BINARY_INV)

    # contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # sorted_ctrs = sorted(contours, key=lambda ctr: cv2.boundingRect(ctr)[0])

    # image_contours = cv2.cvtColor(thresh.copy(), cv2.COLOR_GRAY2RGB)

    # max_area_index = -1
    # max_area = -1
    # max_contour  = None

    # for i, contour in enumerate(sorted_ctrs):
    #     x, y, w, h = cv2.boundingRect(contour)
    #     #cv2.rectangle(image_contours, (x, y), (x+w, y+h), color=(0, 255, 0), thickness=1)
    #     #cv2.drawContours(image_contours, sorted_ctrs, i, (255, 0, 0), 1)
    #     area = w*h
    #     if w*h > max_area:
    #         max_area=area
    #         max_area_index = i
    #         max_contour = contour
            
    # #color in the max area contour, assumed to be our crossword grid
    # cv2.drawContours(image_contours, sorted_ctrs, max_area_index, (255, 0, 0), 3)
    # x, y, w, h = cv2.boundingRect(sorted_ctrs[max_area_index])
    # #cv2.rectangle(image_contours, (x, y), (x+w, y+h), color=(0, 255, 0), thickness=2)
    
    # return image_contours


    # TODO: THIS IS GOOD, BUT REMOVE NUMBERS FIRST
    # height,width = image.shape[:2]

    # thresh = cv2.adaptiveThreshold(image.copy(), 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 7, 10)

    # #draw a rectangle to cover the numbers
    # #coverup_x=int(image.shape[1]*.6)
    # #coverup_y=int(image.shape[0]*.5)

    # #cv2.rectangle(thresh, (0, 0), (coverup_x,coverup_y), (0,0,0),-1)

    # kernel = np.ones((2,2), np.uint8)

    # image_dilation = cv2.dilate(thresh, kernel, iterations=1)

    # contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # sorted_ctrs = sorted(contours, key=lambda ctr: cv2.boundingRect(ctr)[0])

    # image_contours = cv2.cvtColor(image.copy(), cv2.COLOR_GRAY2RGB)

    # max_area_index = -1
    # max_area = -1
    # max_contour  = None

    # for i, contour in enumerate(sorted_ctrs):
    #     x, y, w, h = cv2.boundingRect(contour)
    #     #cv2.rectangle(image_contours, (x, y), (x+w, y+h), color=(0, 255, 0), thickness=1)
    #     if w >= (width*.8) and h >= (height*.8):
    #         area = w*h
    #         if w*h > max_area:
    #             max_area=area
    #             max_area_index = i
    #             max_contour = contour
            
    # #color in the max area contour, assumed to be our crossword grid
    # cv2.drawContours(image_contours, sorted_ctrs, max_area_index, (255, 0, 0), 3)
    # x, y, w, h = cv2.boundingRect(sorted_ctrs[max_area_index])
    # print(x,y,w,h)
    # cv2.rectangle(image_contours, (x, y), (x+w, y+h), color=(0, 255, 0), thickness=2)
    
    # return image_contours

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

