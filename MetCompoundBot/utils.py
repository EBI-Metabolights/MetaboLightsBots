#!/usr/bin/env python

import os
import json
import time
import urllib2
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from math import ceil, floor
import datetime

# MetaboLights api
MetaboLightsWSUrl = "http://www.ebi.ac.uk/metabolights/webservice/"
MetaboLightsWSStudyUrl = "http://www.ebi.ac.uk/metabolights/webservice/study/"
MetaboLightsWSStudiesList = MetaboLightsWSUrl + "study/list"
MetaboLightsWSCompoundsUrl = "http://www.ebi.ac.uk/metabolights/webservice/compounds/"
MetaboLightsWSCompoundsList = MetaboLightsWSUrl + "compounds/list"

# CHEBI api
chebiapi ="https://www.ebi.ac.uk/webservices/chebi/2.0/test/getCompleteEntity?chebiId="
chebiNSMap = {"envelop": "http://schemas.xmlsoap.org/soap/envelope/","chebi":"http://www.ebi.ac.uk/webservices/chebi"}

# Chemical Translation Service [ http://cts.fiehnlab.ucdavis.edu/ ]
ctsapi = "http://cts.fiehnlab.ucdavis.edu/service/compound/"

# CACTUS Chemical identifier resolver
cactusapi = "https://cactus.nci.nih.gov/chemical/structure/"

epmcAPI = "http://www.ebi.ac.uk/europepmc/webservices/rest/search?query="

MLStudiesList = []
MLCompoundsList = []

ReactomeJSON = {}
ReactomeUrl = "http://www.reactome.org/download/current/ChEBI2Reactome.txt"

#Rhea API
rheaapi = "http://www.rhea-db.org/rest/1.0/ws/reaction?q="

chebiCompound = {}

def fetchMetaboLightsStudiesList():
    response = urllib2.urlopen(MetaboLightsWSStudiesList)
    return json.loads(response.read())['content']

def fetchMetaboLightsCompoundsList():
    response = urllib2.urlopen(MetaboLightsWSCompoundsList)
    return json.loads(response.read())['content']

def generateMLStudyCompoundMappingFile(mappingFile):
    studiesList = {}
    compoundsList = {}
    speciesList = []
    mt = {}
    global MLStudiesList
    MLStudiesList = fetchMetaboLightsStudiesList()
    for study in MLStudiesList:
        print study
        studyContent = json.loads(urllib2.urlopen(MetaboLightsWSStudyUrl + study).read())["content"]
        assayNumber = 1
        for assay in studyContent["assays"]:
            try:
                metabolitesLines = json.loads(urllib2.urlopen( MetaboLightsWSStudyUrl + study + "/assay/" + str(assayNumber) + "/maf").read())["content"]['metaboliteAssignmentLines']
                for line in metabolitesLines:
                    dbID = str(line['databaseIdentifier'])
                    if dbID != '':
                        species = str(line['species'])
                        if species not in speciesList and species != "":
                            speciesList.append(species)
                        tempCompound = {}
                        if dbID not in compoundsList:
                            compoundsList[dbID] = []
                            tempCompound['study'] = study
                            tempCompound['assay'] = assayNumber
                            tempCompound['species'] = species
                            tempCompound['mafEntry'] = line
                            compoundsList[dbID].append(tempCompound)
                        else:
                            tempCompound['study'] = study
                            tempCompound['assay'] = assayNumber
                            tempCompound['species'] = species
                            tempCompound['mafEntry'] = line
                            compoundsList[dbID].append(tempCompound)
                        tempStudy = {}
                        if study not in studiesList:
                            studiesList[study] = []
                            tempStudy['compound'] = dbID
                            tempStudy['assay'] = assayNumber
                            tempStudy['species'] = species
                            studiesList[study].append(tempStudy)
                        else:
                            tempStudy['compound'] = dbID
                            tempStudy['assay'] = assayNumber
                            tempStudy['species'] = species
                            studiesList[study].append(tempStudy)
                assayNumber += 1
            except:
                pass
    mt['studyMapping'] = studiesList
    mt['compoundMapping'] = compoundsList
    mt['speciesList'] = speciesList
    mt['updatedAt'] = str(datetime.datetime.now())
    writeDataToFile(mappingFile, mt)

