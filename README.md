# LCValidationPandora
Scripts for running jet energy resolution validation check on LC Pandora code

To run the validation script please do the following:

1) Create a template steering file in MarlinJobs/Templates:
	1.1) Put in the following variables that will be changed by the python scripts:
		<parameter name="LCIOInputFiles"> LcioInputFile </parameter>
		GearFile <- Only if using MarlinPandora

	1.2) Replace the MarlinPandora, DDMarlinPandora and PfoAnalysis headers by:
		PandoraHeader 

	1.3) Replace the MarlinPandora, DDMarlinPandora and PfoAnalysis implementations by:
		PandoraImplementation

	1.4) Make sure DD4HEP is pointing to correct compact file

2) Put Pandora settings file into PandoraSettings/PandoraSettingsDefault.xml (and cheated if needed) pointing to the correct likelihood data file(s).

3) Create an executable bash script called MarlinJobs/Templates/Marlin.sh script that sources the relevant ilcsoft and runs Marlin $1.

4) Check the steering parameters for MarlinPandora, DDMarlinPandora and PfoAnalysis found in MarlinJobs/Logic/LCPandoraValidationLogic.py to see if they need altering in any way e.g. calibration

5) Modify paths in MarlinJobs/LCValidatePandora.py, cd into the MarlinJobs directory and run 'python LCValidatePandora.py' to set the marlin jobs running.

6) Wait for jobs to finish.  

