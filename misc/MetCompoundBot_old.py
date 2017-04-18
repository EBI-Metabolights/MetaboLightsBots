#!/usr/bin/env python

# Author: Venkata chandrasekhar Nainala 
# Version: 0.1.0
# Email: mailcs76@gmail.com / venkata@ebi.ac.uk
# Date: 22 March 2016

""" A python script to scrape metabolite data from various online resources
    This script accepts the following command line argument(s):
        - study : MetaboLights Study Identifies (String)
	    Usage: python MetCompoundBot.py <MTBLC{}>
        Example:  python MetStudyBot.py MTBLC15355
                  ALL COMPOUNDS : python MetCompoundBot.py '/Users/venkata/Development/MetaboLightsBots/mapping.json' '/Users/venkata/Development/MetaboLightsBots/Compounds' --compound=MTBLC15354
                  MTBLS15354: python MetCompoundBot.py '/Users/venkata/Development/MetaboLightsBots/mapping.json' '/Users/venkata/Development/MetaboLightsBots/Compounds'
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

import json
import shutil
import urllib2
import re
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET


# Chemical Translation Service [ http://cts.fiehnlab.ucdavis.edu/ ]
ctsapi = "http://cts.fiehnlab.ucdavis.edu/service/compound/"

# MetaboLights Compounds Webservice
mcapi = "http://www.ebi.ac.uk/metabolights/webservice/compounds/"
MetaboLightsCompoundsList = mcapi + "/list"

# CACTUS Chemical identifier resolver
cactusapi = "https://cactus.nci.nih.gov/chemical/structure/"

# CHEBI api
chebiapi ="https://www.ebi.ac.uk/webservices/chebi/2.0/test/getCompleteEntity?chebiId="
chebiNSMap = {"envelop": "http://schemas.xmlsoap.org/soap/envelope/","chebi":"http://www.ebi.ac.uk/webservices/chebi"}

# ReactomeData
reactomeFile = "/Users/venkata/Development/MetaboLightsBots/reactome.json"

#Rhea API
rheaapi = "http://www.rhea-db.org/rest/1.0/ws/reaction?q="

version = "1.0.0"

# chebiCompound
chebiCompound = {}
metabolite = {}
mlmapping = {}
metabolites = []
threadsCreated = []
threads = 1
compound = ""
reactomeData = {}

def main(arguments):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("mapfile", help="- Mapping file location")
    parser.add_argument("workingdirectory", help="- Working Directory")
    parser.add_argument("--compound", help="- MetaboLights Compound Identifier", default="all")

    # Parsing command line arguments
    args = parser.parse_args(arguments)
    wd = args.workingdirectory
    mapfile = args.mapfile
    compound = args.compound

    # Check if the folder structure exist and create if it doesn't
    if not os.path.exists(wd):
        os.makedirs(wd)
    if not os.path.exists(wd+"/logs"):
        os.makedirs(wd+"/logs")

    with open(reactomeFile) as reactome_file:  
        global reactomeData
        reactomeData = json.load(reactome_file)
    
    with open(mapfile) as mapping_file:  
        global mlmapping
        mlmapping = json.load(mapping_file)

    if compound == "all":
        fetchMetaboLightsCompoundsList()
        total = len(metabolites)
        interval = int(math.ceil(total/threads))
        current = 0
        for i in range(0,threads):
            logger = logging.getLogger('thread-%s' % i)
            logger.setLevel(logging.INFO)
            # create a file handler writing to a file named after the thread
            logfilePath = wd + ("/logs/MetCompoundBot_thread-%s.log" % i)
            file_handler = logging.FileHandler(logfilePath)

            # create a custom formatter and register it for the file handler
            formatter = logging.Formatter('(%(threadName)-10s) %(message)s')
            file_handler.setFormatter(formatter)

            # register the file handler for the thread-specific logger
            logger.addHandler(file_handler)

            compoundsTemp = metabolites[current: current + interval]
            t = threading.Thread(target=runThread, args=(compoundsTemp, logger, wd, i))
            threadsCreated.append(t)
            t.start()
            current = current + interval
    else:
        logger = logging.getLogger(compound)
        logger.setLevel(logging.INFO)
        # create a file handler writing to a file named after the thread
        logfilePath = wd + ("/logs/%s.log" % compound)
        file_handler = logging.FileHandler(logfilePath)

        # create a custom formatter and register it for the file handler
        formatter = logging.Formatter('(%(threadName)-10s) %(message)s')
        file_handler.setFormatter(formatter)

        # register the file handler for the thread-specific logger
        logger.addHandler(file_handler)
        fetchCompound(compound, logger, wd)

def runThread(compounds, logger, wd, i):
    # Creating log file
    timestr = time.strftime("%Y%m%d_%H%M%S")

    logger.info("Thread started at: " +timestr)

    for compound in compounds:
        logger.info("=============================================================")
        logger.info("Fetching: " + compound)
        logger.info("=============================================================")
        try:
            fetchCompound(compound, logger, wd)
        except:
            logger.info("Fetching failed: " + compound)
        logger.info("=============================================================")
    return

def update_progress(progress):
    print '\r[{0}] {1}%'.format('#'*(progress/10000), progress)

def fetchCompound(compound,logger,wd):
    logger.info("Input Parameters:")
    logger.info("-------------------------------")
    logger.info("Compound ID: " + compound)
    logger.info("-------------------------------")
    logger.info("Started Compound: "+compound)
    logger.info("Fetching MetaboLights Compound Info:")
    mtblcs = json.loads(urllib2.urlopen(mcapi+compound).read())["content"]
    logger.info("Fetching ChEBI Compound Info:")
    chebiId = compound.replace("MTBLC","").strip();

    getChebi(chebiId);

    logger.info("Fetching CTS Data:")
    try:
        ctsc = json.loads(urllib2.urlopen(ctsapi+chebiCompound["inchiKey"]).read())
    except:
        pass

    logger.info("Fetching Structure Data:")
    try:
        cstructure = urllib2.urlopen(cactusapi+chebiCompound["inchiKey"]+"/sdf").read()
    except:
        pass
        
    try:
        metabolite["name"] = chebiCompound["chebiAsciiName"]
    except:
        metabolite["name"] = "NA"
        logger.info("Compound Error: "+compound + "Name not assigned")
        pass

    try:   
        metabolite["definition"] = chebiCompound["definition"]
    except:
        metabolite["definition"] = "NA"
        logger.info("Compound Error: "+compound + "Definition not assigned")
        pass

    try:
        metabolite["iupacNames"] = chebiCompound["IupacNames"]
    except:
        metabolite["iupacNames"] = []
        logger.info("Compound Error: "+compound + "IUPAC Names not assigned")
        pass

    try:
        metabolite["smiles"] = chebiCompound["smiles"]
    except:
        metabolite["smiles"] = "NA"
        logger.info("Compound Error: "+compound + "Smiles not assigned")
        pass

    try:
        metabolite["inchi"] = chebiCompound["inchi"]
    except:
        metabolite["inchi"] = "NA"
        logger.info("Compound Error: "+compound + "Inchi not assigned")
        pass

    try:
        metabolite["inchiKey"] = chebiCompound["inchiKey"]
    except:
        metabolite["inchiKey"] = "NA"
        logger.info("Compound Error: "+compound + "Inchikey not assigned")

        pass

    try:
        metabolite["charge"] = chebiCompound["charge"]
    except:
        metabolite["charge"] = "NA"
        logger.info("Compound Error: "+compound + "Charge not assigned")

        pass

    try:
        metabolite["averagemass"] = chebiCompound["mass"]
    except:
        metabolite["averagemass"] = "NA"
        logger.info("Compound Error: "+compound + "Average Mass not assigned")
        pass

    try:
        metabolite["exactmass"] = ctsc["exactmass"]
    except:
        metabolite["exactmass"] = "NA"
        logger.info("Compound Error: "+compound + "Exact Mass not assigned")
        pass

    try:
        metabolite["molweight"] = ctsc["molweight"]
    except:
        metabolite["molweight"] = "NA"
        logger.info("Compound Error: "+compound + "molweight not assigned")
        pass

    try:
        metabolite["formula"] = ctsc["formula"]
    except:
        metabolite["formula"] = "NA"
        logger.info("Compound Error: "+compound + "formula Mass not assigned")
        pass


    try:
        metabolite["citations"] = getCitations(chebiCompound["Citations"])
    except:
        metabolite["citations"] = []
        logger.info("Compound Error: "+compound + "Citations not assigned")

        pass

    try:
        metabolite["species"] = chebiCompound["Species"]
    except:
        metabolite["species"] = []
        logger.info("Compound Error: "+compound + "Species not assigned")

        pass

    try:
        metabolite["structure"] = cstructure
    except:
        metabolite["structure"] = "NA"
        logger.info("Compound Error: "+compound + "Structure not assigned")

        pass

    try:
        metabolite["synonyms"] = getSynonymns(chebiCompound,ctsc)
    except:
        metabolite["synonyms"] = []
        logger.info("Compound Error: "+compound + "Synonyms not assigned")
        pass

    try:
        metabolite["externalIds"] = mapExternalIDS(chebiCompound, ctsc)
    except:
        metabolite["externalIds"] = []
        logger.info("Compound Error: "+compound + "External Ids not assigned")

        pass

    try:
        metabolite["pathways"] = mapPathways(chebiCompound,ctsc,compound)
    except:
        metabolite["pathways"] = []
        logger.info("Compound Error: "+compound + "Pathways not assigned")
        pass

    try:
        metabolite["reactions"] = fetchReactions(chebiCompound)
    except:
        metabolite["reactions"] = []
        logger.info("Compound Error: "+compound + "Reactions not assigned")

        pass

    try:
        metabolite["spectra"] = processSpectra(mtblcs['mc']['metSpectras'])
    except:
        metabolite["spectra"] = []
        logger.info("Compound Error: "+compound + "Spectra not assigned")
        pass

    if chebiCompound["id"] in mlmapping['compoundMapping']:
        metabolite["studiesMapping"] = mlmapping['compoundMapping'][chebiCompound["id"]]
    else:
        metabolite["studiesMapping"] = []

    metabolite["version"] = {}
    metabolite["version"]["dateAdded"] =  datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
    metabolite["version"]["oldVersions"] = []
    metabolite["version"]["version"] = version
    

    metabolite["id"] = compound

    #print wd + "/" + compound + "/" + compound + ".json"
    writeDataToFile(wd + "/" + compound + "/" + compound + "_data.json", metabolite)
    logger.info("Completed Compound: "+compound)
    logger.info("----------------------------------------")


def getCitations(citationsList):
    epmcList = []
    for citation in citationsList:
        try:
            tempCitation = citation
            epmc = "http://www.ebi.ac.uk/europepmc/webservices/rest/search?query=" + str(citation['value']) + "&format=json&resulttype=core";
            epmcData = urllib2.urlopen(epmc).read()
            citationData =  json.loads(epmcData)['resultList']['result'][0]
            tempCitation['title'] = citationData['title']
            tempCitation['abstract'] = citationData['abstractText']
            try:
                tempCitation['doi'] = citationData['doi']
            except:
                tempCitation['doi'] = "NA"
                pass
            tempCitation['author'] = citationData['authorString']
            epmcList.append(tempCitation)
        except:
            pass
    return epmcList;

def fetchMetaboLightsCompoundsList():
    global metabolites
    response = urllib2.urlopen(MetaboLightsCompoundsList)
    metabolites = json.loads(response.read())['content']

def processSpectra(spectra):
    MetSpec = []
    for spec in spectra:
        tempSpec = {}
        tempSpec["name"] = spec["name"]
        tempSpec["id"] = str(spec["id"])
        tempSpec["url"] = "http://www.ebi.ac.uk/metabolights/webservice/compounds/spectra/" + str(spec["id"]) + "/json"
        tempSpec["path"] = spec["pathToJsonSpectra"]
        tempSpec["type"] = spec["spectraType"]
        attriArray = []
        for attri in spec["attributes"]:
            tempAttri = {}
            tempAttri["attributeName"] = attri["attributeDefinition"]["name"]
            tempAttri["attributeDescription"] = attri["attributeDefinition"]["description"]
            tempAttri["attributeValue"] = attri["value"]
            attriArray.append(tempAttri)
        tempSpec["attributes"] = attriArray
        MetSpec.append(tempSpec)
    return MetSpec

def getChebi(chebiid):
    chebiRESTResponse = urllib2.urlopen(chebiapi + chebiid).read();
    root = ET.fromstring(chebiRESTResponse).find("envelop:Body", namespaces=chebiNSMap).find("chebi:getCompleteEntityResponse", namespaces=chebiNSMap).find("chebi:return", namespaces=chebiNSMap)
    
    try:
        chebiCompound["id"] = root.find("chebi:chebiId", namespaces=chebiNSMap).text
    except:
        pass

    try:
        chebiCompound["definition"] = root.find("chebi:definition", namespaces=chebiNSMap).text
    except:
        pass

    try:
        chebiCompound["smiles"] = root.find("chebi:smiles", namespaces=chebiNSMap).text
    except:
        pass

    try:
        chebiCompound["inchi"] = root.find("chebi:inchi", namespaces=chebiNSMap).text
    except:
        pass

    try:
        chebiCompound["inchiKey"] = root.find("chebi:inchiKey", namespaces=chebiNSMap).text
    except:
        pass

    try:
        chebiCompound["charge"] = root.find("chebi:charge", namespaces=chebiNSMap).text
    except:
        pass

    try:
        chebiCompound["mass"] = root.find("chebi:mass", namespaces=chebiNSMap).text
    except:
        pass

    try:
        chebiCompound["chebiAsciiName"] = root.find("chebi:chebiAsciiName", namespaces=chebiNSMap).text
    except:
        pass

    try:
        chebiCompound["Synonyms"] = []
        for synonymn in root.findall("chebi:Synonyms", namespaces=chebiNSMap):
            chebiCompound["Synonyms"].append(synonymn.find("chebi:data", namespaces=chebiNSMap).text)
    except:
        pass

    try:
        chebiCompound["IupacNames"] = []
        for iupacname in root.findall("chebi:IupacNames", namespaces=chebiNSMap):
            chebiCompound["IupacNames"].append(synonymn.find("chebi:data", namespaces=chebiNSMap).text)
    except:
        pass

    try:
        chebiCompound["Citations"] = []
        for citation in root.findall("chebi:Citations", namespaces=chebiNSMap):
            citationDic = {}
            citationDic["source"] = citation.find("chebi:source", namespaces=chebiNSMap).text
            citationDic["type"] = citation.find("chebi:type", namespaces=chebiNSMap).text
            citationDic["value"] = citation.find("chebi:data", namespaces=chebiNSMap).text
            chebiCompound["Citations"].append(citationDic)
    except:
        pass

    try:
        chebiCompound["DatabaseLinks"] = []
        for databaselink in root.findall("chebi:DatabaseLinks", namespaces=chebiNSMap):
            databaselinkDic = {}
            databaselinkDic["source"] = databaselink.find("chebi:type", namespaces=chebiNSMap).text
            databaselinkDic["value"] = databaselink.find("chebi:data", namespaces=chebiNSMap).text
            chebiCompound["DatabaseLinks"].append(databaselinkDic)
    except:
        pass

    try:
        chebiCompound["CompoundOrigins"] = []
        chebiCompound["Species"] = {}
        for origin in root.findall("chebi:CompoundOrigins", namespaces=chebiNSMap):
            chebispecies = origin.find("chebi:speciesText", namespaces=chebiNSMap).text
            if chebispecies not in chebiCompound["Species"]:
                originDic = {}
                chebiCompound["Species"][chebispecies] = []
                originDic["SpeciesAccession"] = origin.find("chebi:speciesAccession", namespaces=chebiNSMap).text
                originDic["SourceType"] = origin.find("chebi:SourceType", namespaces=chebiNSMap).text
                originDic["SourceAccession"] = origin.find("chebi:SourceAccession", namespaces=chebiNSMap).text
                chebiCompound["Species"][chebispecies].append(originDic)
            else:
                originDic = {}
                originDic["SpeciesAccession"] = origin.find("chebi:speciesAccession", namespaces=chebiNSMap).text
                originDic["SourceType"] = origin.find("chebi:SourceType", namespaces=chebiNSMap).text
                originDic["SourceAccession"] = origin.find("chebi:SourceAccession", namespaces=chebiNSMap).text
                chebiCompound["Species"][chebispecies].append(originDic)
    except:
        pass

    try:
        if chebiCompound["id"] in mlmapping['compoundMapping']:
            studyspecies = mlmapping['compoundMapping'][chebiCompound["id"] ]
            for studyS in studyspecies:
                if studyS['species'] not in chebiCompound["Species"]:
                    originDic = {}
                    chebiCompound["Species"][studyS['species']] = []
                    originDic["Species"] = studyS['species']
                    originDic["SpeciesAccession"] = studyS['study']
                    chebiCompound["Species"][studyS['species']].append(originDic)
                else:
                    originDic = {}
                    originDic["Species"] = studyS['species']
                    originDic["SpeciesAccession"] = studyS['study']
                    chebiCompound["Species"][studyS['species']].append(originDic)
    except:
        pass

def fetchReactions(chebi):
    rheaData = urllib2.urlopen(rheaapi+chebi["id"]).read()
    soup = BeautifulSoup(rheaData, "html.parser")
    reactions = []
    for reaction in soup.findAll("rheareaction"):
        reactionDic = {}
        reactionDic["id"] = reaction.rheaid.id.string
        for rheauri in reaction.rheaid.findAll("rheauri"):
            reactionDic[rheauri.uriresponseformat.string] =  rheauri.uri.string
        reactionCML = urllib2.urlopen(reactionDic['cmlreact']).read()
        reactionRoot = ET.fromstring(reactionCML)
        reactionDic["name"] = reactionRoot.find("{http://www.xml-cml.org/schema/cml2/react}name").text
        reactions.append(reactionDic)
    return reactions

def mapPathways(chebi,ctsc,compound):
    tempPathwayDictionary = {}
    tempPathwayDictionary["WikiPathways"] = getWikiPathwaysData(chebi)
    tempPathwayDictionary["KEGGPathways"] = getKEGGData(chebi)
    tempPathwayDictionary["ReactomePathways"] = getReactomeData(compound)
    return tempPathwayDictionary

def getReactomeData(compound):
    tempReactomePathways = reactomeData[compound]
    reactomePathways = {}
    for pathway in tempReactomePathways:
        tempPathway = {}
        tempPathway['name'] = pathway['pathway']
        tempPathway['pathwayId'] = pathway['pathwayId']
        tempPathway['url'] = pathway['reactomeUrl']
        tempPathway['reactomeId'] = pathway['reactomeId']
        if pathway['species'] not in reactomePathways:
            reactomePathways[pathway['species']] = [tempPathway]
        else:
            reactomePathways[pathway['species']].append(tempPathway)
    return reactomePathways

def getKEGGData(chebi):
    pathways = []
    try:
        keggapi = "http://rest.kegg.jp/conv/compound/" + chebi["id"].lower()
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
            pathways.append(tempDict)
    except:
        pass
    return pathways


def getWikiPathwaysData(chebi):
    wikipathwaysapi = "http://webservice.wikipathways.org/index.php?ids="+chebi["id"]+"&codes=Ce&method=findPathwaysByXref&format=json"
    wikipathways =  json.loads(urllib2.urlopen(wikipathwaysapi).read())["result"]
    pathways = {}
    if len(wikipathways) > 0 :
        for pathway in wikipathways:
            if pathway["species"] in pathways:
                tempDict = {}
                tempDict["id"] = pathway["id"]
                tempDict["url"] = pathway["url"]
                tempDict["name"] = pathway["name"]
                if tempDict not in pathways[pathway["species"]]:
                    pathways[pathway["species"]].append(tempDict)
            else:
                pathways[pathway["species"]] = []
                tempDict = {}
                tempDict["id"] = pathway["id"]
                tempDict["url"] = pathway["url"]
                tempDict["name"] = pathway["name"]
                pathways[pathway["species"]].append(tempDict)
    return pathways

def mapExternalIDS(chebi,ctsc):
    externalIDs = {}
    for link in chebi["DatabaseLinks"]:
        if link["source"] != "":
            if link["source"] in externalIDs:
                externalIDs[link["source"]].append(link["value"])
            else:
                externalIDs[link["source"]] = [link["value"]]

    for link in ctsc["externalIds"]:
        if link["name"] != "":
            if link["name"] in externalIDs:
                externalIDs[link["name"]].append(link["value"])
            else:
                externalIDs[link["name"]] = [link["value"]]
    return externalIDs

def getSynonymns(chebi,ctsc):
    synonyms = chebi["Synonyms"]
    # cts synonyms
    for synonym in ctsc["synonyms"]:
        synonyms.append(synonym["name"])
    # remove duplicates
    synonyms = list(set(name.lower() for name in synonyms))
    return synonyms

def writeDataToFile(filename, data):
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    with open(filename, "w") as fp:
        json.dump(data, fp)

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))