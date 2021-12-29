import logging
from pathlib import Path
import os
from src.data import image_proccessor as ip
from src.data import crossword_downloader as cd
import datetime
import cv2
import shutil
import json


def main(input_filepath, output_filepath,delete_files):

    image_input_path = os.path.join(input_filepath,"image_uploads")
    image_output_path = os.path.join(output_filepath,"image_uploads")
    crossword_input_path = os.path.join(input_filepath,"nyt_answer_keys")
    crossword_output_path = os.path.join(output_filepath,"nyt_answer_keys")

    warped_output_path = os.path.join(image_output_path,"warped")
    lined_output_path = os.path.join(image_output_path,"lines_drawn")
    __make_folder_if_not_exists(warped_output_path,delete_files)
    __make_folder_if_not_exists(lined_output_path,delete_files)
    __make_folder_if_not_exists(crossword_output_path,delete_files)

    for file in os.scandir(image_input_path):
        answer_key = __process_crossword(file,crossword_input_path,crossword_output_path)
        __process_image(file,image_input_path,warped_output_path,lined_output_path,image_output_path,answer_key)
        

def __make_folder_if_not_exists(folder_path,delete_files):
    path_exists = os.path.exists(folder_path)

    if delete_files and path_exists:
            shutil.rmtree(folder_path)
            os.makedirs(folder_path)

    if not path_exists:
        os.makedirs(folder_path)

def __process_image(file,image_input_path,warped_output_path,lined_output_path,image_output_path,answer_key):
    puzzle_date = datetime.datetime.strptime(file.name[0:10],'%Y-%m-%d').date()
    image_raw = cv2.imread(os.path.join(image_input_path,file.name))
    
    # warp and save image
    processor = ip.ImageProcessor(image_raw)
    processor.warp_and_transform()
    
    
    cv2.imwrite(os.path.join(warped_output_path,file.name),processor.image['warped'])
    

    # slice and save individual cell images
    processor.slice_up_grid()

    # save lined images
    cv2.imwrite(os.path.join(lined_output_path,file.name),processor.image['lines_drawn'])

    # make image folder if it doesn't exist
    output_folder = os.path.join(image_output_path,"cells",os.path.splitext(file.name)[0])
    __make_folder_if_not_exists(output_folder,delete_files)
    
    # save all cells as individual images
    for i,cell in enumerate(processor.image['cells']):
        cv2.imwrite(os.path.join(output_folder,f"{str(i).rjust(4,'0')}.png"),cell)

        # save the individual cell to the letter folder it's supposed to go to
        letter_output_folder = os.path.join(image_output_path,"letters/",str(answer_key[i]))
        __make_folder_if_not_exists(letter_output_folder,False)
        letter_file_path = os.path.join(letter_output_folder, f"{os.path.splitext(file.name)[0]}-{str(i).rjust(4,'0')}.png")
        cv2.imwrite(letter_file_path, cell)

def __process_crossword(file,crosswords_input_path,crossword_output_path):
    date = datetime.datetime.strptime(file.name[0:10],'%Y-%m-%d').date()

    downloader = cd.CrosswordDownloader()
    answer_key = downloader.get_answer_key(date)
    with open(os.path.join(crossword_output_path,f"{date}.json"), "w") as text_file:
        text_file.write(json.dumps(answer_key))
    
    return answer_key

if __name__ == '__main__':
    project_dir = Path(__file__).resolve().parents[2]

    input_filepath = os.path.join(project_dir,"data/raw")
    output_filepath = os.path.join(project_dir,"data/interim")

    delete_files = True

    main(input_filepath,output_filepath,delete_files)
