
from PyQt6.QtWidgets import QLabel

def add_mdi(parent):
	parent.mdi_command_le.setText(f'{parent.mdi_history_lw.currentItem().text()}')

def jog_slider(parent):
	if parent.findChild(QLabel, 'jog_vel_lb'):
		parent.jog_vel_lb.setText(f'{parent.jog_vel_s.value() / 10:.2f}')

def clear_mdi_history(parent):
	print('clear mdi')
