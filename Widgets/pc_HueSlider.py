#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from Qt import QtGui, QtCore,QtWidgets
from pc_DoubleSlider import pc_DoubleSlider
styleSheet = """

QSlider,QSlider:disabled,QSlider:focus     {  
                          background: qcolor(0,0,0,0);   }

 QSlider::groove:horizontal {
 
    border: 1px solid #999999;
    background: qcolor(0,0,0,0);
 }
QSlider::handle:horizontal {
    background:  rgba(100,100,100,255);
    width: 6px;
 } 
"""

class pc_HueSlider(pc_DoubleSlider):
    def __init__(self, parent,*args):
        super(pc_HueSlider, self).__init__(parent=parent,*args)
        self.parent = parent
        self.color = QtGui.QColor()
        self.color.setHslF(0, 1,0.5, 1)
        self.defColor = self.color.name()
        

        self.setOrientation(QtCore.Qt.Horizontal)
        self.setStyleSheet(styleSheet)
        self.setMouseTracking(True)

    def setColor(self,color):
        if isinstance(color,QtGui.QColor):
            self.color = color
            self.defColor = self.color.name()
            self.update()

    def getColor(self):
        return self.getHue(self.value())

    def getHue(self,hue):
        c = QtGui.QColor(self.defColor)
        h,s,l,a = c.getHslF()
        c.setHslF((h+hue)%1, s, l, a)
        return c
        

    def paintEvent(self, event):

        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawWidget(qp)
        qp.end()        
        super(pc_HueSlider, self).paintEvent(event)

    def drawWidget(self, qp):
        w = self.width()
        h = self.height()
            
        gradient = QtGui.QLinearGradient(0, 0, w, h)
        for i in range(11):
            gradient.setColorAt(i*0.1, self.getHue(i*0.1))

        qp.setBrush(QtGui.QBrush(gradient))

        qp.drawRect(0, 0, w, h)                
  
    def mousePressEvent(self,event):
        if event.button() == QtCore.Qt.LeftButton:
            butts = QtCore.Qt.MouseButtons(QtCore.Qt.MidButton)
            nevent = QtGui.QMouseEvent(event.type(),event.pos(),event.globalPos(),4,butts,event.modifiers())
            super(pc_HueSlider, self).mousePressEvent(nevent)
        else:
            super(pc_HueSlider, self).mousePressEvent(event)




        
class testWidg(QtWidgets.QWidget):

    def __init__(self,parent):
        super(testWidg, self).__init__(parent)
             
        self.setLayout(QtWidgets.QVBoxLayout())
        self.sld = pc_HueSlider(self)
        self.layout().addWidget(self.sld)
        
        self.setGeometry(800, 300, 390, 80)

        
def main():
    
    app = QtWidgets.QApplication(sys.argv)

    ex = testWidg(None)
    ex.setStyle(QtWidgets.QStyleFactory.create("motif"))
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()