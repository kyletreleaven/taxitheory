#!/usr/bin/python
from PyQt4 import QtGui as gui, QtCore as core

import matplotlib.pyplot as plt
import setiptah.taxitheory.gui.mplcanvas as mplcanvas

# simulation components
from setiptah.eventsim.signaling import Signal
from setiptah.eventsim.simulation import Simulation
from setiptah.queuesim.sources import PoissonClock, UniformClock
from setiptah.dyvehr.euclidean import EuclideanPlanner
#
from setiptah.dyvehr.taxi import Taxi, GatedTaxiDispatch
from setiptah.dyvehr.taxi import RoundRobinScheduler, kCraneScheduler

import setiptah.taxitheory.euclidean.distributions as distribs

import setiptah.taxitheory.db.sql as experimentdb


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
    parser.add_argument( '--dbfile', type=str, default='mydata.sqlite' )
    
    # fixed variables
    parser.add_argument( 'distr', type=str, default='PairUniform2' )
    parser.add_argument( '--numveh', type=int, default=1 )
    parser.add_argument( '--vehspeed', type=float, default=1. )
    parser.add_argument( '--nonum', action='store_true' )
    
    args, unknown_args = parser.parse_known_args()
    
    
    db = experimentdb.ExperimentDatabase( args.dbfile )
    
    INCLUDE = [ e for e in db.experimentsIter()
               if e.distrib_key == args.distr
               and e.numveh == args.numveh
               and e.vehspeed == args.vehspeed ]
    #eiter = db.experimentsIter()
    
    distr = distribs.distributions[ args.distr ]
    
    mult = distr.meanfetch() + distr.meancarry()
    mult /= args.numveh
    mult /= args.vehspeed
    
    utils = [ mult * e.arrivalrate for e in INCLUDE ]
    orders = [ distr.queueLengthFactor(rho) for rho in utils ]
    
    def computeAverageSystemTime( e ) :
        demands = db.demandsIter( e.uniqueID )
        
        systimes = [ dem.delivery_time - dem.arrival_time for dem in demands
                    if dem.delivery_time is not None ]
        return np.mean( systimes )
    
    meansys = [ computeAverageSystemTime(e) for e in INCLUDE ]
    labels = [ e.uniqueID for e in INCLUDE ]
    
    if True :       # show lines
        plt.scatter( orders, meansys )
        
        if not args.nonum :
            for x,y,label in zip( orders, meansys, labels ) :
                plt.annotate( label, 
                              xy = (x, y), xytext = (-5, 5),
                              textcoords = 'offset points', ha = 'right', va = 'bottom',
                              #bbox = dict(boxstyle = 'round,pad=0.5', fc = 'yellow', alpha = 0.5),
                              #arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0'))
                              )
            
        bounds = distr.boundConstants()
        for c in bounds.itervalues() :
            line = [ c * x for x in orders ]
            plt.plot( orders, line, '--' )
            
    else :          # show levels
        plt.scatter( orders, [ st / n for n, st in zip( orders, meansys ) ] )
        
        if not args.nonum :
            for x,y,label in zip( orders, meansys, labels ) :
                plt.annotate( label, 
                              xy = (x, y/x), xytext = (-5, 5),
                              textcoords = 'offset points', ha = 'right', va = 'bottom',
                              #bbox = dict(boxstyle = 'round,pad=0.5', fc = 'yellow', alpha = 0.5),
                              #arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0'))
                              )
            
        bounds = distr.boundConstants()
        for c in bounds.itervalues() :
            line = [ c for x in orders ]
            plt.plot( orders, line, '--' )
    
    # axes
    ax1 = plt.gca()
    ax2 = ax1.twiny()   # for utilization
    
    o1, o2 = ax1.get_xlim()
    o1 = max(1.,o1)
    #print o1, o2
    numticks = 6
    if False :
        rho1 = distr.inverseQueueLengthFactor(o1)
        rho2 = distr.inverseQueueLengthFactor(o2)
        rhoticks = np.linspace(rho1,rho2, numticks+2 )[1:-1]
        ticks = [ distr.queueLengthFactor(rho) for rho in rhoticks ]
        
    else :
        ticks = np.linspace(o1,o2, numticks+2 )[1:-1]
        rhoticks = [ distr.inverseQueueLengthFactor(o) for o in ticks ]
        
    ticklabels = [ '%.3f' % rho for rho in rhoticks ]
    ax2.set_xticks( ticks )
    ax2.set_xticklabels( ticklabels )
    #ax2.set_xlabel(r"Modified x-axis: $1/(1+X)$")
    
    xlabel = distr.horizontalAxisLabel()
    if xlabel is not None :
        plt.xlabel( xlabel )
        
    plt.show()
    
    
    
    
    
    
    
    
    
    
