#!/usr/bin/python
"""
Module sudoku_py.ui.cli.terminal_size

Defines multiple 'helper' functions but only one 'public' function designed for
the use outside the module. It attempts to obtain the console / terminal
emulation frame size as in columns (width) x lines (height) using various
approaches depending on the current OS and Python installation. If all methods
fail - returns the default (e.g. 80 x 25) size; which values are controlled by
the module globals DEF_CONSOLE_COLUMNS and DEF_CONSOLE_LINES.

Inspired by and based upon the receipes proposed at the Stackoverflow web-site
    *) htts://stackoverflow.com/questions/566746/

This module is specific for the Python 2.7, and it is not required at all with
Python 3.3+.

Tested on:
    1) Linux Mint 19 (Tara) 64 bit (kernel v4.15.0-34) with CPython v2.7.15rc1
    64 bit
        *) In Visual Studio Code v1.27.2
        *) In Geany v1.32 (Bemos)
        *) Directly in Mate Terminal v1.20.0
    2) MS Windows 8 64 bit with CPython v2.7.9 32 bit
        *) In Visual Studio Code v1.27.2
        *) In Geany v1.24 (Sakai)
        *) Directly in the console
    3) MS Windows 8 64 bit with CPython v2.7.15 64 bit
        *) In Visual Studio Code v1.25.1
        *) In Geany v1.33 (Gorgon)
        *) Directly in the console
    4) MS Windows 10 64 bit with CPython v2.7.15 64 bit
        *) Directly in the console

It does not work properly within Eclipse PyDev environment and within IDLE
due to their console implementation. In these situations the default console
size will be returned.

Functions:
    GetTerminalSize()
        None -> (int, int)
"""

__version__ = "0.0.1.0"
__date__ = "24-09-2018"
__status__ = "Production"

__all__ = ['GetTerminalSize']
#in order to hide helper functions from 'from <...> import *'

#imports

#+ standard libraries, generic

import sys
import os
import platform
import subprocess
import struct
import ctypes

#+ standard libraries, OS-dependent (present for Linux)

try:
    import curses
except:
    pass

try:
    import termios
    import fcntl
except:
    pass

#global constants

DEF_CONSOLE_LINES = 25

DEF_CONSOLE_COLUMNS = 80

#functions

#+ helper / single option functions

def _GetWinSize_curses():
    """
    Atempts to define the console size using the curses module from the standard
    library. Available for the POSIX systems. On MS Windows platforms should
    always return None, since the curses module is not available there.
    
    Signature:
        None -> (int, int) OR None
    
    Returns:
        tuple(int, int): width (columns) and height (lines) of the console, if
            determined
        None: if failed to determine the console size
    """
    itupResult = None
    if 'curses' in sys.modules:
        try:
            objFrame = curses.initscr()
            iHeight, iWidth = objFrame.getmaxyx()
            curses.endwin()
            del objFrame
            itupResult = (iWidth, iHeight)
        except:
            pass
    return itupResult

def _GetWinSize_stty():
    """
    Atempts to define the console size by launching a subprocess and making a
    call to the stty system function. Available for the POSIX systems. On
    MS Windows platforms should always return None; might work within the
    CYGWIN environment though.
    
    Signature:
        None -> (int, int) OR None
    
    Returns:
        tuple(int, int): width (columns) and height (lines) of the console, if
            determined
        None: if failed to determine the console size
    """
    itupResult = None
    strCurrentOS = platform.system()
    bCond1 = strCurrentOS == 'Linux'
    bCond2 = strCurrentOS == 'Darwin'
    bCond3 = strCurrentOS.startswith('CYGWIN')
    if bCond1 or bCond2 or bCond3:
        try:
            ilstTemp=map(int, subprocess.check_output(['stty', 'size']).split())
            itupResult = (ilstTemp[1], ilstTemp[0])
        except:
            try: #to account for input redirection
                with open('/dev/tty') as tty:
                    ilstTemp = map(int,
                                    subprocess.check_output(['stty', 'size'],
                                                        stdin = tty).split())
                itupResult = (ilstTemp[1], ilstTemp[0])
            except:
                pass
    return itupResult

