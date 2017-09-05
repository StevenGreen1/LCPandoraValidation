#!/usr/bin/python
# -*- coding: utf-8 -*-

import subprocess, os, sys

inputRootFolder = sys.argv[1]
localBinary = '/var/clus/usera/sg568/LC/Validation/Reconstruction/DD4HEP/v01-19-04/LCPandoraValidation/LCPandoraAnalysis/bin/AnalysePerformance'
releasedBinary = '/cvmfs/ilc.desy.de/sw/x86_64_gcc49_sl6/v01-19-04/PandoraAnalysis/v01-02-01/lib/../bin/AnalysePerformance'

results = ''
for setting in ['Local', 'Release']:
    results = ''
    for energy in [91, 200, 360, 500]:
        for pandoraSettings in ['Default', 'PerfectPhoton', 'PerfectPhotonNeutronK0L', 'PerfectPFA']:
            results += '-----------------------------------------------------------------------------------------------------------------------------------\n'
            results += setting + ' ' + pandoraSettings + ' ' + str(energy) + 'GeV\n'
            results += '-----------------------------------------------------------------------------------------------------------------------------------\n'

            inputRootFileFormat = 'Validating_' + setting + '_PandoraSettings' + pandoraSettings + '_Z_uds_' + str(energy) + '_GeV_Job_Number_*.root'

            if 'Local' in setting:
                argsString = localBinary + ' ' + os.path.join(inputRootFolder, inputRootFileFormat)
            else:
                argsString = releasedBinary + ' ' + os.path.join(inputRootFolder, inputRootFileFormat)

            args = argsString.split()
            popen = subprocess.Popen(args, stdout=subprocess.PIPE)
            popen.wait()
            output = popen.stdout.read()

            resultsLine = ''
            for line in output.splitlines():
                if 'fPFA_L7A' in line:
                    resultsLine = line

            results += resultsLine + '\n'

    resultsFileName = setting + '_JetEnergyResolutions.txt'
    textFile = open(resultsFileName, 'w')
    textFile.write(results)
    textFile.close()
