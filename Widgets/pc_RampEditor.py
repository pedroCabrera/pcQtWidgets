from Qt import QtCore, QtGui,QtWidgets
import random

colors = [QtGui.QColor(255,0,0),QtGui.QColor(0,255,0),QtGui.QColor(0,0,255)]

class Tick(QtWidgets.QGraphicsWidget):
    """ Element Fro Ramp Widgets___Basic U,V,Color Attribute holder """
    def __init__(self, parent=None):
        super(Tick, self).__init__(parent)
        self.setAcceptHoverEvents(True)
        self._width = 10
        self._height = 17
        self.hovered = False
        self.setFlag(QtWidgets.QGraphicsWidget.ItemIsMovable)
        self.setFlag(QtWidgets.QGraphicsWidget.ItemIsFocusable)
        self.setFlag(QtWidgets.QGraphicsWidget.ItemIsSelectable, True)
        self.setFlag(QtWidgets.QGraphicsWidget.ItemSendsGeometryChanges)

    def getU(self):
        return self._u

    def getV(self):
        return self._v

    def getColor(self):
        return self._color

    def setU(self, u):
        self._u = u

    def setV(self, v):
        self._v = v

    def setColor(self, color):
        r, g, b = color
        self._color = QtGui.QColor().fromRgb(r, g, b)
        self.update()
        self.scene().update()

    def hoverEnterEvent(self, event):
        super(Tick, self).hoverEnterEvent(event)
        self.hovered = True
        self.update()

    def hoverLeaveEvent(self, event):
        super(Tick, self).hoverLeaveEvent(event)
        self.hovered = False
        self.update()

    def boundingRect(self):
        return QtCore.QRectF(0, 0, self._width, self._height)

    def paint(self, painter, option, widget):
        bgRect = self.boundingRect()
        painter.setBrush(QtGui.QColor(255, 255, 255, 150))
        pen = QtGui.QPen(QtCore.Qt.black, 1.5)
        if self.isSelected():
            pen.setColor(QtGui.QColor(215, 128, 26))
        elif self.hovered:
            MainColor_Lighter = QtGui.QColor(QtGui.QColor(215, 128, 26))
            MainColor_Lighter.setAlpha(128)        
            pen.setColor(MainColor_Lighter)            
            pen.setWidth(2.25)
        painter.setPen(pen)
        painter.drawRoundedRect(bgRect, 2, 2)

