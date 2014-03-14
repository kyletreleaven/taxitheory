#!/usr/bin/python
from PyQt4 import QtGui as gui, QtCore as core

import matplotlib.pyplot as plt
import setiptah.taxitheory.gui.mplcanvas as mplcanvas

# simulation components
from setiptah.eventsim.simulation import Simulation
from setiptah.queuesim.sources import PoissonClock, UniformClock
from setiptah.dyvehr.euclidean import EuclideanPlanner
#
from setiptah.dyvehr.taxi import Taxi, GatedTaxiDispatch
from setiptah.dyvehr.taxi import RoundRobinScheduler, kCraneScheduler

import setiptah.taxitheory.euclidean.distributions as distribs


# some globals
class data : pass
#SIMULATION = data()

RESULTS = data()




class SimDialog(gui.QDialog) :
    def __init__(self, parent=None ) :
        super(SimDialog,self).__init__(parent)
        
        # Matplotlib canvas
        self.canvas = mplcanvas.MplCanvas()
        layout = gui.QVBoxLayout()
        layout.addWidget( self.canvas )
        #layout.addWidget( self.experiments_view )
        #layout.addWidget( self.tabs )
        self.setLayout( layout )
        self.setWindowTitle('Taxi Simulation')
        
        # set a timer to start simulation!
        
    def closeEvent(self, event ) :
        if hasattr(self, 'simthread' ) :
            self.simthread.terminate()
            self.simthread.wait()
            
        event.accept()      # have to accept to close; otherwise, could "ingore"
        
        
        
        
    def startsim(self) :
        simgroup = self.simgroup
        horizon = simgroup.durationBox.value()
        rate = simgroup.rateBox.value()
        numveh = simgroup.numvehBox.value()
        vehspeed = simgroup.speedBox.value()
        #print horizon, rate, numveh, vehspeed
        
        self.simthread = SimulateThread( experiment )
        self.simthread.simulateDone.connect( self.updatePlot )
        
        self.simthread.start()

        
    def startExperiment(self, index ) :
        item = self.experiments.itemFromIndex( index )
        simconfig = item.config
        
        self.simgroup.numvehBox.setValue( simconfig.numveh )
        self.simgroup.speedBox.setValue( simconfig.vehspeed )
        self.simgroup.rateBox.setValue( simconfig.rate )
        
        self.dosim()
        
        
    def updatePlot(self) :
        #print 'SIMULATION FINISHED'
        fig = self.canvas.getFigure()
        fig.clear()
        ax = fig.add_subplot(1,1,1)
        
        #horizon = self.durationBox.value()      # this could have changed!
        horizon = RESULTS.horizon
        tocs = RESULTS.tocs
        time = np.linspace(0, horizon, tocs )
        #ax.step( time, RESULTS.ever_tape, time, RESULTS.alive_tape )
        ax.step( time, RESULTS.alive_tape[:tocs] )
        
        self.canvas.draw()




class SimulateThread(core.QThread) :
    timeElapsed = core.pyqtSignal(int)
    simulateDone = core.pyqtSignal()
    
    def __init__(self) :
        super(SimulateThread,self).__init__()
        
    def alarm(self) :
        RESULTS.tocs = len( RESULTS.alive_tape )
        RESULTS.horizon = self.sim.get_time()
        self.simulateDone.emit()
        
        
    def run(self) :
        pass
    
    

































class SIMULATION :
    
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
            
        self.alarm()
        
        
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
            self.alarm()
            
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
        self.alarm()
        
        print 'SIMULATION DONE'
        
        
    def alarm(self) :
        self.tocs = len( self.alive_tape )
        self.horizon = self.sim.get_time()
        self.updatePlot()
        
        
    def updatePlot(self) :
        #print 'SIMULATION FINISHED'
        fig = self.fig
        fig.clear()
        ax = fig.add_subplot(1,1,1)
        
        #horizon = self.durationBox.value()      # this could have changed!
        horizon = self.horizon
        tocs = self.tocs
        time = np.linspace(0, horizon, tocs )
        #ax.step( time, RESULTS.ever_tape, time, RESULTS.alive_tape )
        ax.step( time, self.alive_tape[:tocs] )
        
        fig.canvas.draw()











if __name__ == '__main__' :
    import sys
    import argparse
    
    import numpy as np
    import matplotlib.pyplot as plt
    
    import setiptah.taxitheory.db.sql as experimentdb
    
    
    parser = argparse.ArgumentParser()
    parser.add_argument( '--dbfile', type=str, default='mydata.sqlite' )
    #parser.add_argument( '--cleardb', action='store_true' )
    
    #parser.add_argument( '--numveh', type=int, default=1 )
    #parser.add_argument( '--vehspeed', type=float, default=1. )
    #parser.add_argument( '--distr', type=str, default='PairUniform2' )
    #parser.add_argument( '--policy', type=str, default='STACKERCRANE')
    
    # etc...
    INITDUR = 50.
    TIMEFACTOR = 2.
    THRESHFACTOR = 1.1
    EXPLOITRATIO = 2.
    
    #parser.add_argument( 'N', type=int )
    #parser.add_argument( '--ordermin', type=float, default=1. )
    #parser.add_argument( '--ordermax', type=float, default=10. )
    args, unknown_args = parser.parse_known_args()
    
    
    db = experimentdb.ExperimentDatabase( args.dbfile )
    sim = SIMULATION()
    
    eiter = db.experimentsIter()
    e = eiter.next()
    sim.run( e )
    
    
    app = gui.QApplication( sys.argv )
    form = SimDialog()
    
    fig = form.canvas.getFigure()
    ax = fig.add_subplot(1,1,1)
    
    if False :
        t = np.linspace(0,1,100)
        x = np.sin(2*np.pi*t)
        ax.plot(t,x)
    form.canvas.draw()
    
    form.show()
    
    sys.exit( app.exec_() )
    
    



    

