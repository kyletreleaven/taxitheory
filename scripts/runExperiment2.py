#!/usr/bin/python
from PyQt4 import QtGui as gui, QtCore as core

import matplotlib.pyplot as plt
import setiptah.taxitheory.gui.mplcanvas as mplcanvas

# simulation components
from setiptah.eventsim.signaling import Signal
from setiptah.eventsim.simulation import Simulation
from setiptah.queuesim.sources import PoissonClock, UniformClock

from setiptah.dyvehr.taxi import Taxi, GatedTaxiDispatch
from setiptah.dyvehr.taxi import RoundRobinScheduler, kCraneScheduler

from setiptah.dyvehr.euclidean import EuclideanPlanner
# going to need roadmap planner/trajectory... I think I have these somewhere...
from setiptah.roadgeometry.roadmap_paths import RoadmapPlanner

import setiptah.taxitheory.distributions as distribs
from setiptah.taxitheory.euclidean.distributions import EuclideanDistribution
from setiptah.taxitheory.roadmap.distributions import RoadmapDistribution

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
        
        # prepare domain Stacker Crane scheduling --- could be made dynamic
        # cuz i'm dumb...
        getTail = lambda dem : dem.origin
        getHead = lambda dem : dem.destination
        
        
        
        # for a moment, hard-code:
        if isinstance( distr, EuclideanDistribution ) :
            planner = EuclideanPlanner
            
            scheduler = kCraneScheduler( getTail, getHead, distr.distance )
            
        elif isinstance( distr, RoadmapDistribution ) :
            planner = RoadmapPlanner( distr.roadmap )
            
            from setiptah.taxitheory.roadmap.simulation import RoadMap_kCraneScheduler
            scheduler = RoadMap_kCraneScheduler( getTail, getHead, distr.roadmap )
            
        else :
            raise NotImplementedError('unrecognized distribution')
        
        
        
        
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
            
        self.batch_indices = []
        self.simUpdate()
        
        FIRSTBATCH = 50.
        MINBATCH = 20.
        CYCLESPERBATCH = 10.
        CEILINGRATIO = 1.01
        #
        ALPHA = .01
        QUOTA = 20
        # just *assume* we will not simulate above stability!!!
        # XTHRESH = 200       # this needs to be added!!!
        
        # phase I --- simulate base time
        # first, try to get approximately EN0 demands
        T0 = FIRSTBATCH / experiment.arrivalrate
        
        while sim.get_time() < T0 :
            callback = sim.get_next_action()
            callback()
        self.simUpdate()
        
        # phase II
        T = [ T0 ]
        
        quota = QUOTA
        batchmean = globalmean = np.mean( self.alive_tape )
        while quota > 0 :
            # try to get a "replacement", but never go for less that MINBATCH
            #target = max( batchmean, MINBATCH )
            target = max( CYCLESPERBATCH * globalmean, MINBATCH )
            Tk = target / experiment.arrivalrate
            
            epoch = sim.get_time()
            while sim.get_time() - epoch < Tk :
                callback = sim.get_next_action()
                callback()
                
            T.append( Tk )
            self.simUpdate()
            
            if False :
                # branch based on batchmean
                bstart = self.batch_indices[-2]
                batchmean = np.mean( self.alive_tape[bstart:] )
                if batchmean <= CEILINGRATIO * globalmean :
                    quota -= 1
                else :
                    pass
                    #quota = QUOTA
                    
            else :
                # branch based on globalmean, but quota in a row
                globalmean_next = np.mean( self.alive_tape )
                #if globalmean_next <= CEILINGRATIO * globalmean :
                if np.abs( globalmean_next - globalmean ) <= ALPHA * globalmean :
                    quota -= 1
                else :
                    quota = QUOTA
                    
                globalmean = globalmean_next
                
            
        # phase III
        # Tf = gamma * sum( T )
        Tf = 0.     # currently, no phase three
        epoch = sim.get_time()
        while sim.get_time() - epoch < Tf :
            callback = sim.get_next_action()
            callback()
            
        self.finalT = Tf
        self.simUpdate()
        
        
        print 'SIMULATION DONE'
        
        
    def simUpdate(self) :
        self.batch_indices.append( len( self.alive_tape ) )
        self.horizon = self.sim.get_time()
        #self.tocs = len( self.alive_tape )
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
        tocs = sim.batch_indices[-1]
        
        time = np.linspace(0, horizon, tocs )
        ax.step( time, sim.alive_tape[:tocs] )
        
        title = 'Experiment %d' % self.simthread.experimentID
        ax.set_title( title )
        
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
            
            self.experimentID = e.uniqueID
            
            self.sim.run( e )
            
            if True :
                demands = ( convertdemand(dem) for dem in self.sim.DEMANDS )
                db2.insertDemands( demands, e.uniqueID )
                



















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
                
    print invalid
    return selection










if __name__ == '__main__' :
    import sys
    import argparse
    
    import numpy as np
    import matplotlib.pyplot as plt
    
    
    parser = argparse.ArgumentParser()
    parser.add_argument( '--dbfile', type=str, default='mydata.sqlite' )
    parser.add_argument( 'index', type=str )
    
    args, unknown_args = parser.parse_known_args()
    
    db = experimentdb.ExperimentDatabase( args.dbfile )
    
    if True :
        experiments = [ db.getExperiment(k) for k in parseints( args.index ) ]
    else :
        if args.index == 'all' :
            experiments = [ e for e in db.experimentsIter() ]
            
        else :
            index = int( args.index )
            experiments = [ db.getExperiment( index ) ]
    
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
    
    
    
    
    
    
    
    
    
    
    
    
