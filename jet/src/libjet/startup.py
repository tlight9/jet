import os

from functools import partial

from PyQt6.QtWidgets import QLabel, QComboBox, QPlainTextEdit, QListWidget
from PyQt6.QtWidgets import QPushButton, QSlider, QWidget, QVBoxLayout
from PyQt6.QtGui import QTextCursor
from PyQt6.QtOpenGLWidgets import QOpenGLWidget

import linuxcnc
import hal

from libjet import commands
from libjet import editor

def check_required(parent):
	required_buttons = ['estop_pb', 'power_pb', 'run_pb', 'stop_pb']
	for button in required_buttons:
		if not parent.findChild(QPushButton, button):
			print(f'Required QPushButton {button} missing')
			sys.exit()


def set_menu_items(parent):
	if len(parent.status.file) > 0:
		parent.actionReload.setEnabled(True)
		print('here')

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
	'tool_lb', 'jog_units_lb', 'feed_lb',
	'speed_lb',	'tool_offset_lb', 'tool_diam_lb', 'inpos_lb']
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

def setup_mdi(parent):
	for button in parent.findChildren(QPushButton):
		if button.property('function') == 'mdi':
			#print(f'{button.objectName()} {button.property("function")}')
			props = button.dynamicPropertyNames()
			for prop in props:
				prop = str(prop, 'utf-8')
				if prop == 'command':
					cmd = button.property(prop)
					getattr(parent, f'{button.objectName()}').clicked.connect(partial(commands.run_mdi, parent, cmd))

def postgui_hal(parent):
	postgui_halfiles = parent.inifile.findall("HAL", "POSTGUI_HALFILE") or None
	if postgui_halfiles is not None:
		for f in postgui_halfiles:
			if f.lower().endswith('.tcl'):
				res = os.spawnvp(os.P_WAIT, "haltcl", ["haltcl", "-i", parent.ini_path, f])
			else:
				res = os.spawnvp(os.P_WAIT, "halcmd", ["halcmd", "-i", parent.ini_path, "-f", f])
			if res: raise SystemExit(res)

def setup_hal(parent):
	for button in parent.findChildren(QPushButton):
		if button.property('function') == 'hal_pin':
			#print(f'{button.objectName()} {button.property("function")}')
			props = button.dynamicPropertyNames()
			for prop in props:
				prop = str(prop, 'utf-8')
				if prop.startswith('pin_'):
					#print(f'prop {prop}')
					pin_settings = button.property(prop).split(',')
					name = button.objectName()
					#print(f'name {name}')
					pin_name = pin_settings[0]
					#print(f'pin_name {pin_name}')
					pin_type = getattr(hal, f'{pin_settings[1].upper().strip()}')
					#print(f'pin_type {pin_type}')
					pin_dir = getattr(hal, f'{pin_settings[2].upper().strip()}')
					#print(f'pin_dir {pin_dir}')
					parent.halcomp = hal.component('jet')
					#print(f'{parent.hal_comp.getprefix()}')
					#setattr(parent, f'{prop}', parent.hal_comp.newpin(pin_name, pin_type, pin_dir))
					#print(getattr(parent, f'{prop}').name)
					#print(parent.hal_comp[pin_name])
					#print(parent.hal_comp.getpins())
					#print(dir(parent.hal_comp))
					#print(f'parent.{prop}')
					setattr(parent, f'{prop}', parent.halcomp.newpin(pin_name, pin_type, pin_dir))
					getattr(parent, f'{name}').toggled.connect(lambda:
						getattr(parent, f'{prop}').set(getattr(parent, f'{name}').isChecked()))
					#pin = parent.hal_comp.newpin(pin_name, pin_type, pin_dir)
					#print(f'{parent.hal_comp.getpins()}')
					#self.test_hal.toggled.connect(lambda: self.out2.set(self.test_hal.isChecked()))
					#button.clicked.connect(lambda: getattr(parent, f'{prop}').name.set(True))
					#button.pressed.connect(lambda: hal.set_p(f'parent.{prop}', "True"))
					#button.toggled.connect(lambda: parent.hal_comp[pin_name], button.isChecked())


					#hal.component(f'{name}')
					# self.out2 = self.halcomp.newpin('out2', hal.HAL_BIT, hal.HAL_OUT)
					#test
					#print(f'test {test}')


					#print(f'name {name}')
					#setattr(parent, f'hal_{name}', hal.component(f'{name}'))

					'''
					setattr(parent, f'hal_{name}', None)
					test = 
					print(f'pin_name {pin_name}')
					getattr(parent, f'hal_{name}').ready()
					#print(button) self.out2.set(self.test_hal.isChecked()))
					
					'''


	'''

	parent.hal_test = hal.component('test')
	parent.hal_test.newpin('out', hal.HAL_BIT, hal.HAL_OUT)
	parent.hal_test.ready()
	parent.test_hal.pressed.connect(lambda: hal.set_p('test.out', "true"))


	#setattr(parent, f'c_{i}', None)
	#setattr(parent, f'c_{i}', hal.component('buttons'))
	#getattr(parent, f'c_{i}').newpin('out', hal.HAL_BIT, hal.HAL_OUT)
	#getattr(parent, f'c_{i}').ready()
	#setattr(parent, f'c_{i}', getattr(parent, f'c_{i}').newpin('out', hal.HAL_BIT, hal.HAL_OUT))
	#setattr(parent, f'c_{i}', getattr(parent, f'c_{i}').ready())



	#c = hal.component("buttons")
	#c.newpin('out', hal.HAL_BIT, hal.HAL_OUT)
	#c.ready()
	#print(hal.component_exists("buttons"))
	'''

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

