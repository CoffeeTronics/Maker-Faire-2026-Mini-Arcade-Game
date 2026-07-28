import pykit_explorer
import digitalio
import time
from digital_io import DigitalInput, EdgeDetector

# Joystick - 3-bit encoded, active HIGH
sig_a = DigitalInput(board.D0, pull=digitalio.Pull.DOWN)
sig_b = DigitalInput(board.D1, pull=digitalio.Pull.DOWN)
sig_c = DigitalInput(board.D2, pull=digitalio.Pull.DOWN)
sig_d = DigitalInput(board.D9, pull=digitalio.Pull.DOWN)  # Added for Down-Right detection

# Button with edge detection
btn_a = EdgeDetector(board.D10, pull=digitalio.Pull.DOWN)
btn_b = EdgeDetector(board.D5, pull=digitalio.Pull.DOWN)
btn_c = EdgeDetector(board.D6, pull=digitalio.Pull.DOWN)
btn_d = EdgeDetector(board.D7, pull=digitalio.Pull.DOWN)

def get_joystick_direction():
    a = sig_a.value
    b = sig_b.value
    c = sig_c.value
    d = sig_d.value  # Read the new signal for Down-Right
    # Decode from original trace analysis
    if a:
        return "Up"
    if b:
        return "Down"
    if c:
        return "Left"
    if d:
        return "Right"
    else: 
        return None

while True:
    btn_a.update()
    btn_b.update()
    btn_c.update()
    btn_d.update()

    if btn_a.rose:
        print("Button A pressed")
    if btn_b.rose:
        print("Button B pressed")
    if btn_c.rose:
        print("Button C pressed")
    if btn_d.rose:
        print("Button D pressed")
    
    direction = get_joystick_direction()
    if direction:
        print(direction)
    time.sleep(0.05)
