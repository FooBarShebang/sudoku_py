#!/usr/bin/python
"""
Module sudoku_py.ui.cli.basic_ui_elements

Implements prototype classes for the basic interaction with the user in the
CLI mode, e.g. a configurable text menu, an input dialog, etc.

Classes:
    SimpleMenuCLI
"""

__version__ = "0.0.1.1"
__date__ = "24-09-2018"
__status__ = "Development"

#imports

#+ standard libraries

import sys
import os
import json
import collections

#+ other modules from the package

from sudoku_py.ui.cli.terminal_utils import ClearConsole, PrintFW

#globals

DEF_OK_STATUS = 'Ok'

#classes

class SimpleMenuCLI(object):
    """
    Prototype class for the CLI menu. The subclasses must redefine the value of
    the 'private' class attribute _strMenuName - the name of the menu - and to
    implement the event handle methods for each of the menu items. The names of
    these method must be the same, as defined in the configuration file; they
    must be called without arguments and return either a string, or an object,
    which can be converted into a string.
    
    The event handlers, which are intended as the exit points from the current
    (sub-) menu (not call of the nested sub-menus or dialogues, etc.) must
    either set the property Status to the value defined by the module global
    variable (constant) DEF_OK_STATUS or simply return that value. The first
    method is preferable, since the value returned by the event handler, which
    terminated the interactive user choice prompting loop, is returned as the
    'last performed action' to the caller of this (sub-) menu.
    
    Methods:
        run()
            None -> str
    
    Attributes:
        Status: string, actually, the getter and setter property - the current
            status of the menu, i.e. the last performed action
    """
    
    #class fields
    
    _strMenuName = 'Prototype'
    
    #special methods

    def __init__(self, strSourceFile):
        """
        Initializes the class instance with the structure loaded from the
        external configuration file, which defines the valid user input options,
        their textual description and the generated command / event.
        
        Signature:
            str -> None
        
        Args:
            strSourceFile: string, name of a configuration JSON file describing
                the menu structure to be loaded
        
        Rasises:
            Exception: if any of the required event handler methods is not
                defined (in the sub-class)
        """
        with open(strSourceFile) as fFile:
            distlstOptions = json.load(fFile)
        strConfFolder = os.path.dirname(strSourceFile)
        self._dictOptions = collections.OrderedDict([
            (dictItem['key'].lower(), {'text' : dictItem['text'],
                                        'command' : dictItem['command']})
                                                for dictItem in distlstOptions])
        self._dictChildren = dict()
        for dictValue in self._dictOptions.values():
            strCommand = dictValue['command']
            if not hasattr(self, strCommand):
                strError = ''.join([self._strMenuName, ' of ',
                                        self.__class__.__name__, ' class ',
                                        'does not have ', strCommand,
                                        '() event handler method'])
                raise Exception(strError)
        objCurrentModule = sys.modules[self.__class__.__module__]
        for dictItem in distlstOptions:
            strChild = dictItem.get('child', None)
            if not (strChild is None):
                if not (strChild in dir(objCurrentModule)):
                    strError='Class {} is not found or defined'.format(strChild)
                    raise Exception(strError)
                strBaseName = dictItem.get('file', None)
                if not (strBaseName is None):
                    strFilePath = os.path.join(strConfFolder, strBaseName)
                    if not os.path.isfile(strFilePath):
                        strError = 'File {} is not found'.format(strFilePath)
                        raise Exception(strError)
                    self._dictChildren[dictItem['command']] = [strChild,
                                                                    strFilePath]
                else:
                    self._dictChildren[dictItem['command']] = [strChild, None]
        self.Status = 'Undefined'
    
    #helper methods
    
    def _launchChild(self):
        """
        Helper method to launch a sub-menu or a dialog, etc. - as the response
        to the choice of the current menu item.
        
        Extracts the name of the child object class and the path to the
        corresponding configuration file in the 'private' instance attribute
        _dictChildren by the name of the caller method.
        
        Looks up the class in the globals dictionary of the caller`s module by
        the name and instantiates it with a configuration file referred by the
        extracted file name. N.B. the 'child' class must have the method run()
        without arguments.
        
        Signature:
            str, str -> str
        
        Returns:
            str: any type which is returned by the child`s method run() being
                converted into a string
        """
        strCallerName = sys._getframe().f_back.f_code.co_name
        strClassName, strSourceFile = self._dictChildren[strCallerName]
        clsChild = sys.modules[self.__class__.__module__].__dict__[strClassName]
        if strSourceFile is None:
            objChild = clsChild()
        else:
            objChild = clsChild(strSourceFile)
        strResult = str(objChild.run())
        del objChild
        return strResult
    
    def _show(self):
        """
        Helper method do display the menu content. Clears the console. Then it
        prints out the menu name, its items in the same order, as defined in the
        configuration file, the current status (i.e. the last choice made) and
        the user prompt line.
        
        Signature:
            None -> None
        """
        ClearConsole()
        strLine = 'Welcome to the {} menu!\n'.format(self._strMenuName)
        PrintFW(strLine)
        for strKey, dictValue in self._dictOptions.items():
            strLine = '{}) {}'.format(strKey, dictValue['text'])
            PrintFW(strLine)
        strLine = '\nStatus: {}\n'.format(self.Status)
        PrintFW(strLine)
        strLine = 'Please select menu item ({}) '.format('/'.join([strKey
                                            for strKey in self._dictOptions]))
        sys.stdout.write(strLine)

    #public API
    
    #properties
    
    @property
    def Status(self):
        """
        Getter property to return the current status of the menu.
        
        Signature:
            None -> str
        """
        return str(self._strStatus)
    
    @Status.setter
    def Status(self, gValue):
        """
        Setter method for the property Status, i.e. sets the current menu status
        
        Signature:
            type A -> None
        
        Args:
            gValue: any type, which is converted into a string.
        """
        self._strStatus = str(gValue)
    
    #+methods

    def run(self):
        """
        Main method. Implements interactive loop of displaying the menu content
        and prompting the user input, until a proper menu item is chosen. When
        a proper menu item is chosen, the corresponing event handler method is
        called, and the returned result is assigned (as a string) to the current
        status of the menu.
        
        The loop continues until an event handler method returns the value
        defined by the sudoku_py.ui.cli.basic_ui_element.DEF_OK_STATUS module
        global variable (constant) value or explicitely sets the property Status
        to that value. The second option is preferable for the sub-menus, since
        the value returned by the event handler, which has caused the loop
        termination, is returned as a string by this method.
        
        Signature:
            None -> str
        
        Returns:
            str: the converted to a string value returned by the event handler
                method, which resulted in the breakage of the interactive prompt
                loop
        """
        while self.Status != DEF_OK_STATUS:
            self._show()
            strSelection = raw_input()
            strSelection = strSelection.lower()
            if strSelection in self._dictOptions:
                funHandler = getattr(self,
                                    self._dictOptions[strSelection]['command'])
                strResult = funHandler()
                if self.Status != DEF_OK_STATUS:
                    self.Status = strResult
            else:
                self.Status = 'Wrong selection! Try again!'
        return strResult
