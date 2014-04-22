#!/usr/bin/python
#from PyQt4 import QtGui as gui, QtCore as core
#import setiptah.taxitheory.gui.mplcanvas as mplcanvas

# simulation components
#from setiptah.eventsim.signaling import Signal
#from setiptah.eventsim.simulation import Simulation
#from setiptah.queuesim.sources import PoissonClock, UniformClock
#from setiptah.dyvehr.euclidean import EuclideanPlanner
#
#from setiptah.dyvehr.taxi import Taxi, GatedTaxiDispatch
#from setiptah.dyvehr.taxi import RoundRobinScheduler, kCraneScheduler






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
        
        dim = [ 8., 6. ]
        dim = mpl.rcParams['figure.figsize']
        mpl.rcParams['figure.figsize'] = tuple( [ 1.4 * d for d in dim ] )
        
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
    parser.add_argument( '--vehspeed', type=float, default=1. )
    
    parser.add_argument( '--nonum', action='store_true' )
    parser.add_argument( '--nobound', action='store_true' )
    
    #parser.add_argument( '--fit', action='store_true' )     # we'll fill this in later
    
    
    args, unknown_args = parser.parse_known_args()
    
    
    import setiptah.taxitheory.db.sql as experimentdb
    db = experimentdb.ExperimentDatabase( args.dbfile )
    
    INCLUDE = [ e for e in db.experimentsIter()
               if e.distrib_key == args.distr
               #and e.numveh == args.numveh
               and e.vehspeed == args.vehspeed ]
    #eiter = db.experimentsIter()
    SIZES = [ e.numveh for e in INCLUDE ]
    
    import setiptah.taxitheory.distributions as distribs
    distr = distribs.distributions[ args.distr ]
    mcplx_star = distr.meanfetch() + distr.meancarry()
    
    def computeAverageSystemTime( e ) :
        demands = db.demandsIter( e.uniqueID )
        
        systimes = [ dem.delivery_time - dem.arrival_time for dem in demands
                    if dem.delivery_time is not None ]
        return np.mean( systimes )
    
    meansys = [ computeAverageSystemTime(e) for e in INCLUDE ]
    if args.nonum :
        labels = SIZES
    else :
        labels = [ e.uniqueID for e in INCLUDE ]
    
    if True :
        # show lines
        plt.scatter( SIZES, meansys )
        
        # find a trend line for the results?
        if False and args.fit :
            import scipy.stats as stats
            pass
        
        for x,y,label in zip( SIZES, meansys, labels ) :
            plt.annotate( label,
                          xy = (x, y), xytext = (-5, 5),
                          textcoords = 'offset points', ha = 'right', va = 'bottom',
                          #bbox = dict(boxstyle = 'round,pad=0.5', fc = 'yellow', alpha = 0.5),
                          #arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0'))
                          )
                
        # now, draw lines (bounds + fit?), with warping?
        if args.nobound :
            bounds = {}
        else :
            bounds = distr.boundConstants()
            
            
        # assume all orders are the same... generated that way...
        e0 = INCLUDE[0]
        rho = e0.arrivalrate * mcplx_star / e0.numveh / e0.vehspeed
        order_star = distr.queueLengthFactor(rho)
        
        # show the bounds
        for c in bounds.itervalues() :
            line = [ c * order_star / numveh / args.vehspeed for numveh in SIZES ]
            plt.plot( SIZES, line, '--' )
        
        
        
        
        
        
    else :          # show levels
        pass
    
    
    # axes
    RATES = [ e.arrivalrate for e in INCLUDE ]
    ticklabels = [ '%.3f' % rate for rate in RATES ]
    
    ax1 = plt.gca()
    ax2 = ax1.twiny()   # for utilization
    ax2.set_xticks( SIZES )
    ax2.set_xticklabels( ticklabels )
    
    xlabel = distr.horizontalAxisLabel()
    if xlabel is not None :
        plt.xlabel( xlabel )
        
    plt.show()
    
    
    
    
    
    
    
    
    
    
