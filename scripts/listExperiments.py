#!/usr/bin/python

import prettytable as pT




if __name__ == '__main__' :
    import sys
    import argparse
    
    import numpy as np
    
    
    import setiptah.taxitheory.db.sql as experimentdb
    from setiptah.taxitheory.db import ExperimentRecord
    
    
    parser = argparse.ArgumentParser()
    parser.add_argument( '--dbfile', type=str, default='mydata.sqlite' )
    #parser.add_argument( '--cleardb', action='store_true' )
    
    
    """ start script """
    args, unknown_args = parser.parse_known_args()
    
    cols = [ 'ID', 'Status',
            'Arrival Rate', 'Fleet Size', 'Fleet Speed',
            'Distrib',
            'Init Dur', 'Phase Dilat', 'Growth Tresh', 'Exploit' ]
    table = pT.PrettyTable( cols )
    
    # populate table
    db = experimentdb.ExperimentDatabase( args.dbfile )
    STATUS = { None : 'BLANK', 1 : 'SIMULATED', 2 : 'CORRUPT' }
    
    for e in db.experimentsIter() :
        row = [ e.uniqueID, None,
               e.arrivalrate, e.numveh, e.vehspeed,
               e.distrib_key,
               e.init_dur, e.time_factor, e.thresh_factor, e.exploit_ratio ]
        
        row[1] = STATUS[e.status]
        
        table.add_row( row )
        
        
    print table



