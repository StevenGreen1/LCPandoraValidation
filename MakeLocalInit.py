import os
import re
import sys

print """
To run the validation script please do the following
1) Copy the init_ilcsoft.sh and ILCSoft.cmake scripts from your choice of ilcsoft builds to this directory.  Please use a build with gcc48 at least.  Default script in directory is from ilcsoft v01-17-09
2) Run 'python initalise.py' to generate init_ilcsoft_local.sh and ILCSoft_Local.cmake, make the marlin executables and get the marlin template from svn
3) Build PandoraPFA (with LCContent), MarlinPandora and LCPandoraAnalysis in this directory using ILCSoft_Local.cmake for MarlinPandora and LCPandoraAnalysis
4) Modify paths in MarlinJobs/Validate.py and run 'python Validate.py'
"""

#########################
# Edit init_ilcsoft.sh
#########################

releaseMarlinPandora = ''
lines = [line.rstrip('\n') for line in open('init_ilcsoft.sh')]
newContent = ''
cwd = os.getcwd()
for line in lines:
    if 'MarlinPandora' in line:
        newline = ''
        for subline in line.split(':'):
            if 'export' in subline:
                newline += 'export MARLIN_DLL="'
            if 'libPandoraAnalysis' in subline:
                newline += os.path.join(cwd,'LCPandoraAnalysis/lib/libPandoraAnalysis.so:')
            elif 'libMarlinPandora' in subline:
                releaseMarlinPandora = subline
                newline += os.path.join(cwd,'MarlinPandora/lib/libMarlinPandora.so:')
            elif 'libDDMarlinPandora' in subline:
                newline += ''
            elif 'libMarlinDD4hep.so' in subline:
                newline += ''
            elif '$MARLIN_DLL' in subline:
                newline += subline  
            else:
                newline += subline + ':'
        line = newline
    newContent += line + '\n'
releaseMarlinPandoraScriptsFolder = os.path.join(os.path.dirname(releaseMarlinPandora),'../scripts')

newInitFile = open("init_ilcsoft_local.sh", "w")
newInitFile.write(newContent)
newInitFile.close()

#########################
# Edit ILCSoft.cmake
#########################
lines = [line.rstrip('\n') for line in open('ILCSoft.cmake')]
newContent = ''
cwdString  = '"' + cwd + '"'
for line in lines:
    if 'MARK_AS_ADVANCED' in line:
        line = """MARK_AS_ADVANCED( ILC_HOME )
SET( LOCAL_ILC_HOME """ + cwdString + """ CACHE PATH "Path to Local ILC Software" FORCE)
MARK_AS_ADVANCED( LOCAL_ILC_HOME )"""
    elif 'DD' in line:
        continue
    elif 'PandoraAnalysis' in line:
        line = '        ${LOCAL_ILC_HOME}/LCPandoraAnalysis;'
    elif 'MarlinPandora' in line:
        line = '        ${LOCAL_ILC_HOME}/MarlinPandora;'
    elif 'PandoraPFA' in line:
        line = '        ${LOCAL_ILC_HOME}/PandoraPFA;'

    newContent += line + '\n'
newIlcSoftFile = open("ILCSoft_Local.cmake", "w")
newIlcSoftFile.write(newContent)
newIlcSoftFile.close()

#########################
# Make Templates Folder
#########################
templatesFolder = os.path.join(cwd, 'MarlinJobs/Templates')
if not os.path.exists(templatesFolder):
    os.makedirs(templatesFolder)

#########################
# Get Release Pandora Settings
#########################
pandoraSettingsReleaseFolder = os.path.join(cwd, 'MarlinJobs/PandoraSettings/Release')
os.system('cp ' + releaseMarlinPandoraScriptsFolder + '/* ' + pandoraSettingsReleaseFolder)
releasePandoraSettingsDefault = os.path.join(pandoraSettingsReleaseFolder, 'PandoraSettingsDefault.xml')
releasePandoraSettingsLikelihoodData = os.path.join(pandoraSettingsReleaseFolder, 'PandoraLikelihoodData9EBin.xml')

releasePandoraSettingsDefaultFile = open(releasePandoraSettingsDefault, 'r')
content = releasePandoraSettingsDefaultFile.readlines()
releasePandoraSettingsDefaultFile.close()

content = re.sub('PandoraLikelihoodData9EBin.xml', releasePandoraSettingsLikelihoodData, content)

releasePandoraSettingsDefaultFile = open(releasePandoraSettingsDefault, 'w')
releasePandoraSettingsDefaultFile.writelines(content)
releasePandoraSettingsDefaultFile.close()

#########################
# Get Local Pandora Settings
#########################
pandoraSettingsLocalFolder = os.path.join(cwd, 'MarlinJobs/PandoraSettings/Local')
localMarlinPandoraScriptsFolder = os.path.join(cwd, 'MarlinPandora/scripts'
os.system('cp ' + localMarlinPandoraScriptsFolder + '/* ' + pandoraSettingsLocalFolder)
localPandoraSettingsDefault = os.path.join(pandoraSettingsLocalFolder, 'PandoraSettingsDefault.xml')
localPandoraSettingsLikelihoodData = os.path.join(pandoraSettingsLocalFolder, 'PandoraLikelihoodData9EBin.xml')

localPandoraSettingsDefaultFile = open(localPandoraSettingsDefault, 'r')
content = localPandoraSettingsDefaultFile.readlines()
localPandoraSettingsDefaultFile.close()

content = re.sub('PandoraLikelihoodData9EBin.xml', localPandoraSettingsLikelihoodData, content)

localPandoraSettingsDefaultFile = open(localPandoraSettingsDefault, 'w')
localPandoraSettingsDefaultFile.writelines(content)
localPandoraSettingsDefaultFile.close()

#########################
# Make MarlinLocal.sh
#########################
marlinLocal = """
#!/bin/bash
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
marlinLocalFile.write(marlinLocalFileName)
marlinLocalFile.close()
os.system('chmod u+x MarlinJobs/Templates/MarlinLocal.sh')

#########################
# Make MarlinReference.sh
#########################
marlinReference = """
#!/bin/bash

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
marlinReferenceFileName = os.path.join(cwd, 'MarlinJobs/Templates/MarlinReference.sh')
marlinReferenceFile = open(marlinReferenceFileName, 'w')
marlinReferenceFile.write(marlinReferenceFileName)
marlinReferenceFile.close()
os.system('chmod u+x MarlinJobs/Templates/MarlinReference.sh')

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

