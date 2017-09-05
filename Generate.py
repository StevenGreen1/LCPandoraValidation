import os
import re
import sys

# Arguments
compactFile  = sys.argv[1]

print 'Using compact Xml file : ' + compactFile

cwd = os.getcwd()

#########################
# Make Templates Folder
#########################
templatesFolder = os.path.join(cwd, 'MarlinJobs/Templates')
if not os.path.exists(templatesFolder):
    os.makedirs(templatesFolder)

#########################
# Get Release Pandora Settings
#########################

# Get Pandora Settings and Likelihood From ILDConfig
pandoraSettingsReleaseFolder = os.path.join(cwd, 'MarlinJobs/PandoraSettings/Release')
if not os.path.exists(pandoraSettingsReleaseFolder):
    os.makedirs(pandoraSettingsReleaseFolder)

standardConfigFolder = os.path.join(cwd, 'ILDConfig/StandardConfig/lcgeo_current/')
os.system('cp ' + os.path.join(standardConfigFolder, 'PandoraSettingsDefault.xml') + ' ' + pandoraSettingsReleaseFolder)
os.system('cp ' + os.path.join(standardConfigFolder, 'PandoraSettingsPerfectPhoton.xml') + ' ' + pandoraSettingsReleaseFolder)
os.system('cp ' + os.path.join(standardConfigFolder, 'PandoraSettingsPerfectPhotonNeutronK0L.xml') + ' ' + pandoraSettingsReleaseFolder)
os.system('cp ' + os.path.join(standardConfigFolder, 'PandoraSettingsPerfectPFA.xml') + ' ' + pandoraSettingsReleaseFolder)
os.system('cp ' + os.path.join(standardConfigFolder, 'PandoraLikelihoodData9EBin.xml') + ' ' + pandoraSettingsReleaseFolder)

releasePandoraSettingsDefault = os.path.join(pandoraSettingsReleaseFolder, 'PandoraSettingsDefault.xml')
releasePandoraSettingsLikelihoodData = os.path.join(pandoraSettingsReleaseFolder, 'PandoraLikelihoodData9EBin.xml')

releasePandoraSettingsDefaultFile = open(releasePandoraSettingsDefault, 'r')
content = releasePandoraSettingsDefaultFile.read()
releasePandoraSettingsDefaultFile.close()

content = re.sub('PandoraLikelihoodData9EBin.xml', releasePandoraSettingsLikelihoodData, content)

releasePandoraSettingsDefaultFile = open(releasePandoraSettingsDefault, 'w')
releasePandoraSettingsDefaultFile.write(content)
releasePandoraSettingsDefaultFile.close()

# Find Pandora Analysis To Use
releasePandoraAnalysis = ''

lines = [line.rstrip('\n') for line in open('init_ilcsoft.sh')]
newContent = ''
cwd = os.getcwd()
for line in lines:
    if 'DDMarlinPandora' in line:
        newline = ''
        for subline in line.split(':'):
            if 'libPandoraAnalysis' in subline:
                releasePandoraAnalysis = subline

releasePandoraAnalysis = os.path.join(os.path.dirname(releasePandoraAnalysis),'../bin')

#########################
# Get Local Pandora Settings
#########################

# Get Pandora Settings and Likelihood From ILDConfig
pandoraSettingsLocalFolder = os.path.join(cwd, 'MarlinJobs/PandoraSettings/Local')
if not os.path.exists(pandoraSettingsLocalFolder):
    os.makedirs(pandoraSettingsLocalFolder)

os.system('cp ' + os.path.join(standardConfigFolder, 'PandoraSettingsDefault.xml') + ' ' + pandoraSettingsLocalFolder)
os.system('cp ' + os.path.join(standardConfigFolder, 'PandoraSettingsPerfectPhoton.xml') + ' ' + pandoraSettingsLocalFolder)
os.system('cp ' + os.path.join(standardConfigFolder, 'PandoraSettingsPerfectPhotonNeutronK0L.xml') + ' ' + pandoraSettingsLocalFolder)
os.system('cp ' + os.path.join(standardConfigFolder, 'PandoraSettingsPerfectPFA.xml') + ' ' + pandoraSettingsLocalFolder)
os.system('cp ' + os.path.join(standardConfigFolder, 'PandoraLikelihoodData9EBin.xml') + ' ' + pandoraSettingsLocalFolder)

localPandoraSettingsDefault = os.path.join(pandoraSettingsLocalFolder, 'PandoraSettingsDefault.xml')
localPandoraSettingsLikelihoodData = os.path.join(pandoraSettingsLocalFolder, 'PandoraLikelihoodData9EBin.xml')

localPandoraSettingsDefaultFile = open(localPandoraSettingsDefault, 'r')
content = localPandoraSettingsDefaultFile.read()
localPandoraSettingsDefaultFile.close()

content = re.sub('PandoraLikelihoodData9EBin.xml', localPandoraSettingsLikelihoodData, content)

localPandoraSettingsDefaultFile = open(localPandoraSettingsDefault, 'w')
localPandoraSettingsDefaultFile.write(content)
localPandoraSettingsDefaultFile.close()

localPandoraAnalysis = os.path.join(cwd,'LCPandoraAnalysis/bin')