def _GetWinSize_tput():
    """
    Atempts to define the console size by launching a subprocess and making a
    call to the tput system function. Available for the POSIX systems. On
    MS Windows platforms should always return None, unless working within the
    CYGWIN environment.
    
    Signature:
        None -> (int, int) OR None
    
    Returns:
        tuple(int, int): width (columns) and height (lines) of the console, if
            determined
        None: if failed to determine the console size
    """
    itupResult = None
    strCurrentOS = platform.system()
    bCond1 = strCurrentOS == 'Linux'
    bCond2 = strCurrentOS == 'Darwin'
    bCond3 = strCurrentOS.startswith('CYGWIN')
    if bCond1 or bCond2 or bCond3:
        try:
            procTemp = subprocess.Popen(["tput", "cols"],
                            stdin = subprocess.PIPE, stdout = subprocess.PIPE)
            strseqOutput = procTemp.communicate(input = None)
            iWidth = int(strseqOutput[0])
            procTemp = subprocess.Popen(["tput", "lines"],
                            stdin = subprocess.PIPE, stdout = subprocess.PIPE)
            strseqOutput = procTemp.communicate(input = None)
            iHeight = int(strseqOutput[0])
            itupResult = (iWidth, iHeight)
        except:
            pass
    return itupResult

def _GetWinSize_ioctl():
    """
    Atempts to define the console size using the platform dependent modules
    fcntl and termios from the standard library, which are available for the
    POSIX systems. On MS Windows platforms should always return None; might work
    within the CYGWIN environment though.
    
    Signature:
        None -> (int, int) OR None
    
    Returns:
        tuple(int, int): width (columns) and height (lines) of the console, if
            determined
        None: if failed to determine the console size
    """
    itupResult = None
    bCond1 = 'termios' in sys.modules
    bCond2 = 'fcntl' in sys.modules
    if bCond1 and bCond2:
        for iFileDescriptor in [0, 1, 2]: #stdin, stdout, stderr
            try:
                iseqTemp = struct.unpack('hh', fcntl.ioctl(iFileDescriptor,
                                                    termios.TIOCGWINSZ, '1234'))
                itupResult = (int(iseqTemp[1]), int(iseqTemp[0]))
            except:
                pass
            if not (itupResult is None):
                break
        if itupResult is None:
            try:
                iFileDescriptor = os.open(os.ctermid(), os.O_RDONLY)
                iseqTemp = struct.unpack('hh', fcntl.ioctl(iFileDescriptor,
                                                    termios.TIOCGWINSZ, '1234'))
                os.close(iFileDescriptor)
                itupResult = (int(iseqTemp[1]), int(iseqTemp[0]))
            except:
                pass
    return itupResult

def _GetWinSize_windll():
    """
    Atempts to define the console size using the platform dependent module
    windll from the ctypes from the standard library, which is available for the
    MS Windows platforms. On POSIX systems should always return None.
    
    Signature:
        None -> (int, int) OR None
    
    Returns:
        tuple(int, int): width (columns) and height (lines) of the console, if
            determined
        None: if failed to determine the console size
    """
    itupResult = None
    if hasattr(ctypes, 'windll'):
        try:
            objHandle = ctypes.windll.kernel32.GetStdHandle(-12) #stderr
            cstrBuffer = ctypes.create_string_buffer(22)
            Temp = ctypes.windll.kernel32.GetConsoleScreenBufferInfo(objHandle,
                                                                    cstrBuffer)
            if Temp:
                (_, _, _, _, _, iLeft, iTop, iRight, iBottom, _, _) = (
                                struct.unpack("hhhhHhhhhhh", cstrBuffer.raw))
                iWidth = iRight - iLeft + 1
                iHeight = iBottom - iTop + 1
                itupResult = (iWidth, iHeight)
        except:
            pass
    return itupResult

def _GetWinSize_os_environ():
    """
    Atempts to define the console size using the data from the os.environ
    dictionary, if such is available. Useless on the most of the platforms.
    
    Signature:
        None -> (int, int) OR None
    
    Returns:
        tuple(int, int): width (columns) and height (lines) of the console, if
            determined
        None: if failed to determine the console size
    """
    itupResult = None
    bCond1 = 'LINES' in os.environ.keys()
    bCond2 = 'COLUMNS' in os.environ.keys()
    if bCond1 and bCond2:
        itupResult = (int(os.environ['COLUMNS']), int(os.environ['LINES']))
    return itupResult

def _GetWinSize_default():
    """
    Returns as a tuple the default width and height of the console using the
    values of the global constants. It is the ultimate fallback option and is
    useless otherwise.
    
    Signature:
        None -> (int, int)
    
    Returns:
        tuple(int, int): width (columns) and height (lines) of the console, as
            stored in DEF_CONSOLE_COLUMNS and DEF_CONSOLE_LINES global consts
    """
    return (int(DEF_CONSOLE_COLUMNS), int(DEF_CONSOLE_LINES))

