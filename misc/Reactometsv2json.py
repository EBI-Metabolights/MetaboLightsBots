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
import argparse
from os.path import basename

workingDirectory = ""
ReactomeUrl = "http://www.reactome.org/download/current/ChEBI2Reactome.txt"
ReactomeFile = "reactome.txt"
ReactomeJSON = {}

def main(arguments):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    args = parser.parse_args(arguments)
    fetchReactomeData(ReactomeFile)

def fetchReactomeData(reactomeFile):
    with open(reactomeFile) as f:
        for line in f:
            dataArray = line.split("\t")
            metabolightsId = "MTBLC" + str(dataArray[0])
            tempDic = {}
            tempDic['reactomeId'] = str(dataArray[1])
            tempDic['reactomeUrl'] = str(dataArray[2])
            tempDic['pathway'] = str(dataArray[3])
            tempDic['pathwayId'] = str(dataArray[4])
            tempDic['species'] = str(dataArray[5])
            if metabolightsId not in ReactomeJSON:
                ReactomeJSON[metabolightsId] = [tempDic]
            else:
                ReactomeJSON[metabolightsId].append(tempDic)
    writeDataToFile("reactome.json", ReactomeJSON)

def writeDataToFile(filename, data):
    with open(filename, "w") as fp:
        json.dump(data, fp)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))