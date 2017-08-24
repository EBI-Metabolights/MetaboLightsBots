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
import logging
import os
import time
import json
import subprocess
from random import randint
import subprocess as sp
from bsub import bsub

project = ""
token = ""
job = ""
env = "dev"
userSpace = {
    'dev' : "/net/isilonP/public/rw/homes/tc_cm01/metabolights/ftp_private/dev/userSpace/",
    'prod' : "/net/isilonP/public/rw/homes/tc_cm01/metabolights/ftp_private/prod/userSpace/"
}


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
    
    parser.add_argument('-e', '--env', help="- Environment", default="dev")
    parser.add_argument('-p', '--project', help="- MetaboLights Labs project ID", required=True)
    parser.add_argument('-t', '--token', help="- MetaboLights Labs user token", required=True)
    parser.add_argument('-j', '--job', help="- LSF Job id", required=False)
    args = parser.parse_args(arguments)

    global project
    global token
    global job
    global env
    global userSpace

    project = args.project
    token = args.token
    job = args.job
    env = args.env

    baseDirectory = userSpace[env]

    inputLocation = baseDirectory + token + "/" + project
    outputLocation = baseDirectory + token + "/" + project

    if not (job is None):
        # check the status of job and return the value
        print _getJobStatus(_run("bjobs " + job));
    else:
        #check if the folder locations are valid and the submit the job
        #check if the input location / outputlocation exists
        if not os.path.isdir(inputLocation) or not os.path.exists(inputLocation):
            raise Exception("Input folder doesnt exist")

        if not os.path.isdir(outputLocation) or not os.path.exists(outputLocation):
            raise Exception("Output folder doesnt exist")

        sub = bsub("mzml2isaJob", verbose=False)
        sub("mzml2isa -i " + inputLocation + " -o " + outputLocation + " -s ''")
        status = {
            "message": "Job submitted successfully",
            "code"  : "PEND"
        }
        status["jobID"] = sub.job_id
        print status

def _getJobStatus(res):
    status = {
        "message": "",
        "code"  : ""
    }
    if "is not found" in res:
        status["message"] = "Job with the requested ID doesnt exist"
    else:
        output = res.split("\n")[1].split(" ")
        if len(output) > 3:
            statusCode = output[2]
        if statusCode == "RUN":
            status["message"] = "Job running"
            status["code"] = statusCode
        elif statusCode == "PEND":
            status["message"] = "Job pending"
            status["code"] = statusCode
        elif statusCode == "DONE":
            status["message"] = "Job done"
            status["code"] = statusCode
        else:
            status["message"] = "Job error"
            status["code"] = "UNKNOWN"
    return status;

def _run(command, check_str="is submitted"):
    p = sp.Popen(command, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
    p.wait()
    res = p.stdout.read().strip().decode()
    err = p.stderr.read().strip().decode()
    if res == '':
        return err
    return res

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))