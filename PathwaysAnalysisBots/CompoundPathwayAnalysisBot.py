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

compoundsList = []

MetaboLightsWSUrl = "http://www.ebi.ac.uk/metabolights/webservice/"
MetaboLightsWSStudyUrl = "http://www.ebi.ac.uk/metabolights/webservice/study/"
MetaboLightsWSCompoundsList = MetaboLightsWSUrl + "compounds/list"
MetaboLightsWSCompoundData = MetaboLightsWSUrl + "beta/compound/"

def main(arguments):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("resourcesdirectory", help="- Addon files location")
    parser.add_argument("workingdirectory", help="- Working Directory")
    # Parsing command line arguments
    args = parser.parse_args(arguments)
    resourcesDirectory = args.resourcesdirectory
    workingDirectory = args.workingdirectory
    compoundsList = fetchMetaboLightsCompoundsList()
    count = 0
    for compound in compoundsList:
        compoundPathways = getCompound(compound)['pathways']
        if (len(compoundPathways) > 0):
            print compound+ "-" + str(len(compoundPathways["KEGGPathways"])) + "-" + str(len(compoundPathways["ReactomePathways"])) + "-" + str(len(compoundPathways["WikiPathways"]))
            count += 1
 
    print count


def getCompound(compound):
    response = urllib2.urlopen(MetaboLightsWSCompoundData + compound)
    return json.loads(response.read())

def fetchMetaboLightsCompoundsList():
    response = urllib2.urlopen(MetaboLightsWSCompoundsList)
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