
from PyQt6.QtGui import QTextCursor, QTextBlockFormat, QColor
from PyQt6.QtWidgets import QTextEdit, QWidget, QPushButton, QLabel

from libjet import utilities

def update(parent):
	parent.status.poll()

	if parent.mdi_command and parent.status.state == parent.emc.RCS_DONE:
		utilities.update_mdi(parent)

	task_mode = {1: 'MANUAL', 2: 'AUTO', 3: 'MDI'}
	if parent.status_lb_exists:
		parent.status_lb.setText(task_mode[parent.status.task_mode])
	if parent.dro_lb_x_exists:
		if parent.status.tool_in_spindle > 0:
			t_x = parent.status.tool_offset[0]
			t_y = parent.status.tool_offset[1]
			t_z = parent.status.tool_offset[2]
		else:
			t_x = 0
			t_y = 0
			t_z = 0
		g5x = parent.status.g5x_offset[0]
		parent.dro_lb_x.setText(f'{parent.status.position[0] - g5x - t_x:.4f}')
	if parent.dro_lb_y_exists:
		g5y = parent.status.g5x_offset[1]
		parent.dro_lb_y.setText(f'{parent.status.position[1] - g5y - t_y:.4f}')
	if parent.dro_lb_z_exists:
		g5z = parent.status.g5x_offset[2]
		parent.dro_lb_z.setText(f'{parent.status.position[2] - g5z - t_z:.4f}')
	if parent.tool_lb_exists:
		tool = parent.status.tool_in_spindle
		parent.tool_lb.setText(f'Tool: {tool}')
	if parent.feed_lb_exists:
		feed = round(parent.status.current_vel*60,2)
		parent.feed_lb.setText(f'Feed: {feed}')
	if parent.speed_lb_exists:
		speed = parent.status.spindle[0].get('speed')
		parent.speed_lb.setText(f'Speed: {speed}')
	if parent.tool_offset_lb:
			t_offset = parent.status.tool_table[0].zoffset
			parent.tool_offset_lb.setText(f'Tool Z Offset: {t_offset}')
	if parent.tool_diam_lb:
			t_diam = parent.status.tool_table[0].diameter
			parent.tool_diam_lb.setText(f'Tool Diam: {t_diam}')

#	Spindle dict
	if parent.findChild(QLabel, 's_brake_lb'):
		s_brake = parent.status.spindle[0]['brake']			
		parent.s_brake_lb.setText(f'Brake: {s_brake}')
	if parent.findChild(QLabel, 's_direction_lb'):
		s_direction = parent.status.spindle[0]['direction']		
		parent.s_direction_lb.setText(f'Direction: {s_direction}')
	if parent.findChild(QLabel, 's_enabled_lb'):
		s_enabled = parent.status.spindle[0]['enabled']		
		parent.s_enabled_lb.setText(f'Enabled: {s_enabled}')
	if parent.findChild(QLabel, 's_homed_lb'):
		s_homed = parent.status.spindle[0]['homed']
		parent.s_homed_lb.setText(f'Homed: {s_homed}')
#	POSSIBLY UNDEFINED
	if parent.findChild(QLabel, 's_increasing_lb'):
		s_increasing = parent.status.spindle[0].get('increasing')
		parent.s_increasing_lb.setText(f'Increasing: {s_increasing}')
	if parent.findChild(QLabel, 's_orient_fault_lb'):
		s_orient_fault = parent.status.spindle[0]['orient_fault']
		parent.s_orient_fault_lb.setText(f'Orient Fault: {s_orient_fault}')
	if parent.findChild(QLabel, 's_orient_state_lb'):
		s_orient_state = parent.status.spindle[0]['orient_state']
		parent.s_orient_state_lb.setText(f'Orient: {s_orient_state}')
	if parent.findChild(QLabel, 's_override_lb'):
		s_override = parent.status.spindle[0]['override']
		parent.s_override_lb.setText(f'Override: {s_override}')
	if parent.findChild(QLabel, 's_override_enabled_lb'):
		s_override_enabled = parent.status.spindle[0]['override_enabled']
		parent.s_override_enabled_lb.setText(f'Override En: {s_override_enabled}')
	if parent.findChild(QLabel, 's_speed_lb'):
		s_speed = parent.status.spindle[0]['speed']
		parent.s_speed_lb.setText(f'Speed: {s_speed}')

