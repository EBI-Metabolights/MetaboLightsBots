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

metabolites = []
mcapi = "http://www.ebi.ac.uk/metabolights/webservice/compounds/"

def main(arguments):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    args = parser.parse_args(arguments);
    fetchMetaboLightsCompoundsList();
    csvData = "";
    total = len(metabolites)
    for metabolite in metabolites:
        total = total - 1
        print total
        try:
            mtblcs = json.loads(urllib2.urlopen(mcapi+metabolite).read())["content"]
            name = mtblcs['chebiEntity']['chebiAsciiName']
            chebi = metabolite.replace("MTBLC", "CHEBI:")
            wikipathwaysData = getWikiPathwaysData(chebi);
            keggpathwaysData = getKEGGData(chebi);
            wikipathwaysCount = len(wikipathwaysData)
            keggpathwaysCount = len(keggpathwaysData)
            if (wikipathwaysCount == 0 and keggpathwaysCount > 0):
                csvData = metabolite + "\t" + chebi + "\t" + name + "\t" + '; '.join(keggpathwaysData)
                #print str(total) + " | " + metabolite + "," + chebi + "," + name + "," + '; '.join(keggpathwaysData) 
                with open("wikimissingmetabolite.csv", "a") as dataFile:
                    dataFile.write("%s\n" % csvData)
        except:
            pass

def getWikiPathwaysData(id):
    pathways = []
    names = []
    wikipathwaysapi = "http://webservice.wikipathways.org/index.php?ids="+id+"&codes=Ce&method=findPathwaysByXref&format=json"
    try:
        wikipathways =  json.loads(urllib2.urlopen(wikipathwaysapi).read())["result"]
        if len(wikipathways) > 0 :
            for path in wikipathways:
                tempDict = {}
                tempDict["id"] = path["id"]
                tempDict["url"] = path["url"]
                tempDict["name"] = path["name"]
                if path["name"] not in names:
                    names.append(path["name"]);
                tempDict["species"] = path["species"]
                pathways.append(tempDict);
    except:
        pass
    return names

def getKEGGData(id):
    pathways = []
    names = []
    try:
        keggapi = "http://rest.kegg.jp/conv/compound/" + id.lower()
        keggid = urllib2.urlopen(keggapi).read().split("\t")[1].strip()
        pathwayslistapi = "http://rest.kegg.jp/link/pathway/" + keggid
        pathwaysData = urllib2.urlopen(pathwayslistapi).read()
        for line in pathwaysData.strip().split("\n"):
            pathwayId = line.split("\t")[1].strip()
            pathwayapi = "http://rest.kegg.jp/get/" + pathwayId
            pathwayData = urllib2.urlopen(pathwayapi).read()
            tempDict = {}
            tempDict["id"] = pathwayId
            for pline in pathwayData.strip().split("\n"):
                if "NAME" in pline:
                    tempDict["name"] = pline.replace("NAME","").strip()
                elif "KO_PATHWAY" in pline:
                    tempDict["KO_PATHWAY"] = pline.replace("KO_PATHWAY","").strip()
                elif "DESCRIPTION" in pline:
                    tempDict["description"] = pline.replace("DESCRIPTION","").strip()
            if tempDict["name"] not in names:
                names.append(tempDict["name"]);
            pathways.append(tempDict)
    except:
        pass
    return names

def fetchMetaboLightsCompoundsList():
    global metabolites
    response = urllib2.urlopen(MetaboLightsCompoundsList)
    metabolites = json.loads(response.read())['content']

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))