def getReactomeData(reactomeFile):
    reactomeData = urllib2.urlopen(ReactomeUrl).read()
    for line in reactomeData.split("\n"):
        if line:
            dataArray = line.split("\t")
            metabolightsId = "MTBLC" + str(dataArray[0])
            tempDic = {}
            tempDic['reactomeId'] = str(dataArray[1])
            tempDic['reactomeUrl'] = str(dataArray[2])
            tempDic['pathway'] = str(dataArray[3])
            tempDic['pathwayId'] = str(dataArray[4])
            tempDic['species'] = str(dataArray[5])
        if metabolightsId not in ReactomeJSON:
            ReactomeJSON[metabolightsId] = [tempDic]
        else:
            ReactomeJSON[metabolightsId].append(tempDic)
    writeDataToFile( reactomeFile, ReactomeJSON)

def init(loggingObject):
	global logger
	logger = loggingObject

def getChebiData(chebiId,mlMapping):
    global chebiCompound
    chebiRESTResponse = urllib2.urlopen(chebiapi + chebiId).read();
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
        chebiCompound["mass"] = root.find("chebi:mass", namespaces=chebiNSMap).tex
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
            chebispecies = origin.find("chebi:speciesText", namespaces=chebiNSMap).text.lower()
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
        if chebiCompound["id"] in mlMapping['compoundMapping']:
            studyspecies = mlMapping['compoundMapping'][chebiCompound["id"]]
            for studyS in studyspecies:
                if (studyS['species'] != ""):
                    tempSSpecies = str(studyS['species']).lower()
                    if tempSSpecies not in chebiCompound["Species"]:
                        originDic = {}
                        chebiCompound["Species"][tempSSpecies] = []
                        originDic["Species"] = tempSSpecies
                        originDic["SpeciesAccession"] = studyS['study']
                        originDic["MAFEntry"] = studyS['mafEntry']
                        originDic["Assay"] = studyS['assay']
                        chebiCompound["Species"][tempSSpecies].append(originDic)
                    else:
                        originDic = {}
                        originDic["Species"] = tempSSpecies
                        originDic["SpeciesAccession"] = studyS['study']
                        originDic["MAFEntry"] = studyS['mafEntry']
                        originDic["Assay"] = studyS['assay']
                        chebiCompound["Species"][tempSSpecies].append(originDic)
    except:
        pass

