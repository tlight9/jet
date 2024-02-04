import os

from functools import partial

from PyQt6.QtWidgets import QLabel, QComboBox, QPlainTextEdit, QListWidget
from PyQt6.QtWidgets import QSlider, QWidget, QVBoxLayout
from PyQt6.QtGui import QTextCursor
from PyQt6.QtOpenGLWidgets import QOpenGLWidget

import linuxcnc

from libjet import commands
from libjet import editor

def set_menu_items(parent):
	if len(parent.status.file) > 0:
		parent.actionReload.setEnabled(True)

def setup_plot(parent):
	if parent.findChild(QWidget, 'plot_widget'):
		parent.plot = QOpenGLWidget()
		layout = QVBoxLayout(parent.plot_widget)
		layout.addWidget(parent.plot)

def set_labels(parent):
	# search for label widgets
	label_list = ['status_lb', 'file_lb',
	'dro_lb_x', 'dro_lb_y', 'dro_lb_z',
	'motion_line_lb', 'start_line_lb',
	'min_jog_vel_lb', 'max_jog_vel_lb',
	'jog_vel_lb', 'g_codes_lb', 'm_codes_lb',
	'g5x_offsets_lb', 'g92_offsets_lb',
	'interp_state_lb', 'task_state_lb',
	'tool_lb', 'jog_units_lb']
	children = parent.findChildren(QLabel)
	found_label_list = []
	for child in children:
		found_label_list.append(child.objectName())

	for label in label_list: # set a variable for exists
		if label in found_label_list:
			setattr(parent, f'{label}_exists', True)
		else:
			setattr(parent, f'{label}_exists', False)

def setup_jog(parent):
	if parent.findChild(QSlider, 'jog_vel_s'):
		parent.status.poll()
		jog_min = parent.inifile.find('DISPLAY', 'MIN_LINEAR_VELOCITY') or False
		jog_default = parent.inifile.find('DISPLAY', 'DEFAULT_LINEAR_VELOCITY') or False
		jog_max = parent.inifile.find('DISPLAY', 'MAX_LINEAR_VELOCITY') or False
		if jog_min:
			jog_min = int(float(jog_min))
		else:
			jog_min = 0
		parent.jog_vel_s.setMinimum(jog_min)
		if jog_max:
			jog_max = int(float(jog_max) * 60)
			parent.jog_vel_s.setMaximum(jog_max)
		if jog_default:
			jog_default = int(float(jog_default) * 60)
			parent.jog_vel_s.setValue(jog_default)
		if parent.min_jog_vel_lb_exists:
			parent.min_jog_vel_lb.setText(f'{parent.jog_vel_s.minimum()}')
		if parent.max_jog_vel_lb_exists:
			parent.max_jog_vel_lb.setText(f'{parent.jog_vel_s.maximum():.1f}')
		if parent.jog_units_lb_exists:
			linear_units = parent.inifile.find('TRAJ', 'LINEAR_UNITS') or False
			if linear_units == 'inch':
				parent.jog_units_lb.setText('in/min')
			else:
				parent.jog_units_lb.setText('mm/min')

def load_combos(parent):
	combo_list = ['jog_modes_cb']
	children = parent.findChildren(QComboBox)
	found_combo_list = []
	for child in children:
		found_combo_list.append(child.objectName())
	if 'jog_modes_cb' in found_combo_list:
		parent.jog_modes_cb.addItem('Continuous', False)
		increments = parent.inifile.find('DISPLAY', 'INCREMENTS') or False
		#print(increments)
		# INCREMENTS = 1 in, 0.1 in, 10 mil, 1 mil, 1mm, .1mm, 1/8000 in
		if increments:
			for item in increments.split():
				data = ''
				for char in item:
					if char.isdigit() or char == '.':
						data += char
			#print(data)
			# parent.jog_modes_cb.addItem(item, float(data))

def set_buttons(parent):
	if parent.status.task_state == linuxcnc.STATE_ESTOP_RESET:
		commands.estop_toggle(parent)

def get_list_widgets(parent):
	if parent.findChild(QListWidget, 'mdi_history_lw') is not None:
		parent.mdi_history_lw_exists = True
	else:
		parent.mdi_history_lw_exists = False

