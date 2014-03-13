
import sqlite3 as sql


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
    
    policy_key TEXT NOT NULL,
    sim_status INTEGER DEFAULT 0
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
    
    def sqlUpdate(self) :
        fmt = """
        UPDATE experiments
        SET
        arrival_rate=?, num_vehicles=?, vehicle_speed=?,
        init_dur=?, time_factor=?, thresh_factor=?, exploit_ratio=?,
        distrib_key=?, policy_key=?
        WHERE id=?
        """
        return fmt
    
    @classmethod
    def fromID(cls, conn, id ) :
        cur = conn.cursor()
        fmt = """
        SELECT * FROM experiments WHERE id=?
        """
        cur.execute(fmt, (id,) )
        row = cur.fetchone()
        
        e = cls()
        e.arrivalrate = float( row[1] )
        e.numveh = int( row[2] )
        e.vehspeed = float( row[3] )
        
        e.init_dur = float( row[4] )
        e.time_factor = float( row[5] )
        e.thresh_factor = float( row[6] )
        e.exploit_ratio = float( row[7] )
        
        e.distrib_key = row[8]
        e.policy_key = row[9]
        return e
    
    

def experimentsIter( conn ) :
    cur = conn.cursor()
    
    res = []
    for row in cur.execute('SELECT * FROM experiments') :
        e = ExperimentRecord()
        
        e.arrivalrate = float( row[1] )
        e.numveh = int( row[2] )
        e.vehspeed = float( row[3] )
        
        e.init_dur = float( row[4] )
        e.time_factor = float( row[5] )
        e.thresh_factor = float( row[6] )
        e.exploit_ratio = float( row[7] )
        
        e.distrib_key = row[8]
        e.policy_key = row[9]
        
        yield e



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





def prepareDatabase( conn, DEBUG=False ) :
    cur = conn.cursor()
    
    if DEBUG :
        cur.execute('DROP TABLE IF EXISTS experiments')
        cur.execute('DROP TABLE IF EXISTS results')
        
    cur.execute( TABLE_SCHEMA['experiments'] )
    cur.execute( TABLE_SCHEMA['results'] )
    
    conn.commit()







if __name__ == '__main__' :
    # don't need sys
    
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--dbfile', type=str, default='mydata')
    args, unknown_args = parser.parse_known_args()
    # unknown_args can be used, e.g., to initialize a Qt application
    
    
    conn = sql.connect( args.dbfile )
    prepareDatabase( conn, DEBUG=True )
    
    cur = conn.cursor()
    
    experiment = ExperimentRecord()
    fmt = experiment.sqlInsert()
    tup = experiment.sqlTuple()
    
    cur.execute( fmt, tup )
    
    conn.commit()
    conn.close()
    
    
    
    