#	Joint dict
	if parent.findChild(QLabel, 'j_backlash_lb'):
		j_backlash = parent.status.joint[0]['backlash']
		parent.j_backlash_lb.setText(f'Backlash: {j_backlash}')
	if parent.findChild(QLabel, 'j_enabled_lb'):
		j_enabled = parent.status.joint[0]['enabled']
		parent.j_enabled_lb.setText(f'Enabled: {j_enabled}')
	if parent.findChild(QLabel, 'j_fault_lb'):
		j_fault = parent.status.joint[0]['fault']
		parent.j_fault_lb.setText(f'Fault: {j_fault}')
	if parent.findChild(QLabel, 'j_ferror_current_lb'):
		j_ferror_current = parent.status.joint[0]['ferror_current']
		parent.j_ferror_current_lb.setText(f'Ferror_current: {j_ferror_current}')
	if parent.findChild(QLabel, 'j_ferror_highmark_lb'):
		j_ferror_highmark = parent.status.joint[0]['ferror_highmark']
		parent.j_ferror_highmark_lb.setText(f'Ferror_highmark: {j_ferror_highmark}')
	if parent.findChild(QLabel, 'j_homed_lb'):
		j_homed = parent.status.joint[0]['homed']
		parent.j_homed_lb.setText(f'Homed: {j_homed}')
	if parent.findChild(QLabel, 'j_homing_lb'):
		j_homing = parent.status.joint[0]['homing']
		parent.j_homing_lb.setText(f'Homing: {j_homing}')
	if parent.findChild(QLabel, 'j_inpos_lb'):
		j_inpos = parent.status.joint[0]['inpos']
		parent.j_inpos_lb.setText(f'Inpos: {j_inpos}')
	if parent.findChild(QLabel, 'j_input_lb'):
		j_input = parent.status.joint[0]['input']
		parent.j_input_lb.setText(f'Input: {j_input}')
	if parent.findChild(QLabel, 'j_jointType_lb'):
		j_jointType = parent.status.joint[0]['jointType']
		parent.j_jointType_lb.setText(f'JointType: {j_jointType}')
	if parent.findChild(QLabel, 'j_max_ferror_lb'):
		j_max_ferror = parent.status.joint[0]['max_ferror']
		parent.j_max_ferror_lb.setText(f'Max_ferror: {j_max_ferror}')
	if parent.findChild(QLabel, 'j_max_hard_limit_lb'):
		j_max_hard_limit = parent.status.joint[0]['max_hard_limit']
		parent.j_max_hard_limit_lb.setText(f'Max_hard_limit: {j_max_hard_limit}')
	if parent.findChild(QLabel, 'j_max_position_limit_lb'):
		j_max_position_limit = parent.status.joint[0]['max_position_limit']
		parent.j_max_position_limit_lb.setText(f'Max_posn_lmt: {j_max_position_limit}')
	if parent.findChild(QLabel, 'j_max_soft_limit_lb'):
		j_max_soft_limit = parent.status.joint[0]['max_soft_limit']
		parent.j_max_soft_limit_lb.setText(f'Max_soft_limit: {j_max_soft_limit}')
	if parent.findChild(QLabel, 'j_min_ferror_lb'):
		j_min_ferror = parent.status.joint[0]['min_ferror']
		parent.j_min_ferror_lb.setText(f'Min_ferror: {j_min_ferror}')
	if parent.findChild(QLabel, 'j_min_hard_limit_lb'):
		j_min_hard_limit = parent.status.joint[0]['min_hard_limit']
		parent.j_min_hard_limit_lb.setText(f'Min_hard_limit: {j_min_hard_limit}')
	if parent.findChild(QLabel, 'j_min_position_limit_lb'):
		j_min_position_limit = parent.status.joint[0]['min_position_limit']
		parent.j_min_position_limit_lb.setText(f'Min_posn_lmt: {j_min_position_limit}')
	if parent.findChild(QLabel, 'j_min_soft_limit_lb'):
		j_min_soft_limit = parent.status.joint[0]['min_soft_limit']
		parent.j_min_soft_limit_lb.setText(f'Min_soft_limit: {j_min_soft_limit}')
	if parent.findChild(QLabel, 'j_output_lb'):
		j_output = parent.status.joint[0]['output']
		parent.j_output_lb.setText(f'Output: {j_output}')
	if parent.findChild(QLabel, 'j_override_limits_lb'):
		j_override_limits = parent.status.joint[0]['override_limits']
		parent.j_override_limits_lb.setText(f'Override_limits: {j_override_limits}')
	if parent.findChild(QLabel, 'j_units_lb'):
		j_units = round(parent.status.joint[0]['units'],4)
		parent.j_units_lb.setText(f'Units: {j_units}')
	if parent.findChild(QLabel, 'j_velocity_lb'):
		j_velocity = parent.status.joint[0]['velocity']
		parent.j_velocity_lb.setText(f'Velocity: {j_velocity}')

	flood_state = parent.status.flood
	if parent.findChild(QPushButton, 'coolant_flood_pb'):
		if flood_state == parent.emc.FLOOD_OFF:
			if parent.coolant_flood_pb.isChecked() == True:
				parent.coolant_flood_pb.setChecked(False)
		else:
			if parent.coolant_flood_pb.isChecked() == False:
				parent.coolant_flood_pb.setChecked(True)

	mist_state = parent.status.mist
	if parent.findChild(QPushButton, 'coolant_mist_pb'):
		if mist_state == parent.emc.MIST_OFF:
			if parent.coolant_mist_pb.isChecked() == True:
				parent.coolant_mist_pb.setChecked(False)
		else:
			if parent.coolant_mist_pb.isChecked() == False:
				parent.coolant_mist_pb.setChecked(True)

	task_state = parent.status.task_state
	if task_state == parent.emc.STATE_ESTOP:
		parent.estop_pb.setStyleSheet('background-color: rgba(255, 0, 0, 25%);')
		parent.power_pb.setEnabled(False)
	elif task_state == parent.emc.STATE_ESTOP_RESET:
		parent.estop_pb.setStyleSheet('background-color: rgba(0, 255, 0, 25%);')
		parent.power_pb.setEnabled(True)
		parent.power_pb.setStyleSheet('background-color: ;')
		parent.power_pb.setText('Power Off')
	elif task_state == parent.emc.STATE_ON:
		parent.power_pb.setStyleSheet('background-color: rgba(0, 255, 0, 25%);')
		parent.power_pb.setText('Power On')

	task_state = {1:'STATE_ESTOP', 2:'STATE_ESTOP_RESET', 3:'STATE_OFF', 4:'STATE_ON', }
	if parent.task_state_lb_exists:
		parent.task_state_lb.setText(f'{task_state[parent.status.task_state]}')

	interp_state_mode = {1: 'INTERP_IDLE', 2: 'INTERP_READING',
	3: 'INTERP_PAUSED', 4: 'INTERP_WAITING'}
	if parent.interp_state_lb_exists:
		parent.interp_state_lb.setText(f'{interp_state_mode[parent.status.interp_state]}')

	if parent.status.paused:
		parent.resume_pb.setEnabled(True)
		parent.pause_pb.setEnabled(False)
	else:
		parent.resume_pb.setEnabled(False)

	state_mode = {1: 'DONE', 2: 'EXEC', 3: 'ERROR'}
	parent.state_lb.setText(f'{state_mode[parent.status.state]}')
	if parent.status.state == parent.emc.RCS_EXEC:
		#parent.step_pb.setEnabled(False)
		parent.pause_pb.setEnabled(True)

	if parent.status.inpos:
		parent.step_pb.setEnabled(True)
	else:
		parent.step_pb.setEnabled(False)

	if parent.status.state == parent.emc.RCS_DONE and parent.status.task_state == parent.emc.STATE_ON:
		parent.run_pb.setEnabled(True)
		parent.step_pb.setEnabled(True)

	if parent.inpos_lb_exists:
		parent.inpos_lb.setText(f'{parent.status.inpos}')

	if parent.g_codes_lb_exists:
		g_codes = []
		for i in parent.status.gcodes[1:]:
			if i == -1: continue
			if i % 10 == 0:
				g_codes.append(f'G{(i/10):.0f}')
			else:
				g_codes.append(f'G{(i/10):.0f}.{i%10}')
		parent.g_codes_lb.setText(f'{" ".join(g_codes)}')

	if parent.m_codes_lb_exists:
		m_codes = []
		for i in parent.status.mcodes[1:]:
			if i == -1: continue
			m_codes.append(f'M{i}')
		parent.m_codes_lb.setText(f'{" ".join(m_codes)}')

	if parent.g5x_offsets_lb_exists:
		pass

	# handle errors
	#if parent.status.state == parent.emc.RCS_ERROR:
	error = parent.error.poll()
	if error:
		kind, text = error
		if kind in (parent.emc.NML_ERROR, parent.emc.OPERATOR_ERROR):
			error_type = 'Error'
		else:
			error_type = 'Info'
		parent.errors_pte.setPlainText(error_type)
		parent.errors_pte.appendPlainText(text)
		#tabname = 'status_tab'
		#print(parent.tabWidget.findChild(QWidget, 'status_tab'))
		#page = parent.tabWidget.findChild(QWidget, tabname)
		#print(page)
		#index = parent.tabWidget.indexOf(page)
		#print(index)
		if isinstance(parent.tabWidget.findChild(QWidget, 'status_tab'), QWidget):
			parent.tabWidget.setCurrentWidget(parent.tabWidget.findChild(QWidget, 'status_tab'))


	'''
		if not parent.in_error:
			parent.in_error = True
			print(error)
		else:
			parent.in_error = False
			print('no')

	'''

	if parent.motion_line_lb_exists:
		parent.motion_line_lb.setText(f'{parent.status.motion_line}')

	if parent.gcode_pte_exists:
		n = parent.status.motion_line
		if n != parent.last_line:
			format_normal = QTextBlockFormat()
			format_normal.setBackground(QColor('white'))
			highlight_format = QTextBlockFormat()
			highlight_format.setBackground(QColor('yellow'))
			motion_line = parent.status.motion_line

			cursor = parent.gcode_pte.textCursor()
			cursor.select(QTextCursor.SelectionType.Document)
			cursor.setBlockFormat(format_normal)
			cursor = QTextCursor(parent.gcode_pte.document().findBlockByNumber(motion_line))
			cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock, QTextCursor.MoveMode.MoveAnchor)
			cursor.setBlockFormat(highlight_format)
			parent.gcode_pte.setTextCursor(cursor)
			parent.last_line = n
		
		pass
		'''
		highlight_format = QTextBlockFormat()
		highlight_format.setBackground(QColor('yellow'))

		cursor = parent.gcode_pte.textCursor()
		cursor.clearSelection()

		n = parent.status.motion_line
		doc = parent.gcode_pte.document()
		#print(doc.blockCount())
		#cursor = QTextCursor(doc)
		#cursor.select(doc)
		cursor = QTextCursor(doc.findBlockByLineNumber(n - 1))
		parent.gcode_pte.setTextCursor(cursor)
		cursor.setBlockFormat(highlight_format)
		'''


		""" Sets the highlighting of a given line number in the QTextEdit"""
		#cursor = self.editor.textCursor()
		#cursor.select(QTextCursor.Document)
		#cursor.setBlockFormat(self.format_normal)

		#cursor = QTextCursor(self.editor.document().findBlockByNumber(lineNumber))

		''''
		selection = QTextEdit.ExtraSelection();
		selection.format.setBackground(colorValues['currentLineHighlight'])
		selection.format.setProperty(QTextFormat.FullWidthSelection, True)
		selection.cursor = self.textCursor()
		selection.cursor.clearSelection()
		parent.gcode_pte.setExtraSelections([selection])
		'''