def fetchCompound(metabolightsID, wd, dd, reactomeData, mlMapping):
    logger.info("-----------------------------------------------")
    logger.info("Compound ID: " + metabolightsID)
    logger.info("-----------------------------------------------")
    logger.info("Process started: " + metabolightsID)
    logger.info("Requesting compound chemical information from ChEBI:")
    chebiId = metabolightsID.replace("MTBLC","").strip();
    mtblcs = json.loads(urllib2.urlopen(MetaboLightsWSCompoundsUrl+metabolightsID).read())["content"]
    getChebiData(chebiId, mlMapping);
    logger.info("Initialising MetaboLightsCompoundJSON")
    MetaboLightsCompoundJSON = {}
    MetaboLightsCompoundJSON["flags"] = {}
    MetaboLightsCompoundJSON["flags"]['hasLiterature'] = "false"
    MetaboLightsCompoundJSON["flags"]['hasReactions'] = "false"
    MetaboLightsCompoundJSON["flags"]['hasSpecies'] = "false"
    MetaboLightsCompoundJSON["flags"]['hasPathways'] = "false"
    MetaboLightsCompoundJSON["flags"]['hasNMR'] = "false"
    MetaboLightsCompoundJSON["flags"]['hasMS'] = "false"
    logger.info("Requesting compound chemical information from CTS:")
    try:
        ctsc = json.loads(urllib2.urlopen(ctsapi+chebiCompound["inchiKey"]).read())
    except:
        pass
    MetaboLightsCompoundJSON["id"] = metabolightsID
    try:
        MetaboLightsCompoundJSON["name"] = chebiCompound["chebiAsciiName"]
    except:
        MetaboLightsCompoundJSON["name"] = "NA"
        logger.info("Compound Error: "+ metabolightsID + "Name not assigned")
        pass

    try:   
        MetaboLightsCompoundJSON["definition"] = chebiCompound["definition"]
    except:
        MetaboLightsCompoundJSON["definition"] = "NA"
        logger.info("Compound Error: "+metabolightsID + "Definition not assigned")
        pass

    try:
        MetaboLightsCompoundJSON["iupacNames"] = chebiCompound["IupacNames"]
    except:
        MetaboLightsCompoundJSON["iupacNames"] = []
        logger.info("Compound Error: "+metabolightsID + "IUPAC Names not assigned")
        pass

    try:
        MetaboLightsCompoundJSON["smiles"] = chebiCompound["smiles"]
    except:
        MetaboLightsCompoundJSON["smiles"] = "NA"
        logger.info("Compound Error: "+metabolightsID + "Smiles not assigned")
        pass

    try:
        MetaboLightsCompoundJSON["inchi"] = chebiCompound["inchi"]
    except:
        MetaboLightsCompoundJSON["inchi"] = "NA"
        logger.info("Compound Error: "+metabolightsID + "Inchi not assigned")
        pass

    try:
        MetaboLightsCompoundJSON["inchiKey"] = chebiCompound["inchiKey"]
    except:
        MetaboLightsCompoundJSON["inchiKey"] = "NA"
        logger.info("Compound Error: "+metabolightsID + "Inchikey not assigned")
        pass

    try:
        MetaboLightsCompoundJSON["charge"] = chebiCompound["charge"]
    except:
        MetaboLightsCompoundJSON["charge"] = "NA"
        logger.info("Compound Error: "+metabolightsID + "Charge not assigned")
        pass

    try:
        MetaboLightsCompoundJSON["averagemass"] = chebiCompound["mass"]
    except:
        MetaboLightsCompoundJSON["averagemass"] = "NA"
        logger.info("Compound Error: "+metabolightsID + "Average Mass not assigned")
        pass

    try:
        MetaboLightsCompoundJSON["exactmass"] = ctsc["exactmass"]
    except:
        MetaboLightsCompoundJSON["exactmass"] = "NA"
        logger.info("Compound Error: "+metabolightsID + "Exact Mass not assigned")
        pass

    try:
        MetaboLightsCompoundJSON["molweight"] = ctsc["molweight"]
    except:
        MetaboLightsCompoundJSON["molweight"] = "NA"
        logger.info("Compound Error: "+metabolightsID + "molweight not assigned")
        pass

    try:
        MetaboLightsCompoundJSON["formula"] = ctsc["formula"]
    except:
        MetaboLightsCompoundJSON["formula"] = "NA"
        logger.info("Compound Error: "+metabolightsID + "formula Mass not assigned")
        pass

    logger.info("Fetching Citations:")
    try:
        MetaboLightsCompoundJSON["citations"] = getCitations(chebiCompound["Citations"])
        if MetaboLightsCompoundJSON["citations"]:
            MetaboLightsCompoundJSON["flags"]['hasLiterature'] = "true"
    except:
        MetaboLightsCompoundJSON["citations"] = []
        MetaboLightsCompoundJSON["flags"]['hasLiterature'] = "false"
        logger.info("Compound Error: "+metabolightsID + "Citations not assigned")
        pass

    try:
        MetaboLightsCompoundJSON["species"] = chebiCompound["Species"]

        if MetaboLightsCompoundJSON["species"] :
            MetaboLightsCompoundJSON["flags"]['hasSpecies'] = "true"
    except:
        MetaboLightsCompoundJSON["species"] = []
        MetaboLightsCompoundJSON["flags"]['hasSpecies'] = "false"
        logger.info("Compound Error: "+metabolightsID + "Species not assigned")
        pass

    logger.info("Fetching Structure Data:")
    try:
        MetaboLightsCompoundJSON["structure"] = urllib2.urlopen(cactusapi+chebiCompound["inchiKey"]+"/sdf").read()
    except:
        MetaboLightsCompoundJSON["structure"] = "NA"
        logger.info("Compound Error: "+metabolightsID + "Structure not assigned")
        pass

    try:
        MetaboLightsCompoundJSON["synonyms"] = getSynonymns(chebiCompound,ctsc)
    except:
        MetaboLightsCompoundJSON["synonyms"] = []
        logger.info("Compound Error: "+metabolightsID + "Synonyms not assigned")
        pass

    try:
        MetaboLightsCompoundJSON["externalIds"] = mapExternalIDS(chebiCompound, ctsc)
    except:
        MetaboLightsCompoundJSON["externalIds"] = []
        logger.info("Compound Error: "+metabolightsID + "External Ids not assigned")
        pass

    try:
        MetaboLightsCompoundJSON["pathways"] = mapPathways(chebiCompound, ctsc, metabolightsID, reactomeData, MetaboLightsCompoundJSON)
    except:
        MetaboLightsCompoundJSON["pathways"] = {}
        logger.info("Compound Error: "+metabolightsID + "Pathways not assigned")
        pass

    try:
        MetaboLightsCompoundJSON["reactions"] = fetchReactions(chebiCompound)
        if MetaboLightsCompoundJSON["reactions"]:
            MetaboLightsCompoundJSON["flags"]['hasReactions'] = "true"
    except:
        MetaboLightsCompoundJSON["reactions"] = []
        MetaboLightsCompoundJSON["flags"]['hasReactions'] = "false"
        logger.info("Compound Error: "+ metabolightsID + "Reactions not assigned")
        pass
        
    MetaboLightsCompoundJSON["spectra"] = fetchSpectra(mtblcs['mc']['metSpectras'],metabolightsID, dd)
    if MetaboLightsCompoundJSON["spectra"]['MS']:
        MetaboLightsCompoundJSON["flags"]['hasMS'] = "true"
    if MetaboLightsCompoundJSON["spectra"]['NMR']:
        MetaboLightsCompoundJSON["flags"]['hasNMR'] = "true"

    logger.info("Writing data to _data.json file - location: " + dd + "/" + metabolightsID + "/" + metabolightsID + "_data.json")
    writeDataToFile(dd + "/" + metabolightsID + "/" + metabolightsID + "_data.json", MetaboLightsCompoundJSON)
    logger.info("-----------------------------------------------")

