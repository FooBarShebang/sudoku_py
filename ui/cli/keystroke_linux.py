#!/usr/bin/python
"""
Module sudoku_py.ui.cli.keystroke_linux

Implementation of the keystroke listener for the POSIX platforms. Do not import
on the non POSIX OSes! The main class KeyboardListenerLinux must be instantiated
and no more than a single istance of it must exist at any time. Make sure to
delete the previous instance before creating a new one. Also do no forget to
explicitely delete the last remaining instance before exiting the program.
Otherwise the console will behave strangely as well as some sdtin related
threading problems may occur.

Based upon the ideas from
    *) https://stackoverflow.com/questions/2408560/
    * https://stackoverflow.com/questions/21791621/
    *) https://stackoverflow.com/questions/18018033/
    *) https://stackoverflow.com/questions/292095/
    *) https://github.com/magmax/python-readchar
        Danny Yoo (http://code.activestate.com/recipes/134892/)

Tested on:
    1) Linux Mint 19 (Tara) 64 bit (kernel v4.15.0-34) with CPython v2.7.15rc1
    64 bit
        *) In Visual Studio Code v1.27.2
        *) In Geany v1.32 (Bemos)
        *) Directly in Mate Terminal v1.20.0

Classes:
    InputBufferLinux
    KeyboardListenerLinux

Functions:
    ReadSTDIN_NonBlocking_Linux()
        InputBufferLinux, threading.Event -> None
"""

__version__ = "0.0.1.1"
__date__ = "02-10-2018"
__status__ = "Production"

#imports

#+ standard libraries

import sys
import termios
import tty
import select
import threading
import time

#globals

DEF_TIME_DELAY = 0.005
# waiting time for the stdin quering; N.B. may need to adjust it for the
#+ specific computer, since it effects the 'responsiveness' of the queries
DEF_LIFE_TIME = 0.5
#the shortest guaranteed 'lifetime' of the processed characters in the buffer;
#+ after that the buffer is cleared out to prevent accumulation of the
#+ keystrokes, which were made well before the time of the current query

#functions

