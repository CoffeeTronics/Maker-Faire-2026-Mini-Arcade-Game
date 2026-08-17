# Pong Game - Unified Launcher Integration
# For 64x32 RGB Matrix with Joystick and Buttons
#
# Controls:
# - Joystick Up/Down: Move paddle
# - Button A: Start game (from menu)
# - Button C: Select (Game switch)
# - Button D: Start

import time
import gc

from base_game import BaseGame
from games.pong.model import PongModel, InputState
from games.pong.view import PongView

STATE_MENU = 0
STATE_PLAYING = 1
STATE_GAMEOVER = 2


class PongGame(BaseGame):

    NAME = "Pong"
    HIGH_SCORE_SLOT = 2  # Reusing slot 2 (was Mario, then Frogger)

    def setup(self):
        gc.collect()
        print(f"Pong setup start RAM: {gc.mem_free()}")

        self._input_state = InputState()

        gc.collect()
        self.model = PongModel()
        gc.collect()
        print(f"After model RAM: {gc.mem_free()}")

        self.view = PongView(self.display.display, self.audio)
        gc.collect()
        print(f"After view RAM: {gc.mem_free()}")

        self._state = STATE_MENU
        self._gameover_time = 0
        self._frame = 0

        self.model.high_score = self.get_high_score()

        gc.collect()
        print(f"Pong setup done RAM: {gc.mem_free()}")

    def run(self):
        while True:
            self.buttons.update()

            # Check for game switch (Button C = Select)
            if self.buttons.c_fell:
                print("Button C pressed")
                self._save_score()
                return "switch"

            self._read_inputs()

            if self._state == STATE_MENU:
                self.view.blink_start_prompt()
                # Start on button A, D (Start), or any joystick input
                if (self.buttons.a_fell or self.buttons.d_fell or
                    self._input_state.up or self._input_state.down):
                    if self.buttons.d_fell:
                        print("Button D pressed")
                    self.model.reset()
                    self.view.hide_start_menu()
                    self._state = STATE_PLAYING
                    self._frame = 0
                    time.sleep(0.1)
                    continue
                time.sleep(0.033)
                continue

            if self._state == STATE_GAMEOVER:
                elapsed = time.monotonic() - self._gameover_time
                audio_done = not self.view.is_audio_playing()
                if elapsed >= 2.5 and audio_done:
                    self.view.stop_audio()
                    return "gameover"
                time.sleep(0.033)
                continue

            # Game playing state
            events = self.model.update(self._input_state)

            for event in events:
                if event == "hit":
                    self.view.play_sfx("hit")
                elif event == "score_player":
                    self.view.play_sfx("score")
                elif event == "score_ai":
                    self.view.play_sfx("score")
                elif event == "gameover":
                    self.view.play_sfx("gameover")
                    self.view.show_game_over(self.model.winner)
                    self._state = STATE_GAMEOVER
                    self._gameover_time = time.monotonic()
                    self._save_score()

            if self._state == STATE_PLAYING:
                self.view.draw(self.model)

            self._frame += 1
            if self._frame % 90 == 0:
                gc.collect()

            time.sleep(0.033)

    def _read_inputs(self):
        """Read joystick into InputState."""
        self._input_state.up = self.joystick.up
        self._input_state.down = self.joystick.down

    def _save_score(self):
        # High score is player's winning score
        if self.model.player.score > self.get_high_score():
            self.set_high_score(self.model.player.score)

    def cleanup(self):
        if hasattr(self, 'view'):
            self.view.cleanup()
        self.audio.unload_all()
        self.audio.stop()
