#!/usr/bin/python

import os, sys, getopt, re, subprocess, math, dircache, logging, time, random, string

class LCPandoraValidationLogic:
    'Common base class for validating LC Pandora software.'

### ----------------------------------------------------------------------------------------------------
### Start of constructor
### ----------------------------------------------------------------------------------------------------

    def _init_(self, slcioFormat, slcioPath, gearFile, outputPath):
        cwd = os.getcwd()

        self._OutputPath = outputPath

        'Root File Info'
        self._RootFileFolder = os.path.join(self._OutputPath, 'RootFiles') 
        if not os.path.exists(self._RootFileFolder):
            os.makedirs(self._RootFileFolder)

        'Marlin Xml Path'
        self._MarlinXmlPath = os.path.join(self._OutputPath, 'MarlinXml')
        if not os.path.exists(self._MarlinXmlPath):
            os.makedirs(self._MarlinXmlPath)

        'Pndr Path'
        self._PndrPath = os.path.join(self._OutputPath, 'Pndr')
        if not os.path.exists(self._PndrPath):
            os.makedirs(self._PndrPath)

        'Pandora Settings Path'
        self._PandoraSettingsPath = os.path.join(self._OutputPath, 'PandoraSettings')
        if not os.path.exists(self._PandoraSettingsPath):
            os.makedirs(self._PandoraSettingsPath)

        'Logger'
        logFullPath = 'Validation.log'
        if os.path.isfile(logFullPath):
            os.remove(logFullPath)
        self.logger = logging.getLogger(_name_)
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
        pandoraSettings = {}
        pandoraSettings['Default'] = os.path.join(cwd, 'PandoraSettings/PandoraSettingsDefault.xml')
        self._PandoraSettingsFile = pandoraSettings

        'Condor'
        self._UseCondor = True
        self._CondorRunList = []
        self._CondorMaxRuns = 500

        'Random String For Job Submission'
        self._RandomString = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
        self._MarlinExecutable = 'Marlin_' + self._RandomString + '.sh'

        os.system('cp Templates/Marlin.sh ' + self._MarlinExecutable)
        if not os.path.isfile(self._MarlinExecutable):
            self.logger.error('Marlin executable missing.  Exiting.')
            self.logger.error('Marlin executable : ' + self._MarlinExecutable)
            sys.exit()

        self.runPandoras()
        os.system('rm ' + self._MarlinExecutable)

### ----------------------------------------------------------------------------------------------------
### End of constructor
### ----------------------------------------------------------------------------------------------------
### Start of runPandoras function
### ----------------------------------------------------------------------------------------------------

    def runPandoras(self):
        self.prepareSteeringFiles()
        self.runCondorJobs(self._CondorRunList, self._MarlinExecutable)
        self.checkCondorJobs(self._MarlinExecutable)

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

