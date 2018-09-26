#!/usr/bin/python
"""
Module sudoku_py.ui.cli.keystroke_windows

Implementation of the keystroke listener for the MS Windows platforms. Do not
import it on the POSIX OSes! Based upon the msvcrt module from the standard
library.

Reworked idea from
    *) https://github.com/magmax/python-readchar
        Danny Yo & Stephen Chappell (http://code.activestate.com/recipes/134892)

Tested on:
    1) MS Windows 8 64 bit with CPython v2.7.9 32 bit
        *) In Visual Studio Code v1.27.2
        *) In Geany v1.24 (Sakai)
        *) Directly in the console

Classes:
    KeyboardListenerWindows
"""

__version__ = "0.0.1.0"
__date__ = "26-09-2018"
__status__ = "Production"

#imports

#+ standard libraries

import msvcrt

#classes

class KeyboardListenerWindows(object):
    """
    MS Windows specific implementation of the keyboard listener, which detects
    and returns (as a unicode string) the made keystroke. The special keys are
    returned as escape sequences - 2 bytes starting with '\x00' or '\xe0' within
    a unicode string. Unicode input is suported, e.g. Cyrillic, since the
    Windows console generates them properly, and they are captured as wide
    characters using msvcrt.getwch(). However, at least, on Windows 8, the
    console cannot display them.
    
    Does not have to be instantiated, since it defines a single class method.
    
    Methods:
        GetKeystroke()
            None -> unicode
    """
    
    @classmethod
    def GetKeystroke(cls):
        """
        Blocking class method to listen to the keyboard and to return the
        keystroke made as a unicode string.
        
        The special keys, as cursor keys, page up / down, F1, etc., are returned
        as escape sequences - 2 bytes starting with '\x00' or '\xe0' within a
        unicode string.
        
        Unicode support. The unicode characters are already properly generated
        in the u'\u...' form by the console input, but they cannot be displayed
        in the console, at least in Windows 7.
        
        Signature:
            None -> unicode
        
        Returns:
            unicode: the last registered keystroke as a unicode character
                or 2 bytes escape characters sequence in an unicode
                string, starting with either '\x00' or '\xe0'.
        """
        while True:
            if msvcrt.kbhit():
                uChar = msvcrt.getwch()
                if uChar in [u'\x00', u'\xe0']: #control character
                    uChar += msvcrt.getwch()
                break
        return uChar

