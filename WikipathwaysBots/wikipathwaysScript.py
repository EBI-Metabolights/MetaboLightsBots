#!/usr/bin/env python

# Author: Venkata chandrasekhar Nainala 
# Version: 0.1.0
# Email: mailcs76@gmail.com / venkata@ebi.ac.uk

""" A python script to generate Wikipathways - MetaboLights Enrichment spread sheet
"""

import os
import sys
import json
import urllib2
import argparse
from os.path import basename
import csv

workingDirectory = ""
MetaboLightsUrl = "http://www.ebi.ac.uk/metabolights/webservice/"
MetaboLightsStudyUrl = "http://www.ebi.ac.uk/metabolights/webservice/study/"
MetaboLightsStudiesList = MetaboLightsUrl + "study/list"
MetaboLightsCompoundsList = MetaboLightsUrl + "compounds/list"

mt = {}
studies = []
metabolites = []
fieldnames = []
mlmapping = {}

def main(arguments):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("mapfile", help="- Mapping file location")
    args = parser.parse_args(arguments);

    mapfile = args.mapfile
    with open(mapfile) as mapping_file:  
        global mlmapping
        mlmapping = json.load(mapping_file)

    fetchMetaboLightsStudiesList();
    fetchMetaboLightsCompoundsList();

    fieldnames = ["MetabolightsId", "ChEBIId"]

    totalCompoundsIdentifiedRow = {
        "MetabolightsId" : "",
        "ChEBIId" : ""
    }
    for study in studies:
        count  = 0
        if study in mlmapping["studyMapping"]:
            count = len(mlmapping["studyMapping"][study])
        fieldnames.append(study)
        totalCompoundsIdentifiedRow[study] = count
    rows = []

    for compound in metabolites:
        row = {}
        chebiString = compound.replace("MTBLC", "CHEBI:")
        row["MetabolightsId"] = compound
        row["ChEBIId"] = chebiString
        compoundMapping  = {}
        if chebiString in mlmapping["compoundMapping"]:
            compoundMapping  =  mlmapping["compoundMapping"][chebiString];

        for study in studies:
            row[study] = 0
            for stdy in compoundMapping:
                if study == stdy["study"]:
                    row[study] = 1
                    
        rows.append(row)

    with open('wikipathways.csv', 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(totalCompoundsIdentifiedRow)
        for row in rows:
            writer.writerow(row)
        



def fetchMetaboLightsStudiesList():
    global studies
    response = urllib2.urlopen(MetaboLightsStudiesList)
    studies = json.loads(response.read())['content']

def fetchMetaboLightsCompoundsList():
    global metabolites
    response = urllib2.urlopen(MetaboLightsCompoundsList)
    metabolites = json.loads(response.read())['content']

def writeDataToFile(filename, data):
    with open(filename, "w") as fp:
        json.dump(data, fp)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))