#!/usr/bin/env python

# Author: Venkata chandrasekhar Nainala 
# Version: 0.1.0
# Email: mailcs76@gmail.com / venkata@ebi.ac.uk
# Date: 19 May 2016

""" 
    Dependencies:
        Python 2.7
"""
import sys
import argparse
import utils
import logging
import os
import time
import json
import subprocess
from random import randint

destinationDirectory = ""
workingDirectory = ""
ftp = ""

globalReport = {}

class readable_dir(argparse.Action):
    def __call__(self,parser, namespace, values, option_string=None):
        prospective_dir=values
        if not os.path.isdir(prospective_dir):
            raise argparse.ArgumentTypeError("readable_dir:{0} is not a valid path".format(prospective_dir))
        if os.access(prospective_dir, os.R_OK):
            setattr(namespace,self.dest,prospective_dir)
        else:
            raise argparse.ArgumentTypeError("readable_dir:{0} is not a readable dir".format(prospective_dir))

def main(arguments):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-l', '--launch_directory', action=readable_dir, default = "" )
    parser.add_argument('-w', '--destination', action=readable_dir, help="Output directory", default="/nfs/www-prod/web_hx2/cm/metabolights/prod/reference/")
    parser.add_argument('-f', '--ftp', action=readable_dir, default="/ebi/ftp/pub/databases/metabolights/compounds/", help="FTP directory")
    args = parser.parse_args(arguments)
    global workingDirectory
    global destinationDirectory
    global ftp
    global globalReport

    workingDirectory = args.launch_directory
    destinationDirectory = args.destination
    ftp = args.ftp

    if(workingDirectory == ""):
        workingDirectory = os.getcwd();

    # log file configuration
    st = utils.getDateAndTime();
    randomInt = str(randint(1, 1000))
    logDirectory = workingDirectory + "/logs/exporter_" + st 
    if not os.path.exists(logDirectory):
        os.makedirs(logDirectory)
    logging.basicConfig(filename= logDirectory + "/log_" +randomInt +".log",level=logging.DEBUG)
    utils.init(logging)
    logging.info("-----------------------------------------------")
    logging.info('# Run started -' + utils.getDateAndTime())

    requestCompoundsList = utils.fetchMetaboLightsCompoundsList()
    for compound in requestCompoundsList:
        logging.info("-----------------------------------------------")
        try:
            logging.info("Exporting: " + compound)
            tempCompoundReport = {
                "rating" : 5,
                "flags": {
                    "hasInchiKey": False,
                    "hasLiterature": False,
                    "hasReactions": False,
                    "hasNMR": False,
                    "hasSpecies": False,
                    "hasMS": False,
                    "hasPathways": False,
                    "has3d": False
                }
            }
            filePath = destinationDirectory + compound + "/" + compound + "_data.json"
            tempCompoundReport = checkIfFileEmptyOrNotExist(filePath, tempCompoundReport)
            if tempCompoundReport["rating"] != 0:
                tempCompoundReport = setFlags(filePath, tempCompoundReport)
            else:
                logging.warning("WARNING: Missing data - " + compound)
            globalReport[compound] = tempCompoundReport
        except:
            logging.warning("Error: " + compound)
            pass
    utils.writeDataToFile(ftp + "ml_flags.json" , globalReport);

def setFlags(file_path, tempCompoundReport):
    with open(file_path) as compoundData:
        metabolite = json.load(compoundData)
        if metabolite["inchiKey"]:
            tempCompoundReport["flags"]["hasInchiKey"] = "true"
        tempCompoundReport["flags"]["hasLiterature"] = metabolite["flags"]["hasLiterature"]
        tempCompoundReport["flags"]["hasNMR"] = metabolite["flags"]["hasNMR"]
        tempCompoundReport["flags"]["hasMS"] = metabolite["flags"]["hasMS"]
        tempCompoundReport["flags"]["hasPathways"] = metabolite["flags"]["hasPathways"]
        tempCompoundReport["flags"]["hasReactions"] = metabolite["flags"]["hasReactions"]
        tempCompoundReport["flags"]["hasSpecies"] = metabolite["flags"]["hasSpecies"]
        if metabolite["structure"]:
            tempCompoundReport["flags"]["has3d"] = "true"
    return calculateRating(tempCompoundReport)

def checkIfFileEmptyOrNotExist(file_path, tempCompoundReport):
    if not os.path.exists(file_path):
        tempCompoundReport['rating'] = 0
    else:
        if os.stat(file_path).st_size == 0:
            tempCompoundReport['rating'] = 0
    return tempCompoundReport

def calculateRating(tempCompoundReport):
    if tempCompoundReport['rating'] != 0:
        tempCompoundReport['rating'] = 0
        if tempCompoundReport["flags"]["hasInchiKey"] == "true":
            tempCompoundReport['rating'] += 1
        if tempCompoundReport["flags"]["hasNMR"] == "true" or tempCompoundReport["flags"]["hasMS"] == "true":
            tempCompoundReport['rating'] += 1
        if tempCompoundReport["flags"]["hasPathways"]== "true":
            tempCompoundReport['rating'] += 1
        if tempCompoundReport["flags"]["hasReactions"]== "true":
            tempCompoundReport['rating'] += 1
        if tempCompoundReport["flags"]["hasSpecies"]== "true":
            tempCompoundReport['rating'] += 1
    return tempCompoundReport

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))