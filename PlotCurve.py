'''
Created on 2017/8/15

@author: dsou
'''
import numpy as np
from PyQt5 import QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.patches as patches
import matplotlib.ticker as ticker

import random

class GraphObjectBase():
    '''
    classdocs
    '''
    
    # Variable to store visible state
    _visible=True
    
    # variable to store the mask for visible state 
    _visibleMask=True
    
    def __init__(self,visible=True,visibleMask=True):
        #self._visible=visible
        self._visibleMask=visibleMask
        self._visible=visible
    
    # visible
    def getVisible(self):
        return self._visible
    @QtCore.pyqtSlot(bool)
    def setVisible(self,visible):
        if (visible & self._visibleMask) != (self._visible & self._visibleMask):
            self._setVisibleInternal(visible & self._visibleMask)
        self._visible=visible
    visible=property(getVisible, setVisible)

    # implimentation for visible if state changed
    def _setVisibleInternal(self,visible):
        raise NotImplementedError("GraphObjectBase._setVisibleInternal has to be implemented")
        
    def getVisibleMask(self):
        return self._visibleMask
    @QtCore.pyqtSlot(bool)
    def setVisibleMask(self,visibleMask):
        if (self._visible & visibleMask) != (self._visible & self._visibleMask):
            self._setVisibleInternal(self._visible & visibleMask)
        self._visibleMask=visibleMask
    visibleMask=property(getVisibleMask, setVisibleMask)

    # remove the graph from the screen
    def remove(self):
        raise NotImplementedError("GraphObjectBase.remove has to be implemented")

# Sync a group of GraphObjectBase items
# sync methods: visible, remove
class GroupG(GraphObjectBase,list):
    def __init__(self,*args,visible=True):
        list.__init__(self,*args)
        GraphObjectBase.__init__(self,visible=visible)
        self._setVisibleInternal(visible=visible)
        
    def _setVisibleInternal(self, visible):
        for member in self:
            member.setVisibleMask(visible)
    
    # remove all artist in the list from the canvas    
    def remove(self):
        for member in self:
            member.remove()

# Graphical object for artist
# line=matplotlib.lines.Line2D object
# canvas: matplotlib canvas
class GraphObject(GraphObjectBase,QtCore.QObject):
    _canvas=None
    _curve=None
    
    def __init__(self, canvas, visible=True):
        self._canvas=canvas
        QtCore.QObject.__init__(self,canvas)
        GraphObjectBase.__init__(self,visible=visible)

        # Plot only when visible
        if visible == True:
            self._curve=self._initilizePlot()
        else:
            self._curve=None

    # return: matplotlib artist
    def _initilizePlot(self):
        raise NotImplementedError("GraphObjectBase._initilize has to be implemented")

    # curve: matplotlib artist
    def _updatePlot(self,curve):
        raise NotImplementedError("GraphObjectBase._updatePlot has to be implemented")

    @QtCore.pyqtSlot()
    def update(self):
        if self._curve is not None:
            self._updatePlot(self._curve)
            self._canvas.update()
        elif self._visible == True and self._visibleMask == True:
            self._curve=self._initilizePlot()
            self._canvas.update()

    # canvas
    # useless?
    def getCanvas(self):
        return self._canvas
    @QtCore.pyqtSlot(FigureCanvas)
    def setCanvas(self,canvas):
        self._canvas=canvas
    canvas=property(getCanvas, setCanvas)
        
    # visible
    def _setVisibleInternal(self,visible):
        if self._curve is not None:
            self._curve.set_visible(visible)
            self._canvas.update()
        elif visible == True:
            self._curve=self._initilizePlot()
            self._canvas.update()
        
    # curve
    # useless?
    def getCurve(self):
        return self._curve
    def setCurve(self, curve):
        self._curve=curve
    curve=property(getCurve, setCurve)

    # remove the artist from the canvas    
    def remove(self):
        if self._curve is not None:
            self._curve.remove()
            self._curve=None
            self._canvas.update()

