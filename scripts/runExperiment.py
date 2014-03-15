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




class SIMULATION :
    def __init__(self) :
        self.signalUpdate = Signal()    # meh
        
    def run(self, experiment ) :
        """ setup """
        sim = Simulation()
        self.sim = sim
        
        clock = PoissonClock( experiment.arrivalrate )
        clock.join_sim( sim )
        
        # prepare domain planning
        distr = distribs.distributions[ experiment.distrib_key ]
        planner = EuclideanPlanner
        
        # prepare domain Stacker Crane scheduling --- could be made dynamic
        # cuz i'm dumb...
        getTail = lambda dem : dem.origin
        getHead = lambda dem : dem.destination
        scheduler = kCraneScheduler( getTail, getHead, distr.distance )
        
        # prepare geometry queries
        if True :
            pass
        else :
            import setiptah.roadgeometry.roadmap_basic as ROAD
            import setiptah.roadgeometry.probability as roadprob
            from setiptah.roadgeometry.roadmap_paths import RoadmapPlanner
            
            roadmap = roadprob.sampleroadnet()
            U = roadprob.UniformDist( roadmap )
            samplepoint = U.sample
            
            ORIGIN = samplepoint()
            
            distance = lambda x, y : ROAD.distance( roadmap, 
                                                    x, y, length='length' )
            planner = RoadmapPlanner( roadmap )
            
            if True :
                scheduler = RoundRobinScheduler()
            else :
                scheduler = kCraneScheduler( getTail, getHead, distance )
                
        # instantiate the gate
        gate = GatedTaxiDispatch()
        gate.setScheduler( scheduler )
        
        # instantiate the fleet
        ORIGIN = distr.origin()
        
        TAXI = []
        for i in range( experiment.numveh ) :
            taxi = Taxi()
            TAXI.append( taxi )
            
            taxi.setPlanner( planner )
            taxi.setLocation( ORIGIN )
            taxi.setSpeed( experiment.vehspeed )
            
            taxi.join_sim( sim )
            
            gateIF = gate.newInterface()
            gate.add( gateIF )
            gateIF.output.connect( taxi.appendDemands )
            taxi.signalWakeup.connect( gateIF.input )
            taxi.signalIdle.connect( gateIF.input )
            
        gate.join_sim( sim )
        
        def tick() :
            print 'tick, %g' % sim.get_time()
            
            
        self.DEMANDS = []
        def myarrival() :
            demand = distr.sample()
            x = distr.getTail( demand )
            y = distr.getHead( demand )
            
            time = sim.get_time()
            demand = Taxi.Demand( x, y, time )
            print 'demand generated ', x, y, time
            
            self.DEMANDS.append( demand )
            # send the demand to the gate, not any one taxi
            gate.queueDemand( demand )
            
        clock.source().connect( myarrival )
        #clock.source().connect( EVER.increment )
        
        # should do post-hoc analysis... ignore this stuff
        # EDIT: do just for plotting
        self.ever_tape = []
        self.alive_tape = []
        
        def record() :
            self.ever_tape.append( len( self.DEMANDS ) )
            
            total = len( gate._demandQ )
            for taxi in TAXI :
                total += len( taxi._demandQ )
                
            self.alive_tape.append( total )
            
        probe = UniformClock(.1)        # why not
        probe.join_sim( sim )
        probe.source().connect( record )
        
        
        """ SIMULATE """
        if False :
            plt.close('all')
            self.fig = plt.figure()
            plt.show()
        
        T0 = experiment.init_dur
        alpha = experiment.time_factor
        beta = experiment.thresh_factor
        gamma = experiment.exploit_ratio
        XTHRESH = 200       # this needs to be added!!!
        
        # phase I --- simulate base time
        while sim.get_time() <= T0 :
            callback = sim.get_next_action()
            callback()
            
        self.simUpdate()
        
        
        # phase II
        T = [ T0 ]
        xmax = max( self.alive_tape )
        Tk = T0
        while True :
            Tk = alpha*Tk
            
            epoch = sim.get_time()
            while sim.get_time() - epoch <= Tk :
                callback = sim.get_next_action()
                callback()
                
            T.append( Tk )
            self.simUpdate()
            
            newmax = max( self.alive_tape )
            if newmax > XTHRESH :
                print 'TOO MUCH! BAILING!'
                return
            if newmax <= beta * xmax : break
            
            xmax = newmax
            
            
        # phase III
        Tf = gamma * sum( T )
        epoch = sim.get_time()
        while sim.get_time() - epoch <= Tf :
            callback = sim.get_next_action()
            callback()
            
        self.finalT = Tf
        self.simUpdate()
        
        
        print 'SIMULATION DONE'
        
        
    def simUpdate(self) :
        self.horizon = self.sim.get_time()
        self.tocs = len( self.alive_tape )
        self.signalUpdate()     # signal









