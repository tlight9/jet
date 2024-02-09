
from PyQt6.QtGui import QTextCursor, QTextBlockFormat, QColor
from PyQt6.QtWidgets import QTextEdit, QWidget

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
		feed = round(parent.status.settings[1],2)
		parent.feed_lb.setText(f'Feed: {feed}')

	flood_state = parent.status.flood
	if flood_state == parent.emc.FLOOD_OFF:
		if parent.coolant_flood_pb.isChecked() == 1:
			parent.coolant_flood_pb.setChecked(False)
	if flood_state == parent.emc.FLOOD_ON: 
		if parent.coolant_flood_pb.isChecked() == 0:
			parent.coolant_flood_pb.setChecked(True)

	mist_state = parent.status.mist
	if mist_state == parent.emc.MIST_OFF:
		if parent.coolant_mist_pb.isChecked() == 1:
			parent.coolant_mist_pb.setChecked(False)
	if mist_state == parent.emc.MIST_ON: 
		if parent.coolant_mist_pb.isChecked() == 0:
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
		parent.step_pb.setEnabled(False)
		parent.pause_pb.setEnabled(True)

	if parent.status.state == parent.emc.RCS_DONE and parent.status.task_state == parent.emc.STATE_ON:
		parent.run_pb.setEnabled(True)
		parent.step_pb.setEnabled(True)

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