# Plot of a function
class FunctionG(GraphObject):

    # Function of one variable
    _func=None
    
    # canvas: canvas to show the plot
    # func: function of one variable
    def __init__(self, canvas, func, visible=True, **kwargs):
        self._func=func
        self._kwargs=kwargs

        # set sample points
        self._sample = np.arange(-1.0, 1.001, 0.0001)

        super().__init__(canvas, visible=visible)
        
    def _initilizePlot(self):
        curve, = self._canvas.axes.plot(self._sample, self._func(self._sample), **self._kwargs)
        return curve

    def _updatePlot(self,curve):
        curve.set_ydata(self._func(self._sample))

    # function
    def getFunction(self):
        return self._func
    def setFunction(self,func):
        self._func=func
        self.update()

    function=property(getFunction, setFunction)

# QuadContourSet is not inherted from artist
# have to rewrite the base
class ContourG(GraphObjectBase,QtCore.QObject):
    _contour=None
    _cbaxes=None
    _cbar=None
    
    def __init__(self, canvas, func, visible=True, **kwargs):
        self._func=func
        self._kwargs=kwargs
        self._canvas=canvas
        QtCore.QObject.__init__(self,canvas)
        GraphObjectBase.__init__(self,visible=visible)

        # set sample points
        x = np.arange(-1.0, 1.0, 0.0001)
        y = np.arange(-1.0, 1.1, 2)
        self.sampleX,self.sampleY = np.meshgrid(x,y)
        
        # Plot only when visible
        if visible == True:
            self._initilizePlot()
        else:
            self._contour=None
        

    def _initilizePlot(self):
        self._contour = self._canvas.axes.contourf(self.sampleX, self.sampleY, self._func(self.sampleX,self.sampleY),**self._kwargs)
        self._cbaxes = self._canvas.fig.add_axes([0.9, 0.1, 0.03, 0.8]) 
        self._cbar = self._canvas.fig.colorbar(self._contour, cax=self._cbaxes, ticks=ticker.MaxNLocator(integer=True))

    def _updatePlot(self):
        for item in self._contour.collections:
            item.remove()
        self._contour = self._canvas.axes.contourf(self.sampleX, self.sampleY, self._func(self.sampleX,self.sampleY),**self._kwargs)
    
    def _removePlot(self):
        for item in self._contour.collections:
            item.remove()
        self._contour=None
        self._cbaxes.remove()
        self._cbaxes=None
        self._cbar=None
    
    @QtCore.pyqtSlot()
    def update(self):
        if self._contour is not None:
            self._updatePlot()
            self._canvas.update()
        elif self._visible == True and self._visibleMask == True:
            self._initilizePlot()
            self._canvas.update()

    # visible
    # todo: create a new axis and set the visibility of the axis 
    def _setVisibleInternal(self,visible):
        if visible == False and self._contour is not None:
            self._removePlot()
            self._canvas.update()
        elif visible == True and self._contour is None:
            self._initilizePlot()
            self._canvas.update()
            
    # function
    def getFunction(self):
        return self._func
    def setFunction(self,func):
        self._func=func
        self.update()
        
    def remove(self):
        if self._contour is not None:
            self._removePlot()
            self._canvas.update()

    function=property(getFunction, setFunction)

class VerticalLineG(GraphObject):
    def __init__(self, canvas, xValue, visible=True, **kwargs):
        self._xValue=xValue
        self._kwargs=kwargs
        
        super().__init__(canvas, visible)

    def _initilizePlot(self):
        return self._canvas.axes.axvline(x=self._xValue,**self._kwargs)

    def _updatePlot(self,curve):
        curve.set_xdata([self._xValue,self._xValue])

    # function
    def getXValue(self):
        return self._xValue
    @QtCore.pyqtSlot(int)
    def setXValue(self,xValue):
        self._xValue=xValue
        self.update()
    xValue=property(getXValue, setXValue)
    
