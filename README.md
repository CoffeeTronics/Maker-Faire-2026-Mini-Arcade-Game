# Mini Arcade Game - Maker Faire 2026

A multi-game arcade system running on the Microchip Curiosity PyKit Explorer with a 64x32 RGB LED Matrix display. Features classic games: Snake, Pong, and Tetris.

## Table of Contents

- [Overview](#overview)
- [Hardware Requirements](#hardware-requirements)
- [Pin Connections](#pin-connections)
- [Controls](#controls)
- [Games](#games)
- [File Structure](#file-structure)
- [Installation](#installation)
- [Adding New Games](#adding-new-games)
- [Troubleshooting](#troubleshooting)

---

## Overview

This project creates a retro-style arcade cabinet using:
- **Microcontroller**: Microchip Curiosity PyKit Explorer (SAMD51)
- **Display**: 64x32 RGB LED Matrix (HUB75 interface)
- **Input**: 4-direction digital joystick + 4 arcade buttons
- **Language**: CircuitPython

The unified game launcher automatically discovers games in the `/games/` folder and cycles through them. Each game manages its own logic while sharing common hardware resources.

---

## Hardware Requirements

### Core Components

| Component | Description | Quantity |
|-----------|-------------|----------|
| Curiosity PyKit Explorer | SAMD51-based dev board | 1 |
| 64x32 RGB LED Matrix | HUB75 interface, 3mm or 4mm pitch | 1 |
| RGB Matrix Portal | Adafruit MatrixPortal or FeatherWing | 1 |
| 5V Power Supply | 4A minimum for matrix | 1 |
| Digital Joystick | 4-direction with common ground | 1 |
| Arcade Buttons | Momentary push buttons | 4 |

### Optional Components

| Component | Description |
|-----------|-------------|
| Speaker/Buzzer | 8 ohm speaker for audio feedback |
| Enclosure | 3D printed or wooden arcade cabinet |
| USB Cable | For programming and serial debug |

---

## Pin Connections

### Joystick (4-Direction Digital)

| Direction | Board Pin | GPIO | Pull Mode | Active State |
|-----------|-----------|------|-----------|--------------|
| Up | `board.LCD_SCK` | PA13 | Pull-DOWN | HIGH |
| Down | `board.LCD_CS` | PA12 | Pull-DOWN | HIGH |
| Left | `board.LCD_BL` | PA06 | Pull-DOWN | HIGH |
| Right | `board.LCD_MOSI` | PA15 | Pull-DOWN | HIGH |

**Wiring:** Connect each joystick direction switch between the corresponding pin and 3.3V. The internal pull-down resistor keeps the pin LOW when not pressed.

```
Joystick Switch ----+---- 3.3V
                    |
Board Pin ----------+
(internal pull-down to GND)
```

### Arcade Buttons

| Button | Function | Board Pin | GPIO | Pull Mode | Active State |
|--------|----------|-----------|------|-----------|--------------|
| A | Action 1 | `board.D4` | PA04 | Pull-DOWN | HIGH |
| B | Action 2 | `board.D5` | PA05 | Pull-DOWN | HIGH |
| C | Select (Switch Game) | `board.D6` | PA06 | Pull-DOWN | HIGH |
| D | Start | `board.D7` | PA07 | Pull-DOWN | HIGH |

**Wiring:** Same as joystick - connect each button between the pin and 3.3V.

```
Button ----+---- 3.3V
           |
Board Pin -+
(internal pull-down to GND)
```

### RGB Matrix Display

The RGB Matrix uses the HUB75 interface via the Adafruit MatrixPortal library. Pin assignments are handled automatically by the library based on your board configuration.

| Signal | Description |
|--------|-------------|
| R1, G1, B1 | Upper half RGB data |
| R2, G2, B2 | Lower half RGB data |
| A, B, C, D | Row select (directly addressed by MatrixPortal library) |
| CLK | Pixel clock |
| LAT | Latch signal |
| OE | Output enable |

### Audio Output (Optional)

| Signal | Board Pin | Description |
|--------|-----------|-------------|
| Audio | `board.DAC` | DAC output for speaker |

Connect an 8 ohm speaker between DAC and GND (use a small amplifier for louder sound).

---

## Controls

### Button Layout

```
      [JOYSTICK]              [BUTTONS]
         ^
         |                   [A]  [B]
    <----+---->
         |                   [C]  [D]
         v                  Select Start
```

### Button Functions

| Button | In Menu | In Game |
|--------|---------|---------|
| **A** | Start game | Primary action (jump, rotate, etc.) |
| **B** | - | Secondary action (run, hold, etc.) |
| **C (Select)** | - | Switch to next game |
| **D (Start)** | Start game | Start/Pause |
| **Joystick** | Start game (any direction) | Move character/piece |

### Game-Specific Controls

#### Snake
- **Joystick**: Change snake direction (up/down/left/right)
- **Start (D)**: Begin game from menu

#### Pong
- **Joystick Up/Down**: Move paddle
- **A or Start (D)**: Begin game from menu

#### Tetris
- **Joystick Left/Right**: Move piece horizontally
- **Joystick Down**: Soft drop (faster fall)
- **A**: Rotate piece clockwise
- **B**: Rotate piece counter-clockwise
- **Start (D)**: Begin game from menu

---

## Games

### Snake

The classic snake game. Eat food to grow longer, avoid hitting walls and yourself.

- **Objective**: Eat as much food as possible without colliding
- **Scoring**: Points increase with each food item
- **Lives**: 3 lives per game
- **Speed**: Increases as snake grows

### Pong

Single-player Pong against an AI opponent.

- **Objective**: Score points by getting the ball past the AI paddle
- **Scoring**: First to 5 points wins
- **AI Difficulty**: Adaptive based on ball speed

### Tetris

The classic falling block puzzle game.

- **Objective**: Complete horizontal lines to clear them
- **Scoring**: More points for clearing multiple lines at once
- **Speed**: Increases with level (every 10 lines cleared)
- **Game Over**: When blocks stack to the top

---

## File Structure

```
CIRCUITPY/
|-- code.py                 # Main game launcher
|-- base_game.py            # Base class for all games
|-- high_scores.py          # NVM-based high score persistence
|
|-- API/                    # Hardware abstraction modules
|   |-- buttons.py          # 4-button arcade input
|   |-- joystick.py         # 4-direction joystick input
|   |-- matrix_display.py   # 64x32 RGB matrix display
|   |-- audio_out.py        # DAC audio output
|   |-- digital_io.py       # GPIO helpers
|   +-- ...                 # Other PyKit modules
|
|-- games/                  # Game implementations
|   |-- view_utils.py       # Shared rendering utilities
|   |
|   |-- snake/              # Snake game
|   |   |-- __init__.py     # SnakeGame class (controller)
|   |   |-- model.py        # Game logic and state
|   |   +-- view.py         # Display rendering
|   |
|   |-- pong/               # Pong game
|   |   |-- __init__.py     # PongGame class (controller)
|   |   |-- model.py        # Game logic and state
|   |   +-- view.py         # Display rendering
|   |
|   +-- tetris/             # Tetris game
|       |-- __init__.py     # TetrisGame class (controller)
|       |-- model.py        # Game logic and state
|       +-- view.py         # Display rendering
|
|-- lib/                    # Adafruit/third-party libraries
|   |-- adafruit_matrixportal/
|   |-- adafruit_display_shapes/
|   +-- ...
|
|-- AudioFiles/             # Sound effects (WAV files)
|-- Sprites/                # Game graphics (BMP files)
+-- Fonts/                  # Custom fonts
```

### Architecture

Each game follows the **Model-View-Controller (MVC)** pattern:

- **`__init__.py`** (Controller): Handles input, coordinates model and view
- **`model.py`** (Model): Game state, logic, collision detection
- **`view.py`** (View): Rendering, animations, sound effects

---

## Installation

### Step 1: Prepare the PyKit Explorer

1. Connect the PyKit Explorer to your computer via USB
2. Install CircuitPython 9.x on the board (if not already installed)
3. The board should appear as a USB drive named `CIRCUITPY`

### Step 2: Install Required Libraries

Copy these Adafruit libraries to the `/lib/` folder on CIRCUITPY:

- `adafruit_matrixportal/`
- `adafruit_display_shapes/`
- `adafruit_display_text/`
- `adafruit_imageload/`
- `adafruit_bitmap_font/`

You can get these from the [Adafruit CircuitPython Bundle](https://circuitpython.org/libraries).

### Step 3: Copy Project Files

1. Clone or download this repository
2. Copy all files and folders to the CIRCUITPY drive:
   - `code.py`
   - `base_game.py`
   - `high_scores.py`
   - `API/` folder
   - `games/` folder
   - `AudioFiles/` folder (optional, for sound)
   - `Sprites/` folder (optional, for graphics)

### Step 4: Connect Hardware

1. Connect the RGB Matrix to the MatrixPortal
2. Wire the joystick and buttons according to the [Pin Connections](#pin-connections) section
3. Connect 5V power to the RGB Matrix
4. Connect optional speaker to DAC output

### Step 5: Power On

The game launcher will start automatically and display the first game's title screen.

---

## Adding New Games

To create a new game, follow these steps:

### 1. Create Game Folder

```
games/
+-- mygame/
    |-- __init__.py    # Required: Game controller class
    |-- model.py       # Game logic
    +-- view.py        # Display rendering
```

### 2. Implement the Game Class

In `games/mygame/__init__.py`:

```python
import time
import gc
from base_game import BaseGame

class MyGame(BaseGame):
    NAME = "My Game"           # Display name
    HIGH_SCORE_SLOT = 3        # Unique slot 0-29 for high scores
    GAME_OVER_SOUND = None     # Optional: "/AudioFiles/gameover.wav"

    def setup(self):
        """Initialize game resources."""
        gc.collect()
        # Create your model and view here
        self._state = "menu"

    def run(self):
        """Main game loop."""
        while True:
            self.buttons.update()
            
            # Check for game switch (Select button)
            if self.buttons.c_fell:
                return "switch"
            
            # Check for start button
            if self._state == "menu" and self.buttons.d_fell:
                self._state = "playing"
            
            # Your game logic here...
            
            # Return "gameover" when player loses
            if game_over_condition:
                return "gameover"
            
            time.sleep(0.033)  # ~30 FPS

    def cleanup(self):
        """Release game resources."""
        # Stop audio, clear display groups, etc.
        pass
```

### 3. Use Shared Resources

Your game receives these shared hardware instances:

```python
self.display      # MatrixDisplay - 64x32 RGB matrix
self.joystick     # Joystick - up, down, left, right properties
self.buttons      # ButtonSet - a_fell, b_fell, c_fell, d_fell
self.audio        # AudioOutput - play_wav(), play_tone()
self.high_scores  # HighScoreManager - get(), set()
```

### 4. The Game Will Auto-Load

The launcher automatically discovers any folder in `/games/` that contains an `__init__.py` with a class inheriting from `BaseGame`.

---

## Troubleshooting

### Display Not Working

- Check 5V power supply is connected to the RGB Matrix
- Verify MatrixPortal connections to the matrix
- Ensure `adafruit_matrixportal` library is installed

### Buttons/Joystick Not Responding

- Verify wiring: buttons should connect to 3.3V (not 5V)
- Check pin assignments match your wiring
- Test with a simple script:

```python
import time
from buttons import ButtonSet
from joystick import Joystick

buttons = ButtonSet()
joystick = Joystick()

while True:
    buttons.update()
    print(f"A:{buttons.a_pressed} B:{buttons.b_pressed} "
          f"C:{buttons.c_pressed} D:{buttons.d_pressed}")
    print(f"Up:{joystick.up} Down:{joystick.down} "
          f"Left:{joystick.left} Right:{joystick.right}")
    time.sleep(0.1)
```

### Game Not Loading

- Check the game folder has `__init__.py`
- Verify the game class inherits from `BaseGame`
- Check serial console for error messages: `screen /dev/ttyACM0 115200`

### Out of Memory

- Reduce display bit depth in `MatrixDisplay(bit_depth=1)`
- Use smaller sprites and fewer colors
- Call `gc.collect()` regularly in your game loop

### No Sound

- Verify speaker is connected to `board.DAC` and GND
- Check WAV files are 16-bit, mono, 22050 Hz or lower
- Ensure `AudioFiles/` folder exists with valid WAV files

---

## License

This project is open source and available for educational purposes.

## Credits

- **Hardware**: Microchip Curiosity PyKit Explorer
- **Display**: Adafruit MatrixPortal library
- **Games**: Classic arcade game concepts
- **Created for**: Maker Faire 2026
