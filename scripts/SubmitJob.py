#    Purpose
#       Read in a list of containing jobs.
#       Make copy of MESA executable folder
#       Add alpha, beta, M2,Mco, P, Z
#       Submit the newly formed job to the cluster
#       Write into log-file what job has been created

import sys
import shutil
import os
import numpy
import time
import datetime
from tempfile import mkstemp
import subprocess
from astropy.table import Table, vstack
import astropy.io.ascii

def read_joblist(path):
    #Read in list
    #path: string containing full path to joblist.
    dum   = numpy.loadtxt(path)
    n     = dum[:,0]
    M1    = dum[:,1]
    M2    = dum[:,2]
    ai    = dum[:,3]
    Macc_law    = dum[:,4]
    eta    = dum[:,5]
    dotM    = dum[:,6]
    M1_target    = dum[:,7]
    return n,M1,M2,ai, Macc_law,eta,dotM,M1_target

def replace(file, pattern, subst):
    #Create temp file
    fh, abs_path = mkstemp()
    new_file = open(abs_path,'w')
    old_file = open(file)
    for line in old_file:
        new_file.write(line.replace(pattern, subst))
    #close temp file
    new_file.close()
    os.close(fh)
    old_file.close()
    #Remove original file
    os.remove(file)
    #Move new file
    shutil.move(abs_path, file)

def submit_slurm_sbatch(model_name, M1, M2, ai, Macc_law, eta, dotM, M1_target):
    SubmissionScriptFile = key_path+'/scripts/baobab_mono_shared.slurm'
    JobLogsDir = key_path+"job_logs"
    ScriptsHomeDir = key_path+'scripts/'
    os.chdir(JobLogsDir)
    NewSubmissionScriptFile = 'job_'+model_name+'.slurm'
    shutil.copy(SubmissionScriptFile,NewSubmissionScriptFile)
    replace(NewSubmissionScriptFile, "#SBATCH --job-name=DummyJobName", "#SBATCH --job-name="+model_name)
    replace(NewSubmissionScriptFile, "#SBATCH --error=DummyJobName", "#SBATCH --error="+model_name)
    replace(NewSubmissionScriptFile, "#SBATCH --output=DummyJobName", "#SBATCH --output="+model_name)
    replace(NewSubmissionScriptFile, 'python StartJobRLO.py', 'python '+key_path+'scripts/StartJob.py '+' '+ model_name+' '+str(M1)+' '+str(M2)+' '+str(ai)+' '+str(Macc_law)+' '+str(eta)+' '+str(dotM)+' '+str(M1_target) )
    subprocess.Popen('sbatch job_'+model_name+'.slurm', shell=True).wait()
    os.chdir(ScriptsHomeDir)
    time.sleep(0.1)

def check_njobs_submitted_on_cluster(jobs_submitted, maxNjobs=40000):
    #Count the number of jobs submitted by the user.
    #If more than n_threshold has been submitted, wait
    #a time period T and re-count the number of jobs.
    #Then submit up to the given threshold.
    if jobs_submitted < maxNjobs-1000 and jobs_submitted > 1:
        return jobs_submitted
    time.sleep(10)    
    #count number of jobs submitted by user.
    command = 'squeue -h -r > '+key_path+'temp/temp_squeue_cluster.log'
    subprocess.Popen(command, shell=True).wait()
    ff = open(key_path+'temp/temp_squeue_cluster.log','r')
    Nlines = sum(1 for line in ff if line.rstrip())
    ff.close()
    #Remove temporary file
    if Nlines >= maxNjobs:
        # Sleep for 1 hour.
        time.sleep(3600.)
        return Nlines
    else:
        return Nlines    

def check_njobs_submitted_by_user(jobs_submitted, maxNjobs):
    #Count the number of jobs submitted by the user.
    #If more than n_threshold has been submitted, wait
    #a time period T and re-count the number of jobs.
    #Then submit up to the given threshold.
    if jobs_submitted < maxNjobs-100:
        return jobs_submitted
    time.sleep(10)    
    #count number of jobs submitted by user.
    command = 'squeue -h -u sorensen > '+key_path+'temp/temp_squeue_user.log'
    subprocess.Popen(command, shell=True).wait()
    ff = open(key_path+'temp/temp_squeue_user.log','r')
    Nlines = sum(1 for line in ff if line.rstrip())
    ff.close()
    #Remove temporary file
    if Nlines >= maxNjobs:
        # Sleep for 1 hour.
        time.sleep(3600.)
        return Nlines
    else:
        return Nlines

def make_job_log_table():
    #Define table
    names = ('model', 'M1','M2','ai','status','year', 'month','day')
    dtype =('S10','f8','f8','f8','f8','S10','i4','i2','i2')
    print 'making new log table'
    t     = Table(names=names,dtype=dtype)
    return t

if __name__ == '__main__':
    #Define a global path reference
    global key_path
    key_path = '/home/sorensen/BinaryFormation/'

    #User input execution
    joblist = str(sys.argv[1])

    #read in job list
    n, M1, M2, ai, Macc_law, eta, dotM, M1_target = read_joblist(joblist)
    
    maxNjobs_by_user = 8010     #Maximum number of jobs that can be submitted on the cluster at the same time by the user.
    maxNjobs_on_cluster = 40000 #Maximum number of jobs that can be submitted on the cluster at the same time between all users.
    jobs_submitted = 0
    jobs_submitted2cluster = check_njobs_submitted_on_cluster(jobs_submitted)
    print 'jobs on cluster now', jobs_submitted2cluster
    jobs_already_done = 0*8248
    for i in range(0,numpy.size(n)):
        model = 'BF' #Short for Binary Grid
        model_name = model+str('%08.0f'%(n[i]+jobs_already_done))
        #get date
        now = datetime.datetime.now()
        #submit job
        submit_slurm_sbatch(model_name, M1[i], M2[i], ai[i], Macc_law[i], eta[i], dotM[i], M1_target[i])
        print model_name, M1[i], M2[i], ai[i], Macc_law[i], eta[i], dotM[i], M1_target[i], 'submitted ', str('%04.0f'%now.year)+str('%02.0f'%now.month)+str('%02.0f'%now.day)
        jobs_submitted = jobs_submitted + 1
        #Check there is room for more jobs in the user queue.
        if jobs_submitted > maxNjobs_by_user-10:
            jobs_submitted = check_njobs_submitted_by_user(jobs_submitted, maxNjobs_by_user)
        #Check there is room for more jobs in the queue of the cluster.
        if jobs_submitted2cluster > maxNjobs_on_cluster*0.98:
            # Cluster queue is almost full. Keep checking and sleep until a low level is reached.
            jobs_submitted2cluster = check_njobs_submitted_on_cluster(jobs_submitted)
