
# built-in
import itertools
import random

# science common
import numpy as np
import scipy as sp
import networkx as nx

# dev
# mass transport framework
import setiptah.roadearthmover.tests.testcases as testcases
import setiptah.roadearthmover.probability as massprob
from setiptah.roadearthmover.rategraphs import totalrate, scale_rates       # rategraph functions

#import setiptah.roadearthmover.road_Ed as road_Ed
#import setiptah.roadearthmover.roademd as roademd

# roadmap framework
import setiptah.roadgeometry.roadmap_basic as ROAD
import setiptah.roadgeometry.probability as roadprob

# simulation framework
from setiptah.eventsim.signaling import Signal, Message
from setiptah.eventsim.simulation import Simulation
#
#from setiptah.queuesim.queues import GatedQueue
from setiptah.queuesim.sources import UniformClock, PoissonClock, ScriptSource
#
from setiptah.roadearthmover.simulation.sources import RoadnetDemandSource
#from setiptah.roadearthmover.simulation.queues import BatchNNeighDispatcher
#from setiptah.roadearthmover.simulation.servers import Vehicle
from setiptah.dyvehr.taxi import Taxi, GatedTaxiDispatch, TaxiScheduler


""" convenient constructors """
from setiptah.taxitheory.roadmap.generators import get_sim_setting
from setiptah.taxitheory.roadmap.simulation import sample_demands

class data : pass

def debug_input() :
    if False : return raw_input()



""" need to write an FHK taxi scheduler """
import setiptah.vehrouting.roadsplice as roadsplice

class RoadmapFHKScheduler(TaxiScheduler) :
    def __init__(self, roadmap ) :
        self.roadmap = roadmap
        
    def __call__( self, demands, agentLocs ) :
        dems = [ ( dem.origin, dem.destination ) for dem in demands ]
        dems = [ roadsplice.demand( (p.road,p.coord), (q.road,q.coord) ) for p,q in dems ]
        assign = roadsplice.ROADS_kSPLICE( dems, agentLocs, self.roadmap )
        res = {}
        for agent, tour in assign.iteritems() :
            if len( tour ) > 0 :
                res[agent] = [ demands[i] for i in tour ]
                
        print res
        return res