def get_pte(parent):
	if parent.findChild(QPlainTextEdit, 'gcode_pte'):
		parent.gcode_pte_exists = True
		parent.last_line = parent.status.motion_line
		parent.gcode_pte.setCenterOnScroll(True)
		parent.gcode_pte.ensureCursorVisible()
		parent.gcode_pte.viewport().installEventFilter(parent)
		if parent.status.file:
			with open(parent.status.file) as f:
				while line := f.readline():
					parent.gcode_pte.appendPlainText(line.strip())
			cursor = parent.gcode_pte.textCursor()
			cursor.movePosition(QTextCursor.MoveOperation.Start)
			parent.gcode_pte.setTextCursor(cursor)
	else:
		parent.gcode_pte_exists = False

def load_mdi(parent):
	if parent.findChild(QListWidget, 'mdi_history_lw') is not None:
		path = os.path.dirname(parent.status.ini_filename)
		mdi_file = os.path.join(path, 'mdi_history.txt')
		if os.path.exists(mdi_file): # load mdi history
			with open(mdi_file, 'r') as f:
				history_list = f.readlines()
				for item in history_list:
					parent.mdi_history_lw.addItem(item.strip())

def print_constants(parent):
	print(f'MODE_MANUAL = {parent.emc.MODE_MANUAL}')
	print(f'TRAJ_MODE_COORD = {parent.emc.TRAJ_MODE_COORD}')
	print(f'TRAJ_MODE_FREE = {parent.emc.TRAJ_MODE_FREE}')
	print(f'TRAJ_MODE_TELEOP = {parent.emc.TRAJ_MODE_TELEOP}')
	print(f'MODE_MDI = {parent.emc.MODE_MDI}')
	print(f'MODE_AUTO = {parent.emc.MODE_AUTO}')
	print(f'MODE_MANUAL = {parent.emc.MODE_MANUAL}')
	print(f'JOG_STOP = {parent.emc.JOG_STOP}')
	print(f'JOG_CONTINUOUS = {parent.emc.JOG_CONTINUOUS}')
	print(f'JOG_INCREMENT = {parent.emc.JOG_INCREMENT}')
	print(f'RCS_DONE = {parent.emc.RCS_DONE}')
	print(f'RCS_EXEC = {parent.emc. RCS_EXEC}')
	print(f'RCS_ERROR = {parent.emc.RCS_ERROR}')
	print(f'INTERP_IDLE = {parent.emc.INTERP_IDLE}')
	print(f'INTERP_READING = {parent.emc.INTERP_READING}')
	print(f'INTERP_PAUSED = {parent.emc.INTERP_PAUSED}')
	print(f'INTERP_WAITING = {parent.emc.INTERP_WAITING}')
	print(f'STATE_ESTOP = {parent.emc.STATE_ESTOP}')
	print(f'STATE_ESTOP_RESET = {parent.emc.STATE_ESTOP_RESET}')
	print(f'STATE_ON = {parent.emc.STATE_ON}')
	print(f'STATE_OFF = {parent.emc.STATE_OFF}')

def test(parent):
	parent.status.poll()
	#print(parent.emc.INTERP_PAUSED)
	#print(parent.emc.STATE_ON)
	#print(int.bit_count(parent.status.axis_mask))
	#print(parent.status.joints)
	#print(parent.status.spindles)
	#for i in range(parent.status.axes):
	#	print(parent.status.g5x_offset[i])
	#print(parent.status.g5x_offset)
	#print(parent.status.g5x_index)
	#pass
	
	'''
	tabname = 'status_tab'
	#print(parent.tabWidget.findChild(QWidget, 'status_tab'))
	page = parent.tabWidget.findChild(QWidget, tabname)
	print(page)
	index = parent.tabWidget.indexOf(page)
	print(index)
	parent.tabWidget.setCurrentWidget(parent.tabWidget.findChild(QWidget, tabname))
	#print(page)
	#parent.tabWidget.setCurrentWidget(parent.tabWidget.findChild(QWidget, 'Status'))
	'''

