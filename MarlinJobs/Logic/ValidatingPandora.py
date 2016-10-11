#!/usr/bin/python

import os, sys, getopt, re, subprocess, math, dircache, logging, time, random, string

class ValidatingPandora:
    'Common base class for all validating pandora process'

### ----------------------------------------------------------------------------------------------------
### Start of constructor
### ----------------------------------------------------------------------------------------------------

    def __init__(self, configFileName, slcioFormat, slcioPath, gearFile, pandoraSettingsLocal, pandoraSettingsRelease, outputPath):
        'Calibration File'
        self.configFileName = configFileName
        config = {}
        execfile(self.configFileName, config)

        self._OutputPath = outputPath

        'Root File Info'
        self._RootFileFolder = os.path.join(self._OutputPath, 'RootFiles') 
        if not os.path.exists(self._RootFileFolder):
            os.makedirs(self._RootFileFolder)

        'Marlin Xml Path'
        self._MarlinXmlPath = os.path.join(self._OutputPath, 'MarlinXml')
        if not os.path.exists(self._MarlinXmlPath):
            os.makedirs(self._MarlinXmlPath)

        'Logger'
        logFullPath = 'Validation.log'
        if os.path.isfile(logFullPath):
            os.remove(logFullPath)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        handler = logging.FileHandler(logFullPath)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.info('Output path : ' + self._OutputPath)

        'Slcio Path Information'
        self._SlcioFormat = slcioFormat
        self._SlcioPath = slcioPath
        self._SlcioFiles = self.getSlcioFiles()

        'Gear File'
        if not os.path.isfile(gearFile):
            self.logger.error('Gear file does not exist!  Exiting.')
            self.logger.error('Gear file : ' + gearFile)
            sys.exit()

        self._GearFile = gearFile

        'Pandora Settings File'
        if not os.path.isfile(pandoraSettingsLocal):
            self.logger.error('Pandora settings file does not exist!  Exiting.')
            self.logger.error('Pandora settings file : ' + pandoraSettingsLocal)
            sys.exit()

        if not os.path.isfile(pandoraSettingsRelease):
            self.logger.error('Pandora settings file does not exist!  Exiting.')
            self.logger.error('Pandora settings file : ' + pandoraSettingsRelease)
            sys.exit()

        self._PandoraSettingsFileLocal = pandoraSettingsLocal
        self._PandoraSettingsFileRelease = pandoraSettingsRelease

        'Realistic Digitisation'
        self._RealisticDigitisation = config['RealisticDigitisation']
        self._ApplyECalRealisticDigi = 0
        self._ApplyHCalRealisticDigi = 0
        self._ECalMaxDynamicRangeMIP = 0.0 # Set to 0 to avoid accidental truncation if not using realistic digitisation options
        self._HCalMaxDynamicRangeMIP = 0.0 # Set to 0 to avoid accidental truncation if not using realistic digitisation options

        if self._RealisticDigitisation:
            self._ECalMaxDynamicRangeMIP = 2500       # Realistic Values
            self._HCalMaxDynamicRangeMIP = 99999999   # Realistic Values
            self._ApplyHCalRealisticDigi = 1
            self._ApplyECalRealisticDigi = 1

        self.logger.info('Realistic digitsation setting : ' + str(self._RealisticDigitisation))
        self.logger.info('self._ApplyECalRealisticDigi   : ' + str(self._ApplyECalRealisticDigi))
        self.logger.info('self._ApplyHCalRealisticDigi   : ' + str(self._ApplyHCalRealisticDigi))

        'ECal Calibration Variables - Digitisation'
        self._CalibrECal = config['CalibrECal']
        self._CalibrECalMIP = config['CalibrECalMIP']
        self._ECalGapCorrectionFactor = 1
        self._ECalBarrelTimeWindowMax = config['ECalBarrelTimeWindowMax']
        self._ECalEndCapTimeWindowMax = config['ECalEndcapTimeWindowMax']
        self._ECalLayerChange = 20

        'ECal Calibration Variables - Pandora'
        self._ECalGeVToMIP = config['ECalToMIPCalibration']
        self._ECalMIPThresholdPandora = config['ECalMIPThresholdPandora']
        self._ECalToEm = config['ECalToEMGeVCalibration']
        self._ECalToHad = config['ECalToHadGeVCalibration']

        'HCal Calibration Variables - Digitisation'
        self._CalibrHCalBarrel = config['CalibrHCalBarrel']
        self._CalibrHCalEndCap = config['CalibrHCalEndcap']
        self._CalibrHCalOther = config['CalibrHCalOther']
        self._CalibrHCalMIP = config['CalibrHCalMIP']
        self._HCalBarrelTimeWindowMax = config['HCalBarrelTimeWindowMax']
        self._HCalEndCapTimeWindowMax = config['HCalEndcapTimeWindowMax']

        'HCal Calibration Variables - Pandora'
        self._HCalGeVToMIP = config['HCalToMIPCalibration']
        self._HCalMIPThresholdPandora = config['HCalMIPThresholdPandora']
        self._MHHHE = config['MaxHCalHitHadronicEnergy']
        self._HCalToEm = config['HCalToEMGeVCalibration']
        self._HCalToHad = config['HCalToHadGeVCalibration']

        'Muon Chamber Calibration Variables'
        self._CalibrMuon = config['CalibrMuon']
        self._MuonGeVToMIP = config['MuonToMIPCalibration']

        'Condor'
        self._UseCondor = True
        self._CondorRunListRelease = []
        self._CondorRunListLocal = []
        self._CondorMaxRuns = 500

        'Random String For Job Submission'
        self._RandomString = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
        self._MarlinExecutableRelease = 'MarlinRelease_' + self._RandomString + '.sh'

        os.system('cp Templates/MarlinRelease.sh ' + self._MarlinExecutableRelease)
        if not os.path.isfile(self._MarlinExecutableRelease):
            self.logger.error('Marlin executable missing.  Exiting.')
            self.logger.error('Marlin executable : ' + self._MarlinExecutableRelease)
            sys.exit()

        self._RandomString = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
        self._MarlinExecutableLocal = 'MarlinLocal_' + self._RandomString + '.sh'

        os.system('cp Templates/MarlinLocal.sh ' + self._MarlinExecutableLocal)
        if not os.path.isfile(self._MarlinExecutableLocal):
            self.logger.error('Marlin executable missing.  Exiting.')
            self.logger.error('Marlin executable : ' + self._MarlinExecutableLocal)
            sys.exit()

        self.runPandoras()
        os.system('rm ' + self._MarlinExecutableRelease)
        os.system('rm ' + self._MarlinExecutableLocal)

