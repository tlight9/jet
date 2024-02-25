#!/usr/bin/env python3
"""

jet_plugins.py - Qt Designer Hook
Written by  Chad Woitas

Notes:
    A Symlink must be created from:
       /usr/lib/x86_64-linux-gnu/qt5/plugins/designer/python/jet_plugin.py
    To This file. The important part of this link is it ends with _plugin.py,
    Both the file and the link are owned by root:root, and at least 666 permissions.

"""


# Print Out to see designer loaded it
# print("Loading Jet Plugins ============================")
# pylint: disable=wrong-import-position
# pylint: disable=unused-import

from libjet.widgets.plugins.halmeter_plugin import HalMeterWidgetPlugin

# print("Finished loading")