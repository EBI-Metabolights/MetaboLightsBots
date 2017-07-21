#!/usr/bin/env python

"""
Extact metabolites details from the study maf file

Usage: 
> python ./ExtractMetabolites -w . 
(extacts all the studies)
> python ./ExtractMetabolites -w . -s MTBLS1,MTBLS2,MTBLS3
(extacts from the 3 studies MTBLS1, MTBLS2, MTBLS3)
"""
import os
import sys
import argparse
import glob
import json
import urllib2
import zipfile
import logging
import csv
from datetime import datetime
from bs4 import BeautifulSoup

studies = []
MetaboLightsUrl = "http://www.ebi.ac.uk/metabolights/webservice/"

class readable_dir(argparse.Action):
    def __call__(self,parser, namespace, values, option_string=None):
        prospective_dir=values
        if not os.path.isdir(prospective_dir):
            raise argparse.ArgumentTypeError("readable_dir:{0} is not a valid path".format(prospective_dir))
        if os.access(prospective_dir, os.R_OK):
            setattr(namespace,self.dest,prospective_dir)
        else:
            raise argparse.ArgumentTypeError("readable_dir:{0} is not a readable dir".format(prospective_dir))

def fetchMetaboLightsStudiesList():
    global studies
    global MetaboLightsUrl
    MetaboLightsStudiesList = MetaboLightsUrl + "study/list"
    response = urllib2.urlopen(MetaboLightsStudiesList)
    studies = json.loads(response.read())['content']

def main(arguments):
    # Parsing input parameters
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-l', '--launch_directory', action=readable_dir, default = "" )
    parser.add_argument('-w', '--destination', action=readable_dir, default="", help="Output directory")
    parser.add_argument('-s', '--studies', help="Studies list")
    args = parser.parse_args(arguments)
    
    global studies

    # Reading lauching directory and log file details
    root = args.launch_directory
    destination = args.destination
    if(root == ""):
        root = os.getcwd();
    
    if(destination == ""):
        destination = os.getcwd();

    inputStudies = args.studies

    if inputStudies == None:
        fetchMetaboLightsStudiesList()
    else:
        studies = str(inputStudies).split(",")

    fieldnames = ["StudyID", "totalMetabolites", "totalIdentifiedMetabolites"]
    rows = []

    for study in studies:
        print study
        studyID = study.strip().upper()
        MetaboLightsStudyData = MetaboLightsUrl + "study/" + study
        response = urllib2.urlopen(MetaboLightsStudyData)
        studyData = json.loads(response.read())['content']
        assaysCount =  len(studyData['assays'])
        row = {}
        totalCompounds = 0
        totalIdentifiedCompounds = 0
        for i in range(0, assaysCount):
            metabolitesLines = json.loads(urllib2.urlopen( "http://www.ebi.ac.uk/metabolights/webservice/study/" + study + "/assay/" + str(i+1) + "/maf").read())["content"]['metaboliteAssignmentLines']
            if metabolitesLines != None:
                totalCompounds = totalCompounds + len(metabolitesLines)
                identifiedMetabolites = []
                for line in metabolitesLines:
                    dbID = str(line['databaseIdentifier'])
                    if dbID != '': # and "CHEBI" in  dbID
                        if dbID not in identifiedMetabolites:
                            identifiedMetabolites.append(dbID)
            totalIdentifiedCompounds = totalIdentifiedCompounds + len(identifiedMetabolites)
        row['StudyID'] = study
        row['totalMetabolites'] = totalCompounds
        row['totalIdentifiedMetabolites'] = totalIdentifiedCompounds
        rows.append(row)

    with open( destination + "/" + 'output.tsv', 'w') as csvfile:
        writer = csv.DictWriter(csvfile, delimiter='\t', fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))