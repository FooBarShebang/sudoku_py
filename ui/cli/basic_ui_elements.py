#!/usr/bin/python
"""
Module sudoku_py.ui.cli.basic_ui_elements

Implements prototype classes for the basic interaction with the user in the
CLI mode, e.g. a configurable text menu, an input dialog, etc.

Classes:
    SimpleMenuCLI
"""

__version__ = "0.0.1.0"
__date__ = "24-09-201"
__status__ = "Development"

#imports

#+ standard libraries

import sys
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
    either set the 'private' instance attribute _strStatus to the value defined
    by the module global variable (constant) DEF_OK_STATUS or simply return that
    value. The first method is preferable, since the value returned by the event
    handler, which terminated the interactive user choice prompting loop, is
    returned as the 'last performed action' to the caller of this (sub-) menu.
    
    Methods:
        run()
            None -> str
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
        """
        with open(strSourceFile) as fFile:
            distlstOptions = json.load(fFile)
        self._dictOptions = collections.OrderedDict([
            (dictItem['key'].lower(), {'text' : dictItem['text'],
                                        'command' : dictItem['command']})
                                                for dictItem in distlstOptions])
        self._strStatus = 'Undefined'
    
    #helper methods
    
    def _launchChild(self, strClassName, strSourceFile):
        """
        Helper method to launch a sub-menu or a dialog, etc. - as the response
        to the choice of the current menu item. Looks up the class in the
        globals dictionary by the passed name and instantiates it with a
        configuration file referred by the passed file name. N.B. the 'child'
        class must have the method run() without arguments.
        
        Signature:
            str, str -> str
        
        Args:
            strClassName: string, name of the class implementing the submenu,
                dialog, etc.; will be looked up in the globals dictionary
            strSourceFile: string, of a configuration JSON file describing
                the submenu or dialog, etc. structure / content to be loaded
        
        Returns:
            str: any type which is returned by the child`s method run() being
                converted into a string
        """
        clsChild = globals(strClassName)
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
        strLine = '\nStatus: {}\n'.format(self._strStatus)
        PrintFW(strLine)
        strLine = 'Please select menu item ({}) '.format('/'.join([strKey
                                            for strKey in self._dictOptions]))
        sys.stdout.write(strLine)

    #public API

    def run(self):
        """
        Main method. Implements interactive loop of displaying the menu content
        and prompting the user input, until a proper menu item is chosen. When
        a proper menu item is chosen, the corresponing event handler method is
        called, and the returned result is assigned (as a string) to the current
        status of the menu.
        
        The loop continues until an event handler method returns the value
        defined by the sudoku_py.ui.cli.basic_ui_element.DEF_OK_STATUS module
        global variable (constant) value or explicitely sets the 'private'
        attribute _strStatus to that value. The second option is preferable for
        the sub-menus, since the value returned by the event handler, which
        has caused the loop termination, is returned as a string by this method.
        
        Signature:
            None -> str
        """
        while self._strStatus != DEF_OK_STATUS:
            self._show()
            strSelection = raw_input()
            strSelection = strSelection.lower()
            if strSelection in self._dictOptions:
                funHandler = getattr(self,
                                    self._dictOptions[strSelection]['command'])
                strResult = str(funHandler())
                if self._strStatus != DEF_OK_STATUS:
                    self._strStatus = strResult
            else:
                self._strStatus = 'Wrong selection! Try again!'
        return strResult
