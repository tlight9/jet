INI Settings
============

To test on simulated hardware create a configuration with the Step Configuration
Wizard then modify the ini file.

.. note:: All settings are in the [DISPLAY] section of the ini file.

To use the EMC PyQt6 GUI set `DISPLAY = emc` after installing. If no GUI is
specificed then the default GUI will be used.

To use your ui file you created add `GUI = file-name.ui` 'f not entered then the
default ui file will be used.

To use your style sheet add `QSS = file-name.qss` if not entered then the default
qss file will be used.

.. note:: The user ui and qss files must be in the configuration directory.