""" simulation-based network tester """
class RoadmapEMD(object) :
    def __init__(self) :
        self.vehspeed = 1.
        #self.horizon = 500.
        
    def scenario(self, roadnet, rategraph, numveh=1, vehspeed=1. ) :
        self.roadnet = roadnet
        self.rategraph = rategraph
        self.numveh = numveh
        self.vehspeed = vehspeed
        
    def distance(self, p, q ) :
        return ROAD.distance( self.roadnet, p, q, 'length' )
    
    """ make simulation """
    def sim_init( self ) :
        """ simulation setup """
        # construct the simulation blocks
        sim = Simulation()
        self.sim = sim
        
        if False :
            script = sample_demands( self.horizon, self.rategraph, self.roadnet )
            source = ScriptSource( script )
            print 'obtained %d demands' % len( source.script )
            debug_input()
        else :
            source = RoadnetDemandSource( self.roadnet, self.rategraph )
            
        self.source = source
        source.join_sim( sim )
        
        
        # policy setup
        #import setiptah.roadgeometry.probability as roadprob
        #roadmap = roadprob.sampleroadnet()
        #U = roadprob.UniformDist( roadmap )
        #samplepoint = U.sample
        # instantiate the gate
        gate = GatedTaxiDispatch()
        gate.setScheduler( RoadmapFHKScheduler( self.roadnet ) )
        self.gate = gate
        
        # source -> gate
        
        # fleet setup
        vehicles = {}
        self.vehicles = vehicles
        
        # fleet parameters
        from setiptah.roadgeometry.roadmap_paths import RoadmapPlanner
        planner = RoadmapPlanner( self.roadnet ) 
        roads = [ road for _,__,road in self.roadnet.edges(data=True) ]
        road = random.choice( roads )
        ORIGIN = ROAD.RoadAddress(road,0.)      # just... somewhere
        
        for i in range( self.numveh ) :
            taxi = Taxi()
            
            taxi.setPlanner( planner )
            randpoint = roadprob.sampleaddress( self.roadnet, 'length' )
            taxi.setLocation( randpoint )
            taxi.setSpeed( 1. )
            
            taxi.join_sim( sim )
            
            gateIF = gate.newInterface()
            gate.add( gateIF )
            
            vehicles[taxi] = gateIF
            gateIF.output.connect( taxi.appendDemands )
            
            taxi.signalWakeup.connect( gateIF.input )
            taxi.signalIdle.connect( gateIF.input )
            
        gate.join_sim( sim )
        
        
        # record number of unassigned demands
        self.tape = []
        def record_unassigned() :
            # first, count the demands waiting in the gate
            unassg = len( self.gate._demandQ )  #+ len( self.dispatch.demands )
            # then, count the demands in vehicle queues (minus possibly 1 being worked on)
            for veh in self.vehicles :
                temp = len( veh._demandQ )
                temp = max( temp, 1 ) - 1
                unassg += temp
            # recorder the number
            self.tape.append( unassg )
            
        recorder = UniformClock( 1. )
        recorder.join_sim( sim )
        recorder.output.connect( record_unassigned )
        self.recorder = recorder
        
        # report demand arrivals to several places
        self.DEMANDS = []
        def record_arrival( dem ) :
            self.DEMANDS.append( dem )
        
        def give_to_dispatch( dem ) :
            #p, q = dem
            taxidem = Taxi.Demand( *dem )
            self.gate.queueDemand( taxidem )
            
        source_out = source.source()
        #source_out.connect( counting.increment )
        source_out.connect( record_arrival )
        source_out.connect( give_to_dispatch )
        #source.source().connect( give_to_dispatch )
        
        self.timer = data()
        self.timer.last_time = sim.time
        def say( dem ) :
            p, q = dem
            new_time = self.sim.time
            elapsed = new_time - self.timer.last_time
            print 'tick, %f: %s, %s' % ( elapsed, repr(p), repr(q) )
            self.timer.last_time = new_time
            
        source_out.connect( say )
        
        def gimme( *args, **kwargs ) :
            print "need a batch!!"
            
        # creates an interface from gate to interactive dispatcher
        #gate_if = gate.spawn_interface()
        #self.gate_if = gate_if
        #dispatch.request_batch.connect( gate.requestRelease )
        #dispatch.request_batch.connect( gimme )
        #gate.output.connect( dispatch.batch_arrived )
        #gate_if.batch_out.connect( dispatch.batch_arrived )
        
        def hello( *args, **kwargs ) :
            print 'vehicle is ready!'
        
    def tick() :
        print 'tick, %g' % sim.get_time()
        
        
        
        
        
            
            
    """ run simulation """
    def run_sim(self) :
        sim = self.sim
        horizon = self.horizon
        
        while sim.get_time() < horizon :
            call = sim.get_next_action()
            call()
            
            
    """ after the simulation """
    def display(self) :
        recorder = self.recorder
        n = len( self.tape )
        T = recorder.T * np.arange( n )
        plt.plot( T, self.tape )
        plt.xlabel( 'Time elapsed' )
        plt.ylabel( 'Number of Demands Waiting' )
        
        
    def rate_observed(self) :
        # convenience
        horizon = self.horizon
        recorder = self.recorder
        dispatch = self.dispatch
        
        arrivalrate = totalrate( self.rategraph )
        total_demands = len( self.DEMANDS )
        nleft = len( dispatch.demands )
        
        print 'arrival rate (simulated, observed): %f, %f' % ( arrivalrate, total_demands / horizon )
        
        if True :
            # see what this does
            rate_observed = sum([ veh.notches for veh in self.vehicles ]) / self.horizon
        else :
            #overrate_est = float( nleft - preload ) / horizon
            take_only_last = .25 * horizon
            take_num = int( np.ceil( take_only_last / recorder.T ) )
            DY = float( self.tape[-1] - self.tape[-take_num] )
            DT = take_num * recorder.T
            overrate_est = float( DY ) / DT
            rate_observed = arrivalrate - overrate_est
        
        return rate_observed




