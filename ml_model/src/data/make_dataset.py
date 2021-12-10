import logging
from pathlib import Path
import os

def test_func():
    return "hello world"

def main(input_filepath, output_filepath):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger(__name__)
    logger.info('making final data set from raw data')

    for file in os.scandir(input_filepath):
        print(file.path)

if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    project_dir = Path(__file__).resolve().parents[2]
    input_filepath = os.path.join(project_dir,"data/raw")
    output_filepath = os.path.join(project_dir,"data/processed")
    main(input_filepath,output_filepath)
