# Notebooks can't display cv2 images natively, so we use this function to display them inline instead of cv2.imshow()
import io
from IPython.display import clear_output, Image, display
import PIL.Image
import numpy as np
import cv2

def showarray(image, crop=None, scale_factor=1, format='png'):

    image=image.copy()

    height,width = image.shape[:2]

    if crop:
        (x,y,crop_width,crop_height) = crop
        image = image[y:y+crop_height,x:x+crop_width]
        height,width = image.shape[:2] 

    new_height = int(height*scale_factor)
    new_width = int(width*scale_factor)

    resized = cv2.resize(image,(new_width,new_height),interpolation=cv2.INTER_AREA)

    image = np.uint8(np.clip(resized, 0, 255))
    f = io.BytesIO()
    PIL.Image.fromarray(image).save(f, format)
    display(Image(data=f.getvalue()))