class pyf_RampColor(QtWidgets.QGraphicsView):

    tickClicked = QtCore.Signal(object)
    colorClicked = QtCore.Signal(list)
    """ Gradient Editor with evaluateAt support """
    def __init__(self, parent):
        super(pyf_RampColor, self).__init__(parent)
        self._scene = QtWidgets.QGraphicsScene(self)
        self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        self.setScene(self._scene)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorViewCenter)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorViewCenter)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setMaximumHeight(20)
        self.setMinimumHeight(20)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(30, 30, 30)))
        self.mousePressPose = QtCore.QPointF(0, 0)
        self.mousePos = QtCore.QPointF(0, 0)
        self._lastMousePos = QtCore.QPointF(0, 0)
        self.pressed_item = None

    def __getitem__(self,index):
        if len(self.items()) and index >=0 and index <= len(self.items())-1:
            return self.sortedItems()[index].getColor().getRgbF()
        else:
            return None

    @property
    def positions(self):
        return [x.getU() for x in self.sortedItems()]

    @property
    def values(self):
        return [x.getColor().getRgbF() for x in self.sortedItems()]

    def sortedItems(self):
        itms = list(self.items())
        itms.sort(key=lambda x: x.getU())
        return itms

    def addItem(self, color, u):
        item = Tick()
        r, g, b = color
        item._color = QtGui.QColor.fromRgb(r, g, b)
        self._scene.addItem(item)
        item.setU(u)
        item.setPos(item.getU() * (self.sceneRect().width() - 10), 1)

    def setColor(self, color, index=-1):
        if index in range(0, len(self.items()) - 1):
            self.sortedItems()[index].setColor(color)
        elif len(self.items()) > 0:
            for item in self.items():
                if item.isSelected():
                    item.setColor(color)

    def evaluateAt(self, value):
        items = self.sortedItems()
        if len(items) > 1:
            interval = len(items) - 1
            for i, x in enumerate(items):
                if value <= x.getU():
                    interval = i
                    break

            u = max(0, min(1, (((value - items[interval - 1].getU()) * (1.0 - 0.0)) / (
                items[interval].getU() - items[interval - 1].getU())) + 0.0))

            color = self.interpolate(
                items[interval].getColor(), items[interval - 1].getColor(), u)
            return color
        elif len(items) == 1:
            return items[0].getColor()
        else:
            return QtGui.QColor(0, 0, 0)

    def interpolate(self, start, end, ratio):

        r = (ratio * start.red() + (1 - ratio) * end.red())
        g = (ratio * start.green() + (1 - ratio) * end.green())
        b = (ratio * start.blue() + (1 - ratio) * end.blue())
        return QtGui.QColor.fromRgb(r, g, b)

    def resizeEvent(self, event):
        super(pyf_RampColor, self).resizeEvent(event)
        self.scene().setSceneRect(0, 0, self.frameSize().width(), self.frameSize().height())
        self.fitInView(0, 0, self.scene().sceneRect().width(),
                       15, QtCore.Qt.IgnoreAspectRatio)
        for item in self.items():
            item.setPos(item.getU() * (self.sceneRect().width() - 10), 1)
            item.__height = self.frameSize().height()
            item.update()

    def clearSelection(self):
        for item in self.items():
            item.setSelected(False)

    def mousePressEvent(self, event):
        self.pressed_item = self.itemAt(event.pos())
        self.mousePressPose = event.pos()
        self._lastMousePos = event.pos()
        if event.button() == QtCore.Qt.RightButton:
            if self.pressed_item:
                self._scene.removeItem(self.pressed_item)
                del self.pressed_item
                self.pressed_item = None
        elif event.button() == QtCore.Qt.MidButton:
            print(self.evaluateAt(self.mapToScene(event.pos()).x() / self.frameSize().width()))
        else:
            if not self.pressed_item:
                item = Tick()
                item._color = self.evaluateAt(self.mapToScene(
                    event.pos()).x() / self.frameSize().width())
                self._scene.addItem(item)
                item.setPos(self.mapToScene(event.pos()).x(), 1)
                item.setU(
                    max(min(item.scenePos().x() / (self.frameSize().width() - 10), 1), 0))
                item.setPos(item.getU() * (self.sceneRect().width() - 10), 1)
                self.pressed_item = item
        self.clearSelection()
        if self.pressed_item:
            self.pressed_item.setSelected(True)
            self.tickClicked.emit(self.pressed_item)
            self.colorClicked.emit(
                [(x+1.0)/255. for x in self.pressed_item.getColor().getRgb()])
        self.scene().update()

    def mouseMoveEvent(self, event):
        super(pyf_RampColor, self).mouseMoveEvent(event)
        self.mousePos = event.pos()
        mouseDelta = QtCore.QPointF(self.mousePos) - self._lastMousePos
        if self.pressed_item:
            self.pressed_item.moveBy(mouseDelta.x(), 0)
            self.pressed_item.setU(
                max(min(self.pressed_item.scenePos().x() / (self.frameSize().width() - 10), 1), 0))
            self.pressed_item.setPos(
                self.pressed_item.getU() * (self.sceneRect().width() - 10), 1)
        self._lastMousePos = event.pos()
        self.scene().update()

    def mouseReleaseEvent(self, event):
        super(pyf_RampColor, self).mouseReleaseEvent(event)
        self.pressed_item = None
        self.scene().update()

    def drawBackground(self, painter, rect):
        super(pyf_RampColor, self).drawBackground(painter, rect)
        if len(self.items()):
            b = QtGui.QLinearGradient(0, 0, rect.width(), 0)
            for item in self.items():
                b.setColorAt(item.getU(), item.getColor())
        else:
            b = QtGui.QColor(32, 32, 32)
        painter.fillRect(rect, b)

