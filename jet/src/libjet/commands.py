import os

import linuxcnc as emc
#command = linuxcnc.command()

TRAJ_MODE_COORD = 2
TRAJ_MODE_FREE = 1
TRAJ_MODE_TELEOP = 3
MODE_MDI = 3
MODE_AUTO = 2
MODE_MANUAL = 1
TELEOP_DISABLE = 0
TELEOP_ENABLE = 1
JOG_STOP = 0
JOG_CONTINUOUS = 1
JOG_INCREMENT = 2
FLOOD_ON = 1
FLOOD_OFF = 0
MIST_ON = 1
MIST_OFF = 0

def set_mode(parent, mode=None):
	if mode is None:
		if parent.sender().objectName() == 'manual_mode_pb':
			mode = emc.MODE_MANUAL
	if parent.status.task_mode != mode:
		parent.command.mode(mode)
		parent.command.wait_complete()

def set_mode_manual(parent):
	if parent.status.task_mode != emc.MODE_MANUAL:
		parent.command.mode(emc.MODE_MANUAL)
		parent.command.wait_complete()

def set_motion_teleop(parent, value):
	# 1:teleop, 0: joint
	parent.command.teleop_enable(value)
	parent.command.wait_complete()
	parent.status.poll()

def estop_toggle(parent):
	if parent.status.task_state == emc.STATE_ESTOP:
		parent.command.state(emc.STATE_ESTOP_RESET)
	else:
		parent.command.state(emc.STATE_ESTOP)

def power_toggle(parent):
	if parent.status.task_state == emc.STATE_ESTOP_RESET:
		parent.command.state(emc.STATE_ON)
		if parent.status.file:
			parent.run_pb.setEnabled(True)
			parent.step_pb.setEnabled(True)
		for i in range(parent.joints):
			getattr(parent, f'home_pb_{i}').setEnabled(True)
		if home_all_check(parent):
			parent.home_all_pb.setEnabled(True)
		parent.run_mdi_pb.setEnabled(True)
		parent.start_spindle_pb.setEnabled(True)
	else:
		parent.command.state(emc.STATE_OFF)
		parent.home_all_pb.setEnabled(False)
		parent.run_mdi_pb.setEnabled(False)
		for i in range(parent.joints):
			getattr(parent, f'home_pb_{i}').setEnabled(False)
		parent.start_spindle_pb.setEnabled(False)

def run(parent):
	if parent.status.task_state == emc.STATE_ON:
		if parent.status.task_mode != emc.MODE_AUTO:
			parent.command.mode(emc.MODE_AUTO)
		parent.pause_pb.setEnabled(True)
		if parent.start_line_lb_exists:
			if parent.start_line_lb.text():
				n = int(parent.start_line_lb.text())
			else:
				n = 0
		parent.command.auto(emc.AUTO_RUN, n)

def step(parent):
	if parent.status.task_state == emc.STATE_ON:
		if parent.status.task_mode != emc.MODE_AUTO:
			parent.command.mode(emc.MODE_AUTO)
		parent.command.auto(emc.AUTO_STEP)

def pause(parent):
	if parent.status.state == emc.RCS_EXEC: # program is running
		parent.command.auto(emc.AUTO_PAUSE)

def resume(parent):
	if parent.status.paused:
		parent.command.auto(emc.AUTO_RESUME)

def stop(parent):
	parent.command.abort()

def all_homed(parent):
	isHomed=True
	num_joints = parent.status.joints
	for i,h in enumerate(parent.status.homed):
		if i >= num_joints: break
		isHomed = isHomed and h
	return isHomed

def home(parent):
	joint = int(parent.sender().objectName()[-1])
	if parent.status.homed[joint] == 0:
		if parent.status.task_mode != emc.MODE_MANUAL:
			parent.command.mode(MODE_MANUAL)
		#if parent.status.motion_mode != emc.TRAJ_MODE_FREE:
		#	parent.command.traj_mode(emc.TRAJ_MODE_FREE)
		parent.command.home(joint)
		parent.command.wait_complete()
		parent.sender().setStyleSheet('background-color: rgba(0, 255, 0, 25%);')
		getattr(parent, f'unhome_pb_{joint}').setEnabled(True)
		parent.unhome_all_pb.setEnabled(True)

	# homed (returns tuple of integers) - currently homed joints, 0 = not homed, 1 = homed.
	parent.status.poll()
	#print(f'Homed: {parent.status.homed}')
	# home(int) home a given joint.

