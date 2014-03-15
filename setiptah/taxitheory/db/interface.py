

__all__ = [ 'ExperimentDatabase', 'ExperimentRecord', 'DemandRecord' ]

class ExperimentDatabase :
    
    def clear(self) :
        raise NotImplementedError('abstract')
    
    def addExperiment(self, experiment ) :
        raise NotImplementedError('abstract')



class ExperimentRecord :
    def __init__(self) :
        self.uniqueID = None
        self.status = None
        
        self.arrivalrate = None
        self.numveh = None
        self.vehspeed = None
        
        self.init_dur = None
        self.time_factor = None
        self.thresh_factor = None
        self.exploit_ratio = None
        
        self.distrib_key = None
        self.policy_key = None
        
    def setDistribution(self, distr_key ) :
        self.distrib_key = distr_key
        
    def setFleetSize(self, size ) :
        self.numveh = size
        
    def setFleetSpeed(self, speed ) :
        self.vehspeed = speed
        
    def setRate(self, rate ) :
        self.arrivalrate = rate
        
    def setInitialDuration(self, duration ) :
        self.init_dur = duration
        
    def setTimeDilation(self, ratio ) :
        self.time_factor = ratio
        
    def setGrowthThreshold(self, thresh ) :
        self.thresh_factor = thresh
        
    def setExploitRatio(self, ratio ) :
        self.exploit_ratio = ratio
        
    def setPolicy(self, policy_key ) :
        self.policy_key = policy_key
        
    def getStatus(self) :
        return self.status






class DemandRecord :
    def __init__(self) :
        #self.experimentID = None
        
        self.origin = None
        self.destination = None
        
        self.arrival_time = None
        self.embark_time = None
        self.delivery_time = None
        
        self.wait_dur = None
        self.carry_dur = None
        self.system_dur = None
        




