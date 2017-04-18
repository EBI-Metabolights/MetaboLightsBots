#!/usr/bin/env python

# Author: Venkata chandrasekhar Nainala 
# Version: 0.1.0
# Email: mailcs76@gmail.com / venkata@ebi.ac.uk
# Date: 16 March 2016

""" A python script for extracting sample and assay data in the study
    This script accepts the following command line argument(s):
        - study : MetaboLights Study Identifies (String)
	    Usage: python MetStudyBot.py <MTBL{}>
        Example:  python MetStudyBot.py MTBLS35

    Dependencies:
        Python 2.7

    Reference:

"""

import os
import sys
import json
import shutil
import argparse
from os.path import basename
import urllib2
import re

workingDirectory = ""
studyMapping = {}
ftp = "ftp://ftp.ebi.ac.uk/pub/databases/metabolights/studies/public/"

def main(arguments):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('study', help="- Study Identifier")
    parser.add_argument('-p', '--pretty', dest='pretty', required=False, default=False,
                        help="- Pretty printed json output.", action='store_true')
    parser.add_argument('-o', '--output', dest='out_path', required=False,
                        help="- Output path (including filename)", default=None)
    args = parser.parse_args(arguments)
    study = args.study
    filename = study+'_sample_assay_mapping.json'
    if args.out_path is not None:
        filename = args.out_path

    writeDataToFile(filename, extractInvestigationFile(study), pretty=args.pretty)

def extractInvestigationFile(study):
    global ftp
    global studyMapping
    investigationFileLocation = ftp + study + "/i_Investigation.txt"
    response = urllib2.urlopen(investigationFileLocation)
    investigationFile = response.read()
    investigationFileLines = investigationFile.splitlines()
    for line in investigationFileLines:
        if "Study Identifier" in line:
            extractStringFields(line)
        elif "Study Title" in line:
            extractStringFields(line)
        elif "Study Description" in line:
            extractStringFields(line)
        elif "Study Submission Date" in line:
            extractStringFields(line)
        elif "Study Public Release Date" in line:
            extractStringFields(line)
        elif "Study File Name" in line:
            extractArrayFields(line)
        elif "Study Assay File Name" in line:
            extractArrayFields(line)
        elif "Study Factor Name\t" in line:
            extractArrayFields(line)
        elif "Study Factor Type\t" in line:
            extractArrayFields(line)
        elif "Study Assay Technology" in line:
            extractStringFields(line, "Study Assay Technology")
    studyMapping['url'] = ftp + study 
    studyMapping['samples'] = extractSampleData(study, studyMapping['Study File Name']);
    return studyMapping

def extractSampleData(study, filenames):
    global studyMapping
    samples = []
    for filename in filenames:
        sampleFileLocation = ftp + study + "/" + filename
        response = urllib2.urlopen(sampleFileLocation)
        sampleFileContent = response.read()
        sampleFileLines = sampleFileContent.splitlines()
        header =  sampleFileLines[0]
        headerFields = header.split("\t")
        sampleNameIndex = 0
        factors = {}
        for fieldIndex in range(0, len(headerFields)):
            field = headerFields[fieldIndex]
            if "Sample Name" in field:
                sampleNameIndex = fieldIndex
            elif "Factor Value" in field:
                factors[field[field.index("[") + 1:field.rindex("]")]] = fieldIndex
        #print factors
        sample = {}
        for line in sampleFileLines[1:]:
            fieldValues = line.split("\t")
            #sample['rawData'] = line
            sample['name'] = fieldValues[sampleNameIndex].strip('"')
            studyFactors = {}
            for key in factors:
                studyFactors[key] = fieldValues[factors[key]].strip('"')
            sample['studyFactors'] = studyFactors
            sample['assays'] = extractAssayData(sample['name'], study, studyMapping['Study Assay File Name'])
            samples.append(sample)
    return samples

def extractAssayData(samplename,study,filenames):
    assays = []
    for filename in filenames:
        assayFileLocation = ftp + study + "/" + filename
        response = urllib2.urlopen(assayFileLocation)
        assayFileContent = response.read()
        assayFileLines = assayFileContent.splitlines()
        header = assayFileLines[0]
        headerFields = header.split("\t")
        rawFileIndex = 0
        sampleNameIndex = 0
        assayDataField = {}
        for fieldIndex in range(0, len(headerFields)):
            field = headerFields[fieldIndex]
            if "Raw Spectral Data File" in field:
                rawFileIndex = fieldIndex
            elif "Sample Name" in field:
                sampleNameIndex = fieldIndex
        assayData = {}
        allData = {}
        for line in assayFileLines[1:]:
            fieldValues = line.split("\t")
            for f in range(0,len(fieldValues)):
                allData[headerFields[f].strip('"')] = fieldValues[f].strip('"')
            assayData['all_fields'] = allData
            if equals_ignore_case(fieldValues[sampleNameIndex].strip('"'),samplename):
                assayData['rawFile'] = fieldValues[rawFileIndex].strip('"')
                assays.append(assayData)
    return assays

def equals_ignore_case(a,b):
    return a.upper() == b.upper()

def extractStringFields(data, category = None):
    global studyMapping
    fields = data.split("\t");
    fieldname = fields[0]
    fieldvalue = re.sub(r'^"|"$', '', fields[1]) 
    if category is not None:
        if category in studyMapping:
            studyMapping[category][fieldname] = fieldvalue
        else:
            studyMapping[category] = {}
            studyMapping[category][fieldname] = fieldvalue
    else:
        studyMapping[fieldname] = fieldvalue

def extractArrayFields(data):
    fields = data.split("\t");
    fieldname = fields[0]
    oldfieldvalue = fields[1:]
    fieldvalue = []
    for field in oldfieldvalue:
        fieldvalue.append(field.strip('"'))
    studyMapping[fieldname] = fieldvalue

def writeDataToFile(filename, data, pretty=False):
    with open(filename, 'w') as fp:
        if pretty:
            from pprint import PrettyPrinter
            pp = PrettyPrinter(indent=4)
            fp.write(pp.pformat(data))
        else:
            json.dump(data, fp)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))