#        for energy in [91,200,360,500]:
        for energy in [91,200]:
            counter = 0
            jobName = 'Z_uds_' + str(energy) + '_GeV'
            activeSlcioFormat = self._SlcioFormat
            activeSlcioFormat = re.sub('ENERGY',str(energy),activeSlcioFormat)

            baseSteeringFile = os.path.join(os.getcwd(), 'Templates/MarlinTemplate.xml')

            jobList = []

            base = open(baseSteeringFile,'r')
            baseContent = base.read()
            base.close()

            basePandoraSettingsContent = {}
            for key, value in self._PandoraSettingsFile.iteritems():
                basePandoraSettings = open(value,'r')
                basePandoraSettingsContent[key] = basePandoraSettings.read()
                basePandoraSettings.close()

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

                ###################################
                # Create the Marlin Steering Files
                ###################################
                xmlFileName = 'Validating_Pandora_' + jobName + '_Job_Number_' + str(counter) + '.xml'
                xmlFullPath = os.path.join(self._MarlinXmlPath, xmlFileName)

                marlinTemplate = re.sub('LcioInputFile',slcioFileName,marlinTemplate)                                 # Slcio File
                marlinTemplate = re.sub('GearFile',self._GearFile,marlinTemplate)                                     # Gear File

                pandoraSettingsFullPath = {}
                rootFileFullPath = {}
                for key, value in self._PandoraSettingsFile.iteritems():
                    pandoraSettingsFileName = 'PandoraSettings' + key + '_' + jobName + '_Job_Number_' + str(counter) + '.xml'
                    pandoraSettingsFullPath[key] = os.path.join(self._PandoraSettingsPath, pandoraSettingsFileName)
                    rootFileFileName = 'Validating_PandoraSettings' + key + '_' + jobName + '_Job_Number_' + str(counter) + '.root'
                    rootFileFullPath[key] = os.path.join(self._RootFileFolder, rootFileFileName)

                marlinTemplate = self.writeXmlFile(marlinTemplate, pandoraSettingsFullPath)             # Calibration Parameters
                for key, value in rootFileFullPath.iteritems():
                    marlinTemplate = re.sub(key + 'PfoAnalysisRootFile', value, marlinTemplate)         # PfoAnalysis Root File

                file = open(xmlFullPath,'w')
                file.write(marlinTemplate)
                file.close()

                ###################################
                # Create the Pandora Settings Files
                ###################################
                for key, value in basePandoraSettingsContent.iteritems():
                    outputEventPndrFileName = 'Validating_PandoraSettings' + key + '_Event_' + jobName + '_Job_Number_' + str(counter) + '.xml'
                    outputGeometryPndrFileName = 'Validating_PandoraSettings' + key + '_Geometry_' + jobName + '_Job_Number_' + str(counter) + '.xml'
                    outputEventPndrFullPath = os.path.join(self._PndrPath, outputEventPndrFileName)
                    outputGeometryPndrFullPath = os.path.join(self._PndrPath, outputGeometryPndrFileName)
                    eventWritingString = """
    <algorithm type = "EventWriting">
        <EventFileName>""" + outputEventPndrFullPath + """</EventFileName>
        <GeometryFileName>""" + outputGeometryPndrFullPath + """</GeometryFileName>
        <ShouldWriteEvents>true</ShouldWriteEvents>
        <ShouldWriteGeometry>true</ShouldWriteGeometry>
        <ShouldOverwriteEventFile>true</ShouldOverwriteEventFile>
        <ShouldOverwriteGeometryFile>true</ShouldOverwriteGeometryFile>
    </algorithm>
"""
                    content = re.sub('<!-- ALGORITHM SETTINGS -->', '<!-- ALGORITHM SETTINGS --> \n' + eventWritingString, value)
                    pandoraSettingsFile = open(pandoraSettingsFullPath[key], 'w')
                    pandoraSettingsFile.writelines(content)
                    pandoraSettingsFile.close()

                self._CondorRunList.append(xmlFullPath)

        self.logger.debug('The current list of xml files to process is: ')
        self.logger.debug(self._CondorRunList)

### ----------------------------------------------------------------------------------------------------
### End of prepareSteeringFiles function
### ----------------------------------------------------------------------------------------------------
### Start of writeXmlFile function
### ----------------------------------------------------------------------------------------------------

    def writeXmlFile(self, template, pandoraSettingsFile):
        self.logger.debug('Writing xml file.')

        pandoraHeader = self.writePandoraXmlHeader(pandoraSettingsFile)
        template = re.sub('PandoraHeader',pandoraHeader,template)

        pandoraImplementation = self.writeDDMarlinPandoraXml(pandoraSettingsFile)
        pandoraImplementation += '\n'
        pandoraImplementation += self.writePandoraAnalsisXml(pandoraSettingsFile)
        template = re.sub('PandoraImplementation',pandoraImplementation,template)
        return template

### ----------------------------------------------------------------------------------------------------
### End of writeXmlFile function
### ----------------------------------------------------------------------------------------------------
### Start of writeDDMarlinPandoraXmlHeader function
### ----------------------------------------------------------------------------------------------------

    def writePandoraXmlHeader(self, pandoraSettingsFile):
        self.logger.debug('Writing MarlinPandora and PfoAnalysis xml header block.')
        headerString = """
<processor name="MyRecoMCTruthLinker"/>"""
        for key, value in pandoraSettingsFile.iteritems():
            headerString += """
<processor name="MyDDMarlinPandora""" + key + """"/>
<processor name="MyPfoAnalysis""" + key + """"/>"""
        return headerString

