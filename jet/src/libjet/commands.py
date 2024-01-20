import os

import linuxcnc
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

def set_mode(parent, mode):
	if parent.status.task_mode != mode:
		parent.command.mode(mode)
		parent.command.wait_complete()

def set_motion_teleop(parent, value):
	# 1:teleop, 0: joint
	parent.command.teleop_enable(value)
	parent.command.wait_complete()
	parent.status.poll()

def estop_toggle(parent):
	if parent.status.task_state == linuxcnc.STATE_ESTOP:
		parent.command.state(linuxcnc.STATE_ESTOP_RESET)
		parent.estop_pb.setStyleSheet('background-color: rgba(0, 255, 0, 25%);')
		parent.power_pb.setEnabled(True)
	else:
		parent.command.state(linuxcnc.STATE_ESTOP)
		parent.estop_pb.setStyleSheet('background-color: rgba(255, 0, 0, 25%);')
		parent.power_pb.setEnabled(False)
		parent.power_pb.setStyleSheet('background-color: ;')
		parent.power_pb.setText('Power Off')

	controls = {'estop_pb': 'estop_toggle',
	'power_pb': 'power_toggle',
	'run_pb': 'run',
	'step_pb': 'step',
	'pause_pb': 'pause',
	'resume_pb': 'resume',
	'stop_pb': 'stop',
	'home_pb_0': 'home',
	'home_pb_1': 'home',
	'home_pb_2': 'home',
	}

def power_toggle(parent):
	if parent.status.task_state == linuxcnc.STATE_ESTOP_RESET:
		parent.command.state(linuxcnc.STATE_ON)
		parent.power_pb.setStyleSheet('background-color: rgba(0, 255, 0, 25%);')
		parent.power_pb.setText('Power On')
		if parent.status.file:
			parent.run_pb.setEnabled(True)
			parent.step_pb.setEnabled(True)
		for i in range(parent.joints):
			getattr(parent, f'home_pb_{i}').setEnabled(True)
		parent.run_mdi_pb.setEnabled(True)
	else:
		parent.command.state(linuxcnc.STATE_OFF)
		parent.power_pb.setStyleSheet('background-color: ;')
		parent.power_pb.setText('Power Off')
		parent.run_mdi_pb.setEnabled(False)

def run(parent):
	if parent.status.task_state == linuxcnc.STATE_ON:
		if parent.status.task_mode != linuxcnc.MODE_AUTO:
			parent.command.mode(linuxcnc.MODE_AUTO)
		parent.pause_pb.setEnabled(True)
		if parent.start_line_lb_exists:
			if parent.start_line_lb.text():
				n = int(parent.start_line_lb.text())
			else:
				n = 0
		parent.command.auto(linuxcnc.AUTO_RUN, n)

def step(parent):
	if parent.status.task_state == linuxcnc.STATE_ON:
		if parent.status.task_mode != linuxcnc.MODE_AUTO:
			parent.command.mode(linuxcnc.MODE_AUTO)
		parent.command.auto(linuxcnc.AUTO_STEP)

def pause(parent):
	if parent.status.state == linuxcnc.RCS_EXEC: # program is running
		parent.command.auto(linuxcnc.AUTO_PAUSE)

def resume(parent):
	if parent.status.paused:
		parent.command.auto(linuxcnc.AUTO_RESUME)

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
		if parent.status.task_mode != linuxcnc.MODE_MANUAL:
			parent.command.mode(MODE_MANUAL)
		#if parent.status.motion_mode != linuxcnc.TRAJ_MODE_FREE:
		#	parent.command.traj_mode(linuxcnc.TRAJ_MODE_FREE)
		parent.command.home(joint)
		parent.command.wait_complete()
		parent.sender().setStyleSheet('background-color: rgba(0, 255, 0, 25%);')
		getattr(parent, f'unhome_pb_{joint}').setEnabled(True)
		parent.unhome_all_pb.setEnabled(True)

	# homed (returns tuple of integers) - currently homed joints, 0 = not homed, 1 = homed.
	parent.status.poll()
	#print(f'Homed: {parent.status.homed}')
	# home(int) home a given joint.

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

def get_jog_mode(parent):
	parent.status.poll()
	if parent.status.kinematics_type == linuxcnc.KINEMATICS_IDENTITY and all_homed(parent):
		  teleop_mode = 1
		  jjogmode = False
	else:
		  # check motion_mode since other guis (halui) could alter it
		  if parent.status.motion_mode == linuxcnc.TRAJ_MODE_FREE:
		      teleop_mode = 0
		      jjogmode = True
		  else:
		      teleop_mode = 1
		      jjogmode = False
	if (   (    jjogmode and parent.status.motion_mode != linuxcnc.TRAJ_MODE_FREE)
		  or (not jjogmode and parent.status.motion_mode != linuxcnc.TRAJ_MODE_TELEOP) ):
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

def run_mdi(parent):
	mdi_command = parent.mdi_command_le.text()
	if mdi_command:
		if parent.status.task_state == linuxcnc.STATE_ON:
			if parent.status.task_mode != linuxcnc.MODE_MDI:
				parent.command.mode(linuxcnc.MODE_MDI)
			parent.pause_pb.setEnabled(True)
			parent.command.mdi(mdi_command)
			parent.command.wait_complete()
			parent.status.poll()
			if parent.status.state != parent.emc.RCS_ERROR:
				# add mdi to list
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
	else:
		print('no mdi')


