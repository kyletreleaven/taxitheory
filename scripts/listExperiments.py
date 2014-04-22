#!/usr/bin/python





if __name__ == '__main__' :
    import sys
    import argparse
    
    
    parser = argparse.ArgumentParser()
    parser.add_argument( '--dbfile', type=str, default='mydata.sqlite' )
    #parser.add_argument( '--cleardb', action='store_true' )
    
    
    """ start script """
    args, unknown_args = parser.parse_known_args()
    
    import prettytable as pT
    cols = [ 'ID', 'Status',
            'Arrival Rate', 'Fleet Size', 'Fleet Speed',
            'Distrib',
            '\\rho',
            'NO', 'TO' ]
    table = pT.PrettyTable( cols )
    table.float_format = '.5'
    
    # populate table
    STATUS = { None : 'BLANK', 1 : 'SIMULATED', 2 : 'CORRUPT' }
    
    import setiptah.taxitheory.db.sql as experimentdb
    from setiptah.taxitheory.db import ExperimentRecord
    db = experimentdb.ExperimentDatabase( args.dbfile )
    
    import numpy as np
    import setiptah.taxitheory.distributions as distribs
    
    for e in db.experimentsIter() :
        distr = distribs.distributions[ e.distrib_key ]
        mcplx = distr.meanfetch() + distr.meancarry()
        rho = e.arrivalrate * mcplx / e.numveh / e.vehspeed
        NO = distr.queueLengthFactor(rho)
        TO = NO / e.numveh / e.vehspeed
        
        row = [ e.uniqueID, None,
               e.arrivalrate, e.numveh, e.vehspeed,
               e.distrib_key,
               #e.init_dur, e.time_factor, e.thresh_factor, e.exploit_ratio
               rho, NO, TO ]
        
        row[1] = STATUS[e.status]
        
        table.add_row( row )
        
        
    print table



