

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

