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
        self.layoutUI()
        self.connectUI()
        
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
        self.currUtil = gui.QDoubleSpinBox()
        self.currLengthFactor = gui.QDoubleSpinBox()
        
        self.currPolicy = gui.QComboBox()
        
        self.initDur = gui.QDoubleSpinBox()
        self.initDur.setValue(50.)
        self.timeFactor = gui.QDoubleSpinBox()
        self.timeFactor.setValue(2.)
        self.threshFactor = gui.QDoubleSpinBox()
        self.threshFactor.setValue(1.1)
        self.exploitRatio = gui.QDoubleSpinBox()
        self.exploitRatio.setValue(1.)
        
        self.fixStat = gui.QButtonGroup()
        self.rateLabel = gui.QRadioButton('Arrival Rate')
        self.utilLabel = gui.QRadioButton('Utilization')
        self.factorLabel = gui.QRadioButton('Length Factor')
        self.fixStat.addButton( self.rateLabel )
        self.fixStat.addButton( self.utilLabel )
        self.fixStat.addButton( self.factorLabel )
        
        
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
        
        
    def connectUI(self) :
        self.newExperiment.clicked.connect( self.doNewExperiment )
        self.saveExperiment.clicked.connect( self.doSaveExperiment )
        
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
            
        self.activateExperiment()
        
    def activateExperiment(self) :
        # download experiment data from DB
        pass
    
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
    
    
    
    
