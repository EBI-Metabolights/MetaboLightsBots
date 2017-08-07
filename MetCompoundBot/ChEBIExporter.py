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

import csv
import os
import sys
import json
import shutil
import argparse
from os.path import basename
import urllib2
import re
import utils

workingDirectory = ""
mlMapping = {}

import xml.etree.ElementTree as ET


def main(arguments):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    # Export MetaboLights compounds and study mappings
    mlSCMappingFileName = os.getcwd() + "/" + "mapping.json"
    # utils.generateMLStudyCompoundMappingFile(mlSCMappingFileName)

    # Loop through compounds and extract the species information from chebi and MetaboLights
    global mlMapping;

    with open(mlSCMappingFileName) as mapping_file:  
        mlMapping = json.load(mapping_file)
    
    header = ["COMPOUND_ID","SPECIES_TEXT","SPECIES_ACCESSION","COMPONENT_TEXT","COMPONENT_ACCESSION","STRAIN_TEXT","STRAIN_ACCESSION","SOURCE_TYPE","SOURCE_ACCESSION","COMMENTS","STATUS"]

    # CHEBI api
    chebiapi ="https://www.ebi.ac.uk/webservices/chebi/2.0/test/getCompleteEntity?chebiId="
    chebiNSMap = {"envelop": "http://schemas.xmlsoap.org/soap/envelope/","chebi":"http://www.ebi.ac.uk/webservices/chebi"}

    requestCompoundsList = utils.fetchMetaboLightsCompoundsList()
    i = 0
    j = 0
    for compound in requestCompoundsList:
        try:
            row = {}
            i = i + 1
            print str(i) + "-" + str (len(requestCompoundsList))
            chebiId = compound.replace("MTBLC","").strip();
            print chebiId
            #if chebiId == "72853":
            chebiCompound = {}
            chebiRESTResponse = urllib2.urlopen(chebiapi + chebiId).read();
            #print chebiRESTResponse
            root = ET.fromstring(chebiRESTResponse).find("envelop:Body", namespaces=chebiNSMap).find("chebi:getCompleteEntityResponse", namespaces=chebiNSMap).find("chebi:return", namespaces=chebiNSMap)
            try:
                chebiCompound["id"] = root.find("chebi:chebiId", namespaces=chebiNSMap).text
            except:
                pass

            #try:
            chebiCompound["CompoundOrigins"] = []
            chebiCompound["Species"] = {}
            for origin in root.findall("chebi:CompoundOrigins", namespaces=chebiNSMap):
                chebispecies = origin.find("chebi:speciesText", namespaces=chebiNSMap).text.lower()
                if chebispecies not in chebiCompound["Species"]:
                    originDic = {}
                    chebiCompound["Species"][chebispecies] = []
                    if origin.find("chebi:speciesAccession", namespaces=chebiNSMap) is not None:
                        originDic["SpeciesAccession"] = origin.find("chebi:speciesAccession", namespaces=chebiNSMap).text
                    if origin.find("chebi:SourceType", namespaces=chebiNSMap) is not None:
                        originDic["SourceType"] = origin.find("chebi:SourceType", namespaces=chebiNSMap).text
                    if origin.find("chebi:SourceAccession", namespaces=chebiNSMap) is not None:
                        originDic["SourceAccession"] = origin.find("chebi:SourceAccession", namespaces=chebiNSMap).text
                    if origin.find("chebi:strainText", namespaces=chebiNSMap) is not None:
                        originDic["strainText"] = origin.find("chebi:strainText", namespaces=chebiNSMap).text
                    if origin.find("chebi:strainAccession", namespaces=chebiNSMap) is not None:
                        originDic["strainAccession"] = origin.find("chebi:componentText", namespaces=chebiNSMap).text
                    if origin.find("chebi:componentText", namespaces=chebiNSMap) is not None:
                        originDic["componentText"] = origin.find("chebi:componentText", namespaces=chebiNSMap).text
                    if origin.find("chebi:componentAccession", namespaces=chebiNSMap) is not None:
                        originDic["componentAccession"] = origin.find("chebi:componentAccession", namespaces=chebiNSMap).text
                    chebiCompound["Species"][chebispecies].append(originDic)
                else:
                    originDic = {}
                    if origin.find("chebi:speciesAccession", namespaces=chebiNSMap) is not None:
                        originDic["SpeciesAccession"] = origin.find("chebi:speciesAccession", namespaces=chebiNSMap).text
                    if origin.find("chebi:SourceType", namespaces=chebiNSMap) is not None:
                        originDic["SourceType"] = origin.find("chebi:SourceType", namespaces=chebiNSMap).text
                    if origin.find("chebi:SourceAccession", namespaces=chebiNSMap) is not None:
                        originDic["SourceAccession"] = origin.find("chebi:SourceAccession", namespaces=chebiNSMap).text
                    if origin.find("chebi:strainText", namespaces=chebiNSMap) is not None:
                        originDic["strainText"] = origin.find("chebi:strainText", namespaces=chebiNSMap).text
                    if origin.find("chebi:strainAccession", namespaces=chebiNSMap) is not None:
                        originDic["strainAccession"] = origin.find("chebi:strainAccession", namespaces=chebiNSMap).text
                    if origin.find("chebi:componentText", namespaces=chebiNSMap) is not None:
                        originDic["componentText"] = origin.find("chebi:componentText", namespaces=chebiNSMap).text
                    if origin.find("chebi:componentAccession", namespaces=chebiNSMap) is not None:
                        originDic["componentAccession"] = origin.find("chebi:componentAccession", namespaces=chebiNSMap).text
                    chebiCompound["Species"][chebispecies].append(originDic)
            # except:
            #     print "here"
            #     pass

                try:
                    if chebiCompound["id"] in mlMapping['compoundMapping']:
                        studyspecies = mlMapping['compoundMapping'][chebiCompound["id"]]
                        for studyS in studyspecies:
                            if (studyS['species'] != ""):
                                tempSSpecies = str(studyS['species']).lower()
                                if tempSSpecies not in chebiCompound["Species"]:
                                    originDic = {}
                                    chebiCompound["Species"][tempSSpecies] = []
                                    originDic["Species"] = tempSSpecies
                                    originDic["SpeciesAccession"] = studyS['taxid']
                                    originDic["SourceType"] = "MetaboLights"
                                    originDic["SourceAccession"] = studyS['study']
                                    originDic["Comment"] = "From MetaboLights"
                                    originDic["componentText"] = studyS['part']
                                    chebiCompound["Species"][tempSSpecies].append(originDic)
                                else:
                                    originDic = {}
                                    originDic["Species"] = tempSSpecies
                                    originDic["SpeciesAccession"] = studyS['taxid']
                                    originDic["SourceType"] = "MetaboLights"
                                    originDic["SourceAccession"] = studyS['study']
                                    originDic["Comment"] = "From MetaboLights"
                                    originDic["componentText"] = studyS['part']
                                    chebiCompound["Species"][tempSSpecies].append(originDic)
                except:
                    pass

            #print chebiCompound
            for species in chebiCompound['Species']:
                j = j + 1
                row={}
                row["ID"] = str('')
                row["COMPOUND_ID"] = int(chebiId)
                row["SPECIES_TEXT"] = species
                for eachSpecies in chebiCompound['Species'][species]:
                    if 'SpeciesAccession' in eachSpecies:
                        row["SPECIES_ACCESSION"] =  eachSpecies['SpeciesAccession']
                    if 'SourceAccession' in eachSpecies:
                        row["SOURCE_ACCESSION"] =  eachSpecies['SourceAccession']
                    if 'SourceType' in eachSpecies:
                        row["SOURCE_TYPE"] =  eachSpecies['SourceType']
                    if 'strainText' in eachSpecies:
                        row["STRAIN_TEXT"] =  eachSpecies['strainText']
                    if 'strainAccession' in eachSpecies:
                        row["STRAIN_ACCESSION"] =  eachSpecies['strainAccession']
                    if 'componentText' in eachSpecies:
                        row["COMPONENT_TEXT"] =  eachSpecies['componentText']
                    if 'componentAccession' in eachSpecies:
                        row["COMPONENT_ACCESSION"] =  eachSpecies['componentAccession']
                    if "Comment" in chebiCompound['Species'][species][0]:
                        row["COMMENTS"] =  eachSpecies['Comment']
                # print eachSpecies
                # if len(chebiCompound['Species'][species]) > 0:
                #     if 'SpeciesAccession' in chebiCompound['Species'][species][0]:
                #         row["SPECIES_ACCESSION"] =  chebiCompound['Species'][species][0]['SpeciesAccession']
                #     if 'SourceAccession' in chebiCompound['Species'][species][0]:
                #         row["SOURCE_ACCESSION"] =  chebiCompound['Species'][species][0]['SourceAccession']
                #     if 'SourceType' in chebiCompound['Species'][species][0]:
                #         row["SOURCE_TYPE"] =  chebiCompound['Species'][species][0]['SourceType']
                #     if 'strainText' in chebiCompound['Species'][species][0]:
                #         row["STRAIN_TEXT"] =  chebiCompound['Species'][species][0]['strainText']
                #     if 'strainAccession' in chebiCompound['Species'][species][0]:
                #         row["STRAIN_ACCESSION"] =  chebiCompound['Species'][species][0]['strainAccession']
                #     if 'componentText' in chebiCompound['Species'][species][0]:
                #         row["COMPONENT_TEXT"] =  chebiCompound['Species'][species][0]['componentText']
                #     if 'componentAccession' in chebiCompound['Species'][species][0]:
                #         row["COMPONENT_ACCESSION"] =  chebiCompound['Species'][species][0]['componentAccession']
                #     if "Comment" in chebiCompound['Species'][species][0]:
                #         row["COMMENTS"] =  chebiCompound['Species'][species][0]['Comment']
                    row["STATUS"] = "E"
                    writeString = ""
                    writeString = "insert into compound_origins values(compound_origin_sequence.nextval"
                    for key in header:
                        if key != "COMPOUND_ID":
                            if key in row:
                                writeString = writeString + ",'" + row[key] + "'"
                            else:
                                writeString = writeString + ",''"
                        else:
                            writeString = writeString + "," + str(row[key])

                    writeString = writeString + ");"

                    with open(os.getcwd() + "/" + 'chebiOutput.tsv', "a") as outfile:
                        outfile.write(writeString + "\n")
        except:
            pass
            
if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))