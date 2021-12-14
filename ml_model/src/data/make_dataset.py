import logging
from pathlib import Path
import os
from src.data import image_proccessor as ip
import datetime
import cv2
import shutil

def main(input_filepath, output_filepath,delete_files):

    for file in os.scandir(input_filepath):
        puzzle_date = datetime.datetime.strptime(file.name[0:10],'%Y-%m-%d').date()
        image_raw = cv2.imread(os.path.join(input_filepath,file.name))
        
        # warp and save image
        processor = ip.ImageProcessor(image_raw)
        processor.warp_and_transform()
        warped_output_path = os.path.join(output_filepath,"warped")
        __make_folder_if_not_exists(warped_output_path,delete_files)
        cv2.imwrite(os.path.join(warped_output_path,file.name),processor.image['warped'])

        # slice and save individual cell images
        processor.slice_up_grid()

        # make image folder if it doesn't exist
        output_folder = os.path.join(output_filepath,"cells",os.path.splitext(file.name)[0])
        __make_folder_if_not_exists(output_folder,delete_files)
        
        # save all cells as individual images
        for i,cell in enumerate(processor.image['cells']):
            cv2.imwrite(os.path.join(output_folder,f"{str(i)}.png"),cell)

def __make_folder_if_not_exists(folder_path,delete_files):
    path_exists = os.path.exists(folder_path)

    if delete_files and path_exists:
            shutil.rmtree(folder_path)
            os.makedirs(folder_path)

    if not path_exists:
        os.makedirs(folder_path)
        

if __name__ == '__main__':
    project_dir = Path(__file__).resolve().parents[2]

    input_filepath = os.path.join(project_dir,"data/raw/image_uploads")
    output_filepath = os.path.join(project_dir,"data/processed/image_uploads")

    delete_files = True

    main(input_filepath,output_filepath,delete_files)
