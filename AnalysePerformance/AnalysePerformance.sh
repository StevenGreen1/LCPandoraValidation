#!/bin/bash

#cd "/r06/lc/sg568/LCValidationPandora/ilcsoft_v01-17-09-vs-master-06-09-16/RootFiles"
rootFolder="/r06/lc/sg568/LCValidationPandora/ilcsoft_v01-17-10-vs-master-11-10-16/RootFiles"

localBinary=/usera/sg568/LCValidationPandora/LCPandoraAnalysis/bin/AnalysePerformance
releasedBinary=/afs/desy.de/project/ilcsoft/sw/x86_64_gcc44_sl6/v01-17-10/PandoraAnalysis/v01-02-01/bin/AnalysePerformance

localResults="LocalAnalysePerformance-ilcsoft_v01-17-10-vs-master-11-10-16.txt"
releaseResults="RealeaseAnalysePerformance-ilcsoft_v01-17-10-vs-master-11-10-16.txt"

touch ${localResults} ${releaseResults}

for i in 91 200 360 500 
do
    echo "Energy ${i}" >> ${localResults}
    echo "Energy ${i}" >> ${releaseResults}
    echo "$($localBinary "${rootFolder}/Validating_Local_Pandora_Z_uds_${i}_GeV_Job_Number_*.root")" >> ${localResults}
    echo "$($releasedBinary "${rootFolder}/Validating_Release_Pandora_Z_uds_${i}_GeV_Job_Number_*.root")" >> ${releaseResults}
done

