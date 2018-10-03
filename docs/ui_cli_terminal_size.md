# Module ui.cli.terminal_size

## Goals

## Requirements

## Problem Analysis

### References

[^1] [Stackoverflow question 566746](https://stackoverflow.com/questions/566746/how-to-get-linux-console-window-width-in-python)

## Design

## Usage

```python
from sudoku_py.ui.cli.terminal_size import GetTerminalSize()

Columns, Lines = GetTerminalSize()
```

## API Reference

### Globals

DEF_CONSOLE_LINES = 25 : integer, the default number of lines in the terminal, if the real size cannot be determined

DEF_CONSOLE_COLUMNS = 80 : integer, the default number of columns in the terminal, if the real size cannot be determined

### Functions

#### GetTerminalSize()

Signature:

None -> int, int

Returns:

  - **tuple(int, int)**: width (columns) and height (lines) of the console

Description:

Attempts to define the console size using the platform specific options:
  * _GetWinSize_POSIX() for POSIX systems
  * _GetWinSize_MSWIN() for MS Windows systems
  * _GetWinSize_os_environ() for other systems

If the platform specific methods have failed, the fallback option is to return the values of the (module) global constants DEF_CONSOLE_COLUMNS and DEF_CONSOLE_LINES.

## Tested Platforms

* Linux Mint 19 (Tara) 64 bit (kernel v4.15.0-34) with CPython v2.7.15rc1 64 bit
  - In Visual Studio Code v1.27.2
  - In Geany v1.32 (Bemos)
  - Directly in Mate Terminal v1.20.0
* MS Windows 8 64 bit with CPython v2.7.9 32 bit
  - In Visual Studio Code v1.27.2
  - In Geany v1.24 (Sakai)
  - Directly in the console
* MS Windows 8 64 bit with CPython v2.7.15 64 bit
  - In Visual Studio Code v1.25.1
  - In Geany v1.33 (Gorgon)
  - Directly in the console
* MS Windows 10 64 bit with CPython v2.7.15 64 bit
  - Directly in the console
  - In Visual Studio Code v1.27.2