
from Logic.LCPandoraValidationLogic import * 

#slcioFormat = 'Z_uds_ENERGY_GeV_(.*?).slcio'
slcioFormat = 'kaon0L_ENERGY_GeV_(.*?).slcio'
slcioPath = '/r04/lc/sg568/Validation/Simulation/DD4HEP/v01-19-04/ILD_l4_v02/'
gearFile = '/r04/lc/sg568/Validation/Simulation/DD4HEP/v01-19-04/ILD_l4_v02/Gear_ILD_l4_v02.xml'
outputPath = '/r04/lc/sg568/Validation/Reconstruction/DD4HEP/v01-19-04/ILD_l4_v02/'

LCPandoraValidationLogic(slcioFormat, slcioPath, gearFile, outputPath)

