# LCValidationPandora
Scripts for running jet energy resolution validation check on LC Pandora code

To run the validation script please do the following:

1) Copy the init_ilcsoft.sh and ILCSoft.cmake scripts from your choice of ilcsoft builds to this directory.  Default script in directory is from ilcsoft v01-19-04.

2) Run 'python Initalise.py' to generate init_ilcsoft_local.sh and ILCSoft_Local.cmake.

3) Build PandoraPFA (with LCContent), DDMarlinPandora and LCPandoraAnalysis in this directory using init_ilcsoft_local.sh and ILCSoft_Local.cmake for DDMarlinPandora and LCPandoraAnalysis.  Clone the ILDConfig (https://github.com/iLCSoft/ILDConfig.git) folder in the same directory.

4) Run 'python Generate.py' to generate all scripts needed for marlin jobs.

5) Modify paths in MarlinJobs/LCValidatePandora.py, cd into the MarlinJobs directory and run 'python LCValidatePandora.py' to set the marlin jobs running.  Make sure you have a compact xml to gear conversion for the detector model you are working with.

6) Wait for jobs to finish.  Then run 'python AnalysePerformance/AnalsePerformance.py Path_To_Root_Files.  Results saved as Local_JetEnergyResolutions.txt and Release_JetEnergyResolutions.txt.'