### ----------------------------------------------------------------------------------------------------
### End of constructor
### ----------------------------------------------------------------------------------------------------
### Start of runPandoras function
### ----------------------------------------------------------------------------------------------------

    def runPandoras(self):
        self.prepareSteeringFiles()
        self.runCondorJobs(self._CondorRunListRelease, self._MarlinExecutableRelease)
        self.runCondorJobs(self._CondorRunListLocal, self._MarlinExecutableLocal)
        self.checkCondorJobs(self._MarlinExecutableRelease)
        self.checkCondorJobs(self._MarlinExecutableLocal)

### ----------------------------------------------------------------------------------------------------
### End of runPandoras function
### ----------------------------------------------------------------------------------------------------
### ====================================================================================================
### READ CALIBRATION NUMBERS FROM TEXT FILE
### ====================================================================================================
### ====================================================================================================
### MARLIN XML GNERATION 
### ====================================================================================================

### ----------------------------------------------------------------------------------------------------
### Start of getSlcioFiles function
### ----------------------------------------------------------------------------------------------------

    def getSlcioFiles(self):
        fileDirectory = self._SlcioPath
        allFilesInDirectory = dircache.listdir(fileDirectory)
        allFiles = []
        allFiles.extend(allFilesInDirectory)
        allFiles[:] = [ item for item in allFiles if re.match('.*\.slcio$', item.lower()) ]
        allFiles.sort()
        return allFiles

