#!/usr/bin/python
"""
"""

#imports

#+ standard libraries

import sys

#+ my libraries

#+ other modules from the package

from sudoku_py.ui.cli.basic_ui_elements import SimpleMenuCLI

#classes

class MainMenu(SimpleMenuCLI):
    """

    Methods:
        run()
            None -> str
    """
    
    #class fields
    
    _strMenuName = 'Main'
    
    #helper methods - event handlers
    
    def onExit(self):
        """
        """
        sys.stdout.write('Bye!\n')
        sys.exit(0)
    
    def onNewGame(self):
        """
        """
        return 'onNewGame'
    
    def onLoadGame(self):
        """
        """
        return 'onLoadGame'
    
    def onSolvePuzzle(self):
        """
        """
        return 'onSolvePuzzle'
    
    def onGeneratePuzzle(self):
        """
        """
        return 'onGeneratePuzzle'