### ----------------------------------------------------------------------------------------------------
### End of writeDDMarlinPandoraXmlHeader function
### ----------------------------------------------------------------------------------------------------
### Start of writeDDMarlinPandoraXml function
### ----------------------------------------------------------------------------------------------------

    def writeDDMarlinPandoraXml(self, pandoraSettingsFile):
        self.logger.debug('Writing DDMarlinPandora xml block.')
        marlinPandoraTemplate = ''
        for key, value in pandoraSettingsFile.iteritems():
            marlinPandoraTemplate += """
  <processor name="MyDDMarlinPandora""" + key + """" type="DDPandoraPFANewProcessor">
    <parameter name="PandoraSettingsXmlFile" type="String"> """ + value + """ </parameter>
    <!-- Collection names -->
    <parameter name="TrackCollections" type="StringVec"> SiTracks_Refitted </parameter>
    <parameter name="ECalCaloHitCollections" type="StringVec">ECALBarrel ECALEndcap ECALOther</parameter>
    <parameter name="HCalCaloHitCollections" type="StringVec">HCALBarrel HCALEndcap HCALOther</parameter>
    <parameter name="LCalCaloHitCollections" type="StringVec"></parameter>
    <parameter name="LHCalCaloHitCollections" type="StringVec"></parameter>
    <parameter name="MuonCaloHitCollections" type="StringVec">MUON</parameter>
    <parameter name="MCParticleCollections" type="StringVec">MCParticle</parameter>
    <parameter name="RelCaloHitCollections" type="StringVec">RelationCaloHit RelationMuonHit</parameter>
    <parameter name="RelTrackCollections" type="StringVec"> SiTracks_Refitted_Relation </parameter>
    <parameter name="KinkVertexCollections" type="StringVec">KinkVertices</parameter>
    <parameter name="ProngVertexCollections" type="StringVec">ProngVertices</parameter>
    <parameter name="SplitVertexCollections" type="StringVec">SplitVertices</parameter>
    <parameter name="V0VertexCollections" type="StringVec">V0Vertices</parameter>
    <parameter name="ClusterCollectionName" type="String">PandoraClusters""" + key + """</parameter>
    <parameter name="PFOCollectionName" type="String">PandoraPFOs""" + key + """</parameter>
    <!-- Calibration constants -->
    <parameter name="ECalToMipCalibration" type="float">181.818 </parameter>
    <parameter name="HCalToMipCalibration" type="float">41.1523</parameter>
    <parameter name="ECalMipThreshold" type="float">0.5</parameter>
    <parameter name="HCalMipThreshold" type="float">0.3</parameter>
    <parameter name="ECalToEMGeVCalibration" type="float">1.02382098451</parameter>
    <parameter name="HCalToEMGeVCalibration" type="float">1.02382098451</parameter>
    <parameter name="ECalToHadGeVCalibrationBarrel" type="float">1.1944452816</parameter>
    <parameter name="ECalToHadGeVCalibrationEndCap" type="float">1.1944452816</parameter>
    <parameter name="HCalToHadGeVCalibration" type="float">1.04328949699</parameter>
    <parameter name="MuonToMipCalibration" type="float">19607.8</parameter>
    <parameter name="DigitalMuonHits" type="int">0</parameter>
    <parameter name="MaxHCalHitHadronicEnergy" type="float">1000000</parameter>
    <!--Whether to calculate track states manually, rather than copy stored fitter values-->
    <parameter name="UseOldTrackStateCalculation" type="int">0 </parameter>
    <parameter name="NEventsToSkip" type="int">0</parameter>
    <parameter name="Verbosity" options="DEBUG0-4,MESSAGE0-4,WARNING0-4,ERROR0-4,SILENT"> WARNING</parameter>
    <!--Energy Corrections in Marlin Pandora-->
    <!--parameter name="InputEnergyCorrectionPoints" type="FloatVec">InputEnergyCorrectionPoints_XXXX</parameter-->
    <!--parameter name="OutputEnergyCorrectionPoints" type="FloatVec">OutputEnergyCorrectionPoints_XXXX</parameter-->

    <!--Decides whether to create gaps in the geometry (ILD-specific)-->
    <parameter name="CreateGaps" type="bool">false </parameter>

    <!--Track quality settings: need to be optimized! More in processor-->
    <!--Cut on fractional of expected number of BarrelTracker hits-->
    <parameter name="MinBarrelTrackerHitFractionOfExpected" type="int">0 </parameter>
    <!--Cut on minimum number of FTD hits of BarrelTracker hit fraction to be applied-->
    <parameter name="MinFtdHitsForBarrelTrackerHitFraction" type="int">0 </parameter>
    <!--Track quality cut: the minimum number of ftd track hits for ftd only tracks-->
    <parameter name="MinFtdTrackHits" type="int">0 </parameter>
    <!--Min track momentum required to perform final quality checks on number of hits-->
    <parameter name="MinMomentumForTrackHitChecks" type="float">0 </parameter>
    <!--Cut on fractional of expected number of TPC hits-->
    <parameter name="MinTpcHitFractionOfExpected" type="float">0 </parameter>
    <!--Sanity check on separation between ip and track projected ecal position-->
    <parameter name="MinTrackECalDistanceFromIp" type="float">0 </parameter>
    <!--Track quality cut: the minimum number of track hits-->
    <parameter name="MinTrackHits" type="int">0 </parameter>

    <!-- MORE TRACKING  CUTS -->
    <!--Max distance from track to BarrelTracker r max to id whether track reaches ecal-->
    <parameter name="ReachesECalBarrelTrackerOuterDistance" type="float">-100 </parameter>
    <!--Max distance from track to BarrelTracker z max to id whether track reaches ecal-->
    <parameter name="ReachesECalBarrelTrackerZMaxDistance" type="float">-50 </parameter>
    <!--Max distance from track hit to ftd z position to identify ftd hits-->
    <parameter name="ReachesECalFtdZMaxDistance" type="float">1 </parameter>
    <!--Min FTD layer for track to be considered to have reached ecal-->
    <parameter name="ReachesECalMinFtdLayer" type="int">0 </parameter>
    <!--Minimum number of BarrelTracker hits to consider track as reaching ecal-->
    <parameter name="ReachesECalNBarrelTrackerHits" type="int">0 </parameter>
    <!--Minimum number of ftd hits to consider track as reaching ecal-->
    <parameter name="ReachesECalNFtdHits" type="int">0 </parameter>
    <!--Maximum energy for unmatched vertex track-->
    <parameter name="UnmatchedVertexTrackMaxEnergy" type="float">5 </parameter>
    <!--Whether can form pfos from tracks that don't start at vertex-->
    <parameter name="UseNonVertexTracks" type="int">1 </parameter>
    <!--Whether to calculate track states manually, rather than copy stored fitter values-->
    <parameter name="UseOldTrackStateCalculation" type="int">0 </parameter>
    <!--Whether can form pfos from unmatched tracks that don't start at vertex-->
    <parameter name="UseUnmatchedNonVertexTracks" type="int">0 </parameter>
    <!--Whether can form pfos from unmatched tracks that start at vertex-->
    <parameter name="UseUnmatchedVertexTracks" type="int">1 </parameter>
    <!--Track z0 cut used to determine whether track can be used to form pfo-->
    <parameter name="Z0TrackCut" type="float">50 </parameter>
    <!--z0 cut used to determine whether unmatched vertex track can form pfo-->
    <parameter name="Z0UnmatchedVertexTrackCut" type="float">5 </parameter>
    <!--Non vtx track z cut to determine whether track can be used to form pfo-->
    <parameter name="ZCutForNonVertexTracks" type="float">250 </parameter>
    <!--Track quality cut: the maximum number of track hits-->
    <parameter name="MaxTrackHits" type="int">5000 </parameter>
    <!--Cut on fractional track momentum error-->
    <parameter name="MaxTrackSigmaPOverP" type="float">0.15 </parameter>
    <!--Constant relating track curvature in b field to momentum-->
    <parameter name="CurvatureToMomentumFactor" type="float">0.00015 </parameter>
    <!--Track d0 cut used to determine whether track can be used to form pfo-->
    <parameter name="D0TrackCut" type="float">50 </parameter>
    <!--d0 cut used to determine whether unmatched vertex track can form pfo-->
    <parameter name="D0UnmatchedVertexTrackCut" type="float">5 </parameter>

    <!--The algorithm name for filling start vertex-->
    <parameter name="StartVertexAlgorithmName" type="string">PandoraPFANew </parameter>
    <!--Start Vertex Collection Name-->
    <parameter name="StartVertexCollectionName" type="string" lcioOutType="Vertex"> PandoraStartVertices""" + key + """ </parameter>
  </processor> """
        return marlinPandoraTemplate

