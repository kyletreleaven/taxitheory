
import itertools
import random

import numpy as np
import networkx as nx


def get_sim_setting( N=10, p=.3, mu=1., K=5, lam=1. ) :
    """
    get largest connected component of Erdos(N,p) graph
    with exponentially distr. road lengths (avg. mu);
    Choose k road pairs randomly and assign intensity randomly,
    exponential lam
    """
    g = nx.erdos_renyi_graph( N, p )
    g = nx.connected_component_subgraphs( g )[0]
    
    roadnet = nx.MultiDiGraph()
    
    def roadmaker() :
        for i in itertools.count() : yield 'road%d' % i, np.random.exponential( mu )
    road_iter = roadmaker()
    
    for i, ( u,v,data ) in enumerate( g.edges_iter( data=True ) ) :
        label, length = road_iter.next()
        roadnet.add_edge( u, v, label, length=length )
    
    rates = nx.DiGraph()
    ROADS = [ key for u,v,key in roadnet.edges_iter( keys=True ) ]
    for i in range( K ) :
        r1 = random.choice( ROADS )
        r2 = random.choice( ROADS )
        if not rates.has_edge( r1, r2 ) :
            rates.add_edge( r1, r2, rate=0. )
        
        data = rates.get_edge_data( r1, r2 )
        data['rate'] += np.random.exponential( lam )
        
    return roadnet, rates