def fetchSpectra(spectra, metabolightsID, dd):
    MetSpec = {}
    MetSpec['NMR'] = []
    MetSpec['MS'] = []
    try:
        for spec in spectra:
            if(spec["spectraType"] == "NMR"):
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
                MetSpec['NMR'].append(tempSpec)
    except:
        logger.info("Compound Error: "+ metabolightsID + " NMR Spectra not assigned")
        pass
    
    MetSpec['MS'] = fetchMSFromMONA(chebiCompound["inchiKey"], metabolightsID, dd)
   
    return MetSpec

def fetchMSFromMONA(inchikey, metabolightsID, dd):
    ml_spectrum = []
    url = "http://mona.fiehnlab.ucdavis.edu/rest/spectra/search?query=compound.metaData=q=%27name==\%22InChIKey\%22%20and%20value==\%22"+inchikey+"\%22%27"
    result = json.load(urllib2.urlopen(url))
    for spectra in result:
        ml_spectra = {}
        ml_spectra['splash'] = spectra['splash']
        tempSpectraName = str(spectra['id'])
        ml_spectra['name'] =  tempSpectraName
        ml_spectra['type'] = "MS"
        ml_spectra['url'] = "/metabolights/webservice/beta/spectra/"+ metabolightsID + "/" + tempSpectraName
        tempSubmitter = spectra['submitter']
        ml_spectra['submitter'] =  str(tempSubmitter['firstName']) + " " + str(tempSubmitter['lastName']) + " ; " + str(tempSubmitter['emailAddress']) + " ; " + str(tempSubmitter['institution'])
        ml_spectra['attributes'] = []
        for metadata in spectra['metaData']:
            tempAttri = {}
            if metadata['computed'] == False:
                tempAttri['attributeName'] = metadata['name'] 
                tempAttri['attributeValue'] = metadata['value']
                tempAttri['attributeDescription'] = ""
                ml_spectra['attributes'].append(tempAttri)
        #if not copyright:
        ml_spectrum.append(ml_spectra)
        storeSpectra(tempSpectraName, spectra['spectrum'], metabolightsID, dd)
    return ml_spectrum

