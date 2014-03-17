

import itertools

import numpy as np


def enumerate_subcubic_cells( N, dim ) :
    """
    Enumerate cell indices of a hyper cube;
    dimension dim, N divisions per side
    """
    cells = itertools.product( *[ xrange(N) for i in xrange(dim) ] )
    return cells


def enumerate_subcubic_centroids( N, dim ) :
    origin = .5 * np.ones(dim) / N - .5
    for tup in enumerate_subcubic_cells( N, dim ) :
        #print tup
        
        coord = origin + [ float(i)/N for i in tup ]
        yield coord
        
        
def subcubic_volume( N, dim ) :
    return np.power( N, -float(dim) )





def average_distance_between_cubes( x1, N ) :
    """
    compute the average distance between
    a point in one unity hyper-cube and a point in another one
    separated by the vector x1 (also determines dimension)
    """
    dim = len( x1 )
    
    if True :
        total = 0.
        for x in enumerate_subcubic_centroids(N,dim) :
            for y in enumerate_subcubic_centroids(N,dim) :
                print x, y
                total += np.linalg.norm( x1 + y - x )
                
        return subcubic_volume(N,dim) * total
    
    else :
        chords = ( x1 + y - x
                   for x in enumerate_subcubic_centroids(N,dim)
                   for y in enumerate_subcubic_centroids(N,dim) )
        lengths = ( np.linalg.norm(c) for c in chords )
        
        return subcubic_volume( N, dim ) * sum( lengths )
    
    
    

if __name__ == '__main__' :
    import matplotlib.pyplot as plt
    
    coords = [ c for c in enumerate_subcubic_centroids( 100, 2 ) ]
    X = [ x for x,y in coords ]
    Y = [ y for x,y in coords ]
    plt.scatter( X, Y )
    
    M = average_distance_between_cubes( np.zeros(2), 100 )
    print M
    
    
    
    