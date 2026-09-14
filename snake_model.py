# snake_model.py - MODEL (MVC pattern)
# Ported for 64x32 RGB Matrix with 32x16 grid (2x2 pixels per cell)

import struct
import microcontroller

UP    = (0, -1)
DOWN  = (0,  1)
LEFT  = (-1, 0)
RIGHT = (1,  0)

GRID_W = 32
GRID_H = 16

_NVM_MAGIC = b"HSv1"
_NVM_FMT   = "<4sH"
_NVM_SIZE  = struct.calcsize(_NVM_FMT)


class SnakeModel:
    def __init__(self):
        self.snake     = []
        self.direction = RIGHT
        self.food      = (GRID_W // 3, GRID_H // 3)
        self.grow      = 0
        self.score     = 0
        self.high_score = 0
        self.lives     = 3

        self._load_high_score()
        self.reset()

    def reset(self):
        """Reset the snake to starting position in centre of grid."""
        self.snake = [(GRID_W // 2 + i, GRID_H // 2)
                      for i in range(1, -3, -1)]
        self.direction = RIGHT
        self.grow = 0
        self.score = 0

    def reset_full(self):
        """Full reset including lives for a new game."""
        self.lives = 3
        self.reset()

    def lose_life(self):
        """Decrement lives. Returns True if game over (no lives left)."""
        self.lives -= 1
        return self.lives <= 0

    def set_direction(self, new_dir):
        """Accept a new direction. Rejects 180-degree reversals."""
        rev = (-self.direction[0], -self.direction[1])
        if new_dir != rev:
            self.direction = new_dir

    def step(self):
        """Advance the game by one tick.

        Returns:
            None       -- normal move
            "ate_food" -- snake ate the food pellet
            "died"     -- snake hit wall or itself
        """
        dx, dy = self.direction
        nx = self.snake[0][0] + dx
        ny = self.snake[0][1] + dy

        # Wall collision
        if nx < 0 or ny < 0 or nx >= GRID_W or ny >= GRID_H:
            return "died"
        # Self collision
        if (nx, ny) in self.snake:
            return "died"

        # Move snake
        self.snake.insert(0, (nx, ny))

        # Check if we ate food
        event = None
        if (nx, ny) == self.food:
            self.score += 1
            if self.score > self.high_score:
                self.high_score = self.score
                self._save_high_score()
            self.grow += 2
            self._place_food()
            event = "ate_food"

        # Grow or trim tail
        if self.grow > 0:
            self.grow -= 1
        else:
            self.snake.pop()

        return event

    def _place_food(self):
        """Find an empty cell for the next food pellet."""
        start = ((self.food[0] + 7) % GRID_W, (self.food[1] + 5) % GRID_H)
        snake_set = set(self.snake)
        for dy in range(GRID_H):
            for dx in range(GRID_W):
                x = (start[0] + dx) % GRID_W
                y = (start[1] + dy) % GRID_H
                if (x, y) not in snake_set:
                    self.food = (x, y)
                    return

    @staticmethod
    def _nvm_available():
        return getattr(microcontroller, "nvm", None) is not None

    def _load_high_score(self):
        if not self._nvm_available() or len(microcontroller.nvm) < _NVM_SIZE:
            self.high_score = 0
            return
        raw = bytes(microcontroller.nvm[0:_NVM_SIZE])
        try:
            magic, hs = struct.unpack(_NVM_FMT, raw)
            self.high_score = hs if magic == _NVM_MAGIC else 0
        except Exception:
            self.high_score = 0

    def _save_high_score(self):
        if not self._nvm_available() or len(microcontroller.nvm) < _NVM_SIZE:
            return
        try:
            microcontroller.nvm[0:_NVM_SIZE] = struct.pack(
                _NVM_FMT, _NVM_MAGIC, min(self.high_score, 65535)
            )
        except Exception:
            pass
