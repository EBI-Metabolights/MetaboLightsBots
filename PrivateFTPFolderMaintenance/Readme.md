Private FTP Folder Maintenance
================

Tools for maintenance of the private FTP folder used by submitters to upload big files into MTBLS studies.


Scritps
----------

- priv_ftp_check_zip_files.py
    
    Check for integrity of every *.zip file in the folder passed as argument, recursively.
    A log is kept, producing a new file every day. Only errors are logged.
    Python 3.5+ is required by the recursive behavior
    
    Use: python3 priv_ftp_check_zip_files.py path_to_zips

