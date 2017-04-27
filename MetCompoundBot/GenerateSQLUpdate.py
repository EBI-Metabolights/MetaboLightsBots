#!/usr/bin/env python

# Author: Venkata chandrasekhar Nainala 
# Version: 0.1.0
# Email: mailcs76@gmail.com / venkata@ebi.ac.uk
# Date: 19 May 2016

""" 
    Dependencies:
        Python 2.7
"""
import sys
import argparse
import utils
import logging
import os
import time
import json
import subprocess
from random import randint

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
    parser.add_argument('-f', '--ftp', action=readable_dir, default="/ebi/ftp/pub/databases/metabolights/compounds/", help="FTP directory")
    args = parser.parse_args(arguments)
    global destinationDirectory
    global ftp

    workingDirectory = args.launch_directory
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

    metabolightsFlagsJSONFile = ftp + "ml_flags.json"
    with open(metabolightsFlagsJSONFile) as flags_file:
        metabolightsFlagsData = json.load(flags_file)

    query = "";
    for metabolite in metabolightsFlagsData:
        has_species = int (str(metabolightsFlagsData[metabolite]["flags"]["hasSpecies"]).lower() == "true" )
        has_pathways =  int (str(metabolightsFlagsData[metabolite]["flags"]["hasPathways"]).lower() == "true"  )
        has_reactions =  int (str(metabolightsFlagsData[metabolite]["flags"]["hasReactions"]).lower() == "true"  )
        has_nmr =  int (str(metabolightsFlagsData[metabolite]["flags"]["hasNMR"]).lower() == "true"  )
        has_ms =  int (str(metabolightsFlagsData[metabolite]["flags"]["hasMS"]).lower() == "true"  )
        has_literature =  int (str(metabolightsFlagsData[metabolite]["flags"]["hasLiterature"]).lower() == "true"  )
        query += "update mmimtbldev.isatab.ref_metabolite set has_species = "+str(has_species)+", has_pathways = "+str(has_pathways)+", has_reactions = "+str(has_reactions)+", has_nmr= "+str(has_nmr)+", has_ms= "+str(has_ms)+", has_literature= "+str(has_literature)+" where acc = '" + metabolite.strip() + "';" + "\n"

    file = open(workingDirectory + "/query.txt","w") 
    file.write(query) 

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))