def ReadSTDIN_NonBlocking_Linux(InputBuffer, Stopper):
    """
    Implements the listening to the stdin in the non-blocking manner. Changes
    the console to the 'raw' mode (via tty module). Enters the loop, which can
    be stopped by setting the Stopper object in the corresponding state, and
    queries the stdin for the available data (using select.select). If data is
    available the buffer of the stdin is read out one byte at a time, and the
    data is stored in the internal buffer of the function, until a proper bytes
    sequence is accumulated, which is converted into Unicode (and decoded using
    UTF-8 if required) and sent out.
    
    Common situations:
    * 1st read byte is '\x1b' - either a single ESC or CSI / SS3 sequence - read
        more bytes until a proper sequence is formed:
        - '\x1bO' + any ASCII character - 3 bytes SS3 sequence
        - '\x1b[' + any letter (ASCII char), but not a number - CSI 3 bytes
        - '\x1b[' + 1 or more numbers + '~' - CSI 4+ bytes with a terminator
        - An ESC ('\x1b') read before an end of a proper CSI / SS3 sequence is
            treated a broken sequence; the previous input is dropped, a new
            sequence is started
        - Any other character which breaks the CSI / SS3 patterns above leads to
            discarding the previous input; the last received character is
            treated as the first byte in an ASCII / Unicode symbol input, see
            below
    * 1st byte is not '\x1b' but is less then '\x80' - proper ASCII character
    * 1st byte is greater than '\x7f' - part of the UTF-8 encoded Unicode
        character - accumulate more bytes until decoding can be properly
        performed (check with each obtained byte)
        - If accumulated sequence is longer than 4 bytes, drop the first byte
            and try to decode; if fails - keep on getting new bytes and dropping
            the first one until can be decoded
    
    Upon exit (or exception) tries to set the terminal back to the intial state.
    If this happends during the automatic garbage collection at the exit from
    a program, the stdin can be no longer available, so the terminal will remain
    in the 'raw' mode. This function is intended to be run in a separate thread,
    so make sure to stop the listening and terminate the thread manually before
    exiting the program.
    
    Note that the duration of the stdin quering per itteration (waiting) is
    defined by the module global variable (constant) DEF_TIME_DELAY
    
    Known Issues:
        * An ESC key alone cannot be detected, will wait until another key press
        * ESC + any key but '[' or 'O' (capital leter O) - the last key alone
            is registered, ESC is dropped
        * ESC + 'O' + any byte < '\x80' - treated as an SS3 sequence, which may
            be incorrect
        * ESC + 'O' + any byte > '\x80' - ESC + 'O' is dropped, the rest is
            processed as an Unicode character
        * ESC + 'O' + any byte < '\x80' but not a number '1' to '8' - treated as
            a CSI 3butes sequence, which may be incorrect
        * ESC + '[' + any number '1' to '8' - treated as 3+ bytes CSI sequence,
            which may be:
            - properly ended with '~'
            - continued with any number ('0' to '9')
            - terminated with any not number character; anything but the last
                byte is dropped, the last byte is processed as a new control or
                ASCII / Unicode character byte sequence
        * ESC + '[' + any byte > '\x80' - ESC + '[' is dropped, the rest is
            processed as an Unicode character
    
    Signature:
        InputBufferLinux, threading.Event -> None
    
    Args:
        InputBuffer: InputBufferLinux instance, where the data from the sdtin
            will be placed
        Stopper: threading.Event instance, used as an indicator to stop listen
            to the stdin; use the method stop() of this object to do so.
    """
    try:
        iFileDescriptor = sys.stdin.fileno()
        lstOldSettings = termios.tcgetattr(iFileDescriptor)
        tty.setraw(iFileDescriptor)
        while not Stopper.is_set():
            InputStream, _, _= select.select([sys.stdin], [], [],
                                                                DEF_TIME_DELAY)
            if InputStream:
                Char = sys.stdin.read(1)
                if Char == '\x1b': #single ESC or CSI / SS3 sequence
                    bIsCSI = True
                    while bIsCSI:
                        NewChar = sys.stdin.read(1)
                        if NewChar == '\x1b':
                            #second ESC or a new CSI / SS3 sequence to get
                            #+ drop the previous input
                            Char = NewChar
                        elif Char == '\x1b' and NewChar in ['[', 'O']:
                            #second char in CSI / SS3 sequence - Ok, continue
                            Char += NewChar
                        elif Char == '\x1bO':
                            if NewChar <= '\x7f':
                                #SS3 sequence is complete, stop getting
                                Char += NewChar
                            else:
                                #broken sequence, drop previous input
                                Char = NewChar
                            bIsCSI = False
                        elif Char == '\x1b[':
                            #3rd char in CSI sequence
                            if NewChar > '\x7f':
                                #broken sequence, drop previous input
                                bIsCSI = False
                                Char = NewChar
                            elif not NewChar in ['1', '2', '3', '4', '5', '6',
                                                                    '7', '8']:
                                #got the last char, stop
                                bIsCSI = False
                                Char += NewChar
                            else:
                                #3+ bytes CSI - keep on getting
                                Char += NewChar
                        elif len(Char) >= 3:
                            #must be CSI ending with ~
                            if NewChar == '~':
                                #CSI sequence is complete, stop getting
                                Char += NewChar
                                bIsCSI = False
                            elif NewChar in ['0', '1', '2', '3', '4', '5', '6',
                                                                '7', '8', '9']:
                                #CSI sequence with 2 or more numbers, continue
                                Char += NewChar
                            else:
                                #broken CSI sequence, drop previous input
                                Char = NewChar
                                bIsCSI = False
                        else:
                            #broken CSI sequence, drop previous input
                            Char = NewChar
                            bIsCSI = False
                if Char.startswith('\x1b'):
                    #ESC CSI / SS3 sequence is obtained
                    InputBuffer.put(unicode(Char))
                else:
                    #not a ESC CSI / SS3 sequence - might be ASCII or Unicode
                    bNotReady = True
                    while bNotReady:
                        try:
                            ustrNewChar = Char.decode('utf-8')
                            Char = ustrNewChar
                            bNotReady = False
                            #decoding pass, sequence is complete, send away
                        except UnicodeDecodeError:
                            Char += sys.stdin.read(1)
                            #try with +1 byte
                        if len(Char) > 4 and (not bNotReady):
                            #safeguard, should not get here from the real
                            #+ keyboard - too long for proper Unicode
                            Char = Char[1:]
                    InputBuffer.put(Char)
    except Exception as err:
        print err
        pass
    finally:
        try:
            iFileDescriptor = sys.stdin.fileno()
            termios.tcsetattr(iFileDescriptor, termios.TCSADRAIN,
                                                                lstOldSettings)
        except:
            pass

#classes

