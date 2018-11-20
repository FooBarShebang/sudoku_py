# sudoku_py

Playground for CLI utilities and logic / combinatorics algorithms development

## Goal

This project aims for creation of a Sudoku game client, thus it can be played by a human user, as well as of the puzzle generator and solver. Not only the classic 3 x 3 puzzles are concerned, but the generic m x n fields.

The interaction with the user is planned to be implemented with CLI (console) as well as with GUI using various frameworks.

## Package Structure

* **core**
* **docs**
* **resourses**
* **ui**
  - **cli**
    + [basic_ui_elements.py](./ui/cli/basic_ui_elements.py)
    + [keystroke_linux.py](./ui/cli/keystroke_linux.py)
    + [keystroke_windows.py](./ui/cli/keystroke_windows.py)
    + [terminal_size.py](./ui/cli/terminal_size.py)
    + [terminal_utils.py](./ui/cli/terminal_utils.py)
    + [user_menus.py](./ui/cli/user_menus.py)
* [sudoku_py_cli.py](./sudoku_py_cli.py)


## Documentation

The documenation is written in the form of the text files using Markdown format, and it is organized in the hierarhy mirroring the source code modules / packages structure. The entire documentation is placed within the [**docs**](./docs/index.md) folder.

* **core**
* [**ui**](./docs/ui.md)
  - [**cli**](./docs/ui_cli.md)
    + basic_ui_elements.py
    + [keystroke_linux.py](./docs/ui_cli_keystroke_linux.md)
    + [keystroke_windows.py](./docs/ui_cli_keystroke_windows.md)
    + [terminal_size.py](./docs/ui_cli_terminal_size.md)
    + [terminal_utils.py](./docs/ui_cli_terminal_utils.md)
    + user_menus.py
* sudoku_py_cli.py
