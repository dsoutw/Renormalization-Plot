'''
Created on 2017/9/3

@author: dsou
'''
from Plot.Artist import ArtistBase
from PyQt5 import QtCore

class VerticalLine(ArtistBase):
    def __init__(self, parent, xValue, axis=None, visible=True, **kwargs):
        '''
        Plot a vertical line on a canvas
        :param canvas:
        :type canvas:
        :param xValue:
        :type xValue:
        :param axis:
        :type axis:
        :param visible:
        :type visible:
        '''
        self._xValue=xValue
        self._kwargs=kwargs
        if axis == None:
            self._axis=parent.axes
        else:
            self._axis=axis
        
        super().__init__(parent, visible)

    def _initilizePlot(self):
        return self.__plot(self._axis)

    def __plot(self, axis):
        return axis.axvline(x=self.xValue,**self._kwargs)
    
    def draw(self, axis):
        if self.isShowed():
            return self.__plot(axis)
        else:
            return None

    def _updatePlot(self,artist):
        artist.set_xdata([self.xValue,self.xValue])
        return artist

    # function
    def getXValue(self):
        return self._xValue
    @QtCore.pyqtSlot(int)
    def setXValue(self,xValue):
        self._xValue=xValue
        self.update()
    xValue=property(
        lambda self: self.getXValue(), 
        lambda self, value: self.setXValue(value)
        )