class SimDialog(gui.QDialog) :
    def __init__(self, parent=None ) :
        super(SimDialog,self).__init__(parent)
        
        # Matplotlib canvas
        self.canvas = mplcanvas.MplCanvas()
        fig = self.canvas.getFigure()
        fig.add_subplot(1,1,1)
        
        layout = gui.QVBoxLayout()
        layout.addWidget( self.canvas )
        #layout.addWidget( self.experiments_view )
        #layout.addWidget( self.tabs )
        self.setLayout( layout )
        self.setWindowTitle('Taxi Simulations')
        
        
        # schedule experiment(s) launch
        self.eiter = []
        core.QTimer.singleShot( 0, self.launchExperiments )
        
    def closeEvent(self, event ) :
        if hasattr(self, 'simthread' ) :
            self.simthread.terminate()
            self.simthread.wait()
            
        event.accept()      # have to accept to close; otherwise, could "ingore"
        
        
    def setExperiments(self, eiter ) :
        self.eiter = eiter
        
    def launchExperiments(self) :
        self.simthread = SimulateThread( self.eiter )
        
        # make connections
        if True :
            # must resolve entirely before thread moves on!
            conntype = core.Qt.BlockingQueuedConnection
            self.simthread.simUpdate.connect( self.updatePlot, conntype )
        
        # start the thread
        self.simthread.start()
        
        
    def updatePlot(self) :
        sim = self.simthread.sim        # could have used self.sender().sim
        
        fig = self.canvas.getFigure()
        fig.clear()
        ax = fig.add_subplot(1,1,1)
        
        horizon = sim.horizon
        tocs = sim.tocs
        
        time = np.linspace(0, horizon, tocs )
        ax.step( time, sim.alive_tape[:tocs] )
        
        self.canvas.draw()




class SimulateThread(core.QThread) :
    #timeElapsed = core.pyqtSignal(int)
    simUpdate = core.pyqtSignal()
    
    def __init__(self, eiter ) :
        super(SimulateThread,self).__init__()
        
        self.eiter = eiter
        self.sim = SIMULATION()
        
        # connect the SIMULATION update signal to pass-thru
        self.sim.signalUpdate.connect( self.simUpdate.emit )
        
        
    def run(self) :
        db2 = experimentdb.ExperimentDatabase( args.dbfile )    # bad, bad form
        
        from setiptah.taxitheory.db import DemandRecord
        def convertdemand( dem ) :
            d = DemandRecord()
            d.arrival_time = dem.arrived
            d.embark_time = dem.embarked
            d.delivery_time = dem.delivered
            return d
        
        for e in self.eiter :
            db2.clearDemands( e.uniqueID )
            
            self.sim.run( e )
            
            if True :
                demands = [ convertdemand(dem) for dem in self.sim.DEMANDS ]
                db2.insertDemands( demands, e.uniqueID )
                




























if __name__ == '__main__' :
    import sys
    import argparse
    
    import numpy as np
    import matplotlib.pyplot as plt
    
    
    parser = argparse.ArgumentParser()
    parser.add_argument( '--dbfile', type=str, default='mydata.sqlite' )
    parser.add_argument( 'index', type=int )
    #parser.add_argument( '--cleardb', action='store_true' )
    
    #parser.add_argument( '--numveh', type=int, default=1 )
    #parser.add_argument( '--vehspeed', type=float, default=1. )
    #parser.add_argument( '--distr', type=str, default='PairUniform2' )
    #parser.add_argument( '--policy', type=str, default='STACKERCRANE')
    
    #parser.add_argument( 'N', type=int )
    #parser.add_argument( '--ordermin', type=float, default=1. )
    #parser.add_argument( '--ordermax', type=float, default=10. )
    args, unknown_args = parser.parse_known_args()
    
    db = experimentdb.ExperimentDatabase( args.dbfile )
    #eiter = db.experimentsIter()
    
    ALL = True
    if ALL :
        experiments = [ e for e in db.experimentsIter() ]
        
    else :
        experiments = [ db.getExperiment( args.index ) ]
    
    if False :
        sim = SIMULATION()
        sim.run( eiter.next() )     # run the first simulation
        
    else :
        app = gui.QApplication( unknown_args )
        
        form = SimDialog()
        #form.eiter = [ eiter.next() ]
        #form.setExperiments( [ eiter.next() ] )
        form.setExperiments( experiments )
        form.show()
        
        sys.exit( app.exec_() )
    
    
    
    
    
    
    
    
    
    
    
    
