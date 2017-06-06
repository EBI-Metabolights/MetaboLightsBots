"""
    priv_ftp_check_zip_files.py
    
    Check for integrity of every *.zip file in the folder passed as argument, recursively.
    A log is kept, producing a new file every day. Only errors are logged.
    Python 3.5+ is required by the recursive behavior
    
    Use: python3 priv_ftp_check_zip_files.py path_to_zips 
        /net/isilonP/public/rw/homes/tc_cm01/metabolights/software/Python3local/bin/python3 priv_ftp_check_zip_files.py /ebi/ftp/private/mtblight/test
"""

import os
import sys
import glob
import logging
import logging.handlers
import zipfile


def check_zfile(filename):
    try:
        zfile = zipfile.ZipFile(filename)
        zfile.testzip()
    except Exception:
        logger.error("Found bad file in " + filename)
    else:
        logger.info("Zip test PASSED for " + filename)


def setup_log():
    log = logging.getLogger('ZipTest')
    # log.setLevel(logging.DEBUG)
    os.makedirs('logs', exist_ok=True)
    fh = logging.handlers.TimedRotatingFileHandler(filename='logs/priv_ftp_check_zip_files.log', when='midnight')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
    fh.setFormatter(formatter)
    log.addHandler(fh)
    return log


if __name__ == "__main__":
    rootdir = os.path.abspath(sys.argv[1])

    logger = setup_log()
    logger.info("===> Testing zip files in " + rootdir)

    zfiles = glob.glob(os.path.join(rootdir, "**/*.zip"), recursive=True)

    for file in zfiles:
        check_zfile(file)

