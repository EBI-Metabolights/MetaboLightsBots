#!/usr/bin/env python

# Author: Venkata chandrasekhar Nainala 
# Version: 0.1.0
# Email: mailcs76@gmail.com / venkata@ebi.ac.uk
# Date: 5 June 2016

""" 
    Dependencies:
        Python 2.7
"""
import sys
import argparse
import utils
import logging
import os
import urllib2
import time
import json
import subprocess
from random import randint
import csv

destinationDirectory = ""
workingDirectory = ""
ftp = ""

globalReport = {}

class readable_dir(argparse.Action):
    def __call__(self,parser, namespace, values, option_string=None):
        prospective_dir=values
        if not os.path.isdir(prospective_dir):
            raise argparse.ArgumentTypeError("readable_dir:{0} is not a valid path".format(prospective_dir))
        if os.access(prospective_dir, os.R_OK):
            setattr(namespace,self.dest,prospective_dir)
        else:
            raise argparse.ArgumentTypeError("readable_dir:{0} is not a readable dir".format(prospective_dir))

def main(arguments):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-l', '--launch_directory', action=readable_dir, default = "" )
    parser.add_argument('-w', '--destination', action=readable_dir, help="Output directory", default="/nfs/www-prod/web_hx2/cm/metabolights/prod/reference/")
    parser.add_argument('-f', '--ftp', action=readable_dir, default="/ebi/ftp/pub/databases/metabolights/compounds/", help="FTP directory")
    args = parser.parse_args(arguments)
    global workingDirectory
    global destinationDirectory
    global ftp
    global globalReport

    workingDirectory = args.launch_directory
    destinationDirectory = args.destination
    ftp = args.ftp

    if(workingDirectory == ""):
        workingDirectory = os.getcwd();

    # log file configuration
    st = utils.getDateAndTime();
    randomInt = str(randint(1, 1000))
    logDirectory = workingDirectory + "/logs/exporter_" + st 
    if not os.path.exists(logDirectory):
        os.makedirs(logDirectory)
    logging.basicConfig(filename= logDirectory + "/log_" +randomInt +".log",level=logging.DEBUG)
    utils.init(logging)
    logging.info("-----------------------------------------------")
    logging.info('# Run started -' + utils.getDateAndTime())

    fieldnames = ["MetabolightsId", "InChIKey", "HasPathways", "KEGGPathways", "WikiPathways", "ReactomePathways"]
    rows = []

    requestCompoundsList = utils.fetchMetaboLightsCompoundsList()
    i = 0
    for compound in requestCompoundsList:
        i = i + 1
        print str(i) + "-" + str (len(requestCompoundsList))
        compoundURL = "http://www.ebi.ac.uk/metabolights/webservice/beta/compound/" + compound
        response = urllib2.urlopen(compoundURL)
        compoundData = json.loads(response.read())
        row = {}
        chebiString = compound.replace("MTBLC", "CHEBI:")
        row["MetabolightsId"] = compound
        row["InChIKey"] = compoundData['inchiKey']
        row["HasPathways"] = int(compoundData["flags"]["hasPathways"] == 'true')
        row["KEGGPathways"] = ""
        row["WikiPathways"] = ""
        row["ReactomePathways"] = ""
        try:
            if (compoundData["flags"]["hasPathways"]):
                for resource in compoundData["pathways"]:
                    if resource == "WikiPathways":
                        for species in compoundData["pathways"][resource]:
                            for pathway in compoundData["pathways"][resource][species]:
                                if row[resource] != "":
                                    row[resource] = row[resource] + "," + pathway["id"]
                                else:
                                    row[resource] = pathway["id"]
                    elif resource == "ReactomePathways":
                        for species in compoundData["pathways"][resource]:
                            for pathway in compoundData["pathways"][resource][species]:
                                if row[resource] != "":
                                    row[resource] = row[resource] + "," + pathway["reactomeId"]
                                else:
                                    row[resource] = pathway["reactomeId"]
                    else:
                        for pathway in compoundData["pathways"]["KEGGPathways"]:
                            if row[resource] != "":
                                row[resource] = row[resource] + "," + pathway["KO_PATHWAY"]
                            else:
                                row[resource] = pathway["KO_PATHWAY"]
        except:
            logging.error(compound)
        rows.append(row)

    with open('data/metabolites_inchikey.tsv', 'w') as csvfile:
        writer = csv.DictWriter(csvfile, delimiter='\t', fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))