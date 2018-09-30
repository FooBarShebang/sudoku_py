# Module ui.cli.keystroke_linux

## Goals

This module implements the POSIX OS (e.g., LInux) specific keyboard listener, which should detect a keyboard`s key press event and return a string (unicode) representation of the pressed key. This module is complementary to the MS Winsdows keystroke listener implementation (see [documentation](./ui_cli_keystroke_windows.md)), as it is defined in the problem analysis for the ui.cli.terminal_utils module (see [documentation](./ui_cli_terminal_utils.md))

The expected *modus operandi* is that a CLI user interface element (menu, dialog, etc.) will wait for the user input (key press) and perform some action afterwards based on the user input. Therefore, the process of the keyboard listening may be blocking. Such an UI element will expect either a Latin letter (small or capital, no diacritic signs) or a number entered by the user as the choice of an item / option. Thus, for instance, Shift+'1' keypress (resulting in the '!' character with English QWERTY layout) is not a valid input, which should be clearly differentiated from the plain '1' key press. In short, the result returned by the keyboard listener should be identical to the situation when a single character is entered via **stdin** (using **raw_input**() function), but without the necessity to finish the input with the Enter key. This also means that a letter key press using non-English keyboard layout may result in a different character being returned.

## Requirements

* The 'normal' keys - Latin letters (capital and small), numbers, arithmetic signs, punctuation signs, etc. - i.e. all characters with ASCII codes from 32 ('\x20') to 126 ('\x7e') inclusively - must be captured and properly represented; i.e. the keystroke 'q' + Shift (without Caps Lock) or simply 'q' with the Caps Lock should yield 'Q', '[' with Shift - '{', etc.
* The keys corresponding to the control symbols within ASCII - Esc, Backspace, Enter, Tab - must also be captured and returned in an unambiguous manner - either as C escape sequences '\r', '\b', '\t', or by their hex-code, e.g., '\x1b'
* The 'special' keys - cursor keys, Delete, Insert, Home, End, PageUp, PageDown, etc., which are represented by the (platform specific) escape sequences - must be captured and returned as an unambiguous string, e.g., as hex-code
* The 'modifier' keys - Shift, Alt, Ctrl - alone should not be registered as a key press, only in combination with the key that they modify; the resulting control sequences (like Cntrl-C, etc.) should be treated in the same way as the 'special' keys above
* The true Unicode characters as the resul of the key press on the non-English keyboard layout (e.g. Cyrillic) must be detected and properly represented as a Unicode character (u'\uxxxx' format)

## Problem Analysis

Upon internet search the popular solutions are:

* treat **stdin** as a file and read just one character (at the time) using **sys.stdin.read(1)**
* use the standard library **curses**
* use third party libraries, like **pygame**

The last option is unacceptable, because the design choice for the whole project is to minimize the dependence on the third party packages and to use only the standard library functionality as much as possible. The second option, technically, is not more elegant or simple as the first one, so the first option has been chosen.

The main obstacle is that in the usual mode the input from the **stdin** is not available, until the Enter key is pressed. Thus, even if a single (letter or number) key is pressed, and the corresonding character is sent to **stdin**, it cannot be read out until the Enter key is pressed. In other words, exactly as with the **raw_input**() function. The walk-around is to put the console into the 'raw' mode (using **tty** or **fcntl** modules), read the first byte in the buffer of the **stdin** and set the console back to the 'usual' (cbreak) mode, see References [^1] to [^4]. It is absolutely imperative to put the console back into the cbreak mode, otherwise the console output will be 'broken'. Basically, the '\n' (LF) character issued, for instance, by the **print** statement after the printed symbols will only move the console cursor to the next line, but it will not move it left to the beginning of the line. Thus, the explicit issue of the '\r' (CR) character will be required before each new line.

The other problem with this approach is that the **sys.stdin.read(1)** call will block the execution of the program if the **stdin** buffer is currently empty until it receives at least one byte. There is a way to overcome this blocking by periodically asking the **stdin** if it has anything in its bufer (using **select.select**(), see References [^1] to [^4]) before attempting to read from it. In between the checks on the data availability some useful activity may be performed.

Even better approach is to put the function listening the **stdin** into a separate thread (Reference [^2]), which will populate some buffer, whereas another function (in the main thread) will periodically check that buffer and take input from it. As soon as the required user input (keystrokes) is obtained, the **stdin** listening process can be stopped by sending an event (Reference [^5]) or directly setting some flag variable visible to the listening thread even if the buffer is not depleated. The advantage of this approach is that the keyboard listening becomes asynchrous and non-blocking. Therefore, it is selected for the implementation.

During the implementation and testing on Linux Mint (19, Mate edition, 64 bit) two effects have been found:

* a letter key press with non-English layout (Russian Cyrillic to be specific), naturally, generates a Unicode character, e.g. u'\u044f', which is sent into the **stdin** UTF-8 encoded as a *sequence* of bytes (2 bytes for the Cyrillic characters)
* a 'special' key press, as cursor keys, PageUp, Delete, etc., generate a control sequence of ASCII characters starting with ESC ('\x1b'), known as ESC-CSI, with the different length (2 to 5 characters); and the rest of the sequence (after the ESC) is not avilable until any other key (including 'special') is pressed afterwards

The issue of a keystroke being represented by more than a single byte is resolved using double buffering and analysis of the current input.

The potential problem is that the user may press some keys (even unintentionally) between the calls to the buffer. For example, a user may press some keys in between the menus, BEFORE he was prompted for the input. Thus, the buffer will return not the key, which the user wanted to press in response to the prompt, but the first key pressed after the last buffer check. To address this situation the buffer has a finite 'lifetime' of the data whithin, and it clears periodically the not claimed input.

### References

[^1] [Stackoverflow question 21791621](htts://stackoverflow.com/questions/21791621/)

[^2] [Stackoverflow question 292095](htts://stackoverflow.com/questions/292095/)

[^3] [Stackoverflow question 2408560](htts://stackoverflow.com/questions/2408560/)

[^4] [MagMax at GitHub](https://github.com/magmax/python-readchar) . Original authors are [Danny Yo & Stephen Chappel at code.activestate.com](http://code.activestate.com/recipes/134892)

[^5] [Stackoverflow question 18018033](htts://stackoverflow.com/questions/18018033/)

## Design

## Usage

```python
from sudoku_py.ui.cli.keystroke_linux import KeyboardListenerLinux
#instantiate the listener class - the second thread is started!
MyListener = KeyboardListenerLinux()
#listening loop
while SomeCondition:
    Key = MyListener.GetKeystroke()
    #do something useful
