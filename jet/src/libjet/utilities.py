import os

from PyQt6.QtWidgets import QLabel

from libjet import utilities

def add_mdi(parent):
	parent.mdi_command_le.setText(f'{parent.mdi_history_lw.currentItem().text()}')

def jog_slider(parent):
	if parent.jog_vel_lb_exists:
		parent.jog_vel_lb.setText(f'{parent.jog_vel_s.value():.1f}')

def clear_mdi_history(parent):
	parent.mdi_history_lw.clear()

def update_mdi(parent):
	if parent.mdi_history_lw_exists:
		parent.mdi_history_lw.addItem(parent.mdi_command)
	parent.mdi_command_le.setText('')
	if parent.mdi_history_lw_exists:
		path = os.path.dirname(parent.status.ini_filename)
		mdi_file = os.path.join(path, 'mdi_history.txt')
		mdi_codes = []
		for index in range(parent.mdi_history_lw.count()):
			mdi_codes.append(parent.mdi_history_lw.item(index).text())
		with open(mdi_file, 'w') as f:
			f.write('\n'.join(mdi_codes))
	parent.mdi_command = False
	parent.command.mode(parent.emc.MODE_MANUAL)
	parent.command.wait_complete()




