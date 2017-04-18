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
import urllib2
import json

destinationDirectory = ""
workingDirectory = ""
globalReport = {}
metabolites = []
MetaboLightsUrl = "http://www.ebi.ac.uk/metabolights/webservice/"
MetaboLightsCompoundsList = MetaboLightsUrl + "compounds/list"

def main(arguments):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("workingdirectory", help="- Working directory location")
    parser.add_argument("destinationdirectory", help="- Destination Directory")
    args = parser.parse_args(arguments)
    global workingDirectory
    global destinationDirectory
    workingDirectory = args.workingdirectory
    destinationDirectory = args.destinationdirectory
    global globalReport
    # Check if the folder structure exist and create if it doesn't
    if not os.path.exists(workingDirectory):
        os.makedirs(workingDirectory)

    fetchMetaboLightsCompoundsList()

    # log file configuration
    logging.basicConfig(filename=workingDirectory+"/patrol.log",level=logging.DEBUG)

    for metabolite in metabolites:
        try:
            logging.info("-----------------------------------------------")
            logging.info("Reporting: " + metabolite)
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
            filePath = destinationDirectory + metabolite + "/" + metabolite + "_data.json"
            tempCompoundReport = checkIfFileEmptyOrNotExist(filePath, tempCompoundReport)
            if tempCompoundReport["rating"] != 0:
                tempCompoundReport = setFlags(filePath, tempCompoundReport)
            globalReport[metabolite] = tempCompoundReport
        except:
            logging.info("failed : " + metabolite + " <<<<<<<<")
            pass
    writeDataToFile(workingDirectory + "/MetabolitesReport.json" , globalReport);

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
        if metabolite["structure"]:
            tempCompoundReport["flags"]["has3d"] = "true"
    return tempCompoundReport

def checkIfFileEmptyOrNotExist(file_path, tempCompoundReport):
    if not os.path.exists(file_path):
        tempCompoundReport['rating'] = 0
    else:
        if os.stat(file_path).st_size == 0:
            tempCompoundReport['rating'] = 0
    return tempCompoundReport

def fetchMetaboLightsCompoundsList():
    global metabolites
    response = urllib2.urlopen(MetaboLightsCompoundsList)
    metabolites = json.loads(response.read())['content']

def writeDataToFile(filename, data):
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    with open(filename, "w") as fp:
        json.dump(data, fp)

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))