#########################
# Make MarlinLocal.sh
#########################
marlinLocal = """#!/bin/bash
source """ + os.path.join(cwd, 'init_ilcsoft_local.sh') + """
ls $ILCSOFT

Marlin  $1
"""
marlinLocalFileName = os.path.join(cwd, 'MarlinJobs/Templates/MarlinLocal.sh')
marlinLocalFile = open(marlinLocalFileName, 'w')
marlinLocalFile.write(marlinLocal)
marlinLocalFile.close()
os.system('chmod u+x MarlinJobs/Templates/MarlinLocal.sh')

#########################
# Make MarlinRelease.sh
#########################
marlinRelease = """#!/bin/bash
source """ + os.path.join(cwd, 'init_ilcsoft.sh') + """
ls $ILCSOFT

Marlin  $1
"""
marlinReleaseFileName = os.path.join(cwd, 'MarlinJobs/Templates/MarlinRelease.sh')
marlinReleaseFile = open(marlinReleaseFileName, 'w')
marlinReleaseFile.write(marlinRelease)
marlinReleaseFile.close()
os.system('chmod u+x MarlinJobs/Templates/MarlinRelease.sh')

#########################
# Make MarlinTemplate.xml
#########################
standardConfigXml = os.path.join(standardConfigFolder, 'bbudsc_3evt_stdreco_dd4hep.xml')

newContent = ''
lines = [line.rstrip('\n') for line in open(standardConfigXml)]
processorsToRemove = ['BgOverlay', 'MyAdd4MomCovMatrixCharged', 'MyAddClusterProperties', 'MyBeamCalClusterReco', 'BCalAddClusterProperties', 'MyComputeShowerShapesProcessor', 'MyPi0Finder', 'MyEtaFinder', 'MyEtaPrimeFinder', 'MyGammaGammaSolutionFinder', 'MyDistilledPFOCreator', 'MyLikelihoodPID', 'MyTauFinder', 'MyRecoMCTruthLinker', 'VertexFinder', 'MyLCIOOutputProcessor', 'DSTOutput']
delete = False
deleteParam = False
for line in lines:
    line = line.rstrip()
    ### Processors
    if 'processor name' in line and any(processor in line for processor in processorsToRemove) and '/>' in line:
        line = ''
    elif 'processor name' in line and 'MarlinPandora' in line and '/>' in line:
        line = 'PandoraHeader\n'
    elif 'processor name' in line and 'PfoAnalysis' in line and '/>' in line:
        line = ''
    elif 'processor name' in line and 'ILDCaloDigi' in line and '/>' in line:
        line = 'DigitiserHeader\n'
    elif 'processor name' in line and 'SimpleMuonDigi' in line and '/>' in line:
        line = 'SimpleMuonDigiHeader\n'
    elif 'parameter name' in line and 'GearXMLFile' in line and '/>' in line:
        line = '      <parameter name="GearXMLFile" value="GearFile"/>\n'
    elif 'parameter name' in line and 'MaxRecordNumber' in line and '/>' in line:
        line = '      <parameter name="MaxRecordNumber" value="-1"/>\n'
    else:
        ### Implementations
        if 'processor name' in line and 'MarlinPandora' in line and '/>' not in line:
            newContent += 'PandoraImplementation\n'
            delete = True
        elif 'processor name' in line and 'PfoAnalysis' in line and '/>' not in line:
            delete = True
        elif 'processor name' in line and 'ILDCaloDigi' in line and '/>' not in line:
            newContent += 'DigitiserImplementation\n'
            delete = True
        elif 'processor name' in line and 'SimpleMuonDigi' in line and '/>' not in line:
            newContent += 'SimpleMuonDigiImplementation\n'
            delete = True
        elif delete and '</processor>' in line:
            line = ''
            delete = False
        ### Input Slcio File
        if 'parameter name' in line and 'LCIOInputFiles' in line:
            newContent += """      <parameter name="LCIOInputFiles"> LcioInputFile </parameter>\n"""
            deleteParam = True
        elif deleteParam and '</parameter>' in line:
            line = ''
            deleteParam = False

    if not delete and not deleteParam:
        newContent += line + '\n'


newContent = re.sub('\$lcgeo_DIR/ILD/compact/ILD_o1_v05/ILD_o1_v05.xml', compactFile, newContent)

newTemplateFile = open('MarlinJobs/Templates/MarlinTemplate.xml', 'w')
newTemplateFile.write(newContent)
newTemplateFile.close()

#########################
# Make AnalysePerformance.sh
#########################
analysePerformanceRelease = os.path.join(releasePandoraAnalysis,'AnalysePerformance')
analysePerformanceLocal = os.path.join(localPandoraAnalysis,'AnalysePerformance')
analysePerformance = os.path.join(cwd, 'AnalysePerformance/AnalysePerformance.py')

analysePerformanceFile = open(analysePerformance, 'r')
content = analysePerformanceFile.read()
analysePerformanceFile.close()

content = re.sub('#ReleaseBinary#', analysePerformanceRelease, content)
content = re.sub('#LocalBinary#', analysePerformanceLocal, content)

analysePerformanceFile = open(analysePerformance, 'w')
analysePerformanceFile.write(content)
analysePerformanceFile.close()

