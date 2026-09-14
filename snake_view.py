# snake_view.py - VIEW (MVC pattern)
# Ported for 64x32 RGB Matrix with 32x16 grid (2x2 pixels per cell)

import time
import displayio

from snake_model import GRID_W, GRID_H  # 32, 16

# Display dimensions
DISPLAY_W = 64
DISPLAY_H = 32

# Palette indices
_BG    = 0
_SNAKE = 1
_FOOD  = 2
_HEAD  = 3
_WHITE = 4
_YELLOW = 5

# Cell size in pixels (2x2)
CELL_SIZE = 2

# 3x5 pixel font for tiny text
TINY_FONT = {
    "0": [0b111, 0b101, 0b101, 0b101, 0b111],
    "1": [0b010, 0b110, 0b010, 0b010, 0b111],
    "2": [0b111, 0b001, 0b111, 0b100, 0b111],
    "3": [0b111, 0b001, 0b111, 0b001, 0b111],
    "4": [0b101, 0b101, 0b111, 0b001, 0b001],
    "5": [0b111, 0b100, 0b111, 0b001, 0b111],
    "6": [0b111, 0b100, 0b111, 0b101, 0b111],
    "7": [0b111, 0b001, 0b001, 0b001, 0b001],
    "8": [0b111, 0b101, 0b111, 0b101, 0b111],
    "9": [0b111, 0b101, 0b111, 0b001, 0b111],
    "P": [0b111, 0b101, 0b111, 0b100, 0b100],
    "L": [0b100, 0b100, 0b100, 0b100, 0b111],
    "A": [0b111, 0b101, 0b111, 0b101, 0b101],
    "Y": [0b101, 0b101, 0b010, 0b010, 0b010],
    "E": [0b111, 0b100, 0b111, 0b100, 0b111],
    "R": [0b111, 0b101, 0b111, 0b110, 0b101],
    "H": [0b101, 0b101, 0b111, 0b101, 0b101],
    "I": [0b111, 0b010, 0b010, 0b010, 0b111],
    "G": [0b111, 0b100, 0b101, 0b101, 0b111],
    " ": [0b000, 0b000, 0b000, 0b000, 0b000],
}

# 5x5 heart icon
HEART_ICON = [
    0b01010,
    0b11111,
    0b11111,
    0b01110,
    0b00100,
]

# 5x7 pixel font for large GAME OVER text
BIG_FONT = {
    "G": [0b01110, 0b10001, 0b10000, 0b10011, 0b10001, 0b10001, 0b01110],
    "A": [0b01110, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001],
    "M": [0b10001, 0b11011, 0b10101, 0b10101, 0b10001, 0b10001, 0b10001],
    "E": [0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b11111],
    "O": [0b01110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110],
    "V": [0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01010, 0b00100],
    "R": [0b11110, 0b10001, 0b10001, 0b11110, 0b10100, 0b10010, 0b10001],
}


