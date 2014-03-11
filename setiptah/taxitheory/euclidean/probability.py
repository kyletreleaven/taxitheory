

def averageDistance( samplearc, getTail, getHead, distance, N=100000 ) :
    """ trivial statistical mean algorithm """
    total = 0.
    for i in xrange(N) :
        arc = samplearc()
        s = getTail(arc)
        t = getHead(arc)
        total += distance( s, t )
        
    return float(total) / N










