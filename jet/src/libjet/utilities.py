
from PyQt6.QtWidgets import QLabel

def add_mdi(parent):
	parent.mdi_command_le.setText(f'{parent.mdi_history_lw.currentItem().text()}')

def jog_slider(parent):
	if parent.jog_vel_lb_exists:
		parent.jog_vel_lb.setText(f'{parent.jog_vel_s.value():.1f}')

def clear_mdi_history(parent):
	parent.mdi_history_lw.clear()



