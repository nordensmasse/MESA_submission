import sys
import shutil
import os
import time
import subprocess
import numpy
from tempfile import mkstemp
import string

def replace(fname, pattern, subst):
    #Create temp file
    fh, abs_path = mkstemp()
    new_file = open(abs_path,'w')
    old_file = open(fname)
    for line in old_file:
        new_file.write(line.replace(pattern, subst))
    #close temp file
    new_file.close()
    os.close(fh)
    old_file.close()
    #Remove original file
    os.remove(fname)
    #Move new file
    shutil.move(abs_path, fname)

def copy_start_model(M1,M2,JobDir):
   #Identify start model and copy to JobDir
   start_model_dir = key_path + 'start_models'
   dummy = 0
   for fname in os.listdir(start_model_dir):
      if fname.endswith(".mod"):
         dum = fname.split('_')[-1][1:-4]
         if float(dum) == float(M1):
            shutil.copy2(start_model_dir+'/'+ fname, JobDir+'/')
            start_model1 = fname
            if dummy == 2:
               return start_model1, start_model2
            dummy = 1
         if float(dum) == float(M2):
            shutil.copy2(start_model_dir+'/'+fname, JobDir+'/')
            start_model2 = fname
            if dummy == 1:
               return start_model1, start_model2
            dummy = 2

def make_and_submit_mesa_model(model_name, M1, M2, ai, Macc_law, eta, dotM, M1_target):
    #Copy executable folder into new folder named model_name
    #Replace with model parameters
    ExecutableDir = key_path + 'executables/binary_v1.0'
    MTGridsDir = key_path + 'grid'
    ScriptHomeDir = key_path + 'scripts'

    JobDir=MTGridsDir+'/'+ model_name
    shutil.copytree(ExecutableDir, JobDir)
    start_model1, start_model2 = copy_start_model(M1,M2,JobDir)

    #Go to JobDir
    os.chdir(JobDir)

    #Insert models initial conditions
    replace("inlist_project", "m1", "m1 = "+str(M1))
    replace("inlist_project", "m2", "m2 = "+str(M2))
    replace("inlist_project", "initial_separation_in_Rsuns","initial_separation_in_Rsuns = "+str(ai))

    replace("inlist1", "saved_model_name", "saved_model_name = "+"'"+str(start_model1)+"'")
    replace("inlist1", "initial_mass", "initial_mass = "+str(M1))
    replace("inlist1", "x_ctrl(1)","x_ctrl(1) = "+str(Macc_law))
    replace("inlist1", "x_ctrl(2)","x_ctrl(2) = "+str(eta))
    replace("inlist1", "x_ctrl(3)","x_ctrl(3) = "+str(dotM))
    replace("inlist1", "x_ctrl(4)","x_ctrl(4) = "+str(M1_target))

    replace("inlist2", "saved_model_name", "saved_model_name = "+"'"+str(start_model2)+"'")
    replace("inlist2", "initial_mass", "initial_mass = "+str(M2))

    #Begin running MESA
    subprocess.Popen('time ./rn', shell=True).wait()

    #Move relevant data file outside work folder
    check_files_exists = 0
    if os.path.isfile(key_path+'/grid/'+model_name+'/LOGS1/history.data'):
        if os.path.isfile(key_path+'/grid/'+model_name+'/LOGS2/history.data'):
            #If length of binary_history is 1, there is no history on each star.
            check_files_exists = 1
            b = numpy.genfromtxt(key_path+'grid/'+model_name+'/'+'binary_history.data',skip_header=5, names=True)
            s1 = numpy.genfromtxt(key_path+'grid/'+model_name+'/'+'LOGS1/history.data',skip_header=5, names=True)
            s2 = numpy.genfromtxt(key_path+'grid/'+model_name+'/'+'LOGS2/history.data',skip_header=5, names=True)
            numpy.savez_compressed(key_path+'grid/'+model_name+'.npz',B=b, S1=s1, S2=s2)
    else:
        b = numpy.genfromtxt(key_path+'grid/'+model_name+'/'+'binary_history.data',skip_header=5, names=True)
        numpy.savez_compressed(key_path+'grid/'+model_name+'.npz',B=b, S1 = [1], S2=[1])
        print 'MESA: stopped before one time step.'

    os.chdir("../")

    #Delete work folder
    subprocess.Popen('rm -rf '+model_name, shell=True).wait()

    os.chdir(ScriptHomeDir)

    SetupOneRLOJob=1
    return SetupOneRLOJob

if __name__ == '__main__':
    global key_path
    key_path = '/home/sorensen/BinaryFormation/'
    model_name = str(sys.argv[1])
    M1 = str(sys.argv[2])
    M2 = str(sys.argv[3])
    ai = str(sys.argv[4])
    Macc_law = str(sys.argv[5])
    eta = str(sys.argv[6])
    dotM = str(sys.argv[7])
    M1_target = str(sys.argv[8])

    dum = make_and_submit_mesa_model(model_name, M1, M2, ai, Macc_law, eta, dotM, M1_target)
