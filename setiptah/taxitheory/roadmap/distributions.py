
import networkx as nx

import setiptah.roadgeometry.roadmap_basic as ROAD
import setiptah.roadgeometry.probability as roadprob

import setiptah

class Distribution : pass




def ACC2014Square() :
    roadmap = nx.MultiDiGraph()
    roadmap.add_edge(0,1,'N', length=1. )
    roadmap.add_edge(1,2,'E', length=1. )
    roadmap.add_edge(2,3,'S', length=1. )
    roadmap.add_edge(3,0,'W', length=1. )
    
    return roadmap
    

class ACC2014Distr(Distribution) : pass




class PairUniformRoadmap(Distribution) :
    def __init__(self, roadmap, length_attr='length' ) :
        self.roadmap = roadmap
        self.length_attr = length_attr
        
        self.distr = roadprob.UniformDist( self.roadmap, length_attr )
        
        # compute these
        self._meancarry = None
        self._meanfetch = None
        
        
    def sample(self) :
        x = self.distr.sample()
        y = self.distr.sample()
        return x, y
    
    def meancarry(self) : return self._meancarry
    
    def meanfetch(self) : return self._meanfetch
    
    def queueLengthFactor(self, rho ) :
        return np.power( 1 - rho, -2. )     # presumably...
    
    def origin(self) :
        _,__, road = self.roadmap.edges_iter( data=True ).next()
        return ROAD.RoadAddress( road, 0. )
    
    def distance(self, x, y ) :
        return ROAD.distance( self.roadmap, x, y, length=self.length_attr )
    
    
    