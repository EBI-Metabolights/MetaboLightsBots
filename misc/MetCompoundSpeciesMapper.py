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
MetaboLightsCompoundsList = MetaboLightsUrl + "compounds/list"
MetaboLightsWSCompoundsUrl = "http://wwwdev.ebi.ac.uk/metabolights/webservice/beta/compound/"

mt = {}
metabolites = []
fieldnames = []
mlmapping = {}

def main(arguments):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    args = parser.parse_args(arguments);

    fetchMetaboLightsCompoundsList();
    fieldnames = ["MetabolightsCompoundId", "ChEBIId", "Accession", "Species"]
    rows = []
    for compound in metabolites:
        print compound
        row = {}
        chebiString = compound.replace("MTBLC", "CHEBI:")
        try:
            compoundSpeciesData = json.loads(urllib2.urlopen(MetaboLightsWSCompoundsUrl+compound).read())["species"]
            for key, value in compoundSpeciesData.iteritems():
                for entry in compoundSpeciesData[key]:
                    if "MTBLS" in entry['SpeciesAccession']:
                        row["MetabolightsCompoundId"] = compound
                        row["ChEBIId"] = chebiString
                        row["Accession"] = entry['SpeciesAccession']
                        row["Species"] = key
                        rows.append(row)    
        except:
            pass
    rows = list(set(rows))
    with open('compoundSpeciesMapping.csv', 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
        

def fetchMetaboLightsCompoundsList():
    global metabolites
    response = urllib2.urlopen(MetaboLightsCompoundsList)
    metabolites = json.loads(response.read())['content']

def writeDataToFile(filename, data):
    with open(filename, "w") as fp:
        json.dump(data, fp)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))