#!/usr/bin/python

from PyQt4 import QtGui, QtCore

#from numpy import arange, sin, pi
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class MplCanvas(FigureCanvas) :
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self._fig = Figure(figsize=(width, height), dpi=dpi)
        FigureCanvas.__init__(self, self._fig )
        
        # this could be really handy!
        cid = self._fig.canvas.mpl_connect('button_press_event', self.onclick )
        self._canvasid = cid
        # to disconnect, e.g.,
        #self._fig.canvas.mpl_disconnect( self._canvasid )
        
        self.setParent(parent)
        
        # seems reasonable
        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        # what's this do?
        FigureCanvas.updateGeometry(self)
        
    def getFigure(self) : return self._fig
    
    def onclick(self, event ):
        # little click demo
        fmt = 'button=%d, x=%d, y=%d, xdata=%f, ydata=%f'
        data = event.button, event.x, event.y, event.xdata, event.ydata
        
        #print fmt % data




if __name__ == '__main__' :
    import sys
    import numpy as np
    import matplotlib.pyplot as plt
    
    class Form(QtGui.QDialog) :
        def __init__(self, parent=None ) :
            super(Form,self).__init__(parent)
            
            self.canvas = MplCanvas()
            
            layout = QtGui.QVBoxLayout()
            layout.addWidget( self.canvas )
            
            self.setLayout( layout )
            
            self.setWindowTitle('My MPL Canvas Demo')
            
            
    app = QtGui.QApplication( sys.argv )
    form = Form()
    
    fig = form.canvas.getFigure()
    
    t = np.linspace(0,1,100)
    x = np.sin(2*np.pi*t)
    
    ax = fig.add_subplot(1,1,1)
    ax.plot(t,x)
    form.canvas.draw()
    
    form.show()
    
    sys.exit( app.exec_() )
            

