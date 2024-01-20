GUI Builder
===========

Installing the Qt Designer
--------------------------

In a terminal install the Qt Designer with:
::

	sudo apt install qttools5-dev-tools

Building a GUI
--------------

Run the Qt Designer from the Applications > Programming menu and select a
mainwindow.

Adding items from the side bar is drag and drop.

After dragging a widget into the window make sure you use the correct
objectName for that widget. For example the E Stop button is called estop_pb.

Save the GUI in the configuration directory where you launch LinuxCNC.
