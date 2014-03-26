
import numpy as np
import networkx as nx

import setiptah.roadgeometry.roadmap_basic as ROAD
import setiptah.roadgeometry.probability as roadprob

import setiptah.roadearthmover.roadcplx as roadcplx
#import setiptah.roadearthmover.road_Ed as roadEd
#import setiptah.roadearthmover.roademd as roademd

from setiptah.taxitheory.distributions.interface import Distribution


class RoadmapDistribution(Distribution) :
    def __init__(self, roadmap, length_attr ) :
        #super(RoadmapDistribution,self).__init__()
        self.roadmap = roadmap
        self.length_attr = length_attr
    
    def origin(self) :
        _,__, road = self.roadmap.edges_iter( keys=True ).next()
        return ROAD.RoadAddress( road, 0. )
    
    def distance(self, x, y ) :
        return ROAD.distance( self.roadmap, x, y, weight=self.length_attr )
    
    def queueLengthFactor(self, rho ) :
        return np.power( 1 - rho, -2. )     # presumably...




def ACC2014Square() :
    roadmap = nx.MultiDiGraph()
    roadmap.add_edge(0,1,'N', length=1. )
    roadmap.add_edge(1,2,'E', length=1. )
    roadmap.add_edge(2,3,'S', length=1. )
    roadmap.add_edge(3,0,'W', length=1. )
    
    return roadmap




class ACC2014Distr(RoadmapDistribution) :
    def __init__(self) :
        roadmap = ACC2014Square()
        
        super(ACC2014Distr,self).__init__(roadmap, 'length' )
        
        rategraph = nx.DiGraph()
        rategraph.add_edge( 'N', 'E', rate=1./5 )
        rategraph.add_edge( 'W', 'E', rate=1./5 )
        rategraph.add_edge( 'W', 'S', rate=3./5 )
        
        self._meancarry = roadcplx.carryMileageRate( roadmap, rategraph )
        self._meanfetch = roadcplx.fetchMileageRate( roadmap, rategraph )
        
        # for sampler
        weights = { (r1,r2) : data.get( 'rate' )
                   for r1,r2, data in rategraph.edges_iter( data=True )
                   }
        #weights[ ('N','E') ] = 1./5
        #weights[ ('W','E') ] = 1./5
        #weights[ ('W','S') ] = 3./5
        self.wset = roadprob.WeightedSet(weights)
        
        
    def sample(self) :
        road1, road2 = self.wset.sample()
        x = roadprob.sample_onroad( road1, self.roadmap, self.length_attr )
        y = roadprob.sample_onroad( road2, self.roadmap, self.length_attr )
        
        return x,y
    
    def meancarry(self) : return self._meancarry
    
    def meanfetch(self) : return self._meanfetch
    
    
    def validate(self, numsamp=1000 ) :
        """ this was a quick function used to debug sampling """ 
        demands = [ self.sample() for i in xrange(numsamp) ]
        pairs = [ ( self.getTail(dem).road, self.getHead(dem).road )
                 for dem in demands ]
        
        data = {}
        for p in pairs :
            if p not in data : data[p] = 0.     # important
            data[p] += 1
            
        return { p : val / numsamp for p, val in data.iteritems() }




class PairUniformRoadmap(RoadmapDistribution) :
    def __init__(self, roadmap, length_attr='length' ) :
        super(PairUniformRoadmap,self).__init__(roadmap, length_attr)
        
        uniform = roadprob.UniformDist( self.roadmap, self.length_attr )
        self.distr = uniform
        
        # compute carry and fetch --- using roadmap movers complexity
        lendict = { road : data.get( self.length_attr, 1 )
                   for _,__, road, data in self.roadmap.edges_iter( keys=True, data=True )
                   }
        total = sum( lendict.values() )
        W = { road : roadlen / total
                   for road, roadlen in lendict.iteritems() }
        
        if False :
            W2 = { (r1,r2) : w1*w2
                  for r1,w1 in W.iteritems()
                  for r2,w2 in W.iteritems() }
            
            self._meancarry = roadEd.roadEd( self.roadmap, W2, length_attr=self.length_attr )
            
        else :
            rategraph = nx.DiGraph()
            for r1,w1 in W.iteritems() :
                for r2,w2 in W.iteritems() :
                    rategraph.add_edge( r1, r2, rate=w1*w2 )
                    
            self._meancarry = roadcplx.carryMileageRate( self.roadmap, rategraph )
            
        self._meanfetch = 0.
        
        
    def sample(self) :
        x = self.distr.sample()
        y = self.distr.sample()
        return x, y
    
    def meancarry(self) : return self._meancarry
    
    def meanfetch(self) : return self._meanfetch
    
    
    
__all__ = [
           'RoadmapDistribution',
           'ACC2014Square',
           'PairUniformRoadmap',
           'ACC2014Distr',
           ]
    
    
    
if __name__ == '__main__' :
    pass
    
    
    
    
    
    
    
    
    
    
    
    