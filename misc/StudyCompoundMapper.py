#!/usr/bin/env python

# Author: Venkata chandrasekhar Nainala 
# Version: 0.1.0
# Email: mailcs76@gmail.com / venkata@ebi.ac.uk

""" A python crawler to iterate MetaboLights Studies/Compounds and execute specified scripts
"""
import logging
import os
import sys
import json
import time
from urllib import request
import argparse
from os.path import basename
from urllib.error import URLError

workingDirectory = ""
MetaboLightsUrl = "http://www.ebi.ac.uk/metabolights/webservice/"
MetaboLightsStudyUrl = "http://www.ebi.ac.uk/metabolights/webservice/study/"
MetaboLightsStudyDevUrl = "http://wwwdev.ebi.ac.uk/metabolights/webservice/study/"
MetaboLightsStudiesList = MetaboLightsUrl + "study/list"

mt = {}
studiesList = {}
compoundsList = {}
speciesList = []
timer_list = []

def attach_timer(study, elapsed):
    timer_list.append({study: elapsed})



def main(arguments):
    process_start = time.process_time()
    actual_process_start = time.time()
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("workingdirectory", help="- Working Directory")
    args = parser.parse_args(arguments)
    workingDirectory = args.workingdirectory
    fetchMetaboLightsStudiesList()
    for study in studies:
        try:
            studyContent = json.loads(request.urlopen(MetaboLightsStudyUrl + study).read())["content"]
        except OSError as e:
            print(f'OSError while processing {study}: {str(e)}')
            continue
        start = time.process_time()
        actual_start = time.time()
        assayNumber = 1
        try:
            for assay in studyContent["assays"]:
                try:
                    url = f'{MetaboLightsStudyUrl}{study}/assay/{str(assayNumber)}/maf'
                    metabolitesLines = json.loads(
                        request.urlopen(MetaboLightsStudyUrl + study + "/assay/" + str(assayNumber) + "/maf").read())[
                        "content"]['metaboliteAssignmentLines']
                    if metabolitesLines is None:
                        assayNumber += 1
                        continue
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

                except Exception as e:
                    logging.exception('Error processing assay')
                    print(study + " -- assay" + str(assayNumber) + " failed")
                    print(f'{study} -- assay {str(assayNumber)} failed: {str(e)}')
                    continue
            end = time.process_time()
            actual_end = time.time()

            attach_timer(study, end - start)
            print(f'finished {study} in {end - start} / {actual_end - actual_start}')
        except Exception as e:
            logging.exception('Error processing study')
            print(study + " failed")
            continue
    process_end = time.process_time()
    actual_process_end = time.time()
    print(f'overall time taken : {process_end - process_start} / {actual_process_end - actual_process_start}')
    mt['studyMapping'] = studiesList
    mt['compoundMapping'] = compoundsList
    mt['speciesList'] = speciesList
    writeDataToFile(workingDirectory + "mapping.json", mt)


def fetchMetaboLightsStudiesList():
    global studies
    response = request.urlopen(MetaboLightsStudiesList)
    studies = json.loads(response.read())['content']


def writeDataToFile(filename, data):
    with open(filename, "w+") as fp:
        json.dump(data, fp)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
