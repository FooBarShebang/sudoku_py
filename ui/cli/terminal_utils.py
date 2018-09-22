#!/usr/bin/python
"""
Module sudoku_py.ui.cli.terminal_utils

Defines utility functions for simple but often required operations, amongst
others:
    *) clearing of the console
    *) emulation of the fixed size console of the smaller width than the actual
    *) emulation of the paginated output of a large text

Functions:
    ClearConsole()
        None -> None
    PrintFW()
        type A\, int OR None\ -> None
    PrintLess()
        \type A\, type B\, ...\\\ -> None
"""

__all__ = ['ClearConsole', 'PrintFW', 'PrintLess']
#in order to hide helper functions from 'from <...> import *'

#imports

#+ standard libraries

import sys
import os
import platform
import collections

#+ other modules from the package

from sudoku_py.ui.cli.terminal_size import GetTerminalSize

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
    are stored in a buffer unicode string, until the LF ('\n') character is
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
    ('\n') character. If a positive integer is provided the produced string is
    spit up into the sub-strings no longer than that length, and each is printed
    out on its own line in the terminal. The additional LF character is also
    added to the last line.
    
    Signature:
        type A\, int OR None\ -> None
    
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

def _PrintPage(ustrPrintBuffer):
    """
    Helper function, which prints out each string in the passed sequence of
    strings and adds LF ('\n') into each; aftewards prints a prompt message and
    awaits user input. The returned boolean value is defined by the user input.
    
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
        sys.stdout.write('---LESS (type q+Enter to exit)---')
        strResult = raw_input()
        if strResult.lower() == 'q':
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
        \type A\, type B\, ...\\\ -> None
    
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
