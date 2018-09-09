# MESA_submission
Script to submit large number of MESA jobs on a cluster


Start by making a project folder.
In the project folder create the following folder tree:
/executables/
/grid/
/job_logs/
/model_list/
/scripts/

Or download a version of this repository to there.

--------------------
Folder: /executables/
Contains your MESA work directory/ies.

--------------------
Folder: /grid/
Contains a output from MESA runs in the form of npz files.

--------------------
Folder: /job_logs/
Contains the std. out and std. err files generated from running a MESA job on a cluster

--------------------
Folder: /model_list/
Contains the lists of jobs submitted to the cluster with the initial conditions given to MESA.

--------------------
Folder: /scripts/
contains all relevant python scripts to submit a large number of jobs on a cluster.