def convert_complexity_and_servicerate( arg, sys_speed ) :
    return float( sys_speed ) / arg



if __name__ == '__main__' :
    import pickle
    from setiptah.roadearthmover.roadcplx import carryMileageRate, fetchMileageRate 
    
    # plotting
    import matplotlib as mpl
    mpl.rcParams['ps.useafm'] = True
    mpl.rcParams['pdf.use14corefonts'] = True
    mpl.rcParams['text.usetex'] = True
    
    font = {'family' : 'normal',
            'weight' : 'bold',
            'size'   : 22 }
    mpl.rc('font', **font)       # oh please, work!
    import matplotlib.pyplot as plt
    plt.close('all')
    
    
    
    
    # make the roadnet and rategraph
    
    #roadnet, rates = get_sim_setting()
    """ SIM PARAMETERS """
    if False :
        roadnet = testcases.RoadnetExamples.get( 'nesw' )
        for _,__,road, data in roadnet.edges_iter( keys=True, data=True ) :
            data['length'] = 5.
        roadset = [ road for _,__,road in roadnet.edges_iter( keys=True ) ]
        
        normrategraph = nx.DiGraph()
        # is it a "true zero" issue?
        if False :
            for road1, road2 in itertools.product( roadset, roadset ) :
                normrategraph.add_edge( road1, road2, rate=.001 )
        # add the meaningful rates
        normrategraph.add_edge( 'N', 'E', rate=1./5 )
        normrategraph.add_edge( 'W', 'E', rate=1./5 )
        normrategraph.add_edge( 'W', 'S', rate=3./5 )
    
    elif True :
        roadnet = roadprob.sampleroadnet()
        normrategraph = massprob.sample_rategraph( roadnet, normalize=True )
        
    else :
        roadnet = nx.MultiDiGraph()
        roadnet.add_edge( 0,1, 'LEFT', length=1. )
        roadnet.add_edge( 1,2, 'RIGHT', length=1. )
        normrategraph = nx.DiGraph()
        normrategraph.add_edge( 'LEFT', 'RIGHT', rate=1. )
        

    probe = RoadmapEMD()
    probe.horizon = 10000.
    
    complexity_computed = []
    complexity_estimated = []
    
    def showresults() :
        plt.scatter( complexity_computed, complexity_estimated )
        
    for t in range(1) :
        roadnet, rategraph = get_sim_setting( mu=2. )
        
        R = totalrate( rategraph )
        n_rategraph = scale_rates( rategraph, 1. / R )
        
        enroute_velocity = carryMileageRate( roadnet, n_rategraph )
        balance_velocity = fetchMileageRate( roadnet, n_rategraph )
        complexity = enroute_velocity + balance_velocity
        #complexity = moverscomplexity( roadnet, n_rategraph )
        
        
        for k in range(1) :
            numveh = np.random.randint(1,5+1)
            
            rate_predicted = convert_complexity_and_servicerate( complexity, numveh )
            simrates = scale_rates( n_rategraph, .99 * rate_predicted )
            
            probe.scenario( roadnet, simrates, numveh, 1. )
            
            probe.sim_init()
            probe.run_sim()
            rate_observed = probe.rate_observed()
            
            complexity_observed = convert_complexity_and_servicerate( rate_observed, numveh )
            
            complexity_computed.append( complexity )
            complexity_estimated.append( complexity_observed )
        
        
    showresults()
    plt.show()
    
    def saveresult( filename ) :
        data = {}
        data['complexity_estimated'] = complexity_estimated
        data['complexity_computed'] = complexity_computed
        
        pickle.dump( data, open( filename, 'w' ) )
        