### ----------------------------------------------------------------------------------------------------
### End of writeDDMarlinPandoraXml function
### ----------------------------------------------------------------------------------------------------
### Start of writePandoraAnalsisXml function
### ----------------------------------------------------------------------------------------------------

    def writePandoraAnalsisXml(self, pandoraSettingsFile):
        self.logger.debug('Writing PandoraAnalysis xml block.')

        pandoraAnalysisTemplate = ''
        for key, value in pandoraSettingsFile.iteritems():
            pandoraAnalysisTemplate += """ 
<processor name="MyPfoAnalysis""" + key + """" type="PfoAnalysis">
  <!--PfoAnalysis analyses output of PandoraPFANew, Modified for calibration-->
  <!--Names of input pfo collection-->
  <parameter name="PfoCollection" type="string" lcioInType="ReconstructedParticle">PandoraPFOs""" + key + """ </parameter>
  <!--Names of mc particle collection-->
  <parameter name="MCParticleCollection" type="string" lcioInType="MCParticle">MCParticle </parameter>
  <!--Collect Calibration Details-->
  <parameter name="CollectCalibrationDetails" type="int">1</parameter>
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
  <parameter name="ECalCollectionsSimCaloHit" type="StringVec">ECalBarrelCollection ECalEndcapCollection ECalPlugCollection </parameter>
  <!--HCal Barrel Collection SimCaloHit Names-->
  <parameter name="HCalBarrelCollectionsSimCaloHit" type="StringVec"> HCalBarrelCollection </parameter>
  <!--HCal Endcap Collection SimCaloHit Names-->
  <parameter name="HCalEndCapCollectionsSimCaloHit" type="StringVec"> HCalEndcapCollection </parameter>
  <!--HCal Other/Ring Collection SimCaloHit Names-->
  <parameter name="HCalOtherCollectionsSimCaloHit" type="StringVec"> HCalRingCollection </parameter>
  <!--Set the debug print level-->
  <parameter name="Printing" type="int"> 0 </parameter>
  <!--Output root file name-->
  <parameter name="RootFile" type="string">""" + key + """PfoAnalysisRootFile</parameter>
</processor>"""
        return pandoraAnalysisTemplate

