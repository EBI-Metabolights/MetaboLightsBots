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
from random import randint

destinationDirectory = ""
workingDirectory = ""
mlSCMappingFile = ""
reactomeJSONFile = ""
ftp = ""

reactomeData = {}
mlMapping = {}
requestedCompound = ""

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
    parser.add_argument('-c', '--compound', help="- MetaboLights Compound Identifier", default="all")
    parser.add_argument('-f', '--ftp', action=readable_dir, default="/ebi/ftp/pub/databases/metabolights/compounds/", help="FTP directory")
    args = parser.parse_args(arguments)
    global workingDirectory
    global destinationDirectory
    global requestedCompound
    global ftp

    workingDirectory = args.launch_directory
    destinationDirectory = args.destination
    requestedCompound = args.compound.replace('"','')
    ftp = args.ftp

    if(workingDirectory == ""):
        workingDirectory = os.getcwd();

    # log file configuration
    st = utils.getDateAndTime();
    randomInt = str(randint(1, 1000))
    logDirectory = workingDirectory + "/logs/" + st 
    if not os.path.exists(logDirectory):
        os.makedirs(logDirectory)
    logging.basicConfig(filename= logDirectory + "/log_" +randomInt +".log",level=logging.DEBUG)
    utils.init(logging)
    logging.info("-----------------------------------------------")
    logging.info('# Run started -' + utils.getDateAndTime())

    logging.info('Generating MetaboLights Study - Compound Mapping file')

    global mlSCMappingFile
    mlSCMappingFile = ftp + "mapping.json"

    global reactomeJSONFile
    reactomeJSONFile = ftp + "reactome.json"

    with open(reactomeJSONFile) as reactome_file:
        global reactomeData
        reactomeData = json.load(reactome_file)
    
    with open(mlSCMappingFile) as mapping_file:  
        global mlMapping
        mlMapping = json.load(mapping_file)

    if (requestedCompound != "all") :
        requestCompoundsList = requestedCompound.split(",")
        for compound in requestCompoundsList:
            utils.fetchCompound(compound.strip(), workingDirectory, destinationDirectory, reactomeData, mlMapping)
    else:
        MLCompoundsList = utils.fetchMetaboLightsCompoundsList()
        for compound in MLCompoundsList:
            utils.fetchCompound(compound, workingDirectory, destinationDirectory, reactomeData, mlMapping)

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))