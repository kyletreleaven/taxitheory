
import sqlite3 as sql
import interface

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




class ExperimentDatabase(interface.ExperimentDatabase) :
    def __init__(self, filename, cleardb=False ) :
        self.conn = sql.connect( filename )
        if cleardb :
            self.clear()
        
        self.prepareDatabase()
        
    def __del__(self) :
        self.conn.close()
        
    def clear(self) :
        cur = self.conn.cursor()
        cur.execute('DROP TABLE IF EXISTS experiments')
        cur.execute('DROP TABLE IF EXISTS results')
        self.conn.commit()
        cur.close()
        
    def prepareDatabase(self) :
        cur = self.conn.cursor()
        cur.execute( TABLE_SCHEMA['experiments'] )
        cur.execute( TABLE_SCHEMA['results'] )
        self.conn.commit()
        cur.close()
        
    def addExperiment(self, experiment ) :
        cur = self.conn.cursor()
        fmt = self.experimentSQLInsert()
        tup = self.experimentSQLTuple( experiment )
        cur.execute( fmt, tup )
        
        rowindex = cur.lastrowid
        
        self.conn.commit()
        cur.close()
        
        return rowindex     # just in case
        
    def updateExperiment(self, id, experiment ) :
        experiment.uniqueID = id
        cur = self.conn.cursor()
        fmt = self.experimentSQLUpdate()
        tup = self.experimentSQLTuple( experiment ) + (id,)
        cur.execute( fmt, tup )
        self.conn.commit()
        cur.close()
        
        
    def experimentsIter(self) :
        cur = self.conn.cursor()
        for row in cur.execute('SELECT * FROM experiments') :
            yield self._fullRowToExperiment( row )
            
            
            
    """ convenient formatters """
    def experimentSQLTuple(self, e ) :
        return ( e.arrivalrate, e.numveh, e.vehspeed,
                 e.init_dur, e.time_factor, e.thresh_factor,
                 e.exploit_ratio,
                 e.distrib_key, e.policy_key ) 
        
    def experimentSQLInsert(self) :
        return """
        INSERT INTO experiments
        ( arrival_rate, num_vehicles, vehicle_speed,
        init_dur, time_factor, thresh_factor, exploit_ratio,
        distrib_key, policy_key )
        VALUES (?,?,?,?,?,?,?,?,?)
        """
        
    def experimentSQLUpdate(self) :
        return """
        UPDATE experiments
        SET
        arrival_rate=?, num_vehicles=?, vehicle_speed=?,
        init_dur=?, time_factor=?, thresh_factor=?, exploit_ratio=?,
        distrib_key=?, policy_key=?
        WHERE id=?
        """
    
    def getExperiment(self, id ) :
        cur = self.conn.cursor()
        fmt = """
        SELECT * FROM experiments WHERE id=?
        """
        cur.execute(fmt, (id,) )
        row = cur.fetchone()
        return self._fullRowToExperiment( row )
    
    @classmethod
    def _fullRowToExperiment(cls, row ) :
        e = interface.ExperimentRecord()
        e.uniqueID = int( row[0] )
        
        e.arrivalrate = float( row[1] )
        e.numveh = int( row[2] )
        e.vehspeed = float( row[3] )
        
        e.init_dur = float( row[4] )
        e.time_factor = float( row[5] )
        e.thresh_factor = float( row[6] )
        e.exploit_ratio = float( row[7] )
        
        e.distrib_key = row[8]
        e.policy_key = row[9]
        
        e.status = row[10]
        if e.status is not None : e.status = int( e.status )
        
        return e













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
    
    
    
    

