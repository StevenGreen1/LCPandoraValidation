# LCValidationPandora
Scripts for running jet energy resolution validation check on LC Pandora code

To run the validation script please do the following:

1) Copy the init_ilcsoft.sh and ILCSoft.cmake scripts from your choice of ilcsoft builds to this directory.  Please use a build with gcc48 at least.  Default script in directory is from ilcsoft v01-17-09.

2) Run 'python Initalise.py' to generate init_ilcsoft_local.sh and ILCSoft_Local.cmake.

3) Build PandoraPFA (with LCContent), MarlinPandora and LCPandoraAnalysis in this directory using init_ilcsoft_local.sh and ILCSoft_Local.cmake for MarlinPandora and LCPandoraAnalysis.

4) Run 'python Generate.py' to generate all scripts needed for marlin jobs.

5) Modify paths in MarlinJobs/LCValidatePandora.py, cd into the MarlinJobs directory and run 'python LCValidatePandora.py' to set the marlin jobs running.

6) Wait for jobs to finish.  Then run 'python AnalysePerformance/AnalsePerformance.py Path_To_Root_Files.  Results saved as Local_JetEnergyResolutions.txt and Release_JetEnergyResolutions.txt.'

