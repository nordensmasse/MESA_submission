# -*- coding: utf-8 -*-
"""
Created on Thu Dec  4 10:40:34 2014

@author: MS
"""

import subprocess
import os
import sys
import numpy
import string
import glob


if __name__ == '__main__':
    GridPath = sys.argv[1] # path to the MT grid directory
    GridType = sys.argv[2] # Type of Grid within MT grid directory. 'MTseq' or 'BG'

    if GridType == 'MTseq':
        files = glob.glob(GridPath+"*_*")
        print files
        for file in files:
            if os.path.isdir(file):
                dirname = string.split(file,'/')[-1]
                (M2, Mbh, P) =  string.split(dirname,'_')
                OutFileS=str(M2)+'_'+str(Mbh)+'_'+str(P)+'S.data'
                OutFileB=str(M2)+'_'+str(Mbh)+'_'+str(P)+'B.data'

                subprocess.Popen('cp '+GridPath+str(M2)+'_'+str(Mbh)+'_'+str(P)+'/LOGS1/history.data '+GridPath+OutFileS, shell=True).wait()
                subprocess.Popen('cp '+GridPath+str(M2)+'_'+str(Mbh)+'_'+str(P)+'/binary_history.data '+GridPath+OutFileB, shell=True).wait()
                subprocess.Popen('gzip '+GridPath+OutFileS, shell=True).wait()
                subprocess.Popen('gzip '+GridPath+OutFileB, shell=True).wait()
                subprocess.Popen('rm -rf '+GridPath+str(M2)+'_'+str(Mbh)+'_'+str(P), shell=True).wait()
                print str(M2)+'_'+str(Mbh)+'_'+str(P)+' converted to *.data.gz'

    if  GridType == 'BG':
        files = glob.glob(GridPath+"BG*")
        for file in files:
            if os.path.isdir(file):
                dirname = string.split(file,'/')[-1]
                OutFileS=dirname+'S.data'
                OutFileB=dirname+'B.data'

                subprocess.Popen('cp '+GridPath+dirname+'/LOGS1/history.data '+GridPath+OutFileS, shell=True).wait()
                subprocess.Popen('cp '+GridPath+dirname+'/binary_history.data '+GridPath+OutFileB, shell=True).wait()
                subprocess.Popen('gzip -fv '+GridPath+OutFileS, shell=True).wait()
                subprocess.Popen('gzip -fv '+GridPath+OutFileB, shell=True).wait()
                subprocess.Popen('rm -rf '+GridPath+dirname, shell=True).wait()
                print dirname+' converted to *.data.gz'

    if  GridType == 'BF':
        files = glob.glob(GridPath+"BF*")
        for file in files:
            if os.path.isdir(file):
                dirname = string.split(file,'/')[-1]
                check_files_exists = 0
                if os.path.isfile(GridPath+dirname+'/LOGS1/history.data'):
                    if os.path.isfile(GridPath+dirname+'/LOGS2/history.data'):
                        #If length of binary_history is 1, there is no history on each star.
                        check_files_exists = 1
                        b = numpy.genfromtxt(GridPath+dirname+'/'+'binary_history.data',skip_header=5, names=True)
                        s1 = numpy.genfromtxt(GridPath+dirname+'/'+'LOGS1/history.data',skip_header=5, names=True)
                        s2 = numpy.genfromtxt(GridPath+dirname+'/'+'LOGS2/history.data',skip_header=5, names=True)
                        numpy.savez_compressed(GridPath + dirname+'.npz',B=b, S1=s1, S2=s2)
                    else:
                        b = numpy.genfromtxt(GridPath+dirname+'/'+'binary_history.data',skip_header=5, names=True)
                        numpy.savez_compressed(GridPath+dirname+'.npz',B=b, S1=[1], S2=[1])
                        print 'MESA: stopped before one time step.'
                #Delete work folder
                subprocess.Popen('rm -rf '+GridPath+dirname, shell=True).wait()
                print dirname+' converted to *.npz'
