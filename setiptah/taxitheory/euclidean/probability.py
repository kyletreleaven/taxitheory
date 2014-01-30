



def averageDistance( distr, distanceFunc, N=100000 ) :
    """ trivial statistical mean algorithm """
    for i in xrange(N) :
        s, t = distr.sampleODPair()
        total += distanceFunc(s,t)
    return float(total) / N










