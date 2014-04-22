#!/usr/bin/python
from PyQt4 import QtGui as gui, QtCore as core


import setiptah.taxitheory.gui.mplcanvas as mplcanvas

# simulation components
#from setiptah.eventsim.signaling import Signal
#from setiptah.eventsim.simulation import Simulation
#from setiptah.queuesim.sources import PoissonClock, UniformClock
#from setiptah.dyvehr.euclidean import EuclideanPlanner
#
#from setiptah.dyvehr.taxi import Taxi, GatedTaxiDispatch
#from setiptah.dyvehr.taxi import RoundRobinScheduler, kCraneScheduler



def parseints( inputstr ) :
    selection = set()
    invalid = set()
    
    tokens = inputstr.split(',')
    for i in tokens :
        try :
            selection.add( int(i) )
        
        except :
            try :
                token = [ int( k.strip() ) for k in i.split('-') ]
                assert len( token ) == 2
                
                selection.update( xrange( token[0], token[1] + 1 ) )
            
            except :
                invalid.add( i )
                
    if len( invalid ) > 0 : print invalid
    return selection




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
    parser.add_argument( '--numveh', type=int, default=1 )
    parser.add_argument( '--vehspeed', type=float, default=1. )
    
    parser.add_argument( '--nonum', action='store_true' )
    parser.add_argument( '--nobound', action='store_true' )
    parser.add_argument( '--fit', nargs='?', const='all', default=None )
    
    parser.add_argument( '--warp', nargs=3, default=None )
    
    
    args, unknown_args = parser.parse_known_args()
    FLAGS = data()
    
    import setiptah.taxitheory.db.sql as experimentdb
    db = experimentdb.ExperimentDatabase( args.dbfile )
    
    INCLUDE = [ e for e in db.experimentsIter()
               if e.distrib_key == args.distr
               and e.numveh == args.numveh
               and e.vehspeed == args.vehspeed ]
    
    import setiptah.taxitheory.distributions as distribs
    distr = distribs.distributions[ args.distr ]
    
    mcplx_star = distr.meanfetch() + distr.meancarry()
    
    # obtain "orders"
    stime = float( mcplx_star ) / args.vehspeed
    utils = [ e.arrivalrate * stime / args.numveh
             for e in INCLUDE ]
    orders = [ distr.queueLengthFactor(rho) for rho in utils ]
    orders = [ float(o) for o in orders ]
    
    # parse warp options
    if args.warp is not None :
        warp_mode = args.warp[0]
        if warp_mode not in [ 'fit', 'bounds' ] :
            print 'warp modes are "fit" and "bounds"'
        
        warp_alpha = float( args.warp[1] )
        warp_num = int( args.warp[2] )
        
        warp_factors = np.linspace( 1+warp_alpha, 1-warp_alpha, warp_num )
        
        
    # crunch data...
    def computeAverageSystemTime( e ) :
        demands = db.demandsIter( e.uniqueID )
        
        systimes = [ dem.delivery_time - dem.arrival_time for dem in demands
                    if dem.delivery_time is not None ]
        return np.mean( systimes )
    
    meansys = [ computeAverageSystemTime(e) for e in INCLUDE ]
    labels = [ e.uniqueID for e in INCLUDE ]
    
    
    
    if True :
        
        # show lines
        plt.scatter( orders, meansys )
        
        # find a trend line for the results?
        if args.fit is not None :
            # selective fitting?
            if args.fit == 'all' :
                indices = range( len( orders ) )
            else :
                active = parseints( args.fit )
                indices = [ k for k, e in enumerate(INCLUDE) if e.uniqueID in active ]
            #
            orders_active = [ orders[k] for k in indices ]
            meansys_active = [ meansys[k] for k in indices ]
            
            
            import scipy.stats as stats
            #print zip( orders, meansys )
            #print stats.linregress( orders, meansys )
            slope, intercept, r_value, _, __ = stats.linregress( orders_active, meansys_active )
            
            # plot the fit
            fit = [ intercept + slope*o for o in orders ]
            plt.plot( orders, fit, '--' )
            
            print 'slope: %.3f' % slope
            print 'intercept: %.3f' % intercept
            print 'r-value: %.3f' % r_value
            
            if args.warp is not None and warp_mode == 'fit' :
                for alpha in warp_factors :
                    utils_alt = [ alpha * rho for rho in utils ]
                    orders_alt = [ distr.queueLengthFactor(rho) for rho in utils_alt ]
                    
                    plt.plot( orders_alt, fit, '--' )
                    
                    delta_str = '%.3f' % ( alpha - 1. )
                    alpha_str = '%.3f' % alpha
                    plt.annotate( alpha_str, xy = ( orders_alt[-1], fit[-1] ),
                                  xytext = (-5, 5 ),
                                  textcoords = 'offset points', ha='right', va='bottom' )
                    
                    
                    
        if not args.nonum :
            for x,y,label in zip( orders, meansys, labels ) :
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
        # show the bounds (warped?)
        for c in bounds.itervalues() :
            # bound const only accounts for universals and mcplx
            cc = c / args.numveh / args.vehspeed
            line = [ cc * x for x in orders ]
            plt.plot( orders, line, '--' )
            
            if args.warp is not None and warp_mode == 'bounds' :
                for alpha in warp_factors :
                    utils_alt = [ alpha * rho for rho in utils ]
                    orders_alt = [ distr.queueLengthFactor(rho) for rho in utils_alt ]
                    line = [ cc * x for x in orders_alt ]
                    
                    plt.plot( orders, line, '--' )
                    
                    delta_str = '%.3f' % ( alpha - 1. )
                    alpha_str = '%.3f' % alpha
                    plt.annotate( alpha_str, xy = ( orders[-1], line[-1] ),
                                  xytext = (-5, 5 ),
                                  textcoords = 'offset points', ha='right', va='bottom' )
            
            
            
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
    
    
    
    
    
    
