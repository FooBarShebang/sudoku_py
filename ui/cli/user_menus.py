#!/usr/bin/python
"""
Module sudoku_py.ui.cli.user_menus

Implementation of the specific menus used in the CLI of the program.

Classes:
    MainMenu
    HelpMenu
"""

__version__ = "0.0.1.1"
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
        of the program by exiting the main menu loop, since it sets the menu
        status to the sudoku_py.ui.cli.basic_ui_elements.DEF_OK_STATUS value.
        
        Signature:
            None -> str
        
        Returns:
            str: fixed value 'Exit from the main menu and the program'
        """
        sys.stdout.write('Bye!\n')
        self.Status = bue.DEF_OK_STATUS
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
    
    def onHelp(self):
        """
        Handler of the event - 'show help'. ...
        
        Signature:
            None -> str
        
        Returns:
            str: result of the action initiated by this menu item, i.e.
                the value returned by the help menu.
        """
        return self._launchChild()
    
    def onShowRecords(self):
        """
        Handler of the event - 'show high scores / records'. ...
        
        Signature:
            None -> str
        
        Returns:
            str: result of the action initiated by this menu item, i.e.
                the value returned by the help menu.
        """
        return 'onShowRecords'

class HelpMenu(bue.SimpleMenuCLI):
    """
    Help / information / usage menu of the CLI application.
    
    Subclasses sudoku_py.ui.cli.basic_ui_elements.SimpleMenuCLI.
    
    Methods:
        run()
            None -> str
    """
    
    #class fields
    
    _strMenuName = 'Help'
    
    #helper methods - event handlers
    
    def onBack(self):
        """
        Handler of the event - 'back to the previous menu'. ...
        
        Signature:
            None -> str
        
        Returns:
            str: result of the action initiated by this menu item, i.e.
                'Back from the help menu'.
        """
        self.Status = bue.DEF_OK_STATUS
        return 'Back from the help menu'