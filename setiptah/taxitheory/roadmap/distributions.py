
import numpy as np
import networkx as nx

import setiptah.roadgeometry.roadmap_basic as ROAD
import setiptah.roadgeometry.probability as roadprob

import setiptah.roadearthmover.road_Ed as roadEd
import setiptah.roadearthmover.roademd as roademd

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


class ACC2014Distr(RoadmapDistribution) : pass




class PairUniformRoadmap(RoadmapDistribution) :
    def __init__(self, roadmap, length_attr='length' ) :
        super(PairUniformRoadmap,self).__init__(roadmap, length_attr)
        
        uniform = roadprob.UniformDist( self.roadmap, self.length_attr )
        self.distr = uniform
        
        # compute these --- using roadmap movers complexity
        lendict = { road : data.get( self.length_attr, 1 )
                   for _,__, road, data in self.roadmap.edges_iter( keys=True, data=True )
                   }
        total = sum( lendict.values() )
        W = { road : roadlen / total
                   for road, roadlen in lendict.iteritems() }
        
        W2 = { (r1,r2) : w1*w2
              for r1,w1 in W.iteritems()
              for r2,w2 in W.iteritems() }
        
        self._meancarry = roadEd.roadEd( self.roadmap, W2, length_attr=self.length_attr )
        
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
    
    
    
    
    
    
    
    
    
    
    
    