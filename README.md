MetaboLights Bots
===================

Python scripts for MetaboLights data management * This documentation is not extensive and is still in development.

==================================================================================================
### **MetaboLights Study Bots**

Automated tasks / routines over study data that fetches study factors, file extensions / MIME types, assay details and various other files related information like file counts etc. Also performs analysis to a certain extent (Getting better and better).

==================================================================================================

#### **MetStudyBot**

Usage:
```sh
$ python MetStudyBot.py {studyid} # python MetStudyBot.py MTBLS35
```
A python script for extracting sample and assay data in the study
	This script accepts the following command line argument(s):
	- study : MetaboLights Study Identifier (String)

Output: 
> https://raw.githubusercontent.com/CS76/MetaboLightsBots/master/MetStudyBot/MTBLS35_sample_assay_mapping.json

==================================================================================================
#### **Bulk_head**
Usage:
```sh
$ python bulk_head.py
```
A python script for mapping and counting file formats to studies

Output: 
>ftp://ftp.ebi.ac.uk/pub/databases/metabolights/study_file_extensions/ml_file_extension.json

==================================================================================================
#### **Bumble_bee**
Usage:
```sh
$ python bumble_bee.py
```
A python script for travesing study file system and generates a folder tree.

It unzips the compressed files and includes the underlying files / folders in to the parent tree

Output: 
>ftp://ftp.ebi.ac.uk/pub/databases/metabolights/study_file_extensions/study_file_details/MTBLS1.json

==================================================================================================

### **MetaboLights Compound Bots**

#### **MLCompoundsBot.py**

Usage:
```sh
$ python MLCompoundsBot.py --compound "MTBLC115354" <working_directory> <destination_directory>
```
The script accepts the following command line argument(s):

-- compound : MetaboLights Compound Identifier (String) ( default: all)

-- working directory (temporary staging area for log, mappings and other files)

-- destination directory (output and spectra files are stored in this location)

	
 - Output example:
 
> http://wwwdev.ebi.ac.uk/metabolights/webservice/beta/compound/MTBLC15355

#### **Utils**
>  MetaboLightsBots/MetCompoundBot/utils.py

**Helper module for the MLCompoundsBot**

Functions in this module query different rest services to fetch information based on the InChiKey input ( Chemical identification data, Metabolights study mappings, Pathways data from KEGG, Wikipathways and Reactome, Reactions data from Rhea, Citations from European Pubmed Central, Spectroscopic data from MONA - mass bank/hmdb, SPLASH - spectral hash from MONA etc. )

 - Generates the MetaboLights Study Compound mapping file
> https://raw.githubusercontent.com/CS76/MetaboLightsBots/master/resources/mapping.json

 - Generates the Reactome JSON file
> https://raw.githubusercontent.com/CS76/MetaboLightsBots/master/resources/reactome.json

#### **MetCompoundSpeciesMapper**

Usage:
```sh
$ python MetCompoundSpeciesMapper.py
```
A python script for mapping compounds and species with species accessions

Output: 
> https://raw.githubusercontent.com/CS76/MetaboLightsBots/master/resources/compoundSpeciesMappingComplete.csv

==================================================================================================

### **Wikipathways Bots**
-----
#### **MetStudyBot**
Script to generate Wikipathways - MetaboLights Enrichment spread sheet

Usage:
```sh
$ python MetStudyBot.py {studyid} # python MetStudyBot.py MTBLS35
```
Output: 
https://gist.github.com/CS76/12e72c79561bd07944cab0ed3961616b

==================================================================================================