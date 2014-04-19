#!/usr/bin/python

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




if __name__ == '__main__' :
    import sys
    import argparse
    
    parser = argparse.ArgumentParser()
    
    # things which remain general
    parser.add_argument( '--dbfile', type=str, default='mydata.sqlite' )
    parser.add_argument( '--cleardb', action='store_true' )
    parser.add_argument( '--vehspeed', type=float, default=1. )
    parser.add_argument( '--distr', type=str, default='PairUniform2' )
    parser.add_argument( '--policy', type=str, default='STACKERCRANE')
    # now, irrelevant
    parser.add_argument( '--phasedil', type=float, default=2. )
    
    
    # for sub-commands:
    subp = parser.add_subparsers(dest='command')
    
    # for a range of orders
    order_parser = subp.add_parser('orders')
    order_parser.add_argument( '--ordermin', type=float, default=1. )
    order_parser.add_argument( '--ordermax', type=float, default=10. )
    order_parser.add_argument( '--linterp', action='store_true' )
    order_parser.add_argument( 'N', type=int )
    order_parser.add_argument( '--numveh', type=int, default=1 )
    # for a range of fleet sizes
    veh_parser = subp.add_parser('vehicles')
    veh_parser.add_argument( '--torder', type=float, default=100. )
    veh_parser.add_argument( 'sizes', type=str )
    
    
    # etc...
    INITDUR = 50.
    #TIMEFACTOR = 2.
    THRESHFACTOR = 1.1
    EXPLOITRATIO = 2.
    
    
    
    
    """ start script """
    args, unknown_args = parser.parse_known_args()
    
    def default_experiment() :
        e = ExperimentRecord()
        # all irrelevant
        e.setInitialDuration( INITDUR )
        e.setTimeDilation( args.phasedil )
        e.setGrowthThreshold( THRESHFACTOR )
        e.setExploitRatio( EXPLOITRATIO )
        
        e.setDistribution( args.distr )
        e.setPolicy( args.policy )      # fairly irrelevant
        e.setFleetSpeed( args.vehspeed )
        
        #e.setFleetSize( args.numveh )
        #e.setRate( float(rate) )        # sympy is being annoying
        
        return e
    
    # import distributions
    import setiptah.taxitheory.distributions as distribs
    distr = distribs.distributions[ args.distr ]
    moverscplx = distr.meancarry() + distr.meanfetch()
    
    # import database interfaces
    import setiptah.taxitheory.db.sql as experimentdb
    db = experimentdb.ExperimentDatabase( args.dbfile, args.cleardb )
    
    # utilities
    from setiptah.taxitheory.db import ExperimentRecord
    import numpy as np
    
    
    """ dispatch the right sub-command """
    if args.command == 'orders' :
        # construct order-range sim
        
        if args.linterp :
            G = np.linspace( args.ordermin, args.ordermax, args.N )
        else :
            G = np.logspace( np.log10( args.ordermin ), np.log10( args.ordermax ),
                             args.N )
            
        RHO = [ distr.inverseQueueLengthFactor(g) for g in G ]
        
        RATES = [ rho * args.numveh * args.vehspeed / moverscplx for rho in RHO ]
        
        for rate in RATES :
            e = default_experiment()
            e.setFleetSize( args.numveh )
            e.setRate( float(rate) )
            
            db.addExperiment( e )
            
    elif args.command == 'vehicles' :
        # method to construct fleet-size range sim
        NUMVEH = sorted( parseints( args.sizes ) )
        
        ORDERS = [ numveh * args.vehspeed * args.torder for numveh in NUMVEH ]
        UTILS = [ distr.inverseQueueLengthFactor(o) for o in ORDERS ]
        RATES = [ rho * numveh * args.vehspeed / moverscplx
                 for rho, numveh in zip( UTILS, NUMVEH ) ]
        
        for numveh, rate in zip( NUMVEH, RATES ) :
            e = default_experiment()
            e.setFleetSize( numveh )
            e.setRate( float(rate) )
            
            db.addExperiment( e )
            
    else :
        raise Exception('sub-command not recognized')
           
           
           
           
           
           
           
           
           
           
            
           