class SnakeView:
    def __init__(self, display, audio):
        self._display = display
        self._audio = audio

        self._sfx_food = None
        self._sfx_gameover = None
        try:
            from audiocore import WaveFile
            self._wav_food_f = open("AudioFiles/210.wav", "rb")
            self._sfx_food = WaveFile(self._wav_food_f)
            self._wav_gameover_f = open("AudioFiles/140.wav", "rb")
            self._sfx_gameover = WaveFile(self._wav_gameover_f)
        except Exception as e:
            print("Audio init failed:", e)

        self._bitmap = displayio.Bitmap(DISPLAY_W, DISPLAY_H, 6)
        self._palette = displayio.Palette(6)
        self._palette[_BG]     = 0x000000
        self._palette[_SNAKE]  = 0x00FF00
        self._palette[_FOOD]   = 0xFF0000
        self._palette[_HEAD]   = 0x00FFFF
        self._palette[_WHITE]  = 0xFFFFFF
        self._palette[_YELLOW] = 0xFFFF00

        tg = displayio.TileGrid(self._bitmap, pixel_shader=self._palette)

        self._root = displayio.Group()
        self._root.append(tg)
        display.root_group = self._root

        self._score = 0
        self._high_score = 0
        self._lives = 3
        self._prev_score_text = ""
        self._prev_high_text = ""
        self._prev_lives = -1
        self._prev_snake = []
        self._prev_food = None

    def _draw_cell(self, cx, cy, color_idx):
        for dy in range(CELL_SIZE):
            for dx in range(CELL_SIZE):
                px = cx * CELL_SIZE + dx
                py = cy * CELL_SIZE + dy
                if 0 <= px < DISPLAY_W and 0 <= py < DISPLAY_H:
                    self._bitmap[px, py] = color_idx

    def _draw_char(self, char, x, y, color_idx):
        if char not in TINY_FONT:
            return
        rows = TINY_FONT[char]
        for row_idx, row in enumerate(rows):
            for col in range(3):
                px = x + col
                py = y + row_idx
                if 0 <= px < DISPLAY_W and 0 <= py < DISPLAY_H:
                    if row & (0b100 >> col):
                        self._bitmap[px, py] = color_idx
                    else:
                        self._bitmap[px, py] = _BG

    def _draw_text(self, text, x, y, color_idx):
        cursor_x = x
        for char in text:
            self._draw_char(char, cursor_x, y, color_idx)
            cursor_x += 4

    def _draw_heart(self, x, y, color_idx):
        for row_idx, row in enumerate(HEART_ICON):
            for col in range(5):
                px = x + col
                py = y + row_idx
                if 0 <= px < DISPLAY_W and 0 <= py < DISPLAY_H:
                    if row & (0b10000 >> col):
                        self._bitmap[px, py] = color_idx
                    else:
                        self._bitmap[px, py] = _BG

    def _draw_lives(self, lives):
        heart_width = 5
        spacing = 1
        max_hearts = 3
        total_width = max_hearts * heart_width + (max_hearts - 1) * spacing
        start_x = (DISPLAY_W - total_width) // 2

        for i in range(max_hearts):
            hx = start_x + i * (heart_width + spacing)
            if i < lives:
                self._draw_heart(hx, 0, _FOOD)
            else:
                for row_idx in range(5):
                    for col in range(5):
                        px = hx + col
                        py = row_idx
                        if 0 <= px < DISPLAY_W and 0 <= py < DISPLAY_H:
                            self._bitmap[px, py] = _BG

    def _draw_big_char(self, char, x, y, color_idx):
        if char not in BIG_FONT:
            return
        rows = BIG_FONT[char]
        for row_idx, row in enumerate(rows):
            for col in range(5):
                px = x + col
                py = y + row_idx
                if 0 <= px < DISPLAY_W and 0 <= py < DISPLAY_H:
                    if row & (0b10000 >> col):
                        self._bitmap[px, py] = color_idx

    def _draw_big_text(self, text, x, y, color_idx):
        cursor_x = x
        for char in text:
            self._draw_big_char(char, cursor_x, y, color_idx)
            cursor_x += 6

    def render(self, model):
        bmp = self._bitmap
        snake_set = set(model.snake)
        prev_snake_set = set(self._prev_snake)

        for pos in prev_snake_set - snake_set:
            if pos != model.food:
                self._draw_cell(pos[0], pos[1], _BG)

        if self._prev_food and self._prev_food != model.food and self._prev_food not in snake_set:
            self._draw_cell(self._prev_food[0], self._prev_food[1], _BG)

        self._draw_cell(model.food[0], model.food[1], _FOOD)

        for i, (sx, sy) in enumerate(model.snake):
            color = _HEAD if i == 0 else _SNAKE
            self._draw_cell(sx, sy, color)

        score_text = "P " + str(self._score)
        if score_text != self._prev_score_text:
            self._draw_text(score_text, 0, 0, _WHITE)
            self._prev_score_text = score_text

        high_text = "H " + str(self._high_score)
        if high_text != self._prev_high_text:
            text_width = len(high_text) * 4 - 1
            self._draw_text(high_text, DISPLAY_W - text_width, 0, _YELLOW)
            self._prev_high_text = high_text

        if self._lives != self._prev_lives:
            self._draw_lives(self._lives)
            self._prev_lives = self._lives

        self._prev_snake = list(model.snake)
        self._prev_food = model.food

    def update_score(self, score):
        self._score = score

    def update_high_score(self, high_score):
        self._high_score = high_score

    def update_lives(self, lives):
        self._lives = lives

    def show_game_over(self, score, high_score, duration=3.0):
        for y in range(DISPLAY_H):
            for x in range(DISPLAY_W):
                self._bitmap[x, y] = _BG

        self._draw_big_text("GAME", (DISPLAY_W - 24) // 2, 4, _FOOD)
        self._draw_big_text("OVER", (DISPLAY_W - 24) // 2, 18, _FOOD)

        time.sleep(duration)

        for y in range(DISPLAY_H):
            for x in range(DISPLAY_W):
                self._bitmap[x, y] = _BG

        print("Game Over! Score: " + str(score) + "  High: " + str(high_score))

        self._prev_snake = []
        self._prev_food = None
        self._prev_score_text = ""
        self._prev_high_text = ""
        self._prev_lives = -1

    def play_food_sfx(self):
        self._play(self._sfx_food)

    def play_gameover_sfx(self):
        self._play(self._sfx_gameover)

    def play_life_lost_sfx(self):
        self._play(self._sfx_gameover)

    def _play(self, wav):
        if wav is None or self._audio is None:
            return
        try:
            if self._audio.is_playing:
                self._audio.stop()
            self._audio._audio.play(wav)
        except Exception as e:
            print("Audio play error:", e)
