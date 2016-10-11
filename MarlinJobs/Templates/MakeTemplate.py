import re

lines = [line.rstrip('\n') for line in open('StandardConfig/bbudsc_3evt_stdreco.xml')]
newContent = ''

processorsToRemove = ['BgOverlay', 'MyAdd4MomCovMatrixCharged', 'MyAddClusterProperties', 'MyBeamCalClusterReco', 'BCalAddClusterProperties', 'MyComputeShowerShapesProcessor', 'MyPi0Finder', 'MyEtaFinder', 'MyEtaPrimeFinder', 'MyGammaGammaSolutionFinder', 'MyDistilledPFOCreator', 'MyLikelihoodPID', 'MyTauFinder', 'MyRecoMCTruthLinker', 'VertexFinder', 'MyLCIOOutputProcessor', 'DSTOutput']

newContent = ''

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
            
newTemplateFile = open("MarlinTemplate.xml", "w")
newTemplateFile.write(newContent)
newTemplateFile.close()



"""
      <parameter name="LCIOInputFiles">
       ./bbudsc_3evt.slcio
      </parameter>
      <parameter name="GearXMLFile" value="GearOutput.xml"/>





        template = re.sub('DigitiserHeader',digitiserHeader,template)

        simpleMuonDigiHeader = self.writeSimpleMuonDigiXmlHeader()
        template = re.sub('SimpleMuonDigiHeader',simpleMuonDigiHeader,template)

        pandoraHeader = self.writePandoraXmlHeader()
        template = re.sub('PandoraHeader',pandoraHeader,template)

        digitiserImplementation = self.writeILDCaloDigiSiECalXml()
        template = re.sub('DigitiserImplementation',digitiserImplementation,template)

        simpleMuonDigiImplementation = self.writeSimpleMuonDigiXml()
        template = re.sub('SimpleMuonDigiImplementation',simpleMuonDigiImplementation,template)

        pandoraImplementation = self.writeMarlinPandoraSiECalXml()
        pandoraImplementation += '\n'
        pandoraImplementation += self.writePandoraAnalsisSiECalXml()
        template = re.sub('PandoraImplementation',pandoraImplementation,template)



<processor name="MyMarlinPandora" type="PandoraPFANewProcessor">
</processor>

<processor name="MyPfoAnalysis" type="PfoAnalysis">
</processor>

<processor name="MyILDCaloDigi" type="ILDCaloDigi">
</processor>

"""