### ----------------------------------------------------------------------------------------------------
### End of writePandoraAnalsisXml function
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
                    while nQueued >= self._CondorMaxRuns:
                        subprocess.call(["usleep", "500000"])
                        nQueued = self.nQueuedCondorJobs(marlinExecutable)

                    with open(condorJobFile, 'w') as jobFile:
                        jobString = self.getCondorJobString(marlinExecutable, idx)
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

    def getCondorJobString(self, marlinExecutable, idx):
        jobString  = 'executable              = ' + os.getcwd() + '/' + marlinExecutable + '                         \n'
        jobString += 'initial_dir             = ' + os.getcwd() + '                                                  \n'
        jobString += 'notification            = never                                                                \n'
        jobString += 'Requirements            = (OSTYPE == \"SLC6\")                                                 \n'
        jobString += 'Rank                    = memory                                                               \n'
        jobString += 'output                  = ' + os.environ['HOME'] + '/CondorLogs/Marlin' + str(idx) + '.out     \n'
        jobString += 'error                   = ' + os.environ['HOME'] + '/CondorLogs/Marlin' + str(idx) + '.err     \n'
        jobString += 'log                     = ' + os.environ['HOME'] + '/CondorLogs/Marlin' + str(idx) + '.log     \n'
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
        queueProcess = subprocess.Popen(['condor_q','-nobatch'], stdout=subprocess.PIPE)
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
