#!/usr/bin/env python

"""Generate the parallel coordinates compatible JSON and also scripts to
    analyse the coordinates data
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
    parser.add_argument('-w', '--destination', action=readable_dir, default="/ebi/ftp/pub/databases/metabolights/derived/parallel_coordinates/", help="Output directory")
    args = parser.parse_args(arguments)
    
    # Reading lauching directory and log file details
    root = args.launch_directory
    destination = args.destination
    if(root == ""):
        root = os.getcwd();
    
    now = datetime.now()
    
    logsDirectory = args.destination + "logs/" + str(now.strftime("%Y%m%d%H%M"))
    if not os.path.exists(logsDirectory):
        os.makedirs(logsDirectory)

     # Read the input parameters
    outputJSONFile = logsDirectory + "/output.json"
    errorFile = logsDirectory + "/job.error"
    logFile = logsDirectory + "/job.log"

    # Initialising logging setup
    logging.basicConfig(filename=logFile, level=logging.INFO)
    logger = logging.getLogger("ML Bot")


    logger.info("Started extracting file extensions: " + now.strftime("%Y-%m-%d %H:%M"))
    logger.info("Working directory: " + root)
    logger.info("Log File: " + logFile)
    
    # Get list of studies (Public)
    fetchMetaboLightsStudiesList()
    
    global studies
    logger.info("Fetching studies list: " + str(len(studies)))
    
    factorsDistribution = []
    for study in studies:
        print study
        logger.info("Extracting study extension details: " + study)
        global MetaboLightsUrl
        MetaboLightsStudyData = MetaboLightsUrl + "study/" + study
        response = urllib2.urlopen(MetaboLightsStudyData)
        studyData = json.loads(response.read())['content']
        tempDistribution = {}
        tempDistribution['Study'] = study
        tempDistribution['Organism'] = []
        tempDistribution['OrganismPart'] = []
        tempDistribution['Factors'] = {}
        OrganismData = studyData['organism']
        for organism in OrganismData:
            if organism['organismName'] not in tempDistribution['Organism']:
                tempDistribution['Organism'].append(organism['organismName'])
                tempDistribution['Factors']['Organism'] = {}
            if organism['organismPart'] not in tempDistribution['OrganismPart']:
                tempDistribution['OrganismPart'].append(organism['organismPart'])
                tempDistribution['Factors']['Organism part'] = {}
        factors = studyData['factors']
        tempDistribution['TotalFactors'] = len(factors)
        for factor in factors:
            tempDistribution['Factors'][factor['name']] = {}
        tempDistribution['Technology'] = []
        for assay in studyData['assays']:
            if (assay['technology'] not in tempDistribution['Technology']):
                tempDistribution['Technology'].append(assay['technology'])
        AssayFieldIndex = {}
        AssayData = studyData['assays'][0]['assayTable']
        AssayFields = AssayData['fields']
        fileColumnSelected = False
        for field in AssayFields:
            if "sample name" in field:
                AssayFieldIndex['sample name'] = { 'index' :  AssayFields[field]['index'] }
            if "metabolite assignment file" in field:
                AssayFieldIndex['metabolite assignment file'] = { 'index' :  AssayFields[field]['index'] }
            if not fileColumnSelected:
                if "file" in field and "parameter value" not in field:
                    if '.' in studyData['assays'][0]['assayTable']['data'][0][AssayFields[field]['index']]:
                        AssayFieldIndex['raw file'] = { 'index' :  AssayFields[field]['index'] }
                        fileColumnSelected = True
        SampleData = studyData['sampleTable']
        sampleIndex = 'null'
        for field in SampleData['fields']:
            if "factor value" in field:
                if SampleData['fields'][field]['header'] in tempDistribution['Factors']:
                    tempDistribution['Factors'][SampleData['fields'][field]['header']]['index'] = SampleData['fields'][field]['index']
                    tempDistribution['Factors'][SampleData['fields'][field]['header']]['values'] = []
            if "characteristics" in field:
                if SampleData['fields'][field]['header'] in tempDistribution['Factors']:
                    tempDistribution['Factors'][SampleData['fields'][field]['header']]['index'] = SampleData['fields'][field]['index']
                    tempDistribution['Factors'][SampleData['fields'][field]['header']]['values'] = []
            if "sample name" in field:
                sampleIndex = SampleData['fields'][field]['index']
        for factor in tempDistribution['Factors']:
            for data in SampleData['data']:
                if 'index' in tempDistribution['Factors'][factor]:
                    if data[tempDistribution['Factors'][factor]['index']] not in tempDistribution['Factors'][factor]['values']:
                        tempDistribution['Factors'][factor]['values'].append(data[tempDistribution['Factors'][factor]['index']])
        assayMetabolitiesData = {}
        assayId = 1
        for assay in studyData['assays']:
            maf = "http://www.ebi.ac.uk/metabolights/" + study + "/assay/" + str(assay['assayNumber']) + "/maf"
            mafResponse = urllib2.urlopen(maf)
            mafData = mafResponse.read()
            soup = BeautifulSoup(mafData, "html.parser")
            table = soup.find('table')
            rowId = 0
            metabolites = []
            for row in table.findAll('tr'):
                if rowId > 0:
                    metabolite = row.findAll('td')[0].text
                    if metabolite != "":
                        metabolites.append(metabolite.replace("\n",""))
                rowId += 1
            assayMetabolitiesData[str(assay['assayNumber'])] = metabolites
            assayId += 1
        factorsDistribution.append(tempDistribution)
        MLStudy  = tempDistribution
        pCoordinates = []
        i = 1;
        if MLStudy['TotalFactors'] > 0:
            for data in SampleData['data']:
                pCoordinatesValues = {}
                pCoordinatesValues['id'] = i
                pCoordinatesValues['name'] = data[sampleIndex]
                pCoordinatesValues['files'] = []
                pCoordinatesValues['metabolites'] = []
                for assay in studyData['assays']:
                    for assayRow in assay['assayTable']['data']:
                        if pCoordinatesValues['name'] in assayRow[AssayFieldIndex['sample name']['index']]:
                            try:
                                pCoordinatesValues['files'].append(assayRow[AssayFieldIndex['raw file']['index']])
                                pCoordinatesValues['metabolites'] = list(set(pCoordinatesValues['metabolites'] + assayMetabolitiesData[str(assay['assayNumber'])]))
                            except:
                                print "error"
                    pCoordinatesValues['mafFile'] = assay['metaboliteAssignment']['metaboliteAssignmentFileName']
                for factor in MLStudy['Factors']:
                    if ('values' in MLStudy['Factors'][factor]):
                        if len(MLStudy['Factors'][factor]['values']) > 1:
                            pCoordinatesValues[factor] = data[MLStudy['Factors'][factor]['index']]
                pCoordinates.append(pCoordinatesValues)
                i = i+1
        with open( destination + MLStudy['Study'] + ".json", 'w+') as outfile:
            json.dump(pCoordinates, outfile)
    with open(destination + 'factorsDistribution.json', 'w') as outfile:
        json.dump(factorsDistribution, outfile)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))