# -*- coding: utf-8 -*-
"""
Created on Thu Oct 27 21:55:55 2016

@author: MS
"""

import numpy

qs = numpy.linspace(0.1,1,10)
M1s = [1]
ais = 10.**numpy.linspace(1,3,11)
n = 0
for M1 in M1s:
    for q in qs:
        for ai in ais:
            n = n+1
            print n, M1,M1*q,ai