### ----------------------------------------------------------------------------------------------------
### End of getSlcioFiles function
### ----------------------------------------------------------------------------------------------------
### Start of prepareSteeringFiles function
### ----------------------------------------------------------------------------------------------------

    def prepareSteeringFiles(self):
        self.logger.debug('Preparing Z_uds steering files.')

        for energy in [91,200,360,500]:
            counter = 0
            jobName = 'Z_uds_' + str(energy) + '_GeV'
            activeSlcioFormat = self._SlcioFormat
            activeSlcioFormat = re.sub('ENERGY',str(energy),activeSlcioFormat)

            baseSteeringFile = os.path.join(os.getcwd(), 'Templates/MarlinTemplate.xml')

            jobList = []

            base = open(baseSteeringFile,'r')
            baseContent = base.read()
            base.close()

            slcioFiles = []
            slcioFiles = list(self._SlcioFiles)

            if not slcioFiles:
                self.logger.debug('No files in input slcio folder.')
                self.logger.debug('Slcio Folder : ' + self._SlcioPath)
                self.logger.debug('Slcio Format : ' + activeSlcioFormat)
                sys.exit()

            for nfiles in range(len(slcioFiles)):
                marlinTemplate = baseContent
                nextFile = slcioFiles.pop(0)
                matchObj = re.match(activeSlcioFormat, nextFile, re.M|re.I)

                # Check files match
                if not matchObj:
                    continue

                counter += 1

                slcioFileName = os.path.join(self._SlcioPath,nextFile)
                newFileNameRelease = 'Validating_Release_Pandora_' + jobName + '_Job_Number_' + str(counter) + '.xml'
                newFileNameLocal = 'Validating_Local_Pandora_' + jobName + '_Job_Number_' + str(counter) + '.xml'

                xmlFullPathRelease = os.path.join(self._MarlinXmlPath, newFileNameRelease)
                xmlFullPathLocal = os.path.join(self._MarlinXmlPath, newFileNameLocal)

                rootFileFullPathRelease = os.path.join(self._RootFileFolder, 'Validating_Release_Pandora_' + jobName + '_Job_Number_' + str(counter) + '.root')
                rootFileFullPathLocal = os.path.join(self._RootFileFolder, 'Validating_Local_Pandora_' + jobName + '_Job_Number_' + str(counter) + '.root')

                marlinTemplate = re.sub('LcioInputFile',slcioFileName,marlinTemplate)                      # Slcio File
                marlinTemplate = re.sub('GearFile',self._GearFile,marlinTemplate)                          # Gear File

                marlinTemplateLocal = self.writeXmlFile(marlinTemplate,self._PandoraSettingsFileLocal)               # Calibration Parameters
                marlinTemplateLocal = re.sub('PfoAnalysisRootFile',rootFileFullPathLocal,marlinTemplateLocal)        # PfoAnalysis Root File
                file = open(xmlFullPathLocal,'w')
                file.write(marlinTemplateLocal)
                file.close()

                marlinTemplateRelease = self.writeXmlFile(marlinTemplate,self._PandoraSettingsFileRelease)            # Calibration Parameters
                marlinTemplateRelease = re.sub('PfoAnalysisRootFile',rootFileFullPathRelease,marlinTemplateRelease)   # PfoAnalysis Root File
                file = open(xmlFullPathRelease,'w')
                file.write(marlinTemplateRelease)
                file.close()

                self._CondorRunListRelease.append(xmlFullPathRelease)
                self._CondorRunListLocal.append(xmlFullPathLocal)

        self.logger.debug('The current list of xml files to process is: ')
        self.logger.debug(self._CondorRunListRelease)
        self.logger.debug(self._CondorRunListLocal)

### ----------------------------------------------------------------------------------------------------
### End of prepareSteeringFiles function
### ----------------------------------------------------------------------------------------------------
### Start of writeXmlFile function
### ----------------------------------------------------------------------------------------------------

    def writeXmlFile(self, template, pandoraSettingsFile):
        self.logger.debug('Writing xml file.')
        digitiserHeader = self.writeILDCaloDigiSiECalXmlHeader()
        template = re.sub('DigitiserHeader',digitiserHeader,template)

        simpleMuonDigiHeader = self.writeSimpleMuonDigiXmlHeader()
        template = re.sub('SimpleMuonDigiHeader',simpleMuonDigiHeader,template)

        pandoraHeader = self.writePandoraXmlHeader()
        template = re.sub('PandoraHeader',pandoraHeader,template)

        digitiserImplementation = self.writeILDCaloDigiSiECalXml()
        template = re.sub('DigitiserImplementation',digitiserImplementation,template)

        simpleMuonDigiImplementation = self.writeSimpleMuonDigiXml()
        template = re.sub('SimpleMuonDigiImplementation',simpleMuonDigiImplementation,template)

        pandoraImplementation = self.writeMarlinPandoraSiECalXml(pandoraSettingsFile)
        pandoraImplementation += '\n'
        pandoraImplementation += self.writePandoraAnalsisSiECalXml()
        template = re.sub('PandoraImplementation',pandoraImplementation,template)
        return template

### ----------------------------------------------------------------------------------------------------
### End of writeXmlFile function
### ----------------------------------------------------------------------------------------------------
### Start of writeILDCaloDigiSiECalXmlHeader function
### ----------------------------------------------------------------------------------------------------

    def writeILDCaloDigiSiECalXmlHeader(self):
        self.logger.debug('Writing ILDCaloDigi xml header block for Si ECal.')
        ildCaloDigiHeader = """<processor name="MyILDCaloDigi"/>"""
        return ildCaloDigiHeader

