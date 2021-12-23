from flask import Flask, render_template
from pathlib import Path
import os

app = Flask(__name__)

@app.route("/")
def label_data():
    images_to_label = __identify_unverified_files("ml_model/data/interim/image_uploads/letters","ml_model/data/processed/image_uploads/letters")

    return render_template("label_data.html",image_list = images_to_label)

def __identify_unverified_files(input,output):
    project_dir = Path(__file__).resolve().parents[2]
    
    # Get a list of files in all subdirectories of input and output paths
    input_files = __flatten_directories(os.path.join(project_dir,input))
    output_files = __flatten_directories(os.path.join(project_dir,output))

    print(len(input_files))
    # Delete any input files already present somewhere in the output directory
    for input_item in input_files:
        for output_item in output_files:
            if input_item['filename'] == output_item['filename']:
                input_files.remove(input_item)
                break
    
    # At this point, all items in the input_files array still need to be labelled/verified
    return input_files

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



