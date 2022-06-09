import win32con
import win32console
import win32file
import pywintypes
# hello world 


class Event(object):
    """
    A class to hold information about an input event.

    The exact contents varies from event to event.  See specific classes for more information.
    """


class KeyboardEvent(Event):
    """
    An event that represents a key press.

    Its key field is the `key_code`.  This is the ordinal representation of the key (taking into
    account keyboard state - e.g. caps lock) if possible, or an extended key code (the `KEY_xxx`
    constants in the :py:obj:`.Screen` class) where not.
    """

    def __init__(self, key_code: int):
        """
        :param key_code: the ordinal value of the key that was pressed.
        """
        self.key_code: int = key_code

    def __repr__(self):
        """
        :returns: a string representation of the keyboard event.
        """
        return f"KeyboardEvent: {self.key_code}"


class MouseEvent(Event):
    """
    An event that represents a mouse move or click.

    Allowed values for the buttons are any bitwise combination of
    `LEFT_CLICK`, `RIGHT_CLICK` and `DOUBLE_CLICK`.
    """

    # Mouse button states - bitwise flags
    LEFT_CLICK = 1
    RIGHT_CLICK = 2
    DOUBLE_CLICK = 4

    def __init__(self, x_pos: int, y_pos: int, buttons: int):
        """
        :param x: The X coordinate of the mouse event.
        :param y: The Y coordinate of the mouse event.
        :param buttons: A bitwise flag for any mouse buttons that were pressed (if any).
        """
        self.x_pos: int = x_pos
        self.y_pos: int = y_pos
        self.buttons: int = buttons

    def __repr__(self):
        """
        :returns: a string representation of the mouse event.
        """
        return f"MouseEvent ({self.x_pos}, {self.y_pos}) {self.buttons}"


# Virtual key code mapping.
KEY_MAP = {
    win32con.VK_ESCAPE: -1,
    win32con.VK_F1: -2,
    win32con.VK_F2: -3,
    win32con.VK_F3: -4,
    win32con.VK_F4: -5,
    win32con.VK_F5: -6,
    win32con.VK_F6: -7,
    win32con.VK_F7: -8,
    win32con.VK_F8: -9,
    win32con.VK_F9: -10,
    win32con.VK_F10: -11,
    win32con.VK_F11: -12,
    win32con.VK_F12: -13,
    win32con.VK_F13: -14,
    win32con.VK_F14: -15,
    win32con.VK_F15: -16,
    win32con.VK_F16: -17,
    win32con.VK_F17: -18,
    win32con.VK_F18: -19,
    win32con.VK_F19: -20,
    win32con.VK_F20: -21,
    win32con.VK_F21: -22,
    win32con.VK_F22: -23,
    win32con.VK_F23: -24,
    win32con.VK_F24: -25,
    win32con.VK_PRINT: -100,
    win32con.VK_INSERT: -101,
    win32con.VK_DELETE: -102,
    win32con.VK_HOME: -200,
    win32con.VK_END: -201,
    win32con.VK_LEFT: -203,
    win32con.VK_UP: -204,
    win32con.VK_RIGHT: -205,
    win32con.VK_DOWN: -206,
    win32con.VK_PRIOR: -207,
    win32con.VK_NEXT: -208,
    win32con.VK_BACK: -300,
    win32con.VK_TAB: -301
}
# Looks like pywin32 is missing some Windows constants
ENABLE_EXTENDED_FLAGS = 0x0080
ENABLE_QUICK_EDIT_MODE = 0x0040

#: Regex for asciimatics ${c,a,b} embedded colour attributes.
COLOUR_REGEX = r"^\$\{((\d+),(\d+),(\d+)|(\d+),(\d+)|(\d+))\}(.*)"

# Text attributes for use when printing to the Screen.
A_BOLD = 1
A_NORMAL = 2
A_REVERSE = 3
A_UNDERLINE = 4

# Text colours for use when printing to the Screen.
COLOUR_DEFAULT = -1
COLOUR_BLACK = 0
COLOUR_RED = 1
COLOUR_GREEN = 2
COLOUR_YELLOW = 3
COLOUR_BLUE = 4
COLOUR_MAGENTA = 5
COLOUR_CYAN = 6
COLOUR_WHITE = 7

# Line drawing style constants
ASCII_LINE = 0
SINGLE_LINE = 1
DOUBLE_LINE = 2


