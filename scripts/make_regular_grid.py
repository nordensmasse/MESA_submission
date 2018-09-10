# -*- coding: utf-8 -*-
"""
Created on Thu Oct 27 21:55:55 2016

@author: MS
"""

import numpy
import astropy.io.ascii as ascii
#Accretion laws:
# 1 constant
# 2 Churchwell Henning
# 3 exponential decay
Macc_laws = [2]

#Distribution of accretion rate onto each star

#etas = [3,2,1,0.5,0,-0.5]
etas = [3]

#Only used for constant accretion, Macc_laws == 1
#dotMs = [1e-3,1e-4]
dotMs = [0]
#target masses
M1_targets = [65.]

#mass ratios
#qs = numpy.concatenate([numpy.linspace(0.1,0.7,7),numpy.linspace(0.8,1.0,21)])
#qs = numpy.linspace(0.8,1.0,21)
qlow = 0.1
qhigh = 1.0
dq = 0.01
n_qi = (qhigh-qlow)/dq
qs = numpy.zeros(int(n_qi+1))
qs[0] = qlow
i = 1
while i < len(qs):
    qs[i] = qs[i-1]+dq
    i = i + 1
M1s = [1.]
ais_old = [-1]#numpy.linspace(1,3,11)
alow = 1.0
aup = 4.2
dai = 0.01
ais = numpy.array([])
ai = alow
while ai < aup:
    ais = numpy.append(ais,ai)
    ai += dai
    if ai > 2.69:
        dai = 0.05
#ais = numpy.linspace(alow,aup,110)
#If adding into existing grid, read its log and get maximum model number to continue the grid.

#fname_log = 'BF_no_MT.log'
#Define paths
#path = '/data/disk2/sorensen/BinaryFormation/'
#path_grid = path+'grid/'
#path_model_list = path + 'model_list/'
#path_job_logs = path + 'job_logs/'
#path_PPdata = path + 'PPdata/'
#data = ascii.read(path_PPdata+'a_crit_no_MT.dat')
#n = int(numpy.max(data['model']))
n = 109746
#print n

for Macc_law in Macc_laws:
    if Macc_law == 1:
        for eta in etas:
            for dotM in dotMs:
                for M1_target in M1_targets:
                    for M1 in M1s:
                        for q in qs:
                            for ai in ais:
                                n=n+1
                                print '%6.0f' %n, '%6.0f' %M1, '%3.2f' %(M1*q), 10**ai, Macc_law, eta, dotM, M1_target
    else:
        for eta in etas:
            dotM = -1
            for M1_target in M1_targets:
                for M1 in M1s:
                    for q in qs:
#                        if q == 0.8 or q == 0.9 or q == 1.0:
#                            continue
                        for ai in ais:
                            n=n+1
                            print '%6.0f' %n, '%6.0f' %M1, '%3.2f' %(M1*q), 10**ai, Macc_law, eta, dotM, M1_target

