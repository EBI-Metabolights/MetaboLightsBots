#!/usr/bin/env python

# Author: Venkata chandrasekhar Nainala 
# Version: 0.1.0
# Email: mailcs76@gmail.com / venkata@ebi.ac.uk

""" A python crawler to iterate MetaboLights Studies/Compounds and execute specified scripts
"""

import os
import sys
import json
import urllib2
import utils
import argparse
from os.path import basename
import subprocess

workingDirectory = ""
MetaboLightsUrl = "http://www.ebi.ac.uk/metabolights/webservice/"
MetaboLightsCompoundsList = MetaboLightsUrl + "compounds/list"
metabolites = []

def main(arguments):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--request", help="- Import request (all/missing) ", default="missing")
    args = parser.parse_args(arguments)
    request = args.request
    global metabolites
    workingDirectory = "/net/isilonP/public/rw/homes/tc_cm01/metabolights/scripts/MetaboLightsBots/"
    destinationDirectory = "/net/isilonP/public/rw/homes/tc_cm01/metabolights/reference/"
    
    workingDirectory = workingDirectory + "resources"
    mlSCMappingFile = workingDirectory + "/mapping.json"
    reactomeJSONFile = workingDirectory + "/reactome.json"

    utils.generateMLStudyCompoundMappingFile(mlSCMappingFile)
    utils.getReactomeData(reactomeJSONFile)

    if (request == "missing"):
        subprocess.call(["python", "PatrolBot.py", workingDirectory, destinationDirectory])
        with open( workingDirectory + '/MetabolitesReport.json') as reportFile:
            global reportData
            reportData = json.load(reportFile)

        missingMetabolites = []
        for key in reportData:
            report = reportData[key]
            if report['rating'] == 0:
                missingMetabolites.append(key)
        compoundBatches = []
        batches = 10
        interval = len(missingMetabolites)/batches
        current = 0
        for i in range(0, batches):
            compoundsTempList = missingMetabolites[current: current + interval]
            compoundsTempListString = '"' + ', '.join(compoundsTempList) + '"'
            compoundBatches.append(compoundsTempListString)
            current = current + interval
        procs = [subprocess.Popen(["python", "MLCompoundsBot.py",workingDirectory, destinationDirectory, cp]) for cp in compoundBatches]
        for proc in procs:
            proc.wait()
        if any(proc.returncode != 0 for proc in procs):
            print "Error importing missing compound's Data"
    else:
        fetchMetaboLightsCompoundsList()
        compoundBatches = []
        batches = 10
        interval = len(metabolites)/batches
        current = 0
        for i in range(0, batches):
            compoundsTempList = metabolites[current: current + interval]
            compoundsTempListString = '"' + ', '.join(compoundsTempList) + '"'
            compoundBatches.append(compoundsTempListString)
            current = current + interval
        procs = [subprocess.Popen(["python", "MLCompoundsBot.py",workingDirectory, destinationDirectory, cp]) for cp in compoundBatches]
        for proc in procs:
            proc.wait()
        if any(proc.returncode != 0 for proc in procs):
            print "Error reimporting all compound's data"
    
def fetchMetaboLightsCompoundsList():
    global metabolites
    response = urllib2.urlopen(MetaboLightsCompoundsList)
    metabolites = json.loads(response.read())['content']

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
