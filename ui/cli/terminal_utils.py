#!/usr/bin/python
"""
Module sudoku_py.ui.cli.terminal_utils

Defines utility functions for simple but often required operations, amongst
others:
    *) clearing of the console
    *) emulation of the fixed size console of the smaller width than the actual
    *) emulation of the paginated output of a large text
    *) listening for a keystroke event

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
    3) MS Windows 10 (Home, 64 bit) with CPython v2.7.15 64 bit
        *) In Visual Studio Code v1.27.2

Functions:
    ClearConsole()
        None -> None
    PrintFW()
        type A/, int OR None/ -> None
    PrintLess()
        /type A/, type B/, .../// -> None
    GetKeystroke()
        None -> unicode
"""

__version__ = "0.0.1.1"
__date__ = "27-09-2018"
__status__ = "Development"

__all__ = ['ClearConsole', 'PrintFW', 'PrintLess', 'GetKeystroke']
#in order to hide helper functions from 'from <...> import *'

#imports

#+ standard libraries

import sys
import os
import platform
import collections

#+ other modules from the package

from sudoku_py.ui.cli.terminal_size import GetTerminalSize

#+ platform specific imports

try:
    from sudoku_py.ui.cli.keystroke_linux import KeyboardListenerLinux
except:
    try:
        from sudoku_py.ui.cli.keystroke_windows import KeyboardListenerWindows
    except:
        pass

#functions

def ClearConsole():
    """
    Clears the console by issueing control symbols sequence in the case of the
    POSIX systems, calling system function 'cls' for the MS Windows systems, or
    by requesting the current height of the console and printing the
    corresponding amount of the LF characters for the other systems.
    
    Signature:
        None -> None
    """
    strCurrentOS = platform.system()
    bCond1 = strCurrentOS == 'Linux'
    bCond2 = strCurrentOS == 'Darwin'
    bCond3 = strCurrentOS.startswith('CYGWIN')
    bCond4 = strCurrentOS == 'Windows'
    if bCond1 or bCond2 or bCond3:
        sys.stdout.write('\033[H\033[J')
    elif bCond4:
        iFault = os.system('cls')
        if iFault:
            _, iLines = GetTerminalSize()
            strLine = '\n' * (iLines + 1)
            sys.stdout.write(strLine)
            sys.stdout.flush()
    else:
        _, iLines = GetTerminalSize()
        strLine = '\n' * (iLines + 1)
        sys.stdout.write(strLine)
        sys.stdout.flush()

def _SplitString(strLine, iColumns):
    """
    Helper functions, which splits the passed string (ASCII or Unicode) into a
    list of the unicode sub-strings. The passed string (first argument) is
    treated as a stream, and is read-out per character. The extracted characters
    are stored in a buffer unicode string, until the LF (ASCII 10) character is
    encountered or the buffer string becomes of iColumns or greater length, or
    the end of the passed string is reached. In all cases the current buffer
    string is copied into the list of the sub-strings to be returned and is
    reset to the zero length. The LF character is not copied, whereas the other
    characters which caused the reset of the buffer, are copied into the the
    buffer after its reset.
    
    Signature:
        str OR unicode, int -> list(unicode)
    
    Args:
        strLine: ASCII or Unicode string to be split
        iColumns: positive integer, the expected length of the split
            sub-strings
    
    Raises:
        TypeError: the first argument is not a string or the second argument is
            not an integer number
        ValueError: the second argument is zero or negative
    """
    if not isinstance(strLine, basestring):
        raise TypeError('Not an string as the first argument')
    if not isinstance(iColumns, (int, long)):
        raise TypeError('Not an integer number of columns')
    if iColumns < 1:
        raise ValueError('Not positive number of columns')
    iLength = len(strLine)
    if iLength:
        ustrlstBuffer = []
        ustrTempLine = u''
        for ustrChar in strLine:
            if ustrChar != '\n' and (
                                (len(ustrTempLine)+len(ustrChar)<=iColumns)):
                ustrTempLine = u''.join([ustrTempLine, ustrChar])
            elif ustrChar != '\n':
                ustrlstBuffer.append(ustrTempLine)
                ustrTempLine = u'{}'.format(ustrChar)
            else:
                ustrlstBuffer.append(ustrTempLine)
                ustrTempLine = u''
        if len(ustrTempLine):
            ustrlstBuffer.append(ustrTempLine)
    else:
        ustrlstBuffer = [u'']
    return ustrlstBuffer

def PrintFW(gItem, iColumns = None):
    """
    Print function designed for the emulation of the different than actual width
    of the fixed consoles or of the fixed console output on the actually
    horizontally scrollable consoles.
    
    The first passed argument (of any type) is converted into a Unicode string;
    for the class instances the __str__() method is looked up first, and the
    __repr__() - as the fallback option. The second (optional or keyword)
    argument defines the mode of operation. If it is not provided or None, the
    consructed unicode string is printed out as it is but with an additional LF
    (ASCII 10) character. If a positive integer is provided the produced string
    is spit up into the sub-strings no longer than that length, and each is
    printed out on its own line in the terminal. The additional LF character is
    also added to the last line.
    
    Signature:
        type A/, int OR None/ -> None
    
    Args:
        strLine: ASCII or Unicode string to be split
        iColumns: non-negative integer, the expected length of the split
            sub-strings; value greater than the actual console width will result
            in improper lines splitting
    
    Raises:
        TypeError: the second (optional) argument is not None or an integer
            number
        ValueError: the second argument is zero or negative integer
    """
    if iColumns is None:
        sys.stdout.write(u'{}\n'.format(gItem))
    else:
        ustrLine = u'{}'.format(gItem)
        sys.stdout.write(u'{}\n'.format(u'\n'.join(_SplitString(ustrLine,
                                                                    iColumns))))

