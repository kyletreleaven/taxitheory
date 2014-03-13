#!/usr/bin/python
import PyQt4.QtCore as core, PyQt4.QtGui as gui

DBFILENAME = None


class ExperimentsWidget(gui.QWidget) :
    def __init__(self, parent=None ) :
        super(ExperimentsWidget,self).__init__(parent)
        
        self.label = gui.QLabel('My Label, dawg.')
        layout = gui.QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)





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
    
    
    
    
