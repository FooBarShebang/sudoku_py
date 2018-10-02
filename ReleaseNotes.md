# Release Notes

## 2018-10-02 v0.0.1.2

Implemented CLI utilities:

* keystroke listener -> key press detection instead of **raw_input**() call
  - paginated text output to the console is updated to use the keystroke listener

Modified CLI menu features:

* user prompt loop is the menu is updated to use the keystroke listener

## 2018-09-24 v0.0.1.0

Implemented CLI utilities:

* clear console
* fixed width text output to the console
* paginated text output to the console

Impelemented CLI menu features:

* creation and display of the menu defined by a configuration file
* interactive user input prompt loop
* launch of the children objects, such as sub-menus, dialogs, etc. in response to the menu item choice as defined in the configuration file
* automatic check on the existance of the required event handler methods, 'children' classes (sub-menus, etc.) and their configuration files