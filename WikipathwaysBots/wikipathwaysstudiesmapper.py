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
import csv

workingDirectory = ""
studiesMappingFile = "/Users/venkata/Development/MetaboLightsBots/mapping.json"
wikipathwaysMissingTSV = "/Users/venkata/Development/MetaboLightsBots/wikipathwaysBots/wikimissingmetabolite.tsv"
metabolightsMap = {}
compoundMap = {}
fieldnames = ["MetaboLightsID", "ChEBIID", "CompoundName", "KEGGPathwaysMappings", "MTBLSMapping"]

def main(arguments):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    args = parser.parse_args(arguments)
    with open(studiesMappingFile) as mapping_file:  
        metabolightsMap = json.load(mapping_file)
    compoundMap = metabolightsMap['compoundMapping'];
    global compoundMap;
    print compoundMap;
    mapStudies(wikipathwaysMissingTSV);

def mapStudies(wikipathwaysMissingTSV):
	count = 0
	total = 0
	rows = []
	with open(wikipathwaysMissingTSV) as f:
		for line in f:
			row = {}
			total += 1
			tempData = line.split("\t")
			compoundId = tempData[1]
			row['MetaboLightsID'] = tempData[0]
			row['ChEBIID'] = tempData[1]
			row['CompoundName'] = tempData[2]
			row['KEGGPathwaysMappings'] = tempData[3].replace('\r', '').replace('\n', '')
			#print compoundId
			if compoundId in compoundMap:
				studyArr = []
				studyList = ""
				for sMapping in compoundMap[compoundId]:
					if sMapping['study']  not in studyArr:
						studyList = studyList + sMapping['study'] + " (" + sMapping['species'] + "); "
						studyArr.append(sMapping['study'])
				count += 1
				row['MTBLSMapping'] = studyList
			else:
				row['MTBLSMapping'] = "-"
			rows.append(row)
		#print str(total) + "-" + str(count)

	with open('wikipathways_missing_metabolite.csv', 'w') as csvfile:
		writer = csv.DictWriter(csvfile,delimiter='\t', fieldnames=fieldnames)
		writer.writeheader()
		for row in rows:
			writer.writerow(row)

def writeDataToFile(filename, data):
    with open(filename, "w") as fp:
        json.dump(data, fp)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))