#!/usr/bin/python




if __name__ == '__main__' :
    import sys
    import argparse
    import setiptah.taxitheory.db.sql as experimentdb
    
    import numpy as np
    #import matplotlib.pyplot as plt
    
    parser = argparse.ArgumentParser()
    parser.add_argument( '--dbfile', type=str, default='mydata.sqlite' )
    parser.add_argument( '--cleardb', action='store_true' )
    
    parser.add_argument( '--numveh', type=int, default=1 )
    parser.add_argument( '--vehspeed', type=float, default=1. )
    parser.add_argument( '--distr', type=str, default='PairUniform2' )
    parser.add_argument( '--policy', type=str, default='STACKERCRANE')
    
    parser.add_argument( '--phasedil', type=float, default=2. )
    
    # etc...
    INITDUR = 50.
    #TIMEFACTOR = 2.
    THRESHFACTOR = 1.1
    EXPLOITRATIO = 2.
    
    parser.add_argument( 'N', type=int )
    parser.add_argument( '--ordermin', type=float, default=1. )
    parser.add_argument( '--ordermax', type=float, default=10. )
    
    
    
    """ start script """
    args, unknown_args = parser.parse_known_args()
    
    import setiptah.taxitheory.distributions as distribs
    distr = distribs.distributions[ args.distr ]
    
    G = np.logspace( np.log10( args.ordermin ), np.log10( args.ordermax ),
                     args.N )
    
    RHO = [ distr.inverseQueueLengthFactor(g) for g in G ]
    
    moverscplx = distr.meancarry() + distr.meanfetch()
    RATES = [ rho * args.numveh * args.vehspeed / moverscplx for rho in RHO ]
    
    db = experimentdb.ExperimentDatabase( args.dbfile, args.cleardb )
    
    from setiptah.taxitheory.db import ExperimentRecord
    for rate in RATES :
        e = ExperimentRecord()
        
        e.setDistribution( args.distr )
        e.setFleetSize( args.numveh )
        e.setFleetSpeed( args.vehspeed )
        
        #e.setRate( rate )
        e.setRate( float(rate) )        # sympy is being annoying
        
        e.setInitialDuration( INITDUR )
        e.setTimeDilation( args.phasedil )
        e.setGrowthThreshold( THRESHFACTOR )
        e.setExploitRatio( EXPLOITRATIO )
        
        e.setPolicy( args.policy )
        
        db.addExperiment( e )
        






