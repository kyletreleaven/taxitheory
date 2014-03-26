
import scipy.optimize as opt


class Distribution(object) :
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
    
    def horizontalAxisLabel(self) :
        return None
    
    def boundConstants(self) :
        return {}
    
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
    
    