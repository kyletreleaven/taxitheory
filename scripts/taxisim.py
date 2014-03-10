#!/usr/bin/python

from PyQt4 import QtGui as gui, QtCore as core

import setiptah.taxitheory.gui.mplcanvas as mplcanvas


# simulation components
from setiptah.eventsim.simulation import Simulation
from setiptah.queuesim.sources import PoissonClock, UniformClock
from setiptah.dyvehr.euclidean import EuclideanPlanner
from setiptah.dyvehr.taxi import Taxi, GatedTaxiDispatch, kCraneScheduler


class SimResults : pass
# just keep some global results
RESULTS = SimResults()






class SimDialog(gui.QDialog) :
    def __init__(self, parent=None ) :
        super(SimDialog,self).__init__(parent)
        
        self.canvas = mplcanvas.MplCanvas()
        
        self.durationBox = gui.QDoubleSpinBox()
        self.durationBox.setValue( 50. )
        self.durationBox.setSingleStep( 10. )
        
        self.rateBox = gui.QDoubleSpinBox()
        self.rateBox.setValue( 5. )
        self.rateBox.setSingleStep( .1 )
        
        self.numvehBox = gui.QSpinBox()
        self.numvehBox.setValue(2)
        
        self.speedBox = gui.QDoubleSpinBox()
        self.speedBox.setValue( 1. )
        
        self.distrib = gui.QComboBox()
        
        self.startsim = gui.QPushButton('Simulate')
        self.connect( self.startsim, core.SIGNAL('clicked()'), self.dosim )
        
        self.progress = gui.QProgressBar()
        
        widgets = [ self.durationBox, self.rateBox, self.numvehBox,
                   self.speedBox, self.distrib ]
        labels = {
                  self.durationBox : 'Duration',
                  self.rateBox : 'Arrival Rate',
                  self.numvehBox : 'Fleet Size',
                  self.speedBox : 'Vehicle Speed',
                  self.distrib : 'O/D Distribution'
                  }
        
        grid = gui.QGridLayout()
        for row, widget in enumerate( widgets ) :
            grid.addWidget( gui.QLabel( labels[widget] ), row, 0 )
            grid.addWidget( widget, row, 1 )
        
        layout = gui.QVBoxLayout()
        layout.addWidget( self.canvas )
        layout.addLayout( grid )
        layout.addWidget( self.startsim )
        layout.addWidget( self.progress )
        
        self.setLayout( layout )
        self.setWindowTitle('Taxi Simulation')
        
        
    def dosim(self) :
        horizon = self.durationBox.value()
        rate = self.rateBox.value()
        numveh = self.numvehBox.value()
        vehspeed = self.speedBox.value()
        
        print horizon, rate, numveh, vehspeed
        
        self.simthread = SimulateThread( rate, numveh, vehspeed, horizon )
        self.simthread.timeElapsed.connect( self.progress.setValue )
        self.simthread.simulateDone.connect( self.updatePlot )
        
        self.simthread.start()
        
    def simdone(self) :
        pass
        
        
    def updatePlot(self) :
        print 'SIMULATION FINISHED'
        fig = self.canvas.getFigure()
        fig.clear()
        ax = fig.add_subplot(1,1,1)
        
        tocs = len( RESULTS.ever_tape )
        horizon = self.durationBox.value()      # this could have changed!
        time = np.linspace(0, horizon, tocs  )
        ax.step( time, RESULTS.ever_tape, time, RESULTS.alive_tape )
        
        self.canvas.draw()



class dumbcounter :
    def __init__(self) :
        self._value = 0
        
    def increment(self) :
        self._value += 1
        
    def value(self) : return self._value
    
    


class SimulateThread(core.QThread) :
    timeElapsed = core.pyqtSignal(int)
    simulateDone = core.pyqtSignal()
    
    def __init__(self, rate, numveh, vehspeed, horizon ) :
        super(SimulateThread,self).__init__()
        
        self.rate = rate
        self.numveh = numveh
        self.vehspeed = vehspeed
        self.horizon = horizon
        
        
    def run(self) :
        """ setup """
        sim = Simulation()
        
        clock = PoissonClock( self.rate )
        clock.join_sim( sim )
        
        # prepare geometry queries
        if True :
            ORIGIN = np.zeros(2)
            
            def samplepoint() :
                return np.random.rand(2)
                
            planner = EuclideanPlanner
            #scheduler = RoundRobinScheduler()
            
            # Euclidean instantiation
            getTail = lambda dem : dem.origin
            getHead = lambda dem : dem.destination
            distance = lambda x, y : np.linalg.norm( y - x )
            scheduler = kCraneScheduler( getTail, getHead, distance )
            
        else :
            import setiptah.roadgeometry.probability as roadprob
            from setiptah.roadgeometry.roadmap_paths import RoadmapPlanner
            
            roadmap = roadprob.sampleroadnet()
            U = roadprob.UniformDist( roadmap )
            samplepoint = U.sample
            
            ORIGIN = samplepoint()
            
            planner = RoadmapPlanner( roadmap )
            scheduler = RoundRobinScheduler()
        
        # instantiate the gate
        gate = GatedTaxiDispatch()
        gate.setScheduler( scheduler )
        
        # instantiate the fleet
        TAXI = []
        for i in range( self.numveh ) :
            taxi = Taxi()
            TAXI.append( taxi )
            
            taxi.setPlanner( planner )
            taxi.setLocation( ORIGIN )
            taxi.setSpeed( self.vehspeed )
            
            taxi.join_sim( sim )
            
            gateIF = gate.newInterface()
            gate.add( gateIF )
            gateIF.output.connect( taxi.appendDemands )
            taxi.signalWakeup.connect( gateIF.input )
            taxi.signalIdle.connect( gateIF.input )
            
        gate.join_sim( sim )
        
        def tick() :
            print 'tick, %g' % sim.get_time()
            
        def myarrival() :
            x = samplepoint()
            y = samplepoint()
            
            #print x, y
            time = sim.get_time()
            demand = Taxi.Demand( x, y, time )
            print 'demand generated ', x, y, time
            
            # send the demand to the gate, not any one taxi
            gate.queueDemand( demand )
            
        EVER = dumbcounter()
        
        clock.source().connect( myarrival )
        clock.source().connect( EVER.increment )
            
        RESULTS.ever_tape = []
        RESULTS.alive_tape = []
        
        def record() :
            RESULTS.ever_tape.append( EVER.value() )
            
            total = len( gate._demandQ )
            for taxi in TAXI :
                total += len( taxi._demandQ )
                
            RESULTS.alive_tape.append( total )
            
        probe = UniformClock(.1)        # why not
        probe.join_sim( sim )
        probe.source().connect( record )
        
        
        """ run """
        #T = 50.
        while sim.get_time() <= self.horizon :
            callback = sim.get_next_action()
            callback()
            
            frac = sim.get_time() / self.horizon
            perc = int( 100. * frac )
            #print perc
            
            self.timeElapsed.emit( perc )       # emit the custom signal?
            
        self.simulateDone.emit()






if __name__ == '__main__' :
    import sys
    import numpy as np
    import matplotlib.pyplot as plt
            
            
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
            


