
import numpy as np
import scipy as sp
import scipy.optimize as opt


def planarOrder( rho ) :
    return -np.log( 1. - rho ) * np.power( 1. - rho, -2. )

def inversePlanarOrder( g ) :
    assert g >= 0.
    if g == 0. : return 0.
    # otherwise
    ohr = 1.
    while planarOrder( 1.-ohr ) <= g : ohr *= .5
    
    objective = lambda rho : planarOrder( rho ) - g
    return opt.bisect( objective, 1.-2*ohr, 1.-ohr )


def utilizationToRate( util, moverscplx, numveh=1, vehspeed=1. ) :
    rate = util * numveh * vehspeed / moverscplx
    return rate
    


#r = opt.bisect( lambda rho : G(rho) - g, 0.000001, .99999 )


if __name__ == '__main__' :
    import matplotlib.pyplot as plt
    plt.close('all')
    
    rho = np.linspace(0,1,500+2)[1:-1]
    F = planarOrder(rho)
    
    G = np.logspace(0,5,20)
    rhostar = [ inversePlanarOrder( g ) for g in G ]
    
    plt.plot(rho,F)
    plt.scatter( rhostar, G, marker='x' )
    plt.show()
    
    

