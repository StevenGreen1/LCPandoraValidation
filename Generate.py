import os
import re
import sys

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
releaseMarlinPandora = ''
releasePandoraAnalysis = ''
lines = [line.rstrip('\n') for line in open('init_ilcsoft.sh')]
newContent = ''
cwd = os.getcwd()
for line in lines:
    if 'MarlinPandora' in line:
        newline = ''
        for subline in line.split(':'):
            if 'libMarlinPandora' in subline:
                releaseMarlinPandora = subline
            elif 'libPandoraAnalysis' in subline:
                releasePandoraAnalysis = subline
releaseMarlinPandoraScriptsFolder = os.path.join(os.path.dirname(releaseMarlinPandora),'../scripts')
releasePandoraAnalysis = os.path.join(os.path.dirname(releasePandoraAnalysis),'../bin')

pandoraSettingsReleaseFolder = os.path.join(cwd, 'MarlinJobs/PandoraSettings/Release')
if not os.path.exists(pandoraSettingsReleaseFolder):
    os.makedirs(pandoraSettingsReleaseFolder)

os.system('cp ' + releaseMarlinPandoraScriptsFolder + '/* ' + pandoraSettingsReleaseFolder)
releasePandoraSettingsDefault = os.path.join(pandoraSettingsReleaseFolder, 'PandoraSettingsDefault.xml')
releasePandoraSettingsLikelihoodData = os.path.join(pandoraSettingsReleaseFolder, 'PandoraLikelihoodData9EBin.xml')

releasePandoraSettingsDefaultFile = open(releasePandoraSettingsDefault, 'r')
content = releasePandoraSettingsDefaultFile.read()
releasePandoraSettingsDefaultFile.close()

print releasePandoraSettingsLikelihoodData
content = re.sub('PandoraLikelihoodData9EBin.xml', releasePandoraSettingsLikelihoodData, content)

releasePandoraSettingsDefaultFile = open(releasePandoraSettingsDefault, 'w')
releasePandoraSettingsDefaultFile.write(content)
releasePandoraSettingsDefaultFile.close()

#########################
# Get Local Pandora Settings
#########################
pandoraSettingsLocalFolder = os.path.join(cwd, 'MarlinJobs/PandoraSettings/Local')
if not os.path.exists(pandoraSettingsLocalFolder):
    os.makedirs(pandoraSettingsLocalFolder)

localMarlinPandoraScriptsFolder = os.path.join(cwd, 'MarlinPandora/scripts')
os.system('cp ' + localMarlinPandoraScriptsFolder + '/* ' + pandoraSettingsLocalFolder)
localPandoraSettingsDefault = os.path.join(pandoraSettingsLocalFolder, 'PandoraSettingsDefault.xml')
localPandoraSettingsLikelihoodData = os.path.join(pandoraSettingsLocalFolder, 'PandoraLikelihoodData9EBin.xml')

localPandoraSettingsDefaultFile = open(localPandoraSettingsDefault, 'r')
content = localPandoraSettingsDefaultFile.read()
localPandoraSettingsDefaultFile.close()

content = re.sub('PandoraLikelihoodData9EBin.xml', localPandoraSettingsLikelihoodData, content)

localPandoraSettingsDefaultFile = open(localPandoraSettingsDefault, 'w')
localPandoraSettingsDefaultFile.write(content)
localPandoraSettingsDefaultFile.close()

