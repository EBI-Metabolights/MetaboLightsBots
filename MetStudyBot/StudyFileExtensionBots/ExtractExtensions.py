#!/usr/bin/env python

"""Script to extract file extension details
"""
import os
import sys
import argparse
import glob
import json
import zipfile
from datetime import datetime
import logging

logFile = "/ebi/ftp/pub/databases/metabolights/study_file_extensions/ml_file_extension.log"
logging.basicConfig(filename=logFile, level=logging.INFO)
logger = logging.getLogger("ML Bot")

class readable_dir(argparse.Action):
    def __call__(self,parser, namespace, values, option_string=None):
        prospective_dir=values
        if not os.path.isdir(prospective_dir):
            raise argparse.ArgumentTypeError("readable_dir:{0} is not a valid path".format(prospective_dir))
        if os.access(prospective_dir, os.R_OK):
            setattr(namespace,self.dest,prospective_dir)
        else:
            raise argparse.ArgumentTypeError("readable_dir:{0} is not a readable dir".format(prospective_dir))

def get_file_extensions(id , path , fe_json):
    logger = logging.getLogger("ML Bot")
    study_ext = {}
    study_ext['list'] = []
    study_ext['ext_count'] = {}
    for root, dirs, files in os.walk(path):
        for file in files:
            try:
                extension = os.path.splitext(file)[1]
                if extension:
                    if extension not in study_ext['list']:
                        study_ext['list'].append(extension)
                    if extension == '.zip':
                        edata = extractZip(path,file,study_ext['list'],study_ext['ext_count'])
                        study_ext['list'] = edata[0]
                        study_ext['ext_count'] = edata[1]
                    if extension in study_ext['ext_count']:
                        study_ext['ext_count'][extension] = study_ext['ext_count'][extension] + 1
                    else:
                        study_ext['ext_count'][extension] = 1
            except:
                logger.error("Error file details: " + file)
                logger.error(sys.exc_info())
    extensions = study_ext['list']
    extensions_count = study_ext['ext_count']
    study_ext = { 'id' : id }
    study_ext['extensions'] = extensions
    study_ext['extensions_count']  = extensions_count
    return study_ext

def extractZip(filepath, file, list, count):
    zfile = zipfile.ZipFile(os.path.join(filepath, file))
    for finfo in zfile.infolist():
        extension = os.path.splitext(finfo.filename)[1]
        if extension:
            if extension not in list:
                list.append(extension)
            if extension in count:
                count[extension] = count[extension] + 1
            else:
                count[extension] = 1
    return [list, count]

def main(arguments):
    # Parsing input parameters
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-l', '--launch_directory', action=readable_dir, default = "/ebi/ftp/pub/databases/metabolights/studies/public/" )
    parser.add_argument('-w', '--working_directory', action=readable_dir, default="/ebi/ftp/pub/databases/metabolights/study_file_extensions/", help="Output directory")
    args = parser.parse_args(arguments)
    # Reading lauching directory and log file details
    root = args.launch_directory
    outputJSONFile = args.working_directory + "ml_file_extension.json"
    errorFile = args.working_directory + "ml_file_extension.error"
    # Initialising logging setup
    now = datetime.now()
    logger.info("Started extracting file extensions: " + now.strftime("%Y-%m-%d %H:%M"))
    logger.info("Working directory: " + root)
    logger.info("Log File: " + logFile)
    # Get list of studies (Public)
    studies = [name for name in os.listdir(root) if os.path.isdir(os.path.join(root, name))]
    logger.info("Fetching studies list: " + str(len(studies)))
    file_ext = []
    # Iterate over each study and extract data
    for study in studies:
        logger.info("Extracting study extension details: " + study)
        print study
        wd = os.path.join(root, study)
        try:
            file_ext.append(get_file_extensions(study, wd , file_ext))
        except:
            logger.error("Error extracting study extension details: " + study)
            logger.error(sys.exc_info())
    with open(outputJSONFile, 'w') as outfile:
        json.dump(file_ext, outfile)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))