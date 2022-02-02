from flask import Flask, render_template, send_from_directory, request, redirect
from pathlib import Path
import os
import shutil

app = Flask(__name__)

PROJECT_DIR = Path(__file__).resolve().parents[2]
INPUT_IMAGES = "ml_model/data/interim/image_uploads/letters"
OUTPUT_IMAGES = "ml_model/data/processed/image_uploads/letters"

@app.route("/")
def label_data():
    images_to_label = __identify_unverified_files(INPUT_IMAGES,OUTPUT_IMAGES)
    short_list = images_to_label[:10]
    images_remaining = len(images_to_label)
    return render_template("label_data.html",image_list = short_list, images_remaining = images_remaining)


# We use this hack to serve images from outside the flask project directory
@app.route('/img/<path:path>')
def send_img(path):
    input_images = os.path.join(PROJECT_DIR,"ml_model/data/interim/image_uploads/letters")
    return send_from_directory(input_images, path)

@app.route('/save_labels', methods=['post'])
def save_labels():
    items = request.form

    # Build a dictionary from the form data that is easier to work with
    labeled_data = {}

    for item in items:
        field_name = item.split("__")[0]
        index = item.split("__")[1]
        value = request.form[item]

        if f"data_{index}" not in labeled_data:
            labeled_data[f"data_{index}"] = {}
        
        labeled_data[f"data_{index}"][field_name] = value

    # Copy files to final location
    
    for key,value in labeled_data.items():

        __make_folder_if_not_exists(os.path.join(PROJECT_DIR,OUTPUT_IMAGES,value['corrected_label']),False)

        src = os.path.join(PROJECT_DIR,INPUT_IMAGES,value['original_label'],value['original_filename'])
        dst = os.path.join(PROJECT_DIR,OUTPUT_IMAGES,value['corrected_label'],value['original_filename'])
        #print(f"Moving {src} to {dst}")
        shutil.copyfile(src,dst)

    return redirect('/')

def __identify_unverified_files(input,output):

    # Get a list of files in all subdirectories of input and output paths
    input_files = __flatten_directories(os.path.join(PROJECT_DIR,input))
    output_files = __flatten_directories(os.path.join(PROJECT_DIR,output))

    # Delete any input files already present somewhere in the output directory
    to_verify=input_files.copy()

    for input_item in input_files:
        for output_item in output_files:
            if input_item['filename'] == output_item['filename']:
                print(f"Removing {output_item['filename']}")
                to_verify.remove(input_item)
                break
    
    # At this point, all items in the to_verify array still need to be labelled/verified
    return sorted(to_verify, key=lambda k: (k['folder'], k['filename']))

# Traveerse a directory (and subdirectories) and return in a flattened list structure
def __flatten_directories(directory):
    input_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            obj={}
            obj['folder'] = os.path.basename(root)
            obj['filename'] = file
            input_files.append(obj)

    return input_files

def __make_folder_if_not_exists(folder_path,delete_files):
    path_exists = os.path.exists(folder_path)

    if delete_files and path_exists:
            shutil.rmtree(folder_path)
            os.makedirs(folder_path)

    if not path_exists:
        os.makedirs(folder_path)