def home_all(parent): # only works if the home sequence is set for all axes
		set_mode(parent, MODE_MANUAL)
		parent.command.teleop_enable(TELEOP_DISABLE)
		parent.command.wait_complete()
		parent.command.home(-1)
		for i in range(parent.joints):
			getattr(parent, f'home_pb_{i}').setStyleSheet('background-color: rgba(0, 255, 0, 25%);')
			getattr(parent, f'unhome_pb_{i}').setEnabled(True)
		parent.unhome_all_pb.setEnabled(True)

def unhome(parent):
	joint = int(parent.sender().objectName()[-1])
	if parent.status.homed[joint] == 1:
		set_mode(parent, MODE_MANUAL)
		parent.command.teleop_enable(TELEOP_DISABLE)
		parent.command.wait_complete()
		parent.command.unhome(joint)
		getattr(parent, f'home_pb_{joint}').setStyleSheet('background-color: ;')
		getattr(parent, f'unhome_pb_{joint}').setEnabled(False)

def unhome_all(parent):
		set_mode(parent, MODE_MANUAL)
		parent.command.teleop_enable(TELEOP_DISABLE)
		parent.command.wait_complete()
		parent.command.unhome(-1)
		for i in range(parent.joints):
			getattr(parent, f'home_pb_{i}').setStyleSheet('background-color: ;')
			getattr(parent, f'unhome_pb_{i}').setEnabled(False)
		parent.unhome_all_pb.setEnabled(False)

def home_all_check(parent):
	parent.status.poll()
	for i in range(parent.status.joints):
		if parent.inifile.find(f'JOINT_{i}', 'HOME_SEQUENCE') is None:
			return False
	return True

def get_jog_mode(parent):
	parent.status.poll()
	if parent.status.kinematics_type == emc.KINEMATICS_IDENTITY and all_homed(parent):
		teleop_mode = 1
		jjogmode = False
	else:
		# check motion_mode since other guis (halui) could alter it
		if parent.status.motion_mode == emc.TRAJ_MODE_FREE:
			teleop_mode = 0
			jjogmode = True
		else:
			teleop_mode = 1
			jjogmode = False
	if ((jjogmode and parent.status.motion_mode != emc.TRAJ_MODE_FREE)
		or (not jjogmode and parent.status.motion_mode != emc.TRAJ_MODE_TELEOP) ):
		set_motion_teleop(parent, teleop_mode)
	return jjogmode

def jog(parent):
	jog_command = parent.sender().objectName().split('_')
	joint = int(jog_command[-1])
	increment = parent.jog_modes_cb.currentData()
	if 'minus' in jog_command:
		#increment = -increment
		vel = -parent.jog_vel_s.value()
	else:
		vel = parent.jog_vel_s.value()
	jjogmode = get_jog_mode(parent)
	if parent.sender().isDown():
		if increment:
			parent.command.jog(JOG_INCREMENT, jjogmode, joint, vel, increment)
		else:
			parent.command.jog(JOG_CONTINUOUS, jjogmode, joint, vel)

	else:
		parent.command.jog(JOG_STOP, jjogmode, joint)

def run_mdi(parent, cmd=''):
	if cmd:
		mdi_command = cmd
	else:
		mdi_command = parent.mdi_command_le.text()

	if mdi_command:
		if parent.status.task_state == emc.STATE_ON:
			if parent.status.task_mode != emc.MODE_MDI:
				parent.command.mode(emc.MODE_MDI)
				parent.command.wait_complete()
			parent.pause_pb.setEnabled(True)
			parent.command.mdi(mdi_command)
			parent.status.poll()
			while parent.status.state == parent.emc.RCS_EXEC:
				parent.status.poll()
			if parent.status.state == parent.emc.RCS_DONE:
				print('done')
	'''
				if parent.mdi_history_lw_exists:
					parent.mdi_history_lw.addItem(mdi_command)
				parent.mdi_command_le.setText('')
				if parent.mdi_history_lw_exists:
					path = os.path.dirname(parent.status.ini_filename)
					mdi_file = os.path.join(path, 'mdi_history.txt')
					mdi_codes = []
					for index in range(parent.mdi_history_lw.count()):
						mdi_codes.append(parent.mdi_history_lw.item(index).text())
					with open(mdi_file, 'w') as f:
						f.write('\n'.join(mdi_codes))
				parent.command.mode(emc.MODE_MANUAL)
				parent.command.wait_complete()
	'''

