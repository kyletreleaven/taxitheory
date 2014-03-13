
import numpy as np

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
    
    
class PairUniform3(Distribution) :
    def sample(self) :
        x = np.random.rand(3)
        y = np.random.rand(3)
        return x, y
    
    def meancarry(self) :
        return 0.6617071822
    
    def meanfetch(self) :
        return 0.       # EMD=0.
    
    
    
    