class InputBufferLinux(object):
    """
    Buffer to store the processed input from the stdin. Intended to be used as
    an instance shared by two threads: the stdin listener and the 'user
    interface' object. The input from the stdin is supposed to be already
    processed, i.e. it may be:
        * An ASCII character (< u'u0080'), which may be represented by a single
            byte using UTF-8 encoding, stored as a unicode string
        * A non ASCII Unicodecharacter (>= 'u0080'), which is represented by 2
            or more byte using UTF-8 encoding, stored as a unicode string
        * An ESC CSI / SS3 sequence of 3 or more ASCII characters (bytes)
            starting with '\xb1O' or '\xb1[' and stored as a unicode string,
            e.g. u'xb1[A' for up arrow cursor key press
    
    Any input received from the stdin listener purges the previous data from the
    buffer, puts the received data into the buffer and resets the data counter.
    
    The unclaimed data is removed from the buffer and not returned to the 'user
    interface' is the data timer has expired, i.e. the data have been stored
    for longer than DEF_LIFE_TIME (global variable).
    
    When the data is claimed by the 'user interface', its is removed from the
    buffer and returned (unless expired) to the caller. The data timer is reset.
    
    Attributes:
        IsReady: bool, read-only property with the True state indicating that
            there is data available.
    
    Methods:
        put()
            str OR unicode -> None
        get()
            None -> unicode
    """
    
    #special methods
    
    def __init__(self):
        """
        Initialization of the 'private' instance data attributes: the buffer
        itself and the data timer.
        
        Signature:
            None -> None
        """
        self._strOutBuffer = u''
        self._dLastTime = time.time()
    
    #public API
    
    @property
    def IsReady(self):
        """
        Read-only property with the True state indicating that there is data
        available in the output buffer. Performs the check on how long the
        current data is already stored, which may result in clearing of the
        buffer.
        
        Signature:
            None -> bool
        
        Returns:
            bool: True if the output buffer contains some data and its not yet
                outdated (will be removed automatically), otherwise - false
        """
        dCurrentTime = time.time()
        if (dCurrentTime - self._dLastTime) > DEF_LIFE_TIME:
            self._strOutBuffer = u''
            self._dLastTime = dCurrentTime
        return len(self._strOutBuffer) > 0
    
    def put(self, ustrData):
        """
        Method to put one or more characters (ASCII or encoded unicode) into the
        buffer. Each such trnsfer clears the buffer from the previously stored
        content and resets the data timer.
        
        Signature:
            str OR unicode-> None
        
        Args:
            strData: string, unicode supposedly, the data to be put into the
                buffer
        """
        self._strOutBuffer = unicode(ustrData)
        self._dLastTime = time.time()
    
    def get(self):
        """
        Method to retrieve the content of the buffer. Note that the buffer is
        checked for how long the data is stored by calling the property IsReady,
        which may result in clearing of the buffer. So, either call this method
        directly after the check for the data availability with the property
        IsReady, or check the result is it None or a unicode string.
        
        Signature:
            None -> unicode OR None
        
        Returns:
            unicode: the entire content of the buffer if it is not empty
            None: if the buffer is empty
        """
        if self.IsReady:
            strlstData = unicode(self._strOutBuffer)
            self._strOutBuffer = u''
            self._dLastTime = time.time()
        else:
            strlstData = None
        return strlstData

class KeyboardListenerLinux(object):
    """
    Linux (POSIX) specific implementation of the keyboard listener, which
    detects and returns (as a unicode string) the made keystroke. The special
    keys, like F1 to F12, PageUp / PageDown, cursor keys, etc. are returned as
    the ASCII CSI or SS3 sequences (as generated by the console itself), which
    are stored as ASCII codes in the unicode string. Real unicode characters
    (e.g. generated by the Russian keyboard layout, etc.) are treated properly
    if the underlying console treats the keystrokes as the UTF-8 encoded
    sequence of bytes.
    
    Make sure to 'destroy' an existing instance of this class before creating
    a new one, as well as to explicitely 'destroy' the last used instance before
    exiting the program. Otherwise the console will behave strangly as well as
    some sdtin related threading problems may occur.
    
    Methods:
        GetKeystroke()
            None -> unicode
    """
    
    #special methods
    
    def __init__(self):
        """
        Initialization. Starts the stdin listening in a separate thread.
        
        Signature:
            None -> None
        """
        self.InputBuffer = InputBufferLinux()
        self.objStopper = threading.Event()
        self.InputThread = threading.Thread(
                                    target=ReadSTDIN_NonBlocking_Linux,
                                    args=(self.InputBuffer, self.objStopper))
        self.InputThread.daemon = True
        self.InputThread.start()
    
    def __del__(self):
        """
        Destructor method. Makes sure that the bound thread for the stdin
        listening is terminated.
        
        Signature:
            None -> None
        """
        if self.InputThread.isAlive():
            self.objStopper.set()
            self.InputThread.join()
        del self.InputThread
        self.InputThread = None
    
    #public API
    
    def GetKeystroke(self):
        """
        Blocking method, which listens to the keyboard input (keystroke), until
        such event is registered, and returns it. Based on the periodic quering
        the buffer object for the available processed data. If data is available
        the entire buffer is copied and returned; the buffer itself is cleared.
        
        Otherwise the method sleeps for the twice the time period defined by the
        module global variable (const) DEF_TIME_DELAY before the next query. The
        buffer itself is populated asynchroniously from the stdin using another
        thread.
        
        Signature:
            None -> unicode
        
        Returns:
            unicode: the last registered keystroke as a unicode character
                (decoded) or ASCII CSI or SS3 characters sequence in an unicode
                string
        """
        ustrInput = u''
        while not len(ustrInput):
            ustrTemp = self.InputBuffer.get()
            if not (ustrTemp is None):
                ustrInput = ustrTemp
            else:
                time.sleep(2 * DEF_TIME_DELAY)
        return ustrInput