### ----------------------------------------------------------------------------------------------------
### End of writeILDCaloDigiSiECalXmlHeader function
### ----------------------------------------------------------------------------------------------------
### Start of writeILDCaloDigiSiECalXml function
### ----------------------------------------------------------------------------------------------------

    def writeILDCaloDigiSiECalXml(self):
        self.logger.debug('Writing ILDCaloDigi xml block for Si ECal.')
        ildCaloDigi  = """
<processor name="MyILDCaloDigi" type="ILDCaloDigi">
  <!--ILD digitizer...-->
  <!--Calibration coefficients for ECAL-->
  <parameter name="CalibrECAL" type="FloatVec">""" + str(self._CalibrECal) + ' ' + str(2*self._CalibrECal) + """</parameter>
  <!--Calibration coefficients for HCAL barrel, endcap, other-->
  <parameter name="CalibrHCALBarrel" type="FloatVec">""" + str(self._CalibrHCalBarrel) + """</parameter>
  <parameter name="CalibrHCALEndcap" type="FloatVec">""" + str(self._CalibrHCalEndCap) + """</parameter>
  <parameter name="CalibrHCALOther" type="FloatVec">""" + str(self._CalibrHCalOther) + """</parameter>
  <!--ECAL Collection Names-->
  <parameter name="ECALCollections" type="StringVec">EcalBarrelSiliconCollection EcalEndcapSiliconCollection  EcalEndcapRingCollection </parameter>
  <!--Index of ECal Layers-->
  <parameter name="ECALLayers" type="IntVec">""" + str(self._ECalLayerChange) + """ 100 </parameter>
  <!--Threshold for ECAL Hits in GeV-->
  <parameter name="ECALThreshold" type="float">5e-05 </parameter>
  <!--HCAL Collection Names-->
  <parameter name="HCALCollections" type="StringVec">HcalBarrelRegCollection  HcalEndCapsCollection HcalEndCapRingsCollection</parameter>
  <!--Index of HCal Layers-->
  <parameter name="HCALLayers" type="IntVec">100  </parameter>
  <!--Threshold for HCAL Hits in MIPs - given HCALThresholdUnit is specified-->
  <parameter name="HCALThreshold" type="float">0.5 </parameter>
  <!--Digital Ecal-->
  <parameter name="IfDigitalEcal" type="int">0 </parameter>
  <!--Digital Hcal-->
  <parameter name="IfDigitalHcal" type="int">0 </parameter>
  <!--name for the new collection -->
  <parameter name="ECALOutputCollection0" type="stringVec">ECALBarrel </parameter>
  <parameter name="ECALOutputCollection1" type="stringVec">ECALEndcap </parameter>
  <parameter name="ECALOutputCollection2" type="stringVec">ECALOther </parameter>
  <parameter name="HCALOutputCollection0" type="stringVec">HCALBarrel </parameter>
  <parameter name="HCALOutputCollection1" type="stringVec">HCALEndcap </parameter>
  <parameter name="HCALOutputCollection2" type="stringVec">HCALOther </parameter>
  <!--CaloHit Relation Collection-->
  <parameter name="RelationOutputCollection" type="string"> RelationCaloHit</parameter>
  <!--Gap Correction-->
  <parameter name="ECALGapCorrection" type="int"> 1 </parameter>
  <!--Gap Correction Fudge Factor-->
  <parameter name="ECALGapCorrectionFactor" type="float">""" + str(self._ECalGapCorrectionFactor) + """</parameter>
  <parameter name="ECALModuleGapCorrectionFactor" type="float"> 0.0 </parameter>
  <!-- Timing -->
  <parameter name="UseEcalTiming" type="int">1</parameter>
  <parameter name="UseHcalTiming" type="int">1</parameter>
  <parameter name="ECALBarrelTimeWindowMax" type="float">""" + str(self._ECalBarrelTimeWindowMax) + """</parameter>
  <parameter name="HCALBarrelTimeWindowMax" type="float">""" + str(self._HCalBarrelTimeWindowMax) + """</parameter>
  <parameter name="ECALEndcapTimeWindowMax" type="float">""" + str(self._ECalEndCapTimeWindowMax) + """</parameter>
  <parameter name="HCALEndcapTimeWindowMax" type="float">""" + str(self._HCalEndCapTimeWindowMax) + """</parameter>
  <parameter name="ECALTimeWindowMin" type="float"> -1.0 </parameter>
  <parameter name="HCALTimeWindowMin" type="float"> -1.0 </parameter>
  <parameter name="ECALCorrectTimesForPropagation" type="int">1</parameter>
  <parameter name="HCALCorrectTimesForPropagation" type="int">1</parameter>
  <parameter name="ECALDeltaTimeHitResolution" type="float"> 20.0 </parameter>
  <parameter name="HCALDeltaTimeHitResolution" type="float"> 20.0 </parameter>
  <!-- Realistic ECal -->
  <parameter name="ECAL_apply_realistic_digi" type="int">""" + str(self._ApplyECalRealisticDigi) + """</parameter>
  <parameter name="CalibECALMIP" type="float">""" + str(self._CalibrECalMIP) + """</parameter>
  <parameter name="ECAL_maxDynamicRange_MIP" type="float">""" + str(self._ECalMaxDynamicRangeMIP) + """</parameter>
  <parameter name="ECAL_elec_noise_mips" type="float">0.07</parameter>
  <parameter name="ECAL_deadCellRate" type="float">0</parameter>
  <parameter name="ECAL_miscalibration_uncorrel" type="float">0</parameter>
  <parameter name="ECAL_miscalibration_uncorrel_memorise" type="bool">false</parameter>
  <parameter name="ECAL_miscalibration_correl" type="float">0</parameter>
  <parameter name="energyPerEHpair" type="float">3.6</parameter>
  <parameter name="ECAL_PPD_PE_per_MIP" type="float">7</parameter>
  <parameter name="ECAL_PPD_N_Pixels" type="int">10000</parameter>
  <parameter name="ECAL_PPD_N_Pixels_uncertainty" type="float">0.05</parameter>
  <parameter name="ECAL_pixel_spread" type="float">0.05</parameter>
  <!-- Realistic HCal -->
  <parameter name="HCAL_apply_realistic_digi" type="int">""" + str(self._ApplyHCalRealisticDigi) + """</parameter>
  <parameter name="HCALThresholdUnit" type="string">MIP</parameter>
  <parameter name="CalibHCALMIP" type="float">""" + str(self._CalibrHCalMIP) + """</parameter>
  <parameter name="HCAL_maxDynamicRange_MIP" type="float">""" + str(self._HCalMaxDynamicRangeMIP) + """</parameter>
  <parameter name="HCAL_elec_noise_mips" type="float">0.06</parameter>
  <parameter name="HCAL_deadCellRate" type="float">0</parameter>
  <parameter name="HCAL_PPD_N_Pixels" type="int">2000</parameter>
  <parameter name="HCAL_PPD_PE_per_MIP" type="float">15</parameter>
  <parameter name="HCAL_pixel_spread" type="float">0.05</parameter>
  <parameter name="HCAL_PPD_N_Pixels_uncertainty" type="float">0</parameter>
  <parameter name="HCAL_miscalibration_uncorrel" type="float">0</parameter>
  <parameter name="HCAL_miscalibration_correl" type="float">0</parameter>
  <!-- Histograms-->
  <parameter name="Histograms" type="int"> 0 </parameter>
</processor>"""
        return ildCaloDigi

