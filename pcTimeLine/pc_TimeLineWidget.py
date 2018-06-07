#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from Qt import QtGui, QtCore,QtWidgets

styleSheet = """

QSlider,QSlider:disabled,QSlider:focus     {  
                          background: qcolor(0,0,0,0);   }

QSlider:item:hover    {   background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #ffa02f, stop: 1 #eaa553);
                          color: #000000;              }

QWidget:item:selected {   background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #ffa02f, stop: 1 #d7801a);      }

 QSlider::groove:horizontal {
 
    border: 1px solid #999999;
    background: qcolor(0,0,0,0);
 }
QSlider::handle:horizontal {
    background:  qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(255,160,47, 141), stop:0.497175 rgba(255,160,47, 200), stop:0.497326 rgba(255,160,47, 200), stop:1 rgba(255,160,47, 147));
    width: 3px;
 } 
"""

class PC_timeline(QtWidgets.QSlider):
    def __init__(self, parent,*args):
        super(PC_timeline, self).__init__(parent=parent,*args)
        self.parent = parent
        self.cachedFrmaes = []
        self.missingFrames=[]
        self.hover = False
        self.hoverPos = None
        self.PressPos = None
        self.MovePos = None
        self.setRange(0,30)
        self.origMax = self.maximum()
        self.oriMin = self.minimum()
        self.setOrientation(QtCore.Qt.Horizontal)
        self.setStyleSheet(styleSheet)
        self.setMouseTracking(True)
        self.setPageStep(1)
        self.setMinimumSize(1, 40)
        self.installEventFilter(self)
    def setRange(self,min,max,setOrig=True):
        if setOrig:
            self.origMax = max
            self.oriMin = min
        return super(PC_timeline, self).setRange( min, max)
    def setCached(self,cached):
        self.cachedFrmaes = cached
    def setMissing(self,missing):
        self.missingFrames = missing        
    def paintEvent(self, event):

        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawWidget(qp)
        qp.end()        
        super(PC_timeline, self).paintEvent(event)
    def drawWidget(self, qp):
        font = QtGui.QFont('Serif', 7, QtGui.QFont.Light)
        qp.setFont(font)

        w = self.width()
        h = self.height()
        nb =  (self.maximum()-self.minimum())
        fStep = float(w) / nb
        step = max(1,int(round(fStep)))
        
        pen = QtGui.QPen(QtGui.QColor(200, 200, 200), 1, 
            QtCore.Qt.SolidLine)
            
        qp.setPen(pen)
        qp.setBrush(QtCore.Qt.NoBrush)
        #qp.drawRect(0, 0, w-50, h-50)
        
        pxNb = int(round((nb+1)*step))
        r = range(self.minimum(),self.maximum()+1,1)
        metrics = qp.fontMetrics()
        fh = metrics.height()      
        for e,i in enumerate(range(0,pxNb, step)):
            pos = self.style().sliderPositionFromValue(self.minimum(),self.maximum(),r[e],self.width())
            half = h/2
            if r[e] in self.cachedFrmaes:
                qp.setPen(QtGui.QColor(0, 255, 0))
                qp.setBrush(QtGui.QColor(0, 255, 0))
                qp.drawRect(pos-(fStep/2),half+5, fStep, 1.5)  
                qp.setPen(pen)
                qp.setBrush(QtCore.Qt.NoBrush)
            elif r[e] in self.missingFrames:
                qp.setPen(QtGui.QColor(255, 0, 0))
                qp.setBrush(QtGui.QColor(255, 0, 0))
                qp.drawRect(pos-(fStep/2),half+5, fStep, 1.5)  
                qp.setPen(pen)
                qp.setBrush(QtCore.Qt.NoBrush)                
            if (r[e]%5) == 0:
                s = 4
                text = r[e]
                fw = metrics.width(str(text))
                qp.drawText((pos)-fw/2, h-fh/3, str(text))
            else:
                s = 1.5
            qp.drawLine(pos,half+s, pos,half-s)
        pos = self.style().sliderPositionFromValue(self.minimum(),self.maximum(),self.value(),self.width())
        fw = metrics.width(str(self.value()))
        qp.setPen(QtGui.QColor(255,160,47))
        qp.drawText((pos)+fw/2, 0+fh, str(self.value())) 
        if self.hover:
            val = self.style().sliderValueFromPosition(self.minimum(),self.maximum(),self.hoverPos.x(),self.width())
            if val != self.value():
                    pos = self.style().sliderPositionFromValue(self.minimum(),self.maximum(),val,self.width())
                    fw = metrics.width(str(val))
                    pen2 = QtGui.QPen(QtGui.QColor(255,160,47,100), 2, QtCore.Qt.SolidLine)
                    qp.setPen(pen2)
                    qp.drawLine(pos,0, pos,h)
                    qp.drawText((pos)+fw/2, 0+fh, str(val)) 
        qp.setPen(pen)       
    def mousePressEvent(self,event):
        if event.modifiers() == QtCore.Qt.AltModifier:
            self.PressPos = event.globalPos()
            self.MovePos = event.globalPos()
        if event.button() == QtCore.Qt.LeftButton:
            butts = QtCore.Qt.MouseButtons(QtCore.Qt.MidButton)
            nevent = QtGui.QMouseEvent(event.type(),event.pos(),event.globalPos(),4,butts,event.modifiers())
            super(PC_timeline, self).mousePressEvent(nevent)
        else:
            super(PC_timeline, self).mousePressEvent(event)
    def wheelEvent(self,event):
        newMin = self.minimum()+(round(120/event.delta()))
        newMax = self.maximum()-(round(120/event.delta()))
        self.setRange(newMin,newMax)
        self.repaint()
    def eventFilter(self, widget, event):
        if event.type() == QtCore.QEvent.MouseMove:
            self.hover = True
            self.hoverPos = event.pos()
            self.repaint()
        elif event.type() == QtCore.QEvent.Leave:
            self.hover = False
            self.repaint()
        return super(PC_timeline, self).eventFilter( widget, event)

    def mouseMoveEvent(self, event):
        if event.modifiers() == QtCore.Qt.AltModifier:
            if event.buttons() in [QtCore.Qt.MidButton,QtCore.Qt.LeftButton] :
                globalPos = event.globalPos()
                diff = globalPos - self.MovePos
                a = (self.width()/(self.maximum()-self.minimum()))
                if abs(diff.x()) > a : 
                    self.MovePos = globalPos
                    newMin = self.minimum()-(1*(diff.x()/abs(diff.x())))
                    newMax = self.maximum()-(1*(diff.x()/abs(diff.x())))
                    self.setRange(newMin,newMax)
                    self.repaint()
        else:
            return super(PC_timeline, self).mouseMoveEvent( event)

        
class testWidg(QtWidgets.QWidget):

    def __init__(self,parent):
        super(testWidg, self).__init__(parent)
             
        self.setLayout(QtWidgets.QVBoxLayout())
        self.sld = PC_timeline(self)
        self.layout().addWidget(self.sld)
        
        self.setGeometry(-800, 300, 390, 80)

        
def main():
    
    app = QtWidgets.QApplication(sys.argv)

    ex = testWidg(None)
    ex.setStyle(QtWidgets.QStyleFactory.create("motif"))
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()