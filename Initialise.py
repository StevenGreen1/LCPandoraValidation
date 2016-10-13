import os
import re
import sys

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