class RectangleG(GraphObject):
    def __init__(self, canvas, xValue, yValue, width, height, visible=True, **kwargs):
        self._xValue=xValue
        self._yValue=yValue
        self._width=width
        self._height=height
        self._kwargs=kwargs
        
        super().__init__(canvas, visible)

    def _initilizePlot(self):
        curve = patches.Rectangle((self._xValue,self._yValue), self._width, self._height,**self._kwargs)
        self._canvas.axes.add_patch(curve)
        return curve

    def _updatePlot(self,curve):
        curve.set_bounds(self._xValue, self._yValue, self._width, self._height)

    # function
    def getBounds(self):
        return (self._xValue, self._yValue, self._width, self._height)
    def setBounds(self, xValue, yValue, width, height):
        self._xValue=xValue
        self._yValue=yValue
        self._width=width
        self._height=height
        self.update()
    bounds=property(getBounds, setBounds)

# todo: sync axes
# https://stackoverflow.com/questions/4999014/matplotlib-pyplot-how-to-zoom-subplots-together-and-x-scroll-separately
class TicksG(GraphObject):
    positionValues = ["left", "right", "top", "bottom"]
    xPosition = ["top", "bottom"]
    yPosition = ["left", "right"]
    
    def __init__(self, canvas, position, ticks=[], ticksLabel=[], visible=True, **kwargs):
        if position not in TicksG.positionValues:
            raise ValueError("position [%s] must be one of %s" %
                             (position, TicksG.positionValues))
        self._position=position
        self._ticks=ticks
        self._ticksLabel=ticksLabel
     
        super().__init__(canvas, visible)

    def _initilizePlot(self):
        if self._position == "left":
            curve=self._canvas.figure.add_axes(self._canvas.axes.get_position(True),sharex=self._canvas.axes,label=str(random.getrandbits(128)))
            curve.yaxis.tick_left()
            curve.yaxis.set_label_position('left')
            curve.yaxis.set_offset_position('left')
            curve.set_autoscalex_on(self._canvas.axes.get_autoscalex_on())
            curve.xaxis.set_visible(False)
            curve.set_yticks(self._ticks)
            curve.set_yticklabels(self._ticksLabel)
        elif self._position == "right":
            curve=self._canvas.figure.add_axes(self._canvas.axes.get_position(True),sharex=self._canvas.axes,label=str(random.getrandbits(128)))
            curve.yaxis.tick_right()
            curve.yaxis.set_label_position('right')
            curve.yaxis.set_offset_position('right')
            curve.set_autoscalex_on(self._canvas.axes.get_autoscalex_on())
            curve.xaxis.set_visible(False)
            curve.set_yticks(self._ticks)
            curve.set_yticklabels(self._ticksLabel)
        elif self._position == "top":
            curve=self._canvas.figure.add_axes(self._canvas.axes.get_position(True),sharey=self._canvas.axes,label=str(random.getrandbits(128)))
            curve.xaxis.tick_top()
            curve.xaxis.set_label_position('top')
            #curve.xaxis.set_offset_position('top')
            curve.set_autoscaley_on(self._canvas.axes.get_autoscaley_on())
            curve.yaxis.set_visible(False)
            curve.set_xticks(self._ticks)
            curve.set_xticklabels(self._ticksLabel)
        elif self._position == "bottom":
            curve=self._canvas.figure.add_axes(self._canvas.axes.get_position(True),sharey=self._canvas.axes,label=str(random.getrandbits(128)))
            curve.xaxis.tick_bottom()
            curve.xaxis.set_label_position('bottom')
            #curve.xaxis.set_offset_position('bottom')
            curve.set_autoscaley_on(self._canvas.axes.get_autoscaley_on())
            curve.yaxis.set_visible(False)
            curve.set_xticks(self._ticks)
            curve.set_xticklabels(self._ticksLabel)

        curve.patch.set_visible(False)
        return curve
    
    def _updatePlot(self,curve):
        if self._position in TicksG.xPosition:
            xLimit=curve.get_xlim()
            curve.set_xticks(self._ticks)
            curve.set_xticklabels(self._ticksLabel)
            curve.set_xlim(*xLimit)
        elif self._position in TicksG.yPosition:
            yLimit=curve.get_ylim()
            curve.set_yticks(self._ticks)
            curve.set_yticklabels(self._ticksLabel)
            curve.set_ylim(*yLimit)
    
    def setTicks(self, ticks):
        self._ticks=ticks
        self.update()
        
    def setTicksLabel(self, ticksLabel):
        self._ticksLabel=ticksLabel
        self.update()
        