### ----------------------------------------------------------------------------------------------------
### End of writeILDCaloDigiSiECalXml function
### ----------------------------------------------------------------------------------------------------
### Start of writeSimpleMuonDigiXmlHeader function
### ----------------------------------------------------------------------------------------------------

    def writeSimpleMuonDigiXmlHeader(self):
        self.logger.debug('Writing SimpleMuonDigi xml header block.')
        simpleMuonDigiHeader = """<processor name="MySimpleMuonDigi"/>"""
        return simpleMuonDigiHeader

### ----------------------------------------------------------------------------------------------------
### End of writeSimpleMuonDigiXmlHeader function
### ----------------------------------------------------------------------------------------------------
### Start of writeSimpleMuonDigiXml function
### ----------------------------------------------------------------------------------------------------

    def writeSimpleMuonDigiXml(self):
        self.logger.debug('Writing SimpleMuonDigi xml block.')
        simpleMuonDigi = """
<processor name="MySimpleMuonDigi" type="SimpleMuonDigi">
  <!--Performs simple digitization of sim calo hits...-->
  <!--Calibration coefficients for MUON-->
  <parameter name="CalibrMUON" type="FloatVec">""" + str(self._CalibrMuon) + """</parameter>
  <!-- maximum hit energy for a MUON hit -->
  <parameter name="MaxHitEnergyMUON" type="float">2.0</parameter>
  <!--MUON Collection Names-->
  <parameter name="MUONCollections" type="StringVec">
   MuonBarrelCollection MuonEndCapCollection</parameter>
  <!--MUON Collection of real Hits-->
  <parameter name="MUONOutputCollection" type="string">MUON </parameter>
  <!--Threshold for MUON Hits in GeV-->
  <parameter name="MUONThreshold" type="float">1e-06 </parameter>
  <!--MuonHit Relation Collection-->
  <parameter name="RelationOutputCollection" type="string">RelationMuonHit </parameter>
</processor>"""
        return simpleMuonDigi

