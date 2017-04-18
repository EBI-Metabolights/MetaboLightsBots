#!/usr/bin/env python

"""A simple python script template.
"""

import os
import sys
import argparse
import glob
import json
import zipfile
from datetime import datetime
import logging

logFile = "/ebi/ftp/pub/databases/metabolights/study_file_extensions/study_file_details/error.log"
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

def path_to_dict(path):
    logger = logging.getLogger("ML Bot")
    try:
        d = {'name': os.path.basename(path)}
        filename, file_extension = os.path.splitext(path)
        if os.path.isdir(path):
            d['type'] = "directory"
            d['children'] = [path_to_dict(os.path.join(path,x)) for x in os.listdir(path)]
        elif file_extension == ".zip":
            d['type'] = "directory"
            d['children'] = read_zip_file(path, os.path.basename(path))
        else:
            d['type'] = "file"
        return d
    except:
        logger.error("Error: " + path)
        logger.error(sys.exc_info())

def read_zip_file(filepath, filename):
    zfile = zipfile.ZipFile(filepath)
    root = os.path.splitext(filename)[0] + "/"
    zipFilesList = []
    for finfo in zfile.infolist():
        zipFilesList.append(finfo.filename)
    return getTree(root,zipFilesList, [])[0]

def getTree(folderName, filesList, scannedList):
    el = []
    for file in filesList:
        if folderName in file:
            if file != folderName and file not in scannedList:
                e = {'name': file}
                if file.endswith('/'):
                    e['type'] = "directory"
                    temparr = getTree(file, filesList, scannedList)
                    e['children'] = temparr[0]
                    scannedList = scannedList + temparr[1]
                    scannedList.append(file)
                    el.append(e)
                else:
                    e['type'] = "file"
                    scannedList.append(file)
                    el.append(e)
    return [ el , scannedList ]

def main(arguments):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-l', '--launch_directory', action=readable_dir, default = "/ebi/ftp/pub/databases/metabolights/studies/public/" )
    parser.add_argument('-o', '--output_directory', action=readable_dir, default="/ebi/ftp/pub/databases/metabolights/study_file_extensions/study_file_details/", help="Output folder")
    args = parser.parse_args(arguments)
    root = args.launch_directory
    now = datetime.now()
    logger.info("Started creating folder tree: " + now.strftime("%Y-%m-%d %H:%M"))
    studies = [name for name in os.listdir(root) if os.path.isdir(os.path.join(root, name))]
    for study in studies:
        wd = os.path.join(root, study)
        logger.info("Extracting folder tree: " + study)
        try:
            jsonData = path_to_dict(wd)
            output_file =  os.path.join(args.output_directory, study + ".json")
            with open(output_file, 'w') as outfile:
                json.dump(jsonData, outfile)
            print output_file
            logger.info("Done creating tree: " + output_file)
        except:
            logger.error("Error extracting study tree: " + study)
            logger.error(sys.exc_info())
    #/homes/venkata/studies_json/
    #/net/isilonP/public/rw/homes/tc_cm01/metabolights/prod/studies/stage/private/
    #json.dump(path_to_dict(args.launch_directory), args.outfile)
if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))