COLOURS = {
    COLOUR_DEFAULT: (win32console.FOREGROUND_RED |
                     win32console.FOREGROUND_GREEN |
                     win32console.FOREGROUND_BLUE),
    COLOUR_BLACK: 0,
    COLOUR_RED: win32console.FOREGROUND_RED,
    COLOUR_GREEN: win32console.FOREGROUND_GREEN,
    COLOUR_YELLOW: (win32console.FOREGROUND_RED |
                    win32console.FOREGROUND_GREEN),
    COLOUR_BLUE: win32console.FOREGROUND_BLUE,
    COLOUR_MAGENTA: (win32console.FOREGROUND_RED |
                     win32console.FOREGROUND_BLUE),
    COLOUR_CYAN: (win32console.FOREGROUND_BLUE |
                  win32console.FOREGROUND_GREEN),
    COLOUR_WHITE: (win32console.FOREGROUND_RED |
                   win32console.FOREGROUND_GREEN |
                   win32console.FOREGROUND_BLUE)
}

# Background colour lookup table.
BG_COLOURS = {
    COLOUR_DEFAULT: 0,
    COLOUR_BLACK: 0,
    COLOUR_RED: win32console.BACKGROUND_RED,
    COLOUR_GREEN: win32console.BACKGROUND_GREEN,
    COLOUR_YELLOW: (win32console.BACKGROUND_RED |
                    win32console.BACKGROUND_GREEN),
    COLOUR_BLUE: win32console.BACKGROUND_BLUE,
    COLOUR_MAGENTA: (win32console.BACKGROUND_RED |
                     win32console.BACKGROUND_BLUE),
    COLOUR_CYAN: (win32console.BACKGROUND_BLUE |
                  win32console.BACKGROUND_GREEN),
    COLOUR_WHITE: (win32console.BACKGROUND_RED |
                   win32console.BACKGROUND_GREEN |
                   win32console.BACKGROUND_BLUE)
}

# Attribute lookup table
ATTRIBUTES = {
    0: lambda x: x,
    A_BOLD: lambda x: x | win32console.FOREGROUND_INTENSITY,
    A_NORMAL: lambda x: x,
    # Windows console uses a bitmap where background is the top nibble,
    # so we can reverse by swapping nibbles.
    A_REVERSE: lambda x: ((x & 15) * 16) + ((x & 240) // 16),
    A_UNDERLINE: lambda x: x
}


# Clone the standard output buffer so that we can do whatever we
# need for the application, but restore the buffer at the end.
# Note that we need to resize the clone to ensure that it is the
# same size as the original in some versions of Windows.
old_out_def = win32console.PyConsoleScreenBufferType(
    win32file.CreateFile("CONOUT$",
                         win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                         win32file.FILE_SHARE_WRITE,
                         None,
                         win32file.OPEN_ALWAYS,
                         0,
                         None))
try:
    info_def = old_out_def.GetConsoleScreenBufferInfo()
    # unused pylint:  disable=no-member
except pywintypes.error:
    info_def = None
win_out = win32console.CreateConsoleScreenBuffer()
if info_def:
    win_out.SetConsoleScreenBufferSize(info_def['Size'])
else:
    win_out.SetStdHandle(win32console.STD_OUTPUT_HANDLE)
win_out.SetConsoleActiveScreenBuffer()

# Get the standard input buffer.
win_in = win32console.PyConsoleScreenBufferType(
    win32file.CreateFile("CONIN$",
                         win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                         win32file.FILE_SHARE_READ,
                         None,
                         win32file.OPEN_ALWAYS,
                         0,
                         None))
win_in.SetStdHandle(win32console.STD_INPUT_HANDLE)

# Hide the cursor.
win_out.SetConsoleCursorInfo(1, 0)

# Disable scrolling
out_mode = win_out.GetConsoleMode()
win_out.SetConsoleMode(
    out_mode & ~ win32console.ENABLE_WRAP_AT_EOL_OUTPUT)

# Enable mouse input, disable quick-edit mode and disable ctrl-c
# if needed.
in_mode = win_in.GetConsoleMode()
new_mode = (in_mode | win32console.ENABLE_MOUSE_INPUT |
            ENABLE_EXTENDED_FLAGS)
new_mode &= ~ENABLE_QUICK_EDIT_MODE
win_in.SetConsoleMode(new_mode)
