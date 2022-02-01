import cv2
import numpy as np
from imutils import contours
from src.util import utilities as util

# Detecting blobs https://en.wikipedia.org/wiki/Blob_detection

def load_image(path):
    print(path)
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
    #thresh = cv2.adaptiveThreshold(image.copy(), 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 3, 10)
    ret,thresh = cv2.threshold(image.copy(), 100,255, cv2.THRESH_BINARY_INV)
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
    image_removed_grid_lines = __remove_grid_lines(hlines,vlines,image)
    
    cropped_cells = __crop_cells(hlines,vlines,image_removed_grid_lines)

    cropped_letters = []

    for cell in cropped_cells:
        found_bounding_box = __find_letter_bounding_box(cell)
        cropped_letter = __crop_letter(cell,found_bounding_box[0])
        cropped_letters.append(cropped_letter)

    return cropped_letters

def __find_grid_lines(image):
    image_hough=image.copy()
    height,width = image.shape[:2]

    image_canny = cv2.Canny(image,400,500)

    kernel = np.ones((3, 3), np.uint8)

    image_dilation = cv2.dilate(image_canny, kernel, iterations=4)

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
        cv2.line(image_hough, (line[0],line[1]), (line[2],line[3]), (255,0,0), 1, cv2.LINE_AA)
    for line in vlines:
        cv2.line(image_hough, (line[0],line[1]), (line[2],line[3]), (0,0,255), 1, cv2.LINE_AA)

    return hlines,vlines,image_hough

def __dedupe_similar_lines(hlines,vlines):
    hlines_unique=[]
    vlines_unique=[]

    minimum_gap_between_lines=30

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

def __find_letter_bounding_box(image):
    result = image.copy()
    image_height,image_width=image.shape[:2]

    # Cover the numbers up partially, just enough so they aren't the largest recognized contour.
    coverup_x=int(image_width*.7)
    coverup_y=int(image_height*.4)
    cv2.rectangle(result, (0, 0), (coverup_x,coverup_y), (255,255,255),-1)

    ret,thresh = cv2.threshold(result, 170, 255, cv2.THRESH_BINARY_INV)
    kernel = np.ones((3,3),np.uint8)
    dilation = cv2.dilate(thresh,kernel,iterations =3 )
    contours, _ = cv2.findContours(dilation, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    sorted_ctrs = sorted(contours, key=lambda ctr: cv2.boundingRect(ctr)[0])

    image_contours = cv2.cvtColor(image.copy(), cv2.COLOR_GRAY2RGB)

    max_area_index = -1
    max_area = -1
    max_contour  = None
    x=0
    y=0
    w=image_width
    h=image_height

    for i, contour in enumerate(sorted_ctrs):
        x, y, w, h = cv2.boundingRect(contour)

        area = w*h
        if w*h > max_area:
            max_area=area
            max_area_index = i
            max_contour = contour

    # get the bounding box if an object is found
    if max_area_index != -1:
        x,y,w,h = cv2.boundingRect(sorted_ctrs[max_area_index])

    #draw a box around the max area contour, assumed to be our crossword grid
    
    cv2.rectangle(image_contours, (x, y), (x+w, y+h), color=(0, 255, 0), thickness=2)

    return (x,y,w,h),thresh,image_contours

def __crop_letter(image,bounding_box):
    x,y,w,h=bounding_box
    image_height,image_width = image.shape[:2]
    result = image.copy()

    x1=x
    x2=x+w
    y1=y
    y2=y+h


    if w > h:
        delta_height = w - h 
        delta_to_add = int(delta_height/2)

        y1 -=delta_to_add
        y2 += delta_to_add
    if w < h:
        delta_width = h - w
        delta_to_add = int(delta_width/2)

        x1 -= delta_to_add
        x2 += delta_to_add

    # Fix any numbers going behind image dimensions
    if x1 < 0:
        x1=0
    if y1 < 0:
        y1=0
    if x2 > image_width:
        x2=image_width
    if y2 > image_height:
        y2=image_height


    square_crop = result[y1:y2, x1:x2]

    ret,thresh = cv2.threshold(square_crop, 170, 255, cv2.THRESH_BINARY)
    resized_crop = cv2.resize(thresh,(24,24),interpolation=cv2.INTER_AREA )

    

    return resized_crop
   

