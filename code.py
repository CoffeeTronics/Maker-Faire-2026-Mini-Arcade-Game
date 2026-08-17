# code.py - Unified Game Launcher for PyKit Explorer
# ==================================================
# For 64x32 RGB Matrix with Joystick and Buttons
#
# Launcher Flow:
# --------------
# 1. Initialize shared hardware (RGB Matrix, Joystick, Buttons, Audio)
# 2. Discover games by scanning /games/ subfolders for BaseGame classes
# 3. Main loop:
#    a. Show transition screen with next game name (3 seconds)
#    b. Create fresh AudioOutput for the game
#    c. Instantiate game class with shared hardware
#    d. Call game.setup() to initialize game-specific resources
#    e. Call game.run() - runs until game over or Button C (Select) press
#    f. Call game.cleanup() to release game-specific resources
#    g. Deinit audio to free DAC
#    h. Cycle to next game and repeat
#
# Hardware Resources (shared across all games):
# ---------------------------------------------
# - display: MatrixDisplay (64x32 RGB Matrix)
# - joystick: Joystick (4-direction digital joystick)
# - buttons: ButtonSet (4 arcade buttons A, B, Select=C, Start=D)
# - audio: AudioOutput (created fresh for each game)
# - high_scores: HighScoreManager (NVM persistence)

import sys
sys.path.insert(0, "/API")

import time
import gc
import os
import displayio

from matrix_display import MatrixDisplay, WIDTH, HEIGHT
from joystick import Joystick
from buttons import ButtonSet
from audio_out import AudioOutput
from high_scores import HighScoreManager
from base_game import BaseGame
from games.view_utils import draw_tiny_text, draw_big_text, clear_bitmap, text_width_tiny

TRANSITION_DURATION = 3.0
GAME_OVER_DURATION = 5.0


def discover_games():
    games = []
    possible_paths = ["/games", "games", "./games"]
    games_path = None
    for path in possible_paths:
        try:
            entries = os.listdir(path)
            games_path = path
            print(f"Found games folder at: {path}")
            break
        except OSError:
            continue
    if games_path is None:
        print("ERROR: games folder not found")
        return games
    print(f"Games folder contents: {entries}")
    for name in entries:
        if name.startswith(".") or name.startswith("_"):
            continue
        if name.endswith(".md") or name.endswith(".txt") or name.endswith(".py"):
            continue
        folder_path = f"{games_path}/{name}"
        try:
            stat_result = os.stat(folder_path)
            is_dir = stat_result[0] & 0x4000
            if not is_dir:
                continue
        except OSError as e:
            print(f"  Cannot stat {folder_path}: {e}")
            continue
        init_path = f"{folder_path}/__init__.py"
        try:
            os.stat(init_path)
        except OSError:
            print(f"  Skipping {name}: no __init__.py")
            continue
        try:
            print(f"  Importing games.{name}...")
            module = __import__(f"games.{name}")
            submodule = getattr(module, name)
            for attr_name in dir(submodule):
                attr = getattr(submodule, attr_name)
                if (isinstance(attr, type) and
                    issubclass(attr, BaseGame) and
                    attr is not BaseGame):
                    games.append(attr)
                    print(f"  Loaded: {attr.NAME}")
                    break
        except Exception as e:
            print(f"  Error loading {name}: {e}")
    return games


def show_transition_screen(display, game_name):
    """Show transition screen on 64x32 matrix."""
    gc.collect()

    # Create bitmap for transition
    bitmap = displayio.Bitmap(WIDTH, HEIGHT, 3)
    palette = displayio.Palette(3)
    palette[0] = 0x000020  # dark blue bg
    palette[1] = 0xFFFFFF  # white text
    palette[2] = 0x00FF00  # green text

    # Fill background
    for y in range(HEIGHT):
        for x in range(WIDTH):
            bitmap[x, y] = 0

    # Draw "NEXT:" centered
    text1 = "NEXT:"
    text_w1 = text_width_tiny(text1)
    x1 = (WIDTH - text_w1) // 2
    draw_tiny_text(bitmap, text1, x1, 6, 1)

    # Draw game name centered (truncate if too long)
    name_upper = game_name.upper()[:10]
    text_w2 = text_width_tiny(name_upper)
    x2 = (WIDTH - text_w2) // 2
    draw_tiny_text(bitmap, name_upper, x2, 16, 2)

    # Set as display root
    tg = displayio.TileGrid(bitmap, pixel_shader=palette)
    grp = displayio.Group()
    grp.append(tg)
    display.root_group = grp