#########################
# Make MarlinLocal.sh
#########################
marlinLocal = """#!/bin/bash
gcc_config_version=4.8.1
mpfr_config_version=3.1.2
gmp_config_version=5.1.1
LCGPLAT=x86_64-slc6-gcc48-opt
LCG_lib_name=lib64
LCG_arch=x86_64

LCG_contdir=/afs/cern.ch/sw/lcg/contrib
LCG_gcc_home=${LCG_contdir}/gcc/${gcc_config_version}/${LCGPLAT}
LCG_mpfr_home=${LCG_contdir}/mpfr/${mpfr_config_version}/${LCGPLAT}
LCG_gmp_home=${LCG_contdir}/gmp/${gmp_config_version}/${LCGPLAT}

export PATH=${LCG_gcc_home}/bin:${PATH}
export COMPILER_PATH=${LCG_gcc_home}/lib/gcc/${LCG_arch}-unknown-linux-gnu/${gcc_config_version}

if [ ${LD_LIBRARY_PATH} ]
then
export LD_LIBRARY_PATH=${LCG_gcc_home}/${LCG_lib_name}:${LCG_mpfr_home}/lib:${LCG_gmp_home}/lib:${LD_LIBRARY_PATH}
else
export LD_LIBRARY_PATH=${LCG_gcc_home}/${LCG_lib_name}:${LCG_mpfr_home}/lib:${LCG_gmp_home}/lib
fi

export PATH=/afs/cern.ch/sw/lcg/external/Python/2.7.4/x86_64-slc6-gcc48-opt/bin/:$PATH
export LD_LIBRARY_PATH=/afs/cern.ch/sw/lcg/external/Python/2.7.4/x86_64-slc6-gcc48-opt/lib/:$LD_LIBRARY_PATH

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

gcc_config_version=4.8.1
mpfr_config_version=3.1.2
gmp_config_version=5.1.1
LCGPLAT=x86_64-slc6-gcc48-opt
LCG_lib_name=lib64
LCG_arch=x86_64

LCG_contdir=/afs/cern.ch/sw/lcg/contrib
LCG_gcc_home=${LCG_contdir}/gcc/${gcc_config_version}/${LCGPLAT}
LCG_mpfr_home=${LCG_contdir}/mpfr/${mpfr_config_version}/${LCGPLAT}
LCG_gmp_home=${LCG_contdir}/gmp/${gmp_config_version}/${LCGPLAT}

export PATH=${LCG_gcc_home}/bin:${PATH}
export COMPILER_PATH=${LCG_gcc_home}/lib/gcc/${LCG_arch}-unknown-linux-gnu/${gcc_config_version}

if [ ${LD_LIBRARY_PATH} ]
then
export LD_LIBRARY_PATH=${LCG_gcc_home}/${LCG_lib_name}:${LCG_mpfr_home}/lib:${LCG_gmp_home}/lib:${LD_LIBRARY_PATH}
else
export LD_LIBRARY_PATH=${LCG_gcc_home}/${LCG_lib_name}:${LCG_mpfr_home}/lib:${LCG_gmp_home}/lib
fi

export PATH=/afs/cern.ch/sw/lcg/external/Python/2.7.4/x86_64-slc6-gcc48-opt/bin/:$PATH
export LD_LIBRARY_PATH=/afs/cern.ch/sw/lcg/external/Python/2.7.4/x86_64-slc6-gcc48-opt/lib/:$LD_LIBRARY_PATH

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
os.system('svn export https://svnsrv.desy.de/public/marlinreco/ILDConfig/trunk/StandardConfig/current/bbudsc_3evt_stdreco.xml')
standardConfigXml = 'bbudsc_3evt_stdreco.xml'

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

newTemplateFile = open('MarlinJobs/Templates/MarlinTemplate.xml', 'w')
newTemplateFile.write(newContent)
newTemplateFile.close()

#########################
# Make AnalysePerformance.sh
#########################
analysePerformanceFolder = os.path.join(cwd, 'AnalysePerformance')
if not os.path.exists(analysePerformanceFolder):
    os.makedirs(analysePerformanceFolder)

analysePerformanceRelease = os.path.join(releasePandoraAnalysis,'AnalysePerformance')
analysePerformanceLocal = os.path.join(cwd,'MarlinPandora/bin/AnalysePerformance')

analysePerformance = """#!/usr/bin/python
# -*- coding: utf-8 -*-

import subprocess, os, sys

inputRootFolder = sys.argv[1]
localBinary = """ + analysePerformanceLocal + """
releasedBinary = """ + analysePerformanceRelease + """

results = ''
for setting in ['Local', 'Release']
    results = ''
    for energy in [91, 200, 360, 500]:
        for pandoraSettings in ['Default', 'PerfectPhoton', 'PerfectPhotonNK0L', 'PerfectPFA']:
            results += '-----------------------------------------------------------------------------------------------------------------------------------'
            results += settign + ' ' + pandoraSettings + ' ' + str(energy) + 'GeV'
            results += '-----------------------------------------------------------------------------------------------------------------------------------'

        inputRootFileFormat = 'Validating_' + setting + '_PandoraSettings' + pandoraSettings + '_Z_uds_' + str(energy) + '_GeV_Job_Number_(.*?).root'

        argsString = executable + ' ' + os.path.join(path,inputRootFileFormat)
        args = argsString.split()
        popen = subprocess.Popen(args, stdout=subprocess.PIPE)
        popen.wait()
        output = popen.stdout.read()

        resultsLine = ''
        for line in output.splitlines():
            if 'fPFA_L7A' in line:
                resultsLine = line

        results += resultsLine

    resultsFileName = setting + '_JetEnergyResolutions.txt'
    textFile = open(resultsFileName, 'w')
    textFile.write(results)
    textFile.close()
"""

analysePerformanceFile = open(os.path.join(analysePerformanceFolder, 'AnalysePeformance.py'), 'w')
analysePerformanceFile.write(analysePerformance)
analysePerformanceFile.close()

