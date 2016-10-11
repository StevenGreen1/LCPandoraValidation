import re

lines = [line.rstrip('\n') for line in open('init_ilcsoft.sh')]
newContent = ''

for line in lines:
    if 'PandoraAnalysis' in line:
        newline = ''
        for subline in line.split(':'):
            if 'export' in subline:
                newline += 'export MARLIN_DLL="'
                subline = re.sub('export MARLIN_DLL="','',subline)
            if 'libPandoraAnalysis' in subline:
                newline += '/var/clus/usera/sg568/LCValidationPandora/LCPandoraAnalysis/lib/libPandoraAnalysis.so:' 
            elif 'libMarlinPandora' in subline:
                newline += '/var/clus/usera/sg568/LCValidationPandora/MarlinPandora/lib/libMarlinPandora.so:'
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

newInitFile = open("init_ilcsoft_local.sh", "w")
newInitFile.write(newContent)
newInitFile.close()

lines = [line.rstrip('\n') for line in open('ILCSoft.cmake')]
newContent = ''

for line in lines:
    if 'MARK_AS_ADVANCED' in line:
        line = """MARK_AS_ADVANCED( ILC_HOME )

SET( LOCAL_ILC_HOME "/var/clus/usera/sg568/LCValidationPandora" CACHE PATH "Path to Local ILC Software" FORCE)
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