def GetKeystroke():
    """
    Keyboard listener. Waits until a keystroke is received and returns it as
    a unicode string. Normal keys (including localized, e.g. Russian, layouts)
    are returned as a single unicode character. The special keys, as cursor
    keys, page up / down, F1, etc., are returned as escape sequences specific to
    a platform. In case of POSIX systems - ASCII ESC-CSI, i.e. sequence of bytes
    within a unicode string (the first character is ESC '\x1b'). With the MS
    Windows - 2 bytes control sequences starting with '\x00' or '\xe0'.
    
    On POSIX systems may return more than one last keystroke, especially if a
    special key (ASCII ESC-CSI) was followed by a 'normal' key.
    
    Unicode support. On POSIX systems the byte code generated by the stdin input
    are converted into the proper Unicode characters (u'\u...') using UTF-8, and
    they can be displayed directly in the console. On Windows (at least,
    Windows 8) the unicode characters are already properly generated in the
    u'\u...' form, but they cannot be displayed in the console.
    
    Signature:
        None -> unicode
    
    Returns:
        unicode: a proper unicode character (decoded!) or an escape sequence
            (platform depended) in a unicode string
    
    Raises:
        Exception: not supported platform / OS
    """
    if 'KeyboardListenerLinux' in globals():
        objTemp = KeyboardListenerLinux()
        ustrResult = objTemp.GetKeystroke()
        del objTemp
    elif 'KeyboardListenerWindows' in globals():
        ustrResult = KeyboardListenerWindows.GetKeystroke()
    else:
        raise Exception('Not supported OS platform')
    return ustrResult

def _PrintPage(ustrPrintBuffer):
    """
    Helper function, which prints out each string in the passed sequence of
    strings and adds LF (ASCII 10) into each; aftewards prints a prompt message
    and awaits the user input, which defines the returned boolean value.
    
    Signature:
        seq(str OR unicode) -> bool
    
    Args:
        ustrPrintBuffer: any sequence of ASCII or Unicode strings
    
    Returns:
        bool: False if the user typed 'Q' or 'q', True otherwise
    
    Raises:
        TypeError: if the passed argument is not a sequence of strings
    """
    bCond1 = isinstance(ustrPrintBuffer, collections.Sequence)
    bCond2 = not isinstance(ustrPrintBuffer, basestring)
    if bCond1 and bCond2:
        bCond3 = all(isinstance(gItem, basestring) for gItem in ustrPrintBuffer)
        if not bCond3:
            raise TypeError('Not a sequence of strings')
        for ustrLine in ustrPrintBuffer:
            sys.stdout.write('{}\n'.format(ustrLine))
        sys.stdout.write('---LESS (press q or Q to exit)---')
        sys.stdout.flush()
        strResult = GetKeystroke()
        sys.stdout.write('\n')
        strResult = strResult.lower()
        if strResult in [u'q', u'Q']:
            return False
        return True
    else:
        raise TypeError('Not a sequence of strings')

def PrintLess(*args):
    """
    Emulates the paginated output (as in less / more console commands) based on
    the current size of the console / terminal. Each passed argument is
    converted into a unicode string and is treated as a separate paragraph, i.e.
    new line (LF) is added after the output of each argument. Thus, if a text is
    stored as a sequence of strings, this sequence must be passed unpacked.
    
    Each generated unicode string is split into sub-strings of lengths not
    exceeding the console width (see _SplitString() function). All sub-strings
    generated from all passed arguments are printed onto the console
    sequentially but in 'pages' with the number of lines equal to the console
    height minus one (or less for the last 'page'). At the bottom of each 'page'
    except the last one the user is prompted. One can type 'q' (case
    insensitive) and press Enter to terminate the output. Any other user input
    will proceed to the next 'page'.
    
    Signature:
        /type A/, type B/, .../// -> None
    
    Args:
        *args: any number of arguments of any type
    """
    ustrPrintBuffer = []
    bContinue = True
    if len(args):
        iColumns, iLines = GetTerminalSize()
    else:
        iColumns, iLines = 0, 0
    for gItem in args:
        ustrTemp = u'{}'.format(gItem)
        ustrlstTemp = _SplitString(ustrTemp, iColumns)
        for ustrLine in ustrlstTemp:
            ustrPrintBuffer.append(ustrLine)
            if len(ustrPrintBuffer) == iLines - 1:
                bContinue = _PrintPage(ustrPrintBuffer)
                ustrPrintBuffer = []
                if not bContinue:
                    break
        if not bContinue:
            break
    if len(ustrPrintBuffer):
        for ustrLine in ustrPrintBuffer:
            sys.stdout.write('{}\n'.format(ustrLine))
