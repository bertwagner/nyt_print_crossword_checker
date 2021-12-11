# Notebooks can't display cv2 images natively, so we use this function to display them inline instead of cv2.imshow()
import io
from IPython.display import clear_output, Image, display
import PIL.Image
import numpy as np

def showarray(a, fmt='jpeg'):
    a = np.uint8(np.clip(a, 0, 255))
    f = io.BytesIO()
    PIL.Image.fromarray(a).save(f, fmt)
    display(Image(data=f.getvalue()))