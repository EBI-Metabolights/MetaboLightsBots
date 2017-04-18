#!/usr/bin/env python

# Author: Venkata chandrasekhar Nainala 
# Version: 0.1.0
# Email: mailcs76@gmail.com / venkata@ebi.ac.uk
# Date: 22 March 2016

""" A python script to scrape metabolite data from various online resources
    This script accepts the following command line argument(s):
        - study : MetaboLights Study Identifies (String)
	    Usage: python MetCompoundBot.py <MTBLC{}>
        Example:  python MetaboLightsBot.py "/Users/venkata/Development/MetaboLightsBots/resources/" "/net/isilonP/public/rw/homes/tc_cm01/metabolights/reference/"
    Dependencies:
        Python 2.7
"""
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

studies = []
studiesList = {}
compoundsList = {}

MetaboLightsUrl = "http://www.ebi.ac.uk/metabolights/webservice/"
MetaboLightsStudyUrl = "http://www.ebi.ac.uk/metabolights/webservice/study/"
MetaboLightsStudiesList = MetaboLightsUrl + "study/list"

def main(arguments):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("resourcesdirectory", help="- Addon files location")
    parser.add_argument("workingdirectory", help="- Working Directory")
    # Parsing command line arguments
    args = parser.parse_args(arguments)
    resourcesDirectory = args.resourcesdirectory
    workingDirectory = args.workingdirectory
    global logFile
    logFile = resourcesDirectory + "run.log"
    log("Import Started")

def log(data):
	print logFile
	writeDataToFile(logFile,data,"a")

def writeDataToFile(filename, data, mode):
	if not os.path.exists(os.path.dirname(filename)):
	    try:
	    	os.makedirs(os.path.dirname(filename))
	    except OSError as exc: # Guard against race condition
	    	if exc.errno != errno.EEXIST:
	    		raise
	 	with open(filename, mode) as fp:
	 		json.dump(data, fp)

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))