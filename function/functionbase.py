'''
Renormalization Plot - function/functionbase.py
    The base class for mathematical functions

Copyright (C) 2017 Dyi-Shing Ou. All Rights Reserved.

This file is part of Renormalization Plot which is released under 
the terms of the GNU General Public License version 3 as published 
by the Free Software Foundation. See LICENSE.txt or 
go to <http://www.gnu.org/licenses/> for full license details.
'''

from abc import ABCMeta,abstractmethod
import typing as tp 
import logging

class FunctionBaseMeta(ABCMeta):
    def __init__(self, name, bases, dct):
        ABCMeta.__init__(self, name, bases, dct)
        #self.__call__=self.function
        #print(str(self))
        #print(str(name))
        #print(str(bases))
        #print(str(dct))
    
class FunctionBase(object,metaclass=FunctionBaseMeta):
    '''
    classdocs
    '''
    _logger:tp.Optional[logging.Logger]=None

    def __init__(self,variables=1,logger:tp.Optional[logging.Logger]=None):
        '''
        Constructor
        '''
        if logger is None:
            self._logger:logging.Logger=logging.LoggerAdapter(logging.getLogger(__name__),{'function':self})
        else:
            self._logger=logging.LoggerAdapter(logger,{'function':self})

        if variables==1:
            self.iterates=self.__iteratesOneVariable
        else:
            self.iterates=self.__iteratesMultipleVariable
        #self.__call__=self.function
        pass
        
    @abstractmethod
    def function(self, *args, **kwargs): pass
    
    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)

    def __str__(self):
        return type(self).__name__
    
    def iterates(self, *args, iteration:int=2, **kwargs):
        '''
        Apply multiple iterations of the function
        @param iteration: number of iterations
        @type iteration: int
        '''
        if len(args)==1:
            self.iterates=self.__iteratesOneVariable
        else:
            self.iterates=self.__iteratesMultipleVariable
        return self.iterates(*args, iteration=iteration, **kwargs)
    
    def __iteratesOneVariable(self, x, iteration:int=2, **kwargs):
        '''
        Apply multiple iterations of the function with one variable
        @param iteration: number of iterations
        @type iteration: int
        '''
        function=self.function
        for t in range(iteration):
            x=function(x,**kwargs)
        return x
    
    def __iteratesMultipleVariable(self, *args, iteration:int=2, **kwargs):
        '''
        Apply multiple iterations of the function with multiple variables
        @param iteration: number of iterations
        @type iteration: int
        '''
        function=self.function
        for t in range(iteration):
            args=function(*args,**kwargs)
        return args
