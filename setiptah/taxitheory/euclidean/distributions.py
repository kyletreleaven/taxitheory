
import random, itertools

import numpy as np

from setiptah.taxitheory.distributions.interface import Distribution
import setiptah.taxitheory.euclidean.constants as eucconst


class EuclideanDistribution(Distribution) :
    DIM = None     # needs to be overwritten
    
    def origin(self) : return np.zeros(self.DIM)
    
    def distance(self, x, y ) : return np.linalg.norm( y - x )
    
    @classmethod
    def uniformcube_centered(cls, dim=None ) :
        if dim is None : dim = cls.DIM
        return np.random.rand(dim) - .5
    
    @classmethod
    def uniformsphere(cls, dim=None ) :
        while True :
            coord = 2. * cls.uniformcube_centered(dim)
            #coord = 2. * np.random.rand(dim) - 1.
            if np.linalg.norm(coord) <= 1. : break
            
        return coord
    
    
class PlanarDistribution(EuclideanDistribution) :
    DIM = 2
    
    def queueLengthFactor(self, rho ) :
        return -np.log( 1. - rho ) * np.power( 1. - rho, -2. )
    
    def visualize(self, samples=None ) :
        import matplotlib.pyplot as plt
        fig = plt.figure()
        
        if samples is None : samples = 1000
        
        ax = fig.add_subplot(1,1,1)
        
        def split( points2 ) :
            temp = [ p for p in points2 ]
            X = [ x for x,y in temp ]
            Y = [ y for x,y in temp ]
            return X, Y
        
        def scatter( ax, demands ) :
            T = ( self.getTail(dem) for dem in demands )
            X1, Y1 = split(T)
            
            H = ( self.getHead(dem) for dem in demands )
            X2, Y2 = split(H)
            
            ax.scatter( X1, Y1, color='red' )
            ax.scatter( X2, Y2, color='blue' )
            
        demands = [ self.sample() for i in xrange(samples) ]
        scatter( ax, demands )
        #ax.set_aspect('equal')
        
        plt.show()

    
class CubicDistribution(EuclideanDistribution) :
    DIM = 3
    
    def queueLengthFactor(self, rho ) :
        return np.power( 1. - rho, -3. )
    
    def visualize(self, samples=None ) :
        import matplotlib.pyplot as plt
        fig = plt.figure()
        
        if samples is None : samples = 1000
        
        from mpl_toolkits.mplot3d import Axes3D     # do I need?
        ax = fig.add_subplot(111, projection='3d')
        
        def split( points3 ) :
            temp = [ p for p in points3 ]
            X = [ x for x,y,z in temp ]
            Y = [ y for x,y,z in temp ]
            Z = [ z for x,y,z in temp ]
            return X, Y, Z
        
        def scatter( ax, demands ) :
            T = ( self.getTail(dem) for dem in demands )
            H = ( self.getHead(dem) for dem in demands )
            
            X1, Y1, Z1 = split(T)
            X2, Y2, Z2 = split(H)
            
            ax.scatter( X1, Y1, Z1, color='red' )
            ax.scatter( X2, Y2, Z2, color='blue' )
        
        demands = [ self.sample() for i in xrange(samples) ]
        scatter( ax, demands )
        #ax.set_aspect('equal')
        
        plt.show()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
""" The Separably I.I.D, Uniform, and Cubic Distributions """

class PairUniform2(PlanarDistribution) :
    def sample(self) :
        x = np.random.rand(self.DIM)
        y = np.random.rand(self.DIM)
        return x, y
    
    def meancarry(self) :
        # http://mathworld.wolfram.com/HypercubeLinePicking.html
        return 0.5214054331
    
    def meanfetch(self) :
        return 0.       # EMD=0.
    
    
    
    
    
class PairUniform3(CubicDistribution) :
    def sample(self) :
        x = np.random.rand(self.DIM)
        y = np.random.rand(self.DIM)
        return x, y
    
    def meancarry(self) :
        # http://mathworld.wolfram.com/HypercubeLinePicking.html
        return 0.6617071822
    
    def meanfetch(self) :
        return 0.       # EMD=0.
    
    def boundConstants(self) :
        """
        origin-fair and general lower bounds;
        EMD = 0, so they are actually *valid*  
        """
        # \gamma_d
        LBConst = eucconst.GAMMA3
        # \int_\env \den^{(d-1)/d} \ dx
        integral_fair = 1.
        # \int_\env \den^{d/(d+1)} \ dx
        integral_general = 1.
        
        carry = self.meancarry()
        
        """
        Stacker Crane policy upper bound
        """
        UBConst = eucconst.BETAMATCH3
        pow = lambda a,d : np.power(a,d)
        
        bounds = {}
        bounds['lower fair'] = pow( LBConst * integral_fair, 3. ) / pow( carry, 2. )
        bounds['lower general'] = pow(LBConst,3.) * pow(integral_fair,4.) / pow(carry,2.)
        bounds['upper'] = pow( UBConst * integral_fair, 3. ) / pow( carry, 2. )
        
        return bounds
    
    
    
    
