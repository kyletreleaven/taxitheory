
import numpy as np
import scipy.optimize as opt

""" TODO: port over those bastards from DynPDP """


class Distribution :
    def __init__(self) :
        raise NotImplementedError('abstract')
    
    def sample(self) :
        raise NotImplementedError('abstract')
    
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
        while planarOrder( 1.-ohr ) <= g : ohr *= .5
        
        objective = lambda rho : planarOrder( rho ) - g
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
    
    
    
distributions = {}
distributions['PairUniform2'] = PairUniform2
distributions['PairUniform3'] = PairUniform3