def storeSpectra(specid, spectraData, metabolightsID, dd):
    destination = dd + metabolightsID + "/" + metabolightsID + "_spectrum" + "/" + specid + "/" + specid + ".json"
    datapoints = spectraData.split(" ");
    mlSpectrum = {}
    mlSpectrum["spectrumId"] = specid
    mlSpectrum["peaks"] = []
    mzArray = []
    for datapoint in datapoints:
        tempArray = datapoint.split(":")
        tempPeak = {}
        tempPeak['intensity'] = float_round(float(tempArray[1].strip()) * 9.99, 6)
        tempPeak['mz'] = float(tempArray[0].strip())
        mlSpectrum["peaks"].append(tempPeak)
        mzArray.append(float(tempPeak['mz']))
    mlSpectrum["mzStart"] = min(mzArray)
    mlSpectrum["mzStop"] = max(mzArray)
    writeDataToFile(destination, mlSpectrum)

def float_round(num, places = 0, direction = floor):
    return direction(num * (10**places)) / float(10**places)

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

def mapPathways(chebi,ctsc,compound, reactomeData, MetaboLightsCompoundJSON):
    tempPathwayDictionary = {}
    tempPathwayDictionary["WikiPathways"] = getWikiPathwaysData(chebi)
    tempPathwayDictionary["KEGGPathways"] = getKEGGData(chebi)
    tempPathwayDictionary["ReactomePathways"] = getReactomePathwaysData(compound, reactomeData)
    
    if (len(tempPathwayDictionary["WikiPathways"]) > 0 ):
        MetaboLightsCompoundJSON["flags"]['hasPathways'] = "true"
    elif(len(tempPathwayDictionary["ReactomePathways"]) >0 ):
        MetaboLightsCompoundJSON["flags"]['hasPathways'] = "true"
    elif(len(tempPathwayDictionary["KEGGPathways"]) > 0):
        MetaboLightsCompoundJSON["flags"]['hasPathways'] = "true"

    return tempPathwayDictionary

def getWikiPathwaysData(chebi):
    pathways = {}
    try:
        wikipathwaysapi = "http://webservice.wikipathways.org/index.php?ids="+chebi["id"]+"&codes=Ce&method=findPathwaysByXref&format=json"
        wikipathways =  json.loads(urllib2.urlopen(wikipathwaysapi).read())["result"]
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
    except:
        pass
    return pathways
    
def getReactomePathwaysData(compound, reactomeData):
    tempReactomePathways = reactomeData[compound]
    reactomePathways = {}
    try:
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
    except:
        pass
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

def getCitations(citationsList):
    epmcList = []
    for citation in citationsList:
        try:
            tempCitation = citation
            epmc = epmcAPI + str(citation['value']) + "&format=json&resulttype=core";
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

def getReactomeData(reactomeFile):
    reactomeData = urllib2.urlopen(ReactomeUrl).read()
    for line in reactomeData.split("\n"):
        if line:
            dataArray = line.split("\t")
            metabolightsId = "MTBLC" + str(dataArray[0])
            tempDic = {}
            tempDic['reactomeId'] = str(dataArray[1])
            tempDic['reactomeUrl'] = str(dataArray[2])
            tempDic['pathway'] = str(dataArray[3])
            tempDic['pathwayId'] = str(dataArray[4])
            tempDic['species'] = str(dataArray[5])
        if metabolightsId not in ReactomeJSON:
            ReactomeJSON[metabolightsId] = [tempDic]
        else:
            ReactomeJSON[metabolightsId].append(tempDic)
    writeDataToFile( reactomeFile, ReactomeJSON)

def getDateAndTime():
	ts = time.time()
	return datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

def writeDataToFile(filename, data):
	if not os.path.exists(os.path.dirname(filename)):
		try:
			os.makedirs(os.path.dirname(filename))
		except OSError as exc:
			if exc.errno != errno.EEXIST:
				raise
	with open(filename, "w") as fp:
		json.dump(data, fp)

def appendDataToFile(filename, data):
	if not os.path.exists(os.path.dirname(filename)):
		try:
			os.makedirs(os.path.dirname(filename))
		except OSError as exc:
			if exc.errno != errno.EEXIST:
				raise
	with open(filename, "a") as fp:
		json.dump(data, fp)