""" TAC2013? Distributions """
    
class Cocentric3_1_2(CubicDistribution) :
    R = 2.
    r = 1.
    
    def sample(self) :
        x = self.r * self.uniformsphere(3)
        y = self.R * self.uniformsphere(3)
        return x, y
    
    def meancarry(self) :
        # best estimate from monte carlo (montecarlo.py), with
        # ORIGSRADIUS = 2. and DESTSRADIUS = 1.
        return 1.6479
        
    def meanfetch(self) :
        return (3./4) * ( self.R - self.r )
    
    def boundConstants(self) :
        """ only upper bounds are valid """
        """
        Stacker Crane policy upper bound
        """
        UBConst = eucconst.BETAMATCH3
        pow = lambda a,d : np.power(a,d)
        
        # see thesis, special bounds appendix
        integral_fair = pow( (4./3)*np.pi * self.r, 1./3 )
        integral_fair_optimistic = pow( (4./3)*np.pi, 1./3 ) * self.r * pow( self.r / self.R, 2. )
        moverscplx = self.meancarry() + self.meanfetch()
        
        bounds = {}
        bounds['upper'] = pow( UBConst * integral_fair, 3. ) / pow( moverscplx, 2. )
        bounds['upper conjecture'] = pow( UBConst * integral_fair_optimistic, 3. ) / pow( moverscplx, 2. )
        
        #bounds = {}
        return bounds
    
    
class XO_X_O(CubicDistribution) :
    LEFT = np.array([ -4, 0, 0 ])
    MIDDLE = np.array([ -2, 0, 0 ])
    RIGHT = np.array([ 2, 0, 0 ])
    
    def sample(self) :
        x = random.choice([ self.LEFT, self.MIDDLE ])
        x = x + self.uniformcube_centered()
        
        y = random.choice([ self.LEFT, self.RIGHT ])
        y = y + self.uniformcube_centered()
        
        return x,y
        
    def meancarry(self) :
        return 3.205        # Monte Carlo
        # return 3.2        # another trial
        
    def meanfetch(self) :
        return .5 * 4.
    
    def boundConstants(self) :
        """ only upper bounds are valid """
        """
        Stacker Crane policy upper bound
        """
        UBConst = eucconst.BETAMATCH3
        moverscplx = self.meancarry() + self.meanfetch()
        
        pow = lambda a,d : np.power(a,d)
        
        # see thesis, special bounds appendix
        integral_fair_optimistic = pow( 1./2, 2./3 )
        integral_fair = 2. * integral_fair_optimistic
        
        bounds = {}
        bounds['upper'] = pow( UBConst * integral_fair, 3. ) / pow( moverscplx, 2. )
        bounds['upper conjecture'] = pow( UBConst * integral_fair_optimistic, 3. ) / pow( moverscplx, 2. )
        
        #bounds = {}
        return bounds
        
        
        
class X_XO_O(CubicDistribution) :
    pass
    
    
""" TODO: port over those bastards from DynPDP """




def utilizationToRate( util, moverscplx, numveh=1, vehspeed=1. ) :
    rate = util * numveh * vehspeed / moverscplx
    return rate






__all__ = [
           'EuclideanDistribution',
           'PlanarDistribution',
           'CubicDistribution',
           'PairUniform2',
           'PairUniform3',
           'Cocentric3_1_2',
           'XO_X_O',
           ]



if __name__ == '__main__' :
    import matplotlib.pyplot as plt
    plt.close('all')
    
    #distr = distributions['PairUniform2']
    distr = PairUniform2()
    
    rho = np.linspace(0,1,500+2)[1:-1]
    F = distr.queueLengthFactor(rho)
    
    G = np.logspace(0,5,20)
    rhostar = [ distr.inverseQueueLengthFactor( g ) for g in G ]
    
    plt.plot(rho,F)
    plt.scatter( rhostar, G, marker='x' )
    
    distr.visualize()
    
    plt.show()
    
    












