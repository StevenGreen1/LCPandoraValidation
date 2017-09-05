import os
import re
import sys

#########################
# Edit init_ilcsoft.sh
#########################

releaseDDMarlinPandora = ''
lines = [line.rstrip('\n') for line in open('init_ilcsoft.sh')]
newContent = ''
cwd = os.getcwd()
for line in lines:
    if 'DDMarlinPandora' in line:
        start_pt = line.find("\"")
        end_pt = line.find("\"", start_pt + 1)  # add one to skip the opening "
        libraries = line[start_pt + 1: end_pt]  # add one to get the quote excluding the ""

        newline = 'export MARLIN_DLL=\"'
        for library in libraries.split(':'):
            if 'libPandoraAnalysis' in library:
                newline += os.path.join(cwd,'LCPandoraAnalysis/lib/libPandoraAnalysis.so:')
            elif 'libDDMarlinPandora' in library:
                releaseDDMarlinPandora = library
                newline += os.path.join(cwd,'DDMarlinPandora/lib/libDDMarlinPandora.so:')
            elif '$MARLIN_DLL' in library:
                newline += library  
            else:
                newline += library + ':'
        newline += '\"'
        line = newline
    newContent += line + '\n'
releaseDDMarlinPandoraScriptsFolder = os.path.join(os.path.dirname(releaseDDMarlinPandora),'../scripts')

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
    elif 'PandoraAnalysis' in line:
        line = '        ${LOCAL_ILC_HOME}/LCPandoraAnalysis;'
    elif 'DDMarlinPandora' in line:
        line = '        ${LOCAL_ILC_HOME}/DDMarlinPandora;'
    elif 'PandoraPFA' in line:
        line = '        ${LOCAL_ILC_HOME}/PandoraPFA;'

    newContent += line + '\n'
newIlcSoftFile = open("ILCSoft_Local.cmake", "w")
newIlcSoftFile.write(newContent)
newIlcSoftFile.close()


