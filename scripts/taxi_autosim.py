#!/usr/bin/python

from PyQt4 import QtGui as gui, QtCore as core

import setiptah.taxitheory.gui.mplcanvas as mplcanvas


# simulation components
from setiptah.eventsim.simulation import Simulation
from setiptah.queuesim.sources import PoissonClock, UniformClock
from setiptah.dyvehr.euclidean import EuclideanPlanner
#
from setiptah.dyvehr.taxi import Taxi, GatedTaxiDispatch
from setiptah.dyvehr.taxi import RoundRobinScheduler, kCraneScheduler


# some globals
class data : pass
SIMULATION = data()

class SimResults : pass
RESULTS = SimResults()




class SimDialog(gui.QDialog) :
    def __init__(self, parent=None ) :
        super(SimDialog,self).__init__(parent)
        
        # Matplotlib canvas
        self.canvas = mplcanvas.MplCanvas()
        
        #self.configs = gui.QStandardItemModel()
        #self.configview = gui.QListView(self.conf)
        self.experiments = gui.QStandardItemModel()
        self.experiments_view = gui.QListView()
        self.experiments_view.setModel( self.experiments )
        self.experiments_view.doubleClicked.connect( self.startExperiment )
        
        # simulation group
        #self.simgroup = self._OneShotSimGroup('One-shot Simulation')
        self.simgroup = self._OneShotSimGroup()
        self.connect( self.simgroup.startsim, core.SIGNAL('clicked()'),
                      self.dosim )
        
        self.calcAvg = self._AverageCarry()
        
        self.utilsim = self._UtilizationRangeSim()
        self.utilsim.registerValuable( self.calcAvg.result )
        self.utilsim.registerOutList( self.experiments )
        
        """ layout """
        self.tabs = gui.QTabWidget()
        self.tabs.addTab( self.simgroup, 'One-shot Simulation' )
        self.tabs.addTab( self.calcAvg, 'Calculate Average')
        self.tabs.addTab( self.utilsim, 'Utilization Sims' )
        
        layout = gui.QVBoxLayout()
        layout.addWidget( self.canvas )
        layout.addWidget( self.experiments_view )
        layout.addWidget( self.tabs )
        
        self.setLayout( layout )
        self.setWindowTitle('Taxi Simulation')
    
    class _OneShotSimGroup(gui.QWidget) :
        def __init__(self, *args, **kwargs ) :
            super(SimDialog._OneShotSimGroup,self).__init__( *args, **kwargs )
            
            # instantiate
            self.durationBox = gui.QDoubleSpinBox()
            self.durationBox.setMaximum( 10000. )
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
            self.progress = gui.QProgressBar()
            
            # layout
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
            layout.addLayout( grid )
            layout.addWidget( self.startsim )
            layout.addWidget( self.progress )
            self.setLayout( layout )
            
    class _AverageCarry(gui.QWidget) :
        def __init__(self, *args, **kwargs ) :
            super(SimDialog._AverageCarry,self).__init__()
            
            self.result = gui.QDoubleSpinBox()
            self.result.setDecimals(6)
            #self.result.setValue(1.)
            
            self.effort = gui.QSpinBox()
            self.effort.setMaximum(10**6)
            self.effort.setValue(10000)
            
            self.compute = gui.QPushButton('Find Average')
            self.connect( self.compute, core.SIGNAL('clicked()'),
                          self.findAverage )
            
            grid = gui.QGridLayout()
            grid.addWidget( gui.QLabel('Average Carry'), 0, 0 )
            grid.addWidget( self.result, 0, 1 )
            grid.addWidget( gui.QLabel('Sampling Effort'), 1, 0 )
            grid.addWidget( self.effort, 1, 1 )
            
            layout = gui.QVBoxLayout()
            layout.addLayout( grid )
            layout.addWidget( self.compute )
            self.setLayout(layout)
            
            
        def findAverage(self) :
            import setiptah.taxitheory.euclidean.probability as eucprob
            
            def samplepair() :
                x, y = [ np.random.rand(2) for i in xrange(2) ]
                return x, y
            
            getTail = lambda pair : pair[0]
            getHead = lambda pair : pair[1]
            distance = lambda x, y : np.linalg.norm(y-x)
            
            N = self.effort.value()
            res = eucprob.averageDistance( samplepair,
                                           getTail, getHead, distance, N)
            
            self.result.setValue( res )
            
            
    class ConfigItem :
        def __init__(self, rate, numveh, vehspeed ) :
            self.rate = rate
            self.numveh = numveh
            self.vehspeed = vehspeed
            
        def __repr__(self) :
            data = self.rate, self.numveh, self.vehspeed
            return '{ rate:%f, fleet:%d, vel:%f }' % data
            
            
    class _UtilizationRangeSim(gui.QWidget) :
        def __init__(self, *args, **kwargs ) :
            super(SimDialog._UtilizationRangeSim,self).__init__()
            
            self.numveh = gui.QSpinBox()
            self.numveh.setValue( 5 )
            self.vehspeed = gui.QDoubleSpinBox()
            self.vehspeed.setValue( 1. )
            
            pLayout = gui.QGridLayout()
            pLayout.addWidget( gui.QLabel('Fleet size'), 0, 0 )
            pLayout.addWidget( self.numveh, 0, 1 )
            pLayout.addWidget( gui.QLabel('Vehicle speed'), 0, 2 )
            pLayout.addWidget( self.vehspeed, 0, 3 )
            
            self.environ = gui.QComboBox()
            self.ordermin = gui.QDoubleSpinBox()
            self.ordermin.setMaximum(1000)
            self.ordermin.setValue( 10 )
            self.ordermax = gui.QDoubleSpinBox()
            self.ordermax.setMaximum(1000)
            self.ordermax.setValue( 100 )
            self.samples = gui.QSpinBox()
            self.samples.setValue( 10 )
            
            rlayout = gui.QGridLayout()
            rlayout.addWidget( gui.QLabel('Env.'), 0, 0 )
            rlayout.addWidget( self.environ, 1, 0 )
            rlayout.addWidget( gui.QLabel('Order min'), 0, 1 )
            rlayout.addWidget( self.ordermin, 1, 1 )
            rlayout.addWidget( gui.QLabel('Order max'), 0, 2 )
            rlayout.addWidget( self.ordermax, 1, 2 )
            rlayout.addWidget( gui.QLabel('(samples)'), 0, 3 )
            rlayout.addWidget( self.samples, 1, 3 )
            
            self.simbutton = gui.QPushButton('Simulate')
            self.connect( self.simbutton, core.SIGNAL('clicked()'),
                          self._prepareRates )
            
            layout = gui.QVBoxLayout()
            layout.addLayout( pLayout )
            layout.addLayout( rlayout )
            layout.addWidget( self.simbutton )
            
            self.setLayout( layout )
            
            
        def registerOutList(self, outlist ) :
            self.outlist = outlist
            
        def registerValuable(self, valuable ) :
            self.valuable = valuable
            
            
        def _prepareRates(self) :
            import setiptah.taxitheory.euclidean.simulation as simhelp
            
            gmin = self.ordermin.value()
            gmax = self.ordermax.value()
            N = self.samples.value()
            
            G = np.logspace( np.log10(gmin), np.log10(gmax), N )
            utils = [ simhelp.inversePlanarOrder(g) for g in G ]
            
            moverscplx = self.valuable.value()
            numveh = self.numveh.value()
            speed = self.vehspeed.value()
            rates = [ simhelp.utilizationToRate( rho, moverscplx, numveh, speed )
                     for rho in utils ]
            
            self.outlist.clear()    # get rid of previous experiments
            for rate in rates :
                c = SimDialog.ConfigItem( rate, numveh, speed )
                item = gui.QStandardItem( repr(c) )
                item.setEditable(False)
                item.config = c
                
                self.outlist.appendRow( item )
                
        
        
    def dosim(self) :
        simgroup = self.simgroup
        horizon = simgroup.durationBox.value()
        rate = simgroup.rateBox.value()
        numveh = simgroup.numvehBox.value()
        vehspeed = simgroup.speedBox.value()
        #print horizon, rate, numveh, vehspeed
        
        self.simthread = SimulateThread( rate, numveh, vehspeed, horizon )
        self.simthread.timeElapsed.connect( self.simgroup.progress.setValue )
        self.simthread.simulateDone.connect( self.updatePlot )
        
        self.simthread.start()
        
    def closeEvent(self, event ) :
        if hasattr(self, 'simthread' ) :
            self.simthread.terminate()
            self.simthread.wait()
            
        event.accept()      # have to accept to close; otherwise, could "ingore"
        
    def startExperiment(self, index ) :
        item = self.experiments.itemFromIndex( index )
        simconfig = item.config
        
        self.simgroup.numvehBox.setValue( simconfig.numveh )
        self.simgroup.speedBox.setValue( simconfig.vehspeed )
        self.simgroup.rateBox.setValue( simconfig.rate )
        
        self.dosim()
        
        
    def simdone(self) :
        pass
        
        
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
        
        
    def alarm(self) :
        RESULTS.tocs = len( RESULTS.alive_tape )
        RESULTS.horizon = self.sim.get_time()
        self.simulateDone.emit()
        
        
    def run(self) :
        """ setup """
        sim = Simulation()
        self.sim = sim
        
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
                getTail = lambda dem : dem.origin
                getHead = lambda dem : dem.destination
                scheduler = kCraneScheduler( getTail, getHead, distance )
        
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
            
            
        SIMULATION.DEMANDS = []
        def myarrival() :
            x = samplepoint()
            y = samplepoint()
            
            #print x, y
            time = sim.get_time()
            demand = Taxi.Demand( x, y, time )
            print 'demand generated ', x, y, time
            
            SIMULATION.DEMANDS.append( demand )
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
        if False :
            while sim.get_time() <= self.horizon :
                callback = sim.get_next_action()
                callback()
                
                frac = sim.get_time() / self.horizon
                perc = int( 100. * frac )
                #print perc
                
                self.timeElapsed.emit( perc )       # emit the custom signal?
                
            self.alarm()
                
        else :
            T0 = 100.
            alpha = 2.
            beta = 1.1
            gamma = 1.
            XTHRESH = 250
            
            # phase I --- simulate base time
            while sim.get_time() <= T0 :
                callback = sim.get_next_action()
                callback()
                
            self.alarm()
            
            
            # phase II
            T = [ T0 ]
            xmax = max( RESULTS.alive_tape )
            Tk = T0
            while True :
                Tk = alpha*Tk
                
                epoch = sim.get_time()
                while sim.get_time() - epoch <= Tk :
                    callback = sim.get_next_action()
                    callback()
                    
                T.append( Tk )
                self.alarm()
                
                newmax = max( RESULTS.alive_tape )
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
                
            RESULTS.finalT = Tf
            self.alarm()
            
            print 'SIMULATION DONE'




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
            


