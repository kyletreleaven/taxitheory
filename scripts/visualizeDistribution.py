#!/usr/bin/python
from PyQt4 import QtGui as gui, QtCore as core

import setiptah.taxitheory.euclidean.distributions as distribs


# some globals
class data : pass




if __name__ == '__main__' :
    import sys
    import argparse
    
    import numpy as np
    
    # plotting
    import matplotlib as mpl
    if True :
        #mpl.rcParams['ps.useafm'] = True
        #mpl.rcParams['pdf.use14corefonts'] = True
        #mpl.rcParams['text.usetex'] = True
        
        font = {
                #'family' : 'normal',
                #'weight' : 'bold',
                'size'   : 18 }
        mpl.rc('font', **font)
    
    import matplotlib.pyplot as plt
    
    
    parser = argparse.ArgumentParser()
    
    # fixed variables
    parser.add_argument( 'distr', type=str, default='PairUniform2' )
    parser.add_argument( '--N', type=int, default=None )
    
    args, unknown_args = parser.parse_known_args()
    
    distr = distribs.distributions[ args.distr ]
    distr.visualize( args.N )
    
    
    
    
    
    
    
    
    