def show_game_over_screen(display, buttons, game_class):
    """Show game-over screen on 64x32 matrix."""
    gc.collect()

    # Create bitmap for game over
    bitmap = displayio.Bitmap(WIDTH, HEIGHT, 2)
    palette = displayio.Palette(2)
    palette[0] = 0x000000  # black bg
    palette[1] = 0xFF0000  # red text

    # Fill background
    for y in range(HEIGHT):
        for x in range(WIDTH):
            bitmap[x, y] = 0

    # Draw "GAME OVER" centered using big font
    draw_big_text(bitmap, "GAME", (WIDTH - 24) // 2, 4, 1)
    draw_big_text(bitmap, "OVER", (WIDTH - 24) // 2, 18, 1)

    # Set as display root
    tg = displayio.TileGrid(bitmap, pixel_shader=palette)
    grp = displayio.Group()
    grp.append(tg)
    display.root_group = grp

    # Play game over sound if available
    audio_obj = None
    if game_class.GAME_OVER_SOUND:
        try:
            audio_obj = AudioOutput()
            audio_obj.play_wav(game_class.GAME_OVER_SOUND)
            print(f"Playing game over sound: {game_class.GAME_OVER_SOUND}")
        except Exception as e:
            print(f"Game over sound failed: {e}")

    # Wait for duration or button press
    start = time.monotonic()
    while time.monotonic() - start < GAME_OVER_DURATION:
        buttons.update()
        if buttons.c_fell:  # Select = skip game over
            print("Button C pressed")
            break
        if audio_obj and not audio_obj.is_playing:
            time.sleep(1.0)
            break
        time.sleep(0.05)

    if audio_obj:
        try:
            audio_obj.stop()
            audio_obj.deinit()
        except:
            pass
    gc.collect()


def show_error(display, message):
    """Show error message on 64x32 matrix."""
    bitmap = displayio.Bitmap(WIDTH, HEIGHT, 2)
    palette = displayio.Palette(2)
    palette[0] = 0x400000  # dark red bg
    palette[1] = 0xFFFFFF  # white text

    for y in range(HEIGHT):
        for x in range(WIDTH):
            bitmap[x, y] = 0

    # Truncate message to fit
    msg_upper = message.upper()[:16]
    text_w = text_width_tiny(msg_upper)
    x = (WIDTH - text_w) // 2
    draw_tiny_text(bitmap, msg_upper, x, 13, 1)

    tg = displayio.TileGrid(bitmap, pixel_shader=palette)
    grp = displayio.Group()
    grp.append(tg)
    display.root_group = grp


def clear_display(display):
    try:
        empty = displayio.Group()
        display.root_group = empty
    except:
        pass
    gc.collect()


def main():
    gc.collect()
    print("=" * 50)
    print("UNIFIED GAME LAUNCHER (RGB Matrix)")
    print("=" * 50)
    print(f"Free RAM: {gc.mem_free()} bytes")

    print("\nInitializing hardware...")
    matrix = MatrixDisplay()
    joystick = Joystick()
    buttons = ButtonSet()
    high_scores = HighScoreManager()

    print("\nDiscovering games...")
    game_classes = discover_games()
    if not game_classes:
        print("ERROR: No games found!")
        show_error(matrix.display, "No games")
        while True:
            time.sleep(1)

    print(f"\nFound {len(game_classes)} game(s)")

    current_game_index = None
    current_game = None

    while True:
        current_game_index = 0 if current_game_index is None else (current_game_index + 1) % len(game_classes)
        game_class = game_classes[current_game_index]

        clear_display(matrix.display)
        gc.collect()
        print(f"Pre-switch RAM: {gc.mem_free()} bytes")
        print(f"\nSwitching to: {game_class.NAME}")

        show_transition_screen(matrix.display, game_class.NAME)
        time.sleep(TRANSITION_DURATION)

        clear_display(matrix.display)
        gc.collect()

        audio = AudioOutput()
        gc.collect()

        current_game = game_class(matrix, joystick, buttons, audio, high_scores)

        try:
            gc.collect()
            current_game.setup()
        except Exception as e:
            print(f"Setup error: {e}")
            if current_game:
                try:
                    current_game.cleanup()
                except:
                    pass
            try:
                audio.deinit()
            except:
                pass
            clear_display(matrix.display)
            gc.collect()
            continue

        exit_reason = None
        try:
            exit_reason = current_game.run()
        except Exception as e:
            print(f"Runtime error: {e}")
            exit_reason = "switch"

        try:
            current_game.cleanup()
        except Exception as e:
            print(f"Cleanup error: {e}")

        try:
            audio.deinit()
        except:
            pass

        current_game = None
        clear_display(matrix.display)
        gc.collect()
        gc.collect()
        print(f"Post-cleanup RAM: {gc.mem_free()} bytes")

        if exit_reason == "gameover":
            show_game_over_screen(matrix.display, buttons, game_class)
            clear_display(matrix.display)
            gc.collect()

        print(f"Switched. Free RAM: {gc.mem_free()} bytes")


if __name__ == "__main__":
    main()
