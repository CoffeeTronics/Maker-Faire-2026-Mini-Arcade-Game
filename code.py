# code.py - CONTROLLER (MVC pattern)

import sys
sys.path.append('/API')

import time
import board
import digitalio
import microcontroller
import neopixel
import gc
import displayio
from fourwire import FourWire
from adafruit_st7789 import ST7789
import terminalio
from adafruit_display_text import label as _label

from digital_io import DigitalInput, EdgeDetector
from mario_model import MarioModel, InputState
from mario_view  import MarioView

Debug = True


def _setup_display():
    backlight           = digitalio.DigitalInOut(microcontroller.pin.PA06)
    backlight.direction = digitalio.Direction.OUTPUT
    backlight.value     = False

    displayio.release_displays()

    spi         = board.LCD_SPI()
    display_bus = FourWire(spi, command=board.D4, chip_select=board.LCD_CS)
    display     = ST7789(
        display_bus,
        rotation=90,
        width=240, height=135,
        rowstart=40, colstart=53,
    )
    print('Display OK')
    return display


class JoystickController:
    def __init__(self):
        print('Initialising joystick and buttons...')
        
        self._joy_up = DigitalInput(board.D0, pull=digitalio.Pull.DOWN)
        self._joy_down = DigitalInput(board.D1, pull=digitalio.Pull.DOWN)
        self._joy_left = DigitalInput(board.D2, pull=digitalio.Pull.DOWN)
        self._joy_right = DigitalInput(board.D9, pull=digitalio.Pull.DOWN)
        
        self._btn_a = EdgeDetector(board.D10, pull=digitalio.Pull.DOWN)
        self._btn_b = EdgeDetector(board.D5, pull=digitalio.Pull.DOWN)
        self._btn_c = EdgeDetector(board.D6, pull=digitalio.Pull.DOWN)
        self._btn_d = EdgeDetector(board.D7, pull=digitalio.Pull.DOWN)
        
        self._buf_frames = 0
        self._state = InputState()
        
        print('Joystick and buttons OK')

    def poll_button(self):
        self._btn_a.update()
        if self._btn_a.rose:
            self._buf_frames = 3

    def read(self):
        self._btn_a.update()
        self._btn_b.update()
        self._btn_c.update()
        self._btn_d.update()
        
        left = self._joy_left.value
        right = self._joy_right.value
        
        if left and not right:
            self._state.tilt_value = -1.0
        elif right and not left:
            self._state.tilt_value = 1.0
        else:
            self._state.tilt_value = 0.0

        if self._btn_a.rose:
            self._buf_frames = 3

        if self._buf_frames > 0:
            self._state.jump = True
            self._buf_frames -= 1
        else:
            self._state.jump = False

        self._state.run = self._btn_b.value

        return self._state


def _show_startup_text(display, lines):
    grp    = displayio.Group()
    bg_bmp = displayio.Bitmap(240, 135, 1)
    bg_pal = displayio.Palette(1)
    bg_pal[0] = 0x000000
    grp.append(displayio.TileGrid(bg_bmp, pixel_shader=bg_pal))

    row_h   = 22
    total_h = len(lines) * row_h
    start_y = (135 - total_h) // 2 + row_h // 2

    for i, text in enumerate(lines):
        lbl = _label.Label(
            terminalio.FONT,
            text=text,
            color=0xFFFFFF,
            scale=2,
            anchor_point=(0.5, 0.5),
            anchored_position=(120, start_y + i * row_h),
        )
        grp.append(lbl)

    display.root_group = grp


def main():
    gc.collect()
    print('Free RAM at start: {} bytes'.format(gc.mem_free()))

    display = _setup_display()
    px      = neopixel.NeoPixel(board.NEOPIXEL, 5, brightness=0.15,
                                auto_write=False)
    px.fill(0x000000)
    px.show()

    _show_startup_text(display, [
        'SUPER MARIO BROS',
        'Joystick Edition',
    ])
    time.sleep(1)

    controller = JoystickController()

    model = MarioModel()
    view  = MarioView(display, px)

    print('\n' + '=' * 50)
    print('SUPER MARIO BROS - JOYSTICK EDITION')
    print('Joystick L/R = move | A = jump | B = run')
    print('=' * 50 + '\n')

    frame            = 0
    gameover_holding = False

    while True:
        controller.poll_button()
        input_state = controller.read()
        events = model.update(input_state)

        for event in events:
            if event == 'jumped':
                view.play_sfx('jump')
            elif event == 'coin':
                view.play_sfx('coin')
            elif event == 'stomp':
                pass
            elif event == 'enemy_hit':
                pass
            elif event == 'gameover':
                view.play_sfx('gameover')
                view.show_game_over()
                view.flash_neopixels_gameover()
                gameover_holding = False
            elif event == 'level_complete':
                view.play_sfx('world_clear')
                view.show_victory(model.score, model.coins)
            elif event == 'level_reset':
                view.hide_overlays()

        view.draw(model)
        view.update_neopixels(model, model.level_complete)

        frame += 1

        if frame % 90 == 0:
            gc.collect()
            if Debug or frame % 180 == 0:
                print('Score: {} | Coins: {} | Lives: {} | RAM: {}'.format(
                    model.score, model.coins, model.lives, gc.mem_free()))

        if model.game_over and not gameover_holding:
            gameover_holding = True
            print('\nGAME OVER!  Final score: {}'.format(model.score))

            for i in range(150):
                time.sleep(0.033)
                if i % 30 == 0:
                    if view.is_audio_playing():
                        print('  gameover audio playing... ({}s)'.format(i // 30 + 1))
                    else:
                        print('  holding screen... ({}s)'.format(i // 30 + 1))

            print('Restarting level...\n')
            view.stop_audio()
            model.reset()
            view.hide_overlays()
            gameover_holding = False

        time.sleep(0.033)


if __name__ == '__main__':
    main()