#do not forget to 'delete' the object / stop the second thread as soon as you
#don`t need it anymore
del MyListener
#do some other stuff
```

## API Reference

### Globals

DEF_TIME_DELAY = 0.05 : positive floating point, the delay time in seconds, during which the **stdin** is queried for the available data and determins the rate at which the bytes are taken from the standard input

DEF_LIFE_TIME = 5.0 : positive floating point, the effective 'lifetime' in seconds of the data in the buffer before it is erased unless claimed. The time elapsed since the last transfer into the buffer is compared to this value, and the data is erased if this time threshold has been exceeded. Note that if another keystroke is registered during this time period, the new data is simply added to the buffer and the time counter is reset.

Both values should be adjusted for the 'pace' of the application, i.e. how often the input from the user is required.

### Functions

#### ReadSTDIN_NonBlocking_Linux(InputBuffer, Stopper)

Signature:

InputBufferLinux, threading.Event -> None

Args:

  - *InputBuffer*: InputBufferLinux instance, where the data from the sdtin will be placed
  - *Stopper*: threading.Event instance, used as an indicator to stop listen to the **stdin**; use the method **stop**() of this object to do so

Description:

Implements the listening to the stdin in the non-blocking manner. Changes the console to the 'raw' mode (via tty module). Enters the loop, which can be stopped by setting the Stopper object in the corresponding state, and queries the stdin for the available data (using select.select). If data is available exactly one character (ASCII - one byte!) is read out and send into the buffer.

Upon exit (or exception) tries to set the terminal back to the intial state. If this happends during the automatic garbage collection at the exit from a program, the stdin can be no longer available, so the terminal will remain in the 'raw' mode. This function is intended to be run in a separate thread, so make sure to stop the listening and terminate the thread manually before exiting the program.

Note that the duration of the stdin quering per itteration (waiting) is defined by the module global variable (constant) DEF_TIME_DELAY.

### class InputBufferLinux

Buffer to accumulate the raw input from the stdin (as bytes sequence), group the received bytes into proper ASCII ESC-CSI sequences of UTF-8 encode unicode characters and to perform the decoding of the unicode bytestrings into the proper unicode characters / strings.

Implements double buffer scheme: the input buffer (as ASCII / byte string) is populated from the sdtin by a listener function running in a separate thread; the output buffer (unicode string) is populated by this class itself from the input buffer as soon as a proper ASCII ESC-CSI or UTF-8 encoded unicode byte sequence is accumulated in the input buffer (for the proper ASCII characters - just one byte). The data put into the output buffer expires after DEF_LIFE_TIME (module global variable), and it is cleared out periodically, unless it is already taken out by get() method call.

#### Instance Attributes

  - *IsReady*: bool, read-only property with the True state indicating that there is data available in the output buffer
  - *_strBuffer*: ASCII string, 'private', the input buffer; the data received from the **stdin** is stored here before transfer to the output buffer
  - *_strOutBuffer*: unicode string, 'private', the output buffer
  - *_NotESC_CSI*: bool, 'private', internal flag used for the processing of the input buffer to treat the ESC-CSI properly
  - *_dLastTime*: positive floating point, 'private', time is seconds passed since the last data transfer from the input into the output buffer

#### Initialization

No arguments are required, and none is accepted

#### Instance Methods

**_checkOutBufferLifeTime**()

Signature:

None -> None

Description:

Private helper method for checking how long the output buffer holds the last stored data, and to clean that buffer if the critical time has passed, as defined by the module global variable DEF_LIFE_TIME (const).

This method is called automatically with each transfer to or from the buffer as well as during the check for the available data.

**_transferBuffer**()

Signature:

None -> None

Description:

Private helper method for transfering the bytes accumulated in the input buffer (as encoded unicode characters) into the output buffer as the decoded unicode characters. The transfer will not occur until the input buffer contains the proper 'utf-8' encoded unicode sequence of bytes.

**put**(strData)

Signature:

str -> None

Args:

  - *strData*: string, ASCII supposedly, the data to be put into the input buffer

Description:

Method to put one or more characters (ASCII or encoded unicode) into the internal buffer for the analysis, splitting / grouping and, finally, transfer into the output buffer.

**get**()

Signature:

None -> unicode OR None

Returns:

  - *unicode*: the entire content of the output buffer if it is not empty
  - *None*: if the output buffer is empty

Description:

Method to retrieve the content of the ouput buffer. Note that the output buffer is checked for how long the data is stored because of the call to the property *IsReady*, which may result in clearing of the buffer. So, either call this method directly after the check for the data availability with the property IsReady, or check the result is it None or a unicode string.

### class KeyboardListenerLinux

Linux (POSIX) specific implementation of the keyboard listener, which detects and returns (as a unicode string) the made keystroke. The special keys, like F1 to F12, PageUp / PageDown, cursor keys, etc. are returned as the ASCII ESC-CSI sequences (as generated by the console itself), which are stored as ASCII codes in the unicode string. Real unicode characters (e.g. Russian keyboard, etc.) are treated properly if the underlying console treats the keystrokes as the UTF-8 encoded sequence of bytes.

In some cases may return two last keystrokes in the single string, however in the proper order. This is especially the issue with the special keys (ASCII ESC-CSI sequences) followed by a 'normal' key.

Make sure to 'destroy' an existing instance of this class before creating a new one, as well as to explicitely 'destroy' the last used instance before exiting the program. Otherwise the console will behave strangly as well as some sdtin related threading problems may occur.

#### Instance Attributes

  - *InputQueue*: InputBufferLinux class instance, the buffer to store the processed input received from the **stdin**
  - *objStopper*: threading.Event class instance, helper event object used only for stoping the keyboard listener
  - *InputThread*: treading.Thread instance, the secondary thread, where the keyboard listener function is run

#### Initialization

No arguments are required, and none is accepted

#### Instance Methods

**GetKeystroke**()

Signature:

None -> unicode

Returns:

  - *unicode*: the last registered keystroke as a unicode character (decoded) or ASCII ESC-CSI characters sequence in an unicode string; N.B. sometimes, especially a the escape sequence followed by a 'normal' character, may return 2 last keystrokes in the proper order but in the single unicode string

Description:

Blocking method, which listens to the keyboard input (keystroke), until such event is registered, and returns it. Based on the periodic quering the buffer object for the available processed data. If data is available the entire buffer is copied and returned; the buffer itself is cleared.

Otherwise the method sleeps for the twice the time period defined by the module global variable (const) DEF_TIME_DELAY before the next query. The buffer itself is populated asynchroniously from the stdin using another thread.

## Tested Platforms

* Linux Mint 19 (Tara) 64 bit (kernel v4.15.0-34) with CPython v2.7.15rc1 64 bit
  - In Visual Studio Code v1.27.2
  - In Geany v1.32 (Bemos)
  -  Directly in Mate Terminal v1.20.0