from pathlib import Path
import os
import datetime
import json
import cv2
import numpy as np


def main(cell_input_path):

    cells = load_dataset(cell_input_path)
    
    

def load_dataset(cell_input_path,dimension=24,letters_to_include=None):
    images = []
    targets = []

    for folder in os.scandir(cell_input_path):
        
        # Skip the unidentified folder
        if folder.name == "?":
            continue

        if letters_to_include != None:
            if folder.name not in letters_to_include:
                continue

        for file in os.scandir(folder):
            image = cv2.imread(os.path.join(cell_input_path,folder.name,file.name),cv2.IMREAD_GRAYSCALE)
            
            #invert colors
            inverted = cv2.bitwise_not(image)

            # Resize all images to the same size.  This does not keep proportions.
            resized = cv2.resize(inverted,(dimension,dimension),interpolation=cv2.INTER_AREA)
     
            images.append(resized)
            targets.append(folder.name)

    cells = {}
    cells["images"] = np.asarray(images)
    cells["targets"] = np.asarray(targets)
    return cells


if __name__ == '__main__':
    project_dir = Path(__file__).resolve().parents[2]

    cell_input_path = os.path.join(project_dir,"data/processed/image_uploads/letters")

    main(cell_input_path)
