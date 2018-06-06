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
MetaboLightsUrl = "http://www.ebi.ac.uk/metabolights/webservice/"
MetaboLightsStudyUrl = "http://www.ebi.ac.uk/metabolights/webservice/study/"
MetaboLightsStudiesList = MetaboLightsUrl + "study/list"

mt = {}
studiesList = {}
compoundsList = {}
speciesList = []

def main(arguments):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("workingdirectory", help="- Working Directory")
    args = parser.parse_args(arguments)
    workingDirectory = args.workingdirectory
    fetchMetaboLightsStudiesList()
    for study in studies:
        studyContent = json.loads(urllib2.urlopen(MetaboLightsStudyUrl + study).read())["content"]
        assayNumber = 1
        try:
            for assay in studyContent["assays"]:
            try:
                metabolitesLines = json.loads(urllib2.urlopen( MetaboLightsStudyUrl + study + "/assay/" + str(assayNumber) + "/maf").read())["content"]['metaboliteAssignmentLines']
                for line in metabolitesLines:
                    dbID = str(line['databaseIdentifier'])
                    if dbID != '':
                        species = str(line['species'])
                        if species not in speciesList and species != "":
                            speciesList.append(species)

                        tempCompound = {}
                        if dbID not in compoundsList:
                            compoundsList[dbID] = []
                            tempCompound['study'] = study
                            tempCompound['species'] = species
                            compoundsList[dbID].append(tempCompound)
                        else:
                            tempCompound['study'] = study
                            tempCompound['species'] = species
                            compoundsList[dbID].append(tempCompound)

                        tempStudy = {}
                        if study not in studiesList:
                            studiesList[study] = []
                            tempStudy['compound'] = dbID
                            tempStudy['species'] = species
                            studiesList[study].append(tempStudy)
                        else:
                            tempStudy['compound'] = dbID
                            tempStudy['species'] = species
                            studiesList[study].append(tempStudy)

                assayNumber += 1
            except:
                print study + " -- assay" + str(assayNumber) + " failed" 
                pass
        except:
            print study + " failed"
            pass

    mt['studyMapping'] = studiesList
    mt['compoundMapping'] = compoundsList
    mt['speciesList'] = speciesList
    writeDataToFile(workingDirectory+"mapping.json", mt)

def fetchMetaboLightsStudiesList():
    global studies
    response = urllib2.urlopen(MetaboLightsStudiesList)
    studies = json.loads(response.read())['content']

def writeDataToFile(filename, data):
    with open(filename, "w") as fp:
        json.dump(data, fp)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))