def touchoff(parent):
	g5x = parent.status.g5x_index
	axis = parent.sender().objectName()[-1].upper()
	value = parent.touchoff_dsb.value()
	mdi_command = f'G10 L20 P{g5x} {axis}{value}'
	if parent.status.task_state == emc.STATE_ON:
		if parent.status.task_mode != emc.MODE_MDI:
			parent.command.mode(emc.MODE_MDI)
			parent.command.wait_complete()
		parent.command.mdi(mdi_command)
		parent.command.wait_complete()
		parent.command.mode(emc.MODE_MANUAL)
		parent.command.wait_complete()

def tool_touchoff(parent):
	axis = parent.sender().objectName()[-1].upper()
	cur_pos = parent.status.actual_position
	cur_tool = parent.status.tool_in_spindle
	offset = parent.tool_touchoff_dsb.value()
	if cur_tool > 0:
		mdi_command = f'G10 L10 P{cur_tool} {axis}{offset}'
		if parent.status.task_state == emc.STATE_ON:
			if parent.status.task_mode != emc.MODE_MDI:
				parent.command.mode(emc.MODE_MDI)
				parent.command.wait_complete()
			parent.command.mdi(mdi_command)
			parent.command.wait_complete()
			# be nice and return to manual mode so jogging works
			parent.command.mode(emc.MODE_MANUAL)
			parent.command.wait_complete()

	else:
		print('no tool in spindle')

def tool_change(parent):
	axis = parent.sender().objectName()[-1].upper()
	tool_num = parent.tool_number_sb.value()
	#print(tool_num)
	#return
	if tool_num > 0:
		mdi_command = f'T{tool_num} M6'
		if parent.status.task_state == emc.STATE_ON:
			if parent.status.task_mode != emc.MODE_MDI:
				parent.command.mode(emc.MODE_MDI)
				parent.command.wait_complete()
			parent.command.mdi(mdi_command)
			parent.command.wait_complete()
			# be nice and return to manual mode so jogging works
			parent.command.mode(emc.MODE_MANUAL)
			parent.command.wait_complete()
	else:
		print('No tool selected')

def flood_coolant(parent):
	if parent.coolant_flood_pb.isChecked():
		print(f'Flood: {emc.stat.flood}')
		mdi_command = f'M8'
		if parent.status.task_state == emc.STATE_ON:
			if parent.status.task_mode != emc.MODE_MANUAL:
				parent.command.mode(emc.MODE_MANUAL)
				parent.command.wait_complete()
			parent.command.flood(emc.FLOOD_ON)
			parent.command.wait_complete()
	else:
		print(f'Flood: {emc.stat.flood}')
		mdi_command = f'M9'
		if parent.status.task_state == emc.STATE_ON:
			if parent.status.task_mode != emc.MODE_MANUAL:
				parent.command.mode(emc.MODE_MANUAL)
				parent.command.wait_complete()
			parent.command.flood(emc.FLOOD_OFF)
			parent.command.wait_complete()

def mist_coolant(parent):
	if parent.coolant_mist_pb.isChecked():
		print(f'Mist: {emc.stat.mist}')
		mdi_command = f'M7'
		if parent.status.task_state == emc.STATE_ON:
			if parent.status.task_mode != emc.MODE_MANUAL:
				parent.command.mode(emc.MODE_MANUAL)
				parent.command.wait_complete()
			parent.command.mist(emc.MIST_ON)
			parent.command.wait_complete()
	else:
		print(f'Mist: {emc.stat.mist}')
		mdi_command = f'M9'
		if parent.status.task_state == emc.STATE_ON:
			parent.command.mode(emc.MODE_MANUAL)
			parent.command.wait_complete()
		parent.command.mist(emc.MIST_OFF)
		parent.command.wait_complete()

def spindle(parent):
	pb = parent.sender().objectName()
	if pb == 'start_spindle_pb':
		run_mdi(parent, f'M3 S{parent.spindle_speed_sb.value()}')
	elif pb == 'stop_spindle_pb':
		run_mdi(parent, 'M5')
	elif pb == 'spindle_plus_pb':
		parent.spindle_speed_sb.setValue(parent.spindle_speed_sb.value() + 100) 
	elif pb == 'spindle_minus_pb':
		parent.spindle_speed_sb.setValue(parent.spindle_speed_sb.value() - 100) 