### ----------------------------------------------------------------------------------------------------
### End of writeSimpleMuonDigiXml function
### ----------------------------------------------------------------------------------------------------
### Start of writeMarlinPandoraXmlHeader function
### ----------------------------------------------------------------------------------------------------

    def writePandoraXmlHeader(self):
        self.logger.debug('Writing MarlinPandora and PfoAnalysis xml header block.')
        headerString = """
<processor name="MyMarlinPandoraDefault"/>
<processor name="MyPfoAnalysisDefault"/>"""
        return headerString

### ----------------------------------------------------------------------------------------------------
### End of writeMarlinPandoraXmlHeader function
### ----------------------------------------------------------------------------------------------------
### Start of writeMarlinPandoraSiECalXml function
### ----------------------------------------------------------------------------------------------------

    def writeMarlinPandoraSiECalXml(self,pandoraSettingsFile):
        self.logger.debug('Writing MarlinPandora xml block for Si ECal.')
        marlinPandoraTemplate  = """
<processor name="MyMarlinPandoraDefault" type="PandoraPFANewProcessor">
  <parameter name="PandoraSettingsXmlFile" type="String">""" + pandoraSettingsFile + """</parameter>
  <!-- Collection names -->
  <parameter name="TrackCollections" type="StringVec">MarlinTrkTracks</parameter>
  <parameter name="ECalCaloHitCollections" type="StringVec">ECALBarrel ECALEndcap ECALOther</parameter>
  <parameter name="HCalCaloHitCollections" type="StringVec">HCALBarrel HCALEndcap HCALOther</parameter>
  <parameter name="LCalCaloHitCollections" type="StringVec">LCAL</parameter>
  <parameter name="LHCalCaloHitCollections" type="StringVec">LHCAL</parameter>
  <parameter name="MuonCaloHitCollections" type="StringVec">MUON</parameter>
  <parameter name="MCParticleCollections" type="StringVec">MCParticle</parameter>
  <parameter name="RelCaloHitCollections" type="StringVec">RelationCaloHit RelationMuonHit</parameter>
  <parameter name="RelTrackCollections" type="StringVec">MarlinTrkTracksMCTruthLink</parameter>
  <parameter name="KinkVertexCollections" type="StringVec">KinkVertices</parameter>
  <parameter name="ProngVertexCollections" type="StringVec">ProngVertices</parameter>
  <parameter name="SplitVertexCollections" type="StringVec">SplitVertices</parameter>
  <parameter name="V0VertexCollections" type="StringVec">V0Vertices</parameter>
  <parameter name="ClusterCollectionName" type="String">PandoraClustersDefault</parameter>
  <parameter name="PFOCollectionName" type="String">PandoraPFOsDefault</parameter>
  <parameter name="StartVertexCollectionName" type="String">StartVerticesDefault</parameter>
  <!-- Calibration constants -->
  <parameter name="ECalToMipCalibration" type="float">""" + str(self._ECalGeVToMIP) + """</parameter>
  <parameter name="HCalToMipCalibration" type="float">""" + str(self._HCalGeVToMIP) + """</parameter>
  <parameter name="ECalMipThreshold" type="float">""" + str(self._ECalMIPThresholdPandora) + """</parameter>
  <parameter name="HCalMipThreshold" type="float">""" + str(self._HCalMIPThresholdPandora) + """</parameter>
  <parameter name="ECalToEMGeVCalibration" type="float">""" + str(self._ECalToEm) + """</parameter>
  <parameter name="HCalToEMGeVCalibration" type="float">""" + str(self._HCalToEm) + """</parameter>
  <parameter name="ECalToHadGeVCalibrationBarrel" type="float">""" + str(self._ECalToHad) + """</parameter>
  <parameter name="ECalToHadGeVCalibrationEndCap" type="float">""" + str(self._ECalToHad) + """</parameter>
  <parameter name="HCalToHadGeVCalibration" type="float">""" + str(self._HCalToHad) + """</parameter>
  <parameter name="MuonToMipCalibration" type="float">""" + str(self._MuonGeVToMIP) + """</parameter>
  <parameter name="DigitalMuonHits" type="int">0</parameter>
  <parameter name="MaxHCalHitHadronicEnergy" type="float">""" + str(self._MHHHE) + """</parameter>
  <parameter name="AbsorberRadLengthECal" type="float">0.2854</parameter>
  <parameter name="AbsorberIntLengthECal" type="float">0.0101</parameter>
  <parameter name="AbsorberRadLengthHCal" type="float">0.0569</parameter>
  <parameter name="AbsorberIntLengthHCal" type="float">0.0060</parameter>
  <parameter name="AbsorberRadLengthOther" type="float">0.0569</parameter>
  <parameter name="AbsorberIntLengthOther" type="float">0.0060</parameter>
  <!--Whether to calculate track states manually, rather than copy stored fitter values-->
  <parameter name="UseOldTrackStateCalculation" type="int">0 </parameter>
</processor> """
        return marlinPandoraTemplate

