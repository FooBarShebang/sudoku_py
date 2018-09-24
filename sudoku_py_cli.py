#!/usr/bin/python
"""
Loader for the CLI version of the program.

Functions:
    run()
        None -> None
"""

__version__ = "0.0.1.0"
__date__ = "24-09-201"
__status__ = "Development"

#imports

import sys
import os

#+ my libraries

strTemp = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if not (strTemp in sys.path):
    sys.path.append(strTemp)

#+ other modules from the package

from sudoku_py.ui.cli.user_menus import MainMenu

#execution area

#globals

ROOT_FOLDER = os.path.dirname(os.path.realpath(__file__))
RESOURCES = os.path.join(ROOT_FOLDER, 'resources', 'cli')

#single and main function

def run():
    """
    Prepares the required objects and launces the CLI version of the program.
    
    Signature:
        None -> None
    """
    objMenu = MainMenu(os.path.join(RESOURCES, 'main_menu.json'))
    print objMenu.run()

if __name__ == '__main__':
    run()