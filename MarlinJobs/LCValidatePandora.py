
from Logic.LCPandoraValidationLogic import * 

slcioFormat = 'Z_uds_ENERGY_GeV_(.*?).slcio'
slcioPath = '/r04/lc/sg568/Validation/Simulation/DD4HEP/v01-19-04/ILD_l1_v01/'
gearFile = '/r04/lc/sg568/Validation/Simulation/DD4HEP/v01-19-04/ILD_l1_v01/Gear_ILD_l1_v01.xml'
outputPath = '/r04/lc/sg568/Validation/Reconstruction/DD4HEP/v01-19-04/ILD_l1_v01/'

LCPandoraValidationLogic(slcioFormat, slcioPath, gearFile, outputPath)

