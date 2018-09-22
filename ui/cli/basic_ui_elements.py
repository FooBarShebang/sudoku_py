#!/usr/bin/python
"""
Module sudoku_py.ui.cli.basic_ui_elements

Implements prototype classes for the basic interaction with the user in the
CLI mode, e.g. a configurable text menu, an input dialog, etc.

Classes:
    SimpleMenuCLI
"""

#imports

#+ standard libraries

import sys
import json
import collections

#+ other modules from the package

from sudoku_py.ui.cli.terminal_utils import ClearConsole, PrintFW

#classes

class SimpleMenuCLI(object):
    """
    
    Methods:
        run()
            None -> type A
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
        Signature:
            str, str -> type A
        
        Args:
            strClassName: string, name of the class implementing the submenu,
                dialog, etc.; will be looked up in the globals dictionary
            strSourceFile: string, of a configuration JSON file describing
                the submenu or dialog, etc. structure / content to be loaded
        
        Returns:
            type A: any type, which is returned by the child`s method run()
        """
        clsChild = globals(strClassName)
        objChild = clsChild(strSourceFile)
        gResult = objChild.run()
        del objChild
        return gResult
    
    def _show(self):
        """
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
        Signature:
            None -> type A
        """
        while self._strStatus != 'Ok':
            self._show()
            strSelection = raw_input()
            strSelection = strSelection.lower()
            if strSelection in self._dictOptions:
                self._strStatus = 'Ok'
                funHandler = getattr(self,
                                    self._dictOptions[strSelection]['command'])
                strResult = funHandler()
            else:
                self._strStatus = 'Wrong selection! Try again!'
        return strResult
