from MetCompoundBot import utils

complist = utils.fetchMetaboLightsCompoundsList()
print(len(complist))

studylist = utils.fetchMetaboLightsStudiesList()
print(len(studylist))