### ----------------------------------------------------------------------------------------------------
### End of writeMarlinPandoraSiECalXml function
### ----------------------------------------------------------------------------------------------------
### Start of writePandoraAnalsisSiECalXml function
### ----------------------------------------------------------------------------------------------------

    def writePandoraAnalsisSiECalXml(self):
        self.logger.debug('Writing PandoraAnalysis xml block for Si ECal.')
        pandoraAnalysis  = """
<processor name="MyPfoAnalysisDefault" type="PfoAnalysis">
  <!--PfoAnalysis analyses output of PandoraPFANew, Modified for calibration-->
  <!--Names of input pfo collection-->
  <parameter name="PfoCollection" type="string" lcioInType="ReconstructedParticle">PandoraPFOsDefault </parameter>
  <!--Names of mc particle collection-->
  <parameter name="MCParticleCollection" type="string" lcioInType="MCParticle">MCParticle </parameter>
  <!--Collect Calibration Details-->
  <parameter name="CollectCalibrationDetails" type="int">1</parameter>
  <!--Detector Geometry Missing From Gear-->
  <parameter name="HCalRingOuterSymmetryOrder" type="int">8</parameter>
  <parameter name="HCalRingOuterPhi0" type="int">0</parameter>
  <!--Name of the ECAL collection used to form clusters-->
  <parameter name="ECalCollections" type="StringVec" lcioInType="CalorimeterHit">ECALBarrel ECALEndcap ECALOther</parameter>
  <!--Name of the HCAL collection used to form clusters-->
  <parameter name="HCalCollections" type="StringVec" lcioInType="CalorimeterHit">HCALBarrel HCALEndcap HCALOther </parameter>
  <!--Name of the MUON collection used to form clusters-->
  <parameter name="MuonCollections" type="StringVec" lcioInType="CalorimeterHit">MUON </parameter>
  <!--Name of the BCAL collection used to form clusters-->
  <parameter name="BCalCollections" type="StringVec" lcioInType="CalorimeterHit">BCAL</parameter>
  <!--Name of the LHCAL collection used to form clusters-->
  <parameter name="LHCalCollections" type="StringVec" lcioInType="CalorimeterHit">LHCAL </parameter>
  <!--Name of the LCAL collection used to form clusters-->
  <parameter name="LCalCollections" type="StringVec" lcioInType="CalorimeterHit">LCAL </parameter>
  <!--ECal Collection SimCaloHit Names-->
  <parameter name="ECalCollectionsSimCaloHit" type="StringVec">EcalBarrelSiliconCollection EcalEndcapSiliconCollection  EcalEndcapRingCollection </parameter>
  <!--HCal Barrel Collection SimCaloHit Names-->
  <parameter name="HCalBarrelCollectionsSimCaloHit" type="StringVec"> HcalBarrelRegCollection </parameter>
  <!--HCal Endcap Collection SimCaloHit Names-->
  <parameter name="HCalEndCapCollectionsSimCaloHit" type="StringVec"> HcalEndCapsCollection </parameter>
  <!--HCal Other/Ring Collection SimCaloHit Names-->
  <parameter name="HCalOtherCollectionsSimCaloHit" type="StringVec"> HcalEndCapRingsCollection</parameter>
  <!--Set the debug print level-->
  <parameter name="Printing" type="int"> 0 </parameter>
  <!--Output root file name-->
  <parameter name="RootFile" type="string">PfoAnalysisRootFile</parameter>
</processor>"""
        return pandoraAnalysis

