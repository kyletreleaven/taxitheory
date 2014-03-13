#!/usr/bin/python

import itertools
import sqlite3

import PyQt4.QtCore as core, PyQt4.QtGui as gui

import setiptah.taxitheory.sql as mysql
import setiptah.taxitheory.euclidean.distributions as distributions

DBFILENAME = None


# this was just for fun
ALPHABET = lambda : ( c for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' )

def ALPHAENUM() :
    for digits in itertools.count(1) :
        parallel = [ ALPHABET() for k in xrange(digits) ]
        for letters in itertools.product( *parallel ) :
            yield ''.join( letters )


class ExperimentsWidget(gui.QWidget) :
    def __init__(self, parent=None ) :
        super(ExperimentsWidget,self).__init__(parent)
        
        self.populateUI()
        self.connectUI()
        self.layoutUI()
        
        self.dbconn = sqlite3.connect(DBFILENAME)
        self.populateForm()
        
        
    def populateUI(self) :
        self.currentExperiment = gui.QComboBox()
        self.newExperiment = gui.QPushButton('New')
        self.saveExperiment = gui.QPushButton('Save')
        
        self.currDistr = gui.QComboBox()
        self.currNumveh = gui.QSpinBox()
        self.currSpeed = gui.QDoubleSpinBox()
        
        self.currRate = gui.QDoubleSpinBox()
        self.currRate.setMaximum(100.)
        self.currRate.setDecimals(10)
        
        self.currUtil = gui.QDoubleSpinBox()
        self.currUtil.setMaximum(10.)
        self.currUtil.setDecimals(10)
        self.currUtil.setSingleStep(.01)
        self.currUtil.setValue(0.)
        
        self.currLengthFactor = gui.QDoubleSpinBox()
        self.currLengthFactor.setMaximum(10000.)
        
        self.currPolicy = gui.QComboBox()
        
        self.initDur = gui.QDoubleSpinBox()
        self.initDur.setValue(50.)
        self.timeFactor = gui.QDoubleSpinBox()
        self.timeFactor.setValue(2.)
        self.threshFactor = gui.QDoubleSpinBox()
        self.threshFactor.setValue(1.1)
        self.exploitRatio = gui.QDoubleSpinBox()
        self.exploitRatio.setValue(1.)
        
        self.rateLabel = gui.QRadioButton('Arrival Rate')
        self.utilLabel = gui.QRadioButton('Utilization')
        self.factorLabel = gui.QRadioButton('Length Factor')
        
    def connectUI(self) :
        self.newExperiment.clicked.connect( self.doNewExperiment )
        self.saveExperiment.clicked.connect( self.doSaveExperiment )
        
        experimentChanged = self.currentExperiment.currentIndexChanged
        experimentChanged.connect( self.activateExperiment )
        
        self.fixStat = gui.QButtonGroup()
        self.fixStat.addButton( self.rateLabel )
        self.fixStat.addButton( self.utilLabel )
        self.fixStat.addButton( self.factorLabel )
        #self.fixStat.buttonClicked.connect( self.ensureFixedStat )    # don't!
        self.utilLabel.click()  # to check it.
        
        # these three things should re-compute rate/util/factor with a fixture
        self.currDistr.currentIndexChanged.connect( self.ensureTuning )
        self.currNumveh.valueChanged.connect( self.ensureTuning )
        self.currSpeed.valueChanged.connect( self.ensureTuning )
        
        # should re-compute with specific fixture
        self.currRate.valueChanged.connect( self.ensureRate )
        self.currUtil.valueChanged.connect( self.ensureUtil )
        self.currLengthFactor.valueChanged.connect( self.ensureFactor )
        
        
        
    def layoutUI(self) :
        file, setup, tuning, timing = [ gui.QHBoxLayout() for k in xrange(4) ]
        
        file.addWidget( gui.QLabel('Experiment') )
        file.addWidget( self.currentExperiment )
        file.addWidget( self.newExperiment )
        file.addWidget( self.saveExperiment )
        #
        setup.addWidget( gui.QLabel('Distribution') )
        setup.addWidget( self.currDistr )
        setup.addWidget( gui.QLabel('Fleet Size') )
        setup.addWidget( self.currNumveh )
        setup.addWidget( gui.QLabel('Fleet Speed') )
        setup.addWidget( self.currSpeed )
        #
        tuning.addWidget( self.rateLabel )
        tuning.addWidget( self.currRate )
        tuning.addWidget( self.utilLabel )
        tuning.addWidget( self.currUtil )
        tuning.addWidget( self.factorLabel )
        tuning.addWidget( self.currLengthFactor )
        
        policyLayout = gui.QHBoxLayout()
        policyLayout.addWidget( gui.QLabel('Policy') )
        policyLayout.addWidget( self.currPolicy )
        
        timing.addWidget( gui.QLabel('Initial Dur') )
        timing.addWidget( self.initDur )
        timing.addWidget( gui.QLabel('Time Factor') )
        timing.addWidget( self.timeFactor )
        timing.addWidget( gui.QLabel('Thresh Factor') )
        timing.addWidget( self.threshFactor )
        timing.addWidget( gui.QLabel('Exploit Ratio') )
        timing.addWidget( self.exploitRatio )
        
        layout = gui.QVBoxLayout()
        layout.addLayout( file )
        layout.addLayout( setup )
        layout.addLayout( tuning )
        layout.addLayout( policyLayout )
        layout.addLayout( timing )
        
        self.setLayout( layout )
        
        
        
    def populateForm(self) :
        self.populateDistributions()
        self.populateExperiments()
        
    def populateDistributions(self) :
        self.currDistr.clear()
        self.currDistr.addItems( distributions.distributions.keys() )
        
    def populateExperiments(self) :
        self.currentExperiment.clear()
        mysql.prepareDatabase( self.dbconn, DEBUG=False )
        
        cur = self.dbconn.cursor()
        for id, in cur.execute('SELECT id FROM experiments') :
            self.currentExperiment.addItem( str(id) )
        #self.activateExperiment()
        
        
    def activateExperiment(self) :
        # download experiment data from DB
        id = self.currentExperiment.currentText()
        e = mysql.ExperimentRecord.fromID( self.dbconn, int(id) )
        
        index = self.currDistr.findText( e.distrib_key )
        self.currDistr.setCurrentIndex( index )
        self.currNumveh.setValue( e.numveh )
        self.currSpeed.setValue( e.vehspeed )
        
        self.currRate.setValue( e.arrivalrate )
        # update may be handled by previous line
        # self.ensureRate()
        
        index = self.currPolicy.findText( e.distrib_key )
        self.currPolicy.setCurrentIndex( index )
        
        self.initDur.setValue( e.init_dur )
        self.timeFactor.setValue( e.time_factor )
        self.threshFactor.setValue( e.thresh_factor )
        self.exploitRatio.setValue( e.exploit_ratio )
        
        
        
    def doNewExperiment(self) :
        e = self._prepareRecord()
        fmt = e.sqlInsert()
        tup = e.sqlTuple()
        
        print fmt, tup
        
        cur = self.dbconn.cursor()
        cur.execute( fmt, tup )
        self.dbconn.commit()
        
        self.populateExperiments()
        
    def doSaveExperiment(self) :
        e = self._prepareRecord()
        fmt = e.sqlUpdate()
        
        id = int( self.currentExperiment.currentText() )
        tup = e.sqlTuple() + (id,)
        
        print fmt, tup
        
        cur = self.dbconn.cursor()
        cur.execute( fmt, tup )
        self.dbconn.commit()
        
        
    def _prepareRecord(self) :
        e = mysql.ExperimentRecord()
        e.arrivalrate = self.currRate.value()
        e.numveh = self.currNumveh.value()
        e.vehspeed = self.currSpeed.value()
        
        e.init_dur = self.initDur.value()
        e.time_factor = self.timeFactor.value()
        e.thresh_factor = self.threshFactor.value()
        e.exploit_ratio = self.exploitRatio.value()
        
        e.distrib_key = unicode( self.currDistr.currentText() )
        e.policy_key = unicode( self.currPolicy.currentText() )
        
        return e
        
    def ensureFixedStat(self) :
        """ this is dumb, don't do this """
        self.currRate.setEnabled( not self.rateLabel.isChecked() )
        self.currUtil.setEnabled( not self.utilLabel.isChecked() )
        self.currLengthFactor.setEnabled( not self.factorLabel.isChecked() )
        
    def _setTuning(self, rate, util, factor ) :
        self.currRate.setValue( rate )
        self.currUtil.setValue( util )
        self.currLengthFactor.setValue( factor )

    def ensureRate(self) :
        numveh = self.currNumveh.value()
        vehspeed = self.currSpeed.value()
        distr_key = self.currDistr.currentText()
        distr = distributions.distributions[ unicode(distr_key) ]
        moverscplx = distr.meancarry() + distr.meanfetch()
        
        rate = self.currRate.value()
        rho = rate * moverscplx / numveh / vehspeed
        factor = distr.queueLengthFactor( rho )
        
        self._setTuning( rate, rho, factor )
        
    def ensureUtil(self) :
        numveh = self.currNumveh.value()
        vehspeed = self.currSpeed.value()
        distr_key = self.currDistr.currentText()
        distr = distributions.distributions[ unicode(distr_key) ]
        moverscplx = distr.meancarry() + distr.meanfetch()
        
        rho = self.currUtil.value()
        rate = rho * numveh * vehspeed / moverscplx
        factor = distr.queueLengthFactor( rho )
        
        self._setTuning( rate, rho, factor )
        
    def ensureFactor(self) :
        numveh = self.currNumveh.value()
        vehspeed = self.currSpeed.value()
        distr_key = self.currDistr.currentText()
        distr = distributions.distributions[ unicode(distr_key) ]
        moverscplx = distr.meancarry() + distr.meanfetch()
        
        factor = self.currLengthFactor.value()
        rho = distr.inverseQueueLengthFactor( factor )
        rate = rho * numveh * vehspeed / moverscplx
        
        self._setTuning( rate, rho, factor )
        
    def ensureTuning(self, reference=None ) :
        """ use radio buttons to dispatch tuning """
        if self.rateLabel.isChecked() :
            self.ensureRate()
        elif self.utilLabel.isChecked() :
            self.ensureUtil()
        elif self.factorLabel.isChecked() :
            self.ensureFactor()
            
        else :
            raise 'no active radio button'
        
        
        
        
        
        
        
        
    
    
    
if False :
    class ExperimentRecord :
        def __init__(self) :
            self.arrivalrate = 1.
            self.numveh = 1
            self.vehspeed = 1.
            
            self.init_dur = 50.
            self.time_factor = 2.
            self.thresh_factor = 1.1
            self.exploit_ratio = 1.
            
            self.distrib_key = 'UNIFORM2'
            self.policy_key = 'STACKERCRANE'
            
        








if __name__ == '__main__' :
    import sys
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--dbfile', type=str, default='mydata.sqlite' )
    
    args, unknown_args = parser.parse_known_args()
    DBFILENAME = args.dbfile
    
    
    
    app = gui.QApplication( unknown_args )
    
    w = ExperimentsWidget()
    w.show()
    
    sys.exit( app.exec_() )
    
    
    
    
