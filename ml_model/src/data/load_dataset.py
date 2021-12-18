from pathlib import Path
import os
import datetime
import json
import cv2


def main(cell_input_path,crossword_input_path):

    filenames,images = __load_cells(cell_input_path)
    answers = __load_answers(crossword_input_path, filenames.keys())
    # TODO: These counts don't match.  Need to probably output these into folders based on the labelled letter to double check answers are correct
    test=1234
    
    

def __load_cells(cell_input_path):
    files = {}
    images = []

    for folder in os.scandir(cell_input_path):
        files[folder.name] = []

        for file in os.scandir(folder):
            files[folder.name].append(file.name)

        files[folder.name].sort(key=lambda x: x)

        # Load images in sorted order
        for image_name in files[folder.name]:
            image_raw = cv2.imread(os.path.join(cell_input_path,folder.name,image_name))
            images.append(image_raw)

    return (files,images)

def __load_answers(crossword_input_path, cells):

    targets = []
    # we lookp over cells because we may have examples of multiple puzzles from the same date and want to maintain the correct answers for each puzzle
    for puzzle_name in cells:
        date = datetime.datetime.strptime(puzzle_name[0:10],'%Y-%m-%d').date()
        with open(os.path.join(crossword_input_path,f'{date}.json'), 'r') as f:
            data=f.read()
            targets = targets + json.loads(data)

    return targets



if __name__ == '__main__':
    project_dir = Path(__file__).resolve().parents[2]

    cell_input_path = os.path.join(project_dir,"data/processed/image_uploads/cells")
    crossword_input_path = os.path.join(project_dir,"data/processed/nyt_answer_keys")

    main(cell_input_path,crossword_input_path)
