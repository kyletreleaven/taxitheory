
from setiptah.dyvehr.taxi import TaxiScheduler

import setiptah.roadgeometry.roadmap_basic as ROAD
import setiptah.vehrouting.roadsplice as roadcrane


class RoadMap_kCraneScheduler(TaxiScheduler) :
    def __init__(self, getTail, getHead, roadmap ) :
        self.getTail = getTail
        self.getHead = getHead
        
        self.roadmap = roadmap      # for kicks
        self.fhk = roadcrane.RoadMapFHK( self.roadmap )
        
        
    def distance(self, p, q ) : return self.fhk.distance( p, q )
    
    def __call__(self, demands, agentLocs ) :
        assign = self.fhk.kSPLICE( demands, agentLocs, self.getTail, self.getHead )
        
        # right... returns the indices... have to convert
        assign = { agent : [ demands[i] for i in seq ]
                  for agent, seq in assign.iteritems() }
        
        return assign




def sample_demands( T, rategraph, roadnet, rate='rate' ) :
    demands = []
    point_on = lambda road : roadprob.sample_onroad( road, roadnet, 'length' )
    for road1, road2, data in rategraph.edges_iter( data=True ) :
        n = np.random.poisson( data.get( rate, 0. ) * T )
        #newdems = [ demand( point_on( road1 ), point_on( road2 ) ) for i in range(n) ]
        newdems = [ ( point_on( road1 ), point_on( road2 ) ) for i in range(n) ]
        demands.extend( newdems )
        
    numdem = len( demands )
    print 'sampled %d' % numdem
    debug_input()
    
    times = T * np.random.rand(numdem)
    script = sorted( zip( times, demands ) )
    return script


