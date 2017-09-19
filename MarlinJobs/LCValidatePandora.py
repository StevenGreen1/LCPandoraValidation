
from Logic.LCPandoraValidationLogic import * 

slcioFormat = 'Z_uds_ENERGY_GeV_(.*?).slcio'
slcioPath = '/r04/lc/sg568/Validation/Simulation/DD4HEP/v01-19-04/CLIC_o3_v13/'
gearFile = '/r04/lc/sg568/Validation/Simulation/DD4HEP/v01-19-04/CLIC_o3_v13/gear_CLIC_o3_v13.xml'
outputPath = '/r04/lc/sg568/Validation/Reconstruction/DD4HEP/v01-19-04/CLIC_o3_v13/'

LCPandoraValidationLogic(slcioFormat, slcioPath, gearFile, outputPath)

