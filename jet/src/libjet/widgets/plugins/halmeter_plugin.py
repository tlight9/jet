#!/usr/bin/env python3
"""

halmeter_plugin.py - Qt Designer Hook

Written by Chad Woitas
"""

from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtDesigner import QPyDesignerCustomWidgetPlugin
from libjet.widgets.halmeter_widget import HalMeterWidget
import os


class HalMeterWidgetPlugin(QPyDesignerCustomWidgetPlugin):
	def __init__(self, parent=None):
		super(HalMeterWidgetPlugin, self).__init__(parent)
		self.initialized = False

	def initialize(self, core):
		if self.initialized:
			return

		self.initialized = True

	def isInitialized(self):
		return self.initialized

	def createWidget(self, parent):
		return HalMeterWidget(parent=parent, sim=True)

	def name(self):
		# Must be Class name
		return "halmeter_widget"

	def group(self):
		# Where Should designer, display these widgets
		return "Jet Widget"

	def icon(self):
		# TODO
		return QIcon(QPixmap(None))

	def toolTip(self):
		return ""

	def whatsThis(self):
		return ""

	def isContainer(self):
		return False

	# Returns an XML description of a custom widget instance that describes
	# default values for its properties. Each custom widget created by this
	# plugin will be configured using this description.
	def domXml(self):
		# Class is the class name per import file
		# Name is the default name given the object in the UI/python generated file
		return '<widget class="halmeter_widget" name="halmeter_widget" />\n'

	def includeFile(self):
		return "libjet.widgets.halmeter_widget"
