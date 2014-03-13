
TABLE_SCHEMA = {}

TABLE_SCHEMA['experiments'] = """
CREATE TABLE IF NOT EXISTS experiments (
    id INTEGER PRIMARY KEY,
    arrival_rate REAL NOT NULL,
    num_vehicles INTEGER NOT NULL,
    vehicle_speed REAL NOT NULL DEFAULT 1,
    
    
    init_dur REAL NOT NULL,
    time_factor REAL NOT NULL,
    thresh_factor REAL NOT NULL,
    exploit_ratio REAL NOT NULL,
    
    distrib_key TEXT NOT NULL,
    meancarry REAL,
    meanfetch REAL,
    moverscplx REAL,
    utilization REAL,
    
    policy_key TEXT NOT NULL
)
"""

class ExperimentRecord :
    def __init__(self) :
        self.arrivalrate = 1.
        self.numveh = 1
        self.vehspeed = 1.
        
        self.init_dur = 50.
        self.time_factor = 2.
        self.thresh_factor = 1.1
        self.exploit_ratio = 1.
        
        self.distrib_key = 'UNIFORM2'
        self.policy_key = 'STACKERCRANE'
        
    def sqlTuple(self) :
        return ( self.arrivalrate, self.numveh, self.vehspeed,
                 self.init_dur, self.time_factor, self.thresh_factor,
                 self.exploit_ratio,
                 self.distrib_key, self.policy_key ) 
        
    def sqlInsert(self) :
        fmt = """
        INSERT INTO experiments
        ( arrival_rate, num_vehicles, vehicle_speed,
        init_dur, time_factor, thresh_factor, exploit_ratio,
        distrib_key, policy_key )
        VALUES (?,?,?,?,?,?,?,?,?)
        """
        return fmt




TABLE_SCHEMA['results'] = """
CREATE TABLE IF NOT EXISTS results (
    experiment_id INTEGER NOT NULL,
    
    origin TEXT,
    destination TEXT,
    
    arrival_time REAL NOT NULL,
    embark_time REAL,
    delivery_time REAL,
    wait_dur REAL,
    carry_dur REAL,
    system_dur REAL,
    
    -- just a hint, won't actually be enforced by sqlite
    FOREIGN KEY(experiment_id) REFERENCES experiments( id )    
)
"""

class DemandRecord :
    def __init__(self) :
        self.experiment = None



if __name__ == '__main__' :
    # don't need sys
    import sqlite3 as sql
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--dbfile', type=str, default='mydata')
    args, unknown_args = parser.parse_known_args()
    # unknown_args can be used, e.g., to initialize a Qt application
    
    conn = sql.connect( args.dbfile )
    cur = conn.cursor()
    
    DEBUG = True
    if DEBUG :
        cur.execute('DROP TABLE IF EXISTS experiments')
        cur.execute('DROP TABLE IF EXISTS results')
    
    cur.execute( TABLE_SCHEMA['experiments'] )
    experiment = ExperimentRecord()
    fmt = experiment.sqlInsert()
    tup = experiment.sqlTuple()
    cur.execute( fmt, tup )
    
    cur.execute( TABLE_SCHEMA['results'] )
    
    conn.commit()
    conn.close()
    
    
    
    

