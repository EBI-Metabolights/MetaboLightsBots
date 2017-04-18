#!/usr/bin/env python

# Author: Venkata chandrasekhar Nainala 
# Version: 0.1.0
# Email: mailcs76@gmail.com / venkata@ebi.ac.uk

import os
import sys
import time
import datetime
import logging
import argparse
import threading
import math

import json
import shutil
import urllib2
import re
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

resourcesDirectory = ""
workingDirectory = ""
logFile = ""

studiesList = []
compoundsList = []

MetaboLightsWSUrl = "http://www.ebi.ac.uk/metabolights/webservice/"
MetaboLightsWSStudyUrl = "http://www.ebi.ac.uk/metabolights/webservice/study/"
MetaboLightsWSStudiesList = MetaboLightsWSUrl + "study/list"
MetExploreMapping = "/getMetExploreMappingData"
MetaboLightsWSGetInChI = "/getMetabolitesInchi"
pathwayMappings = {}
HierarchicalEdgeBundlingData = []
def main(arguments):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("resourcesdirectory", help="- Addon files location")
    parser.add_argument("workingdirectory", help="- Working Directory")
    # Parsing command line arguments
    args = parser.parse_args(arguments)
    resourcesDirectory = args.resourcesdirectory
    workingDirectory = args.workingdirectory
    studiesList = fetchMetaboLightsStudiesList()
    MetExploreMappingStudiesList = []
    NoMetExploreMappingStudiesList = []
    for study in studiesList:
        if len(getMetInChI(study)) > 0 :
            metExData = getMetExploreMappingData(study).strip()
            if metExData != "":
                size = getSize(metExData, study)
                if size > 0 :
                    HierarchicalEdgeBundlingStudyData = {}
                    MetExploreMappingStudiesList.append(study)
                    HierarchicalEdgeBundlingStudyData['name'] = study
                    HierarchicalEdgeBundlingStudyData['size'] = size
                    HierarchicalEdgeBundlingData.append(HierarchicalEdgeBundlingStudyData)
                else:
                    HierarchicalEdgeBundlingStudyData = {}
                    HierarchicalEdgeBundlingStudyData['name'] = study
                    HierarchicalEdgeBundlingStudyData['size'] = 0
                    HierarchicalEdgeBundlingStudyData['imports'] = []
                    HierarchicalEdgeBundlingData.append(HierarchicalEdgeBundlingStudyData)
        else:
            NoMetExploreMappingStudiesList.append(study)
    writeDataToFile("./studyPathwayMapping.json", pathwayMappings)
    getImports()
    writeDataToFile("./HierarchicalEdgeBundlingData.json",HierarchicalEdgeBundlingData)

def getImports():
    for item in HierarchicalEdgeBundlingData:
        if item['size'] > 0:
            similarPathwaysMappedStudies = []
            tempStudy = item['name']
            for pathway in pathwayMappings[tempStudy]:
                for studyKey in pathwayMappings:
                    if studyKey != tempStudy:
                        if pathway in pathwayMappings[studyKey]:
                            if studyKey not in similarPathwaysMappedStudies:
                                similarPathwaysMappedStudies.append(studyKey)
            item['imports'] = similarPathwaysMappedStudies

def getSize(metExData, study):
    metExploreMapping = json.loads(metExData)
    pathwaysList = metExploreMapping['pathwayList']
    length = 0
    mappedMetabolitePathways = []
    for pathway in pathwaysList:
        if pathway['mappedMetabolite'] > 0:
            if (("Transport" not in pathway['name']) and ("Exchange" not in pathway['name'])):
                length = length + 1
                mappedMetabolitePathways.append(pathway['dbIdentifier'])
    pathwayMappings[study] = mappedMetabolitePathways
    return len(mappedMetabolitePathways)

def getMetInChI(study):
    getMetInChIURL = MetaboLightsWSStudyUrl + study + MetaboLightsWSGetInChI
    response = urllib2.urlopen(getMetInChIURL)
    data = json.loads(response.read())['content']
    if data:
        return data
    else:
        return []

def getMetExploreMappingData(study):
    mappingDataURL= MetaboLightsWSStudyUrl + study + MetExploreMapping;
    response = urllib2.urlopen(mappingDataURL)
    data = json.loads(response.read())['content']
    if data:
        return data
    else:
        return ""

def fetchMetaboLightsStudiesList():
    response = urllib2.urlopen(MetaboLightsWSStudiesList)
    return json.loads(response.read())['content']

def writeDataToFile(filename, data):
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise
    with open(filename, "w") as fp:
        json.dump(data, fp)

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))