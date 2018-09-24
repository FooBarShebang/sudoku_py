#!/usr/bin/python
"""
Module sudoku_py.ui.cli.user_menus

Implementation of the specific menus used in the CLI of the program.

Classes:
    MainMenu
"""

__version__ = "0.0.1.0"
__date__ = "24-09-2018"
__status__ = "Development"

#imports

#+ standard libraries

import sys

#+ my libraries

#+ other modules from the package

import sudoku_py.ui.cli.basic_ui_elements as bue

#classes

class MainMenu(bue.SimpleMenuCLI):
    """
    Main menu of the CLI application.
    
    Subclasses sudoku_py.ui.cli.basic_ui_elements.SimpleMenuCLI.
    
    Methods:
        run()
            None -> str
    """
    
    #class fields
    
    _strMenuName = 'Main'
    
    #helper methods - event handlers
    
    def onExit(self):
        """
        Handler of the event - 'exit' from the program. Enforces the termination
        of the program.
        
        Signature:
            None -> None
        """
        sys.stdout.write('Bye!\n')
        self._strStatus = bue.DEF_OK_STATUS
        return 'Exit from the main menu and the program'
    
    def onNewGame(self):
        """
        Handler of the event - 'start new game'. ...
        
        Signature:
            None -> str
        
        Returns:
            str: result of the action initiated by this menu item, e.g.
                'Game played', 'Game cancelled', etc.
        """
        return 'onNewGame'
    
    def onLoadGame(self):
        """
        Handler of the event - 'load saved game'. ...
        
        Signature:
            None -> str
        
        Returns:
            str: result of the action initiated by this menu item, e.g.
                'Game played', 'Cancelled load', 'File load failed', etc.
        """
        return 'onLoadGame'
    
    def onSolvePuzzle(self):
        """
        Handler of the event - 'auto solve puzzle'. ...
        
        Signature:
            None -> str
        
        Returns:
            str: result of the action initiated by this menu item, e.g.
                'Puzzle solved', 'Cancelled puzzle solution', etc.
        """
        return 'onSolvePuzzle'
    
    def onGeneratePuzzle(self):
        """
        Handler of the event - 'create custom puzzle'. ...
        
        Signature:
            None -> str
        
        Returns:
            str: result of the action initiated by this menu item, e.g.
                'Custom puzzle created and saved', 'Cancelled puzzle creation',
                etc.
        """
        return 'onGeneratePuzzle'
