"""
matrix_display.py - 64x32 RGB Matrix Display
=============================================
Board: Curiosity PyKit with RGB Matrix

Provides a display abstraction for the 64x32 RGB LED Matrix using
the adafruit_matrixportal library.

Display Dimensions: 64 pixels wide x 32 pixels tall
"""

from adafruit_matrixportal.matrix import Matrix

# Display dimensions
WIDTH = 64
HEIGHT = 32


class MatrixDisplay:
    """64x32 RGB Matrix display abstraction.

    Wraps the adafruit_matrixportal Matrix class to provide a consistent
    interface similar to the LCDDisplay class.

    Example
    -------
    from matrix_display import MatrixDisplay, WIDTH, HEIGHT
    import displayio

    matrix = MatrixDisplay()

    # Create a simple display group
    group = displayio.Group()
    bitmap = displayio.Bitmap(WIDTH, HEIGHT, 2)
    palette = displayio.Palette(2)
    palette[0] = 0x000000  # black
    palette[1] = 0xFF0000  # red

    # Draw a red pixel
    bitmap[32, 16] = 1

    group.append(displayio.TileGrid(bitmap, pixel_shader=palette))
    matrix.display.root_group = group
    """

    def __init__(self, width=WIDTH, height=HEIGHT, bit_depth=1):
        """Initialize the RGB Matrix display.

        Parameters
        ----------
        width : int, optional
            Display width in pixels (default: 64)
        height : int, optional
            Display height in pixels (default: 32)
        bit_depth : int, optional
            Color bit depth (default: 1, range 1-6)
            Lower values use less memory but fewer colors.
        """
        self._matrix = Matrix(width=width, height=height, bit_depth=bit_depth)
        self._display = self._matrix.display
        self.width = width
        self.height = height

    @property
    def display(self):
        """The raw displayio Display object for direct access."""
        return self._display

    def fill_screen(self, color):
        """Fill the entire screen with a solid color.

        Parameters
        ----------
        color : int
            24-bit RGB color value (e.g., 0xFF0000 for red)

        Returns
        -------
        displayio.Group
            The root group that was created and applied.
        """
        import displayio
        bitmap = displayio.Bitmap(self.width, self.height, 1)
        palette = displayio.Palette(1)
        palette[0] = color
        tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette)
        group = displayio.Group()
        group.append(tile_grid)
        self._display.root_group = group
        return group

    def clear(self):
        """Clear the display to black."""
        self.fill_screen(0x000000)
