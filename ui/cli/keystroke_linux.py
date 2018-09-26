#!/usr/bin/python
"""
Module sudoku_py.ui.cli.keystroke_linux

Implementation of the keystroke listener for the POSIX platforms. Do not import
on the non POSIX OSes! The main class KeyboardListenerLinux must be instantiated
and no more than a single istance of it must exist at any time. Make sure to
delete the previous instance before creating a new one. Also do no forget to
explicitely delete the last remaining instance before exiting the program.
Otherwise the console will behave strangly as well as some sdtin related
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

__version__ = "0.0.1.0"
__date__ = "26-09-2018"
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

DEF_TIME_DELAY = 0.05
# waiting time for the stdin quering; N.B. may need to adjust it for the
#+ specific computer, since it effects the 'responsiveness' of the queries
DEF_LIFE_TIME = 5.0
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
    available exactly one character (ASCII - one byte!) is read out and send
    into the buffer.
    
    Upon exit (or exception) tries to set the terminal back to the intial state.
    If this happends during the automatic garbage collection at the exit from
    a program, the stdin can be no longer available, so the terminal will remain
    in the 'raw' mode. This function is intended to be run in a separate thread,
    so make sure to stop the listening and terminate the thread manually before
    exiting the program.
    
    Note that the duration of the stdin quering per itteration (waiting) is
    defined by the module global variable (constant) DEF_TIME_DELAY
    
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
                InputBuffer.put(Char)
    except:
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
    Buffer to accumulate the raw input from the stdin (as bytes sequence),
    group the received bytes into proper ASCII ESC-CSI sequences of UTF-8
    encode unicode characters and to perform the decoding of the unicode
    bytestrings into the proper unicode characters / strings.
    
    Implements double buffer scheme: the input buffer (as ASCII / byte string)
    is populated from the sdtin by a listener function running in a separate
    thread; the output buffer (unicode string) is populated by this class itself
    from the input buffer as soon as a proper ASCII ESC-CSI or UTF-8 encoded
    unicode byte sequence is accumulated in the input buffer (for the proper
    ASCII characters - just one byte). The data put into the output buffer
    expires after DEF_LIFE_TIME (module global variable), and it is cleared out
    periodically, unless it is already taken out by get() method call.
    
    Attributes:
        IsReady: bool, read-only property with the True state indicating that
            there is data available in the output buffer
    
    Methods:
        put()
            str -> None
        get()
            None -> unicode
    """
    
    #special methods
    
    def __init__(self):
        """
        Initialization of the 'private' instance data attributes.
        
        Signature:
            None -> None
        """
        self._strBuffer = ''
        self._strOutBuffer = u''
        self._NotESC_CSI = True
        self._dLastTime = time.time()
    
    #helper private methods
    
    def _checkOutBufferLifeTime(self):
        """
        Private helper method for checking how long the output buffer holds the
        last stored data, and to clean that buffer if the critical time has
        passed, as defined by the module global variable DEF_LIFE_TIME (const).
        
        This method is called automatically with each transfer to or from the
        buffer as well as during the check for the available data.
        
        Signature:
            None -> None
        """
        dCurrentTime = time.time()
        if (dCurrentTime - self._dLastTime) > DEF_LIFE_TIME:
            self._strOutBuffer = u''
            self._dLastTime = dCurrentTime
    
    def _transferBuffer(self):
        """
        Private helper method for transfering the bytes accumulated in the input
        buffer (as encoded unicode characters) into the output buffer as the
        decoded unicode characters. The transfer will not occur until the input
        buffer contains the proper 'utf-8' encoded unicode sequence of bytes.
        
        Signature:
            None -> None
        """
        self._checkOutBufferLifeTime()
        bResult = False
        if len(self._strBuffer):
            try:
                self._strOutBuffer += self._strBuffer.decode('utf-8')
                self._strBuffer = ''
                bResult = True
                self._dLastTime = time.time()
            except UnicodeDecodeError:
                pass
        return bResult
    
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
        self._checkOutBufferLifeTime()
        return len(self._strOutBuffer) > 0
    
    def put(self, strData):
        """
        Method to put one or more characters (ASCII or encoded unicode) into the
        internal buffer for the analysis, splitting / grouping and, finally,
        transfer into the output buffer.
        
        Signature:
            str -> None
        """
        self._checkOutBufferLifeTime()
        for Char in strData:
            if Char == '\x1b': #ESC or part of the unicode encoded character
                if not len(self._strBuffer): #first ESC, may be part of CSI
                    self._NotESC_CSI = False
                elif not self._NotESC_CSI: #second ESC
                    self._strOutBuffer += unicode(self._strBuffer)
                    self._strBuffer = ''
                    self._dLastTime = time.time()
                else: #part of the unicode encoded
                    self._NotESC_CSI = True
            self._strBuffer += Char
            iLen = len(self._strBuffer)
            if not self._NotESC_CSI: #check for known ESC-CSI codes
                bCond1 = (iLen == 2 and Char != '[' and Char != 'O')
                bCond2 = (iLen == 3 and self._strBuffer.startswith('\x1bO'))
                bCond3 = (iLen == 3 and
                        not (Char in ['1', '2', '3', '4', '5', '6', '7', '8']))
                bCond4 = (iLen >= 4 and Char == '~')
                if bCond1 or bCond2 or bCond3 or bCond4:
                    self._NotESC_CSI = True
            if self._NotESC_CSI:
                if not self._strBuffer.startswith('\x1b'):
                    self._transferBuffer()
                else:
                    self._strOutBuffer += unicode(self._strBuffer)
                    self._strBuffer = ''
                    self._dLastTime = time.time()
                    if Char == '\x1b':
                        self._strBuffer = Char
                        self._NotESC_CSI = False
    
    def get(self):
        """
        Method to retrieve the content of the ouput buffer. Note that the output
        buffer is checked for how long the data is stored because of the call to
        the property IsReady, which may result in clearing of the buffer. So,
        either call this method directly after the check for the data
        availability with the property IsReady, or check the result is it None
        or a unicode string.
        
        Signature:
            None -> unicode OR None
        
        Returns:
            unicode: the entire content of the output buffer if it is not empty
            None: if the output buffer is empty
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
    the ASCII ESC-CSI sequences (as generated by the console itself), which are
    stored as ASCII codes in the unicode string. Real unicode characters (e.g.
    Russian keyboard, etc.) are treated properly if the underlying console
    treats the keystrokes as the UTF-8 encoded sequence of bytes.
    
    In some cases may return two last keystrokes in the single string, however
    in the proper order. This is especially the issue with the special keys
    (ASCII ESC-CSI sequences) followed by a 'normal' key.
    
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
        self.InputQueue = InputBufferLinux()
        self.objStopper = threading.Event()
        self.InputThread = None
        self.InputThread = threading.Thread(
                                        target=ReadSTDIN_NonBlocking_Linux,
                                        args=(self.InputQueue, self.objStopper))
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
                (decoded) or ASCII ESC-CSI characters sequence in an unicode
                string; N.B. sometimes, especially a the escape sequence
                followed by a 'normal' character, may return 2 last keystrokes
                in the proper order but in the single unicode string
        """
        ustrInput = u''
        while not len(ustrInput):
            ustrTemp = self.InputQueue.get()
            if not (ustrTemp is None):
                ustrInput = ustrTemp
            else:
                time.sleep(2 * DEF_TIME_DELAY)
        return ustrInput