### ----------------------------------------------------------------------------------------------------
### End of writePandoraAnalsisSiECalXml function
### ----------------------------------------------------------------------------------------------------
### Start of runCondorJobs function
### ----------------------------------------------------------------------------------------------------

    def runCondorJobs(self, condorRunList, marlinExecutable):
        self.logger.debug('Running condor jobs.')
        nQueued = self.nQueuedCondorJobs(marlinExecutable)
        condorJobFile = 'Job_' + self._RandomString + '.job'

        while True:
            if nQueued >= self._CondorMaxRuns:
                subprocess.call(["usleep", "500000"])

            else:
                for idx, fileToRun in enumerate(condorRunList):
                    nRemaining = len(condorRunList) - idx - 1
                    nQueued = self.nQueuedCondorJobs(marlinExecutable)

                    with open(condorJobFile, 'w') as jobFile:
                        jobString = self.getCondorJobString(marlinExecutable)
                        jobString += 'arguments = ' + fileToRun + '\n'
                        jobString += 'queue 1 \n'
                        jobFile.write(jobString)

                    subprocess.call(['condor_submit', condorJobFile])
                    print 'Submitted job as there were only ' + str(nQueued) + ' jobs in the queue and ' + str(nRemaining) + ' jobs remaining.'
                    subprocess.call(["usleep", "500000"])
                    os.remove(condorJobFile)

                    if 0 == nRemaining:
                        print 'All condor jobs submitted.'
                        return

### ----------------------------------------------------------------------------------------------------
### End of runCondorJobs function
### ----------------------------------------------------------------------------------------------------
### Start of getCondorJobString function
### ----------------------------------------------------------------------------------------------------

    def getCondorJobString(self, marlinExecutable):
        jobString  = 'executable              = ' + os.getcwd() + '/' + marlinExecutable + '                         \n'
        jobString += 'initial_dir             = ' + os.getcwd() + '                                                  \n'
        jobString += 'notification            = never                                                                \n'
        jobString += 'Requirements            = (OSTYPE == \"SLC6\")                                                 \n'
        jobString += 'Rank                    = memory                                                               \n'
        jobString += 'output                  = ' + os.environ['HOME'] + '/CondorLogs/Marlin.out                     \n'
        jobString += 'error                   = ' + os.environ['HOME'] + '/CondorLogs/Marlin.err                     \n'
        jobString += 'log                     = ' + os.environ['HOME'] + '/CondorLogs/Marlin.log                     \n'
        jobString += 'environment             = CONDOR_JOB=true                                                      \n'
        jobString += 'Universe                = vanilla                                                              \n'
        jobString += 'getenv                  = false                                                                \n'
        jobString += 'copy_to_spool           = true                                                                 \n'
        jobString += 'should_transfer_files   = yes                                                                  \n'
        jobString += 'when_to_transfer_output = on_exit_or_evict                                                     \n'
        return jobString

### ----------------------------------------------------------------------------------------------------
### End of getCondorJobString function
### ----------------------------------------------------------------------------------------------------
### Start of checkCondorJobs function
### ----------------------------------------------------------------------------------------------------

    def checkCondorJobs(self, marlinExecutable):
        self.logger.debug('Checking on the running condor jobs.')
        while True: 
            nActiveJobs = self.nQueuedCondorJobs(marlinExecutable)
            if (nActiveJobs > 0):
                time.sleep(10)
            else:
                self.logger.debug('There are no more active condor jobs.')
                return

### ----------------------------------------------------------------------------------------------------
### End of checkCondorJobs function
### ----------------------------------------------------------------------------------------------------
### Start of checkCondorJobs function
### ----------------------------------------------------------------------------------------------------

    def nQueuedCondorJobs(self, marlinExecutable):
        self.logger.debug('Checking on the number of running condor jobs.')
        queueProcess = subprocess.Popen(['condor_q','-w'], stdout=subprocess.PIPE)
        queueOutput = queueProcess.communicate()[0]
        regex = re.compile(marlinExecutable)
        queueList = regex.findall(queueOutput)
        return int(len(queueList))

### ----------------------------------------------------------------------------------------------------
### End of checkCondorJobs function
### ----------------------------------------------------------------------------------------------------

### ====================================================================================================
### GENERAL TOOLS 
### ====================================================================================================

### ----------------------------------------------------------------------------------------------------
### Start of findBetween function
### ----------------------------------------------------------------------------------------------------

def findBetween( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ''

### ----------------------------------------------------------------------------------------------------
### End of findBetween function
### ----------------------------------------------------------------------------------------------------
