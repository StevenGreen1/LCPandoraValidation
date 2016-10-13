
from Logic.PandoraTestingLogic import * 

slcioFormat = 'ILD_o1_v06_GJN38_udsENERGY_(.*?).slcio'
slcioPath = '/r04/lc/sg568/HCAL_Optimisation_Studies/Slcio/GJN38/'
gearFile = '/r04/lc/sg568/HCAL_Optimisation_Studies/GridSandboxes/GJN38_OutputSandbox/ILD_o1_v06_Detector_Model_38.gear'
outputPath = '/r06/lc/sg568/LCValidationPandora/ilcsoft_v01-17-10-vs-master-11-10-16/'

ValidatingPandora(slcioFormat, slcioPath, gearFile, outputPath)