class pyf_RampSpline(QtWidgets.QGraphicsView):

    tickClicked = QtCore.Signal(object)
    valueClicked = QtCore.Signal(float,float)
    """ Ramp/Curve Editor with evaluateAt support , clamped to 0,1 in both x and y"""
    def __init__(self, parent,bezier=True):
        super(pyf_RampSpline, self).__init__(parent)
        self._scene = QtWidgets.QGraphicsScene(self)
        self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        self.setScene(self._scene)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorViewCenter)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorViewCenter)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setMaximumHeight(60)
        self.setMinimumHeight(60)
        self.bezier = bezier
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(30, 30, 30)))
        self.mousePressPose = QtCore.QPointF(0, 0)
        self.mousePos = QtCore.QPointF(0, 0)
        self._lastMousePos = QtCore.QPointF(0, 0)
        self.pressed_item = None
        self.itemSize = 6
        self.displayPoints = []

    def __getitem__(self,index):
        if len(self.items()) and index >=0 and index <= len(self.items())-1:
            return self.sortedItems()[index]._v
        else:
            return None

    @property
    def positions(self):
        return [x.getU() for x in self.sortedItems()]

    @property
    def values(self):
        return [x._v for x in self.sortedItems()]

    def sortedItems(self):
        itms = list(self.items())
        itms.sort(key=lambda x: x.getU())
        return itms

    def addItem(self,u,v):
        item = Tick()
        item._width = item._height = 6
        self._scene.addItem(item)
        item.setU(u)
        item.setV(1-v)
        item.setPos(item.getU() * (self.sceneRect().width() - self.itemSize), item._v * (self.sceneRect().height() - self.itemSize))
        self.computeDisplayPoints()

    def setU(self, u, index=-1):
        if index in range(0, len(self.items()) - 1):
            self.sortedItems()[index].setU(u)
        elif len(self.items()) > 0:
            for item in self.items():
                if item.isSelected():
                    item.setU(u)
        self.computeDisplayPoints()

    def setV(self, v, index=-1):
        if index in range(0, len(self.items()) - 1):
            self.sortedItems()[index].setV(v)
        elif len(self.items()) > 0:
            for item in self.items():
                if item.isSelected():
                    item.setV(v)
        self.computeDisplayPoints()

    def evaluateAt(self, value):
        items = self.sortedItems()
        if len(items) > 1:
            if value >= items[-1].getU():
                return 1- items[-1]._v
            elif value <= items[0].getU():
                return 1-items[0]._v
            interval = len(items) - 1
            for i, x in enumerate(items):
                if value <= x.getU():
                    interval = i
                    break
            u = max(0, min(1, (((value - items[interval - 1].getU()) * (1.0 - 0.0)) / (
                items[interval].getU() - items[interval - 1].getU())) + 0.0))
            if not self.bezier:
                v = self.interpolateLinear(
                    items[interval]._v, items[interval - 1]._v, u)
            else:
                v = 1 - self.interpolateBezier([p._v for p in items], 0, len(items) - 1, value)
            return v
        elif len(items) == 1:
            return 1- items[0]._v
        else:
            return 0.0

    def interpolateBezier(self,coorArr, i, j, t):
        if j == 0:
            return coorArr[i]
        return self.interpolateBezier(coorArr, i, j - 1, t) * (1 - t) + self.interpolateBezier(coorArr, i + 1, j - 1, t) * t

    def interpolateLinear(self, start, end, ratio):
        v = (ratio * start + (1 - ratio) * end)
        return 1-v

    def resizeEvent(self, event):
        super(pyf_RampSpline, self).resizeEvent(event)
        self.scene().setSceneRect(0, 0, self.frameSize().width(), self.frameSize().height())
        self.fitInView(0, 0, self.scene().sceneRect().width(),60, QtCore.Qt.IgnoreAspectRatio)
        for item in self.items():
            item.setPos(item.getU() * (self.sceneRect().width() - self.itemSize), item._v * (self.sceneRect().height() - self.itemSize))
            item.__height = self.frameSize().height()
            item.update()
        self.computeDisplayPoints(self.bezier)

    def clearSelection(self):
        for item in self.items():
            item.setSelected(False)

    def mousePressEvent(self, event):
        self.pressed_item = self.itemAt(event.pos())
        self.mousePressPose = event.pos()
        self._lastMousePos = event.pos()
        if event.button() == QtCore.Qt.RightButton:
            if self.pressed_item:
                self._scene.removeItem(self.pressed_item)
                del self.pressed_item
                self.pressed_item = None
                self.computeDisplayPoints(self.bezier)
        elif event.button() == QtCore.Qt.MidButton:
            print(self.evaluateAt(self.mapToScene(event.pos()).x() / (self.frameSize().width() - self.itemSize)))
        else:
            if not self.pressed_item:
                item = Tick()
                item._width = item._height = 6
                self._scene.addItem(item)
                item.setPos(self.mapToScene(event.pos()))
                item.setU(
                    max(min(item.scenePos().x() / (self.frameSize().width() - self.itemSize), 1), 0))
                item.setV(
                    max(min(item.scenePos().y() / (self.frameSize().height() - self.itemSize), 1), 0))                
                item.setPos(item.getU() * (self.sceneRect().width() - self.itemSize), item._v * (self.sceneRect().height() - self.itemSize))
                self.pressed_item = item
                self.computeDisplayPoints(self.bezier)
        self.clearSelection()
        if self.pressed_item:
            self.pressed_item.setSelected(True)
            self.tickClicked.emit(self.pressed_item)
            self.valueClicked.emit(self.pressed_item.getU(),self.pressed_item._v)
        self.scene().update()

    def mouseMoveEvent(self, event):
        super(pyf_RampSpline, self).mouseMoveEvent(event)
        self.mousePos = event.pos()
        mouseDelta = QtCore.QPointF(self.mousePos) - self._lastMousePos
        if self.pressed_item:
            self.pressed_item.moveBy(mouseDelta.x(), mouseDelta.y())
            self.pressed_item.setU(
                max(min(self.pressed_item.scenePos().x() / (self.frameSize().width() - self.itemSize), 1), 0))
            self.pressed_item.setV(
                max(min(self.pressed_item.scenePos().y() / (self.frameSize().height() - self.itemSize), 1), 0)) 
            self.pressed_item.setPos(
                self.pressed_item.getU() * (self.sceneRect().width() - self.itemSize),self.pressed_item._v * (self.sceneRect().height() - self.itemSize))
            self.computeDisplayPoints(self.bezier)
        self._lastMousePos = event.pos()
        
        self.scene().update()

    def mouseReleaseEvent(self, event):
        super(pyf_RampSpline, self).mouseReleaseEvent(event)
        self.pressed_item = None
        self.scene().update()
        
    def computeDisplayPoints(self,bezier=False):
        items = self.sortedItems()
        val = self.mapToScene(QtCore.QPoint(-1.5,-1.5))
        points = []
        if len(items):
            if not bezier:
                points = [QtCore.QPointF(self.itemSize/2,self.frameSize().height()-self.itemSize/2),
                          QtCore.QPointF(self.itemSize/2,items[0].scenePos().y()-val.y())]
            for item in items:
                points.append(item.scenePos()-val)

            if bezier:
                bezierPoints = [QtCore.QPointF(self.itemSize/2,self.frameSize().height()-self.itemSize/2),
                          QtCore.QPointF(self.itemSize/2,items[0].scenePos().y()-val.y())]
                numSteps = 50
                for k in range(numSteps):
                    t = float(k) / (numSteps - 1)
                    x = int(self.interpolateBezier([p.x() for p in points], 0, len(items) - 1, t))
                    y = int(self.interpolateBezier([p.y() for p in points], 0, len(items) - 1, t))  
                    bezierPoints.append(QtCore.QPointF(x,y))
                points = bezierPoints
            points.append(QtCore.QPointF(self.frameSize().width()-self.itemSize/2,items[-1].scenePos().y()-val.y()))
            points.append(QtCore.QPointF(self.frameSize().width()-self.itemSize/2,self.frameSize().height()-self.itemSize/2))            
        self.displayPoints = points  
              
    def drawBackground(self, painter, rect):
        painter.fillRect(rect.adjusted(self.itemSize/2,self.itemSize/2,-self.itemSize/2,-self.itemSize/2),QtGui.QColor(32, 32, 32))
        painter.setBrush(QtGui.QColor(0,0,0,0))
        painter.setPen(QtGui.QColor(0,0,0,255))
        painter.drawRect(rect.adjusted(self.itemSize/2,self.itemSize/2,-self.itemSize/2,-self.itemSize/2))
        items = self.sortedItems()
        val = self.mapToScene(QtCore.QPoint(-1.5,-1.5))
        if len(items):
            painter.setBrush(QtGui.QColor(100,100,100))
            painter.drawPolygon(self.displayPoints, QtCore.Qt.WindingFill);
        else:
            b = QtGui.QColor(32, 32, 32)
if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = pyf_RampSpline(None)
    window.setGeometry(500, 300, 800, 600)
    window.show()
    sys.exit(app.exec_())