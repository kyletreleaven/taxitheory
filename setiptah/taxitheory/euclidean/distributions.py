
import numpy as np
import scipy.optimize as opt

""" TODO: port over those bastards from DynPDP """


class Distribution :
    def sample(self) :
        raise NotImplementedError('abstract')
    
    def getTail(self, pair ) :
        return pair[0]
    
    def getHead(self, pair ) :
        return pair[1]
    
    def meancarry(self) :
        raise NotImplementedError('abstract')
    
    def meanfetch(self) :
        raise NotImplementedError('abstract')
    
    def queueLengthFactor(self, rho ) :
        raise NotImplementedError('abstract')
    
    def inverseQueueLengthFactor(self, g ) :
        """
        comput rho to achieve a certain queue length multiplier;
        assumes, rightfully, monotonicity
        """
        assert g >= 0.
        if g == 0. : return 0.
        # otherwise
        ohr = 1.
        while self.queueLengthFactor( 1.-ohr ) <= g : ohr *= .5
        
        objective = lambda rho : self.queueLengthFactor( rho ) - g
        return opt.bisect( objective, 1.-2*ohr, 1.-ohr )

    
    
# Uniform Statistics from:
# http://mathworld.wolfram.com/HypercubeLinePicking.html

class PairUniform2(Distribution) :
    def sample(self) :
        x = np.random.rand(2)
        y = np.random.rand(2)
        return x, y
    
    def meancarry(self) :
        return 0.5214054331
    
    def meanfetch(self) :
        return 0.       # EMD=0.
    
    def queueLengthFactor(self, rho ) :
        return -np.log( 1. - rho ) * np.power( 1. - rho, -2. )
    
    
    def origin(self) :
        return np.zeros(2)
    
    def distance(self, x, y ) :
        return np.linalg.norm(y-x)
    

    
class PairUniform3(Distribution) :
    def sample(self) :
        x = np.random.rand(3)
        y = np.random.rand(3)
        return x, y
    
    def meancarry(self) :
        return 0.6617071822
    
    def meanfetch(self) :
        return 0.       # EMD=0.
    
    def queueLengthFactor(self, rho ) :
        return np.power( 1. - rho, -3. )
    
    
    def origin(self) :
        return np.zeros(2)
    
    def distance(self, x, y ) :
        return np.linalg.norm(y-x)

    
    
distributions = {}
distributions['PairUniform2'] = PairUniform2()
distributions['PairUniform3'] = PairUniform3()




def utilizationToRate( util, moverscplx, numveh=1, vehspeed=1. ) :
    rate = util * numveh * vehspeed / moverscplx
    return rate




if __name__ == '__main__' :
    import matplotlib.pyplot as plt
    plt.close('all')
    
    distr = distributions['PairUniform2']
    
    rho = np.linspace(0,1,500+2)[1:-1]
    F = distr.queueLengthFactor(rho)
    
    G = np.logspace(0,5,20)
    rhostar = [ distr.inverseQueueLengthFactor( g ) for g in G ]
    
    plt.plot(rho,F)
    plt.scatter( rhostar, G, marker='x' )
    plt.show()
    
    