#+ aggregation functions

def _GetWinSize_POSIX():
    """
    Attempts to define the console size using the POSIX platforms specific
    options in the following order:
        1) _GetWinSize_ioctl()
        2) _GetWinSize_stty()
        3) _GetWinSize_tput()
        4) _GetWinSize_curses()
    
    The first successful (not None result) call is returned; if all 4 methods
    have failed - the None value is returned.
    
    Signature:
        None -> (int, int) OR None
    
    Returns:
        tuple(int, int): width (columns) and height (lines) of the console, if
            determined
        None: if failed to determine the console size
    """
    itupResult = _GetWinSize_ioctl()
    if itupResult is None:
        itupResult = _GetWinSize_stty()
    if itupResult is None:
        itupResult = _GetWinSize_tput()
    if itupResult is None:
        itupResult = _GetWinSize_curses()
    return itupResult

def _GetWinSize_MSWIN():
    """
    Attempts to define the console size using the MS Windows platforms specific
    options in the following order:
        1) _GetWinSize_windll()
        2) _GetWinSize_tput()
    
    The first successful (not None result) call is returned; if the both methods
    have failed - the None value is returned.
    
    Signature:
        None -> (int, int) OR None
    
    Returns:
        tuple(int, int): width (columns) and height (lines) of the console, if
            determined
        None: if failed to determine the console size
    """
    itupResult = _GetWinSize_windll()
    if itupResult is None:
        itupResult = _GetWinSize_tput()
    return itupResult

#+ main function!

def GetTerminalSize():
    """    
    Attempts to define the console size using the platform specific options:
        *) _GetWinSize_POSIX() for POSIX systems
        *) _GetWinSize_MSWIN() for MS Windows systems
        *) _GetWinSize_os_environ() for other systems
    
    If the platform specific methods have failed, the fallback option is to
    return the values of the (module) global constants DEF_CONSOLE_COLUMNS and
    DEF_CONSOLE_LINES.
    
    Signature:
        None -> (int, int)
    
    Returns:
        tuple(int, int): width (columns) and height (lines) of the console
    """
    itupResult = None
    strCurrentOS = platform.system()
    bCond1 = strCurrentOS == 'Linux'
    bCond2 = strCurrentOS == 'Darwin'
    bCond3 = strCurrentOS.startswith('CYGWIN')
    bCond4 = strCurrentOS == 'Windows'
    if bCond1 or bCond2 or bCond3:
        itupResult = _GetWinSize_POSIX()
    elif bCond4:
        itupResult = _GetWinSize_MSWIN()
    else:
        itupResult = _GetWinSize_os_environ()
    if itupResult is None:
        itupResult = _GetWinSize_default()
    return itupResult

#testing area

if __name__ == '__main__':
    #the clear screen part is implemented as a separate function, here it is
    #reproduced to avoid circular dependency between the modules
    strCurrentOS = platform.system()
    bCond1 = strCurrentOS == 'Linux'
    bCond2 = strCurrentOS == 'Darwin'
    bCond3 = strCurrentOS.startswith('CYGWIN')
    bCond4 = strCurrentOS == 'Windows'
    if bCond1 or bCond2 or bCond3:
        sys.stdout.write('\033[H\033[J')
    elif bCond4:
        _ = os.system('cls')
    #actual self-test
    print "Performing self-test..."
    print "{} v {} ({}) on {}".format(platform.python_implementation(),
                                    platform.python_version(),
                                    platform.architecture(),
                                    platform.platform())
    print "Checking the GetTerminalSize options..."
    print "Using curses: {}".format(_GetWinSize_curses())
    print "Using stty: {}".format(_GetWinSize_stty())
    print "Using tput: {}".format(_GetWinSize_tput())
    print "Using ioctl: {}".format(_GetWinSize_ioctl())
    print "Using windll: {}".format(_GetWinSize_windll())
    print "Using os.environ: {}".format(_GetWinSize_os_environ())
    print "Using defaults: {}".format(_GetWinSize_default())
    print "Checking the aggregation functions..."
    print "Using all POSIX options: {}".format(_GetWinSize_POSIX())
    print "Using all MS Windows options: {}".format(_GetWinSize_MSWIN())
    print "Checking the main function GetTerminalSize()..."
    print GetTerminalSize()
