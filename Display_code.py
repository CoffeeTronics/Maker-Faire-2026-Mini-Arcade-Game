# Simple RGB Matrix Test
import pykit_explorer
import time
import board
import terminalio
from adafruit_matrixportal.matrix import Matrix
from adafruit_display_text import label
import displayio
import digitalio
from digital_io import DigitalInput, EdgeDetector

# Joystick - moved to LCD pins (active HIGH)
sig_a = DigitalInput(board.LCD_CS, pull=digitalio.Pull.DOWN)    # Down
sig_b = DigitalInput(board.LCD_BL, pull=digitalio.Pull.DOWN)    # Up
sig_c = DigitalInput(board.LCD_SCK, pull=digitalio.Pull.DOWN)   # Left
sig_d = DigitalInput(board.LCD_MOSI, pull=digitalio.Pull.DOWN)  # Right

# Buttons - moved to D4-D7
btn_a = EdgeDetector(board.D4, pull=digitalio.Pull.DOWN)
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
        return "Down"
    if b:
        return "Left"
    if c:
        return "Up"
    if d:
        return "Right"
    else: 
        return None

# Initialize the matrix display
# matrix = Matrix()
matrix = Matrix(width=64, height=32, bit_depth=1)
display = matrix.display

# Create a display group
main_group = displayio.Group()

# Create scrolling text label
text_label = label.Label(
    terminalio.FONT,
    text="HELLO MATRIX!",
    color=0xFF0000  # Red
)
text_label.y = display.height // 2
main_group.append(text_label)

display.root_group = main_group

print("Display initialized - scrolling text...")

# Scroll the text across the display
while True:

    text_width = len(text_label.text) * 6
    for x in range(display.width, -text_width, -1):
        text_label.x = x
        time.sleep(0.02)

    




