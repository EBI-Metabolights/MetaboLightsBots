#!/usr/bin/env python

# Author: Venkata chandrasekhar Nainala 
# Version: 0.1.0
# Email: mailcs76@gmail.com / venkata@ebi.ac.uk
# Date: 12 May 2016

""" 
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

import decimal
import json
import shutil
import urllib
import urllib2
import re
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET


# MetaboLights Compounds Webservice
MLC_API = "http://www.ebi.ac.uk/metabolights/webservice/compounds/"
MetaboLightsCompoundsList = MLC_API + "/list"

MLC_Data_Url = "http://wwwdev.ebi.ac.uk/metabolights/webservice/beta/compound/"
MSSpectraJson = "http://www.ebi.ac.uk/metabolights/webservice/compounds/spectra/"


MONA_Data_Url = "http://mona.fiehnlab.ucdavis.edu/rest/spectra/search"

destination = "/net/isilonP/public/rw/homes/tc_cm01/metabolights/reference"

version = "1.0.0"
metabolites = []

def main(arguments):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    fetchMetaboLightsCompoundsList()
    total = len(metabolites)
    index = 0
    for metabolite in metabolites:
        index += 1
        print index
        print "========================"
        fetchSpectraList(metabolite)

def fetchSpectraList(metabolite):
    print metabolite
    response = urllib2.urlopen(MLC_Data_Url + metabolite)
    MLC_DATA = json.loads(response.read())
    MLC_SpectraList = MLC_DATA['spectra']
    if len(MLC_SpectraList) > 0 :
        temStr = metabolite + " : <" + MLC_Data_Url + metabolite + ">"
        print temStr
        for spectra in MLC_SpectraList:
            try:
                if spectra['type'] == "MS":
                    print metabolite + " <-> " + spectra['name']
                    SpecID = spectra['id']
                    MSSpectraUrl = spectra['url']
                    ML_MS_SPECTRA = fetchMetaboLightsCompoundSpectra(MSSpectraUrl)
                    #print ML_MS_SPECTRA
                    MONA_MS_SPECTRA = fetchMONACompoundSpectra(spectra['name'])
                    merge_data = mergeMONA_MS_SPECTRA(ML_MS_SPECTRA, MONA_MS_SPECTRA);
                    merge_data['splash'] = MONA_MS_SPECTRA['Splash']
                    destinationPath = destination + "/" + metabolite + "/" + metabolite + "_spectra" + "/" + spectra['name'] + "/" + spectra['name'] + ".json"
                    writeDataToFile(destinationPath, merge_data, "w")
            except:
                writeDataToFile("/net/isilonP/public/rw/homes/tc_cm01/metabolights/scripts/MetaboLightsBots/error.log", temStr + "/n" , "a")
                pass

def writeDataToFile(filename, data, mode):
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    with open(filename, mode) as fp:
        json.dump(data, fp)

def mergeMONA_MS_SPECTRA(ml,mona):
    datapoints = mona['Spectrum'].split(" ");
    for datapoint in datapoints:
        tempArray = datapoint.split(":")
        mz = tempArray[0].strip()
        intensity = float(tempArray[1].strip()) * 9.99
        count = 0
        #print mz + " <---> " + intensity 
        for peak in ml['peaks']:
            #print str(dropzeros(peak['mz'])) + " <---> " + str(mz)
            if peak['mz'] == mz or str(dropzeros(peak['mz'])) == str(mz):
                #print str(intensity) + " <---> " + str(ml['peaks'][count]['intensity'])
                ml['peaks'][count]['intensity'] = str( intensity)
                break;
            count += 1
    return ml

def getHighestNumber(numbers):
    return 0;

def dropzeros(number):
    mynum = decimal.Decimal(number).normalize()
    # e.g 22000 --> Decimal('2.2E+4')
    return mynum.__trunc__() if not mynum % 1 else float(mynum)

def fetchMONACompoundSpectra(name):
    mona_spectra = {}
    curl = 'curl -H "Content-Type: application/json" -d ' + '\'{"compound":{},"metadata":[{"name":"origin","value":{"eq":"' +name+ '.txt"}}],"tags":[]}\'' + ' http://mona.fiehnlab.ucdavis.edu/rest/spectra/search'
    result = json.loads(os.popen(curl).read())[0]
    mona_spectra['Splash'] = result['splash']
    mona_spectra['Spectrum'] = result['spectrum']
    return mona_spectra

def fetchMetaboLightsCompoundSpectra(MSSpectraUrl):
    response = urllib2.urlopen(MSSpectraUrl)
    return json.loads(response.read())

def fetchMetaboLightsCompoundsList():
    global metabolites
    response = urllib2.urlopen(MetaboLightsCompoundsList)
    metabolites = json.loads(response.read())['content']     

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))