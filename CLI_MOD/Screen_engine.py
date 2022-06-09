# -*- coding: utf-8 -*-
"""
This module defines common screen output function.
"""


import win32con
import win32console
import pywintypes
from . import const


class _DoubleBuffer(object):
    """
    Pure python Screen buffering.
    """

    def __init__(self, height: int, width: int):
        """
        :param height: Height of the buffer to create.
        :param width: Width of the buffer to create.
        """
        super(_DoubleBuffer, self).__init__()
        self.height = height
        self.width = width
        self._double_buffer = None
        line = [(" ", const.COLOUR_WHITE, 0, 0, 1)
                for _ in range(self.width)]
        self._screen_buffer = [line[:] for _ in range(self.height)]
        self.clear()

    def clear(self, fg=const.COLOUR_WHITE, attr=0, bg=0):
        """
        Clear a box in the double-buffer.

        This does not clear the screen buffer and so the
        next call to deltas will still show all changes.
        Default box is the whole screen buffer.

        :param fg: The foreground colour to use for the new buffer.
        :param attr: The attribute value to use for the new buffer.
        :param bg: The background colour to use for the new buffer.
        :param x: Optional X coordinate for top left of box.
        :param y: Optional Y coordinate for top left of box.
        :param w: Optional width of the box.
        :param h: Optional height of the box.
        """
        line = [(" ", fg, attr, bg, 1)
                for _ in range(self.width)]
        self._double_buffer = [line[:] for _ in range(self.height)]

    def get(self, x_pos: int, y_pos: int):
        """
        Get the cell value from the specified location

        :param x: The column (x coord) of the character.
        :param y: The row (y coord) of the character.

        :return: A 5-tuple of (unicode, foreground, attributes, background, width).
        """
        return self._double_buffer[y_pos][x_pos]

    def set(self, x_pos: int, y_pos: int, value: tuple):
        """
        Set the cell value from the specified location

        :param x: The column (x coord) of the character.
        :param y: The row (y coord) of the character.
        :param value: A 5-tuple of (unicode, foreground, attributes, background, width).
        """
        self._double_buffer[y_pos][x_pos] = value

    def deltas(self, start, height):
        """
        Return a list-like (i.e. iterable) object of (y, x) tuples
        """
        for y in range(start, min(start + height, self.height)):
            for x in range(self.width):
                old_cell = self._screen_buffer[y][x]
                new_cell = self._double_buffer[y][x]
                if old_cell != new_cell:
                    yield y, x

    def slice(self, x_pos, y_pos, width):
        """
        Provide a slice of data from the buffer at the specified location

        :param x: The X origin
        :param y: The Y origin
        :param width: The width of slice required
        :return: The slice of tuples from the current double-buffer
        """
        return self._double_buffer[y_pos][x_pos: x_pos + width]

    def sync(self):
        """
        Synchronize the screen buffer with the double buffer.
        """
        # We're copying an array of tuples, so only need to copy the 2-D array (as the tuples are immutable).
        # This is way faster than a deep copy (which is INCREDIBLY slow).
        self._screen_buffer = [row[:] for row in self._double_buffer]


class _Screen():
    """
    Windows screen implementation.
    """

    def __init__(self, stdout, stdin, old_out, old_in):
        """
        :param stdout: The win32console PyConsoleScreenBufferType object for stdout.
        :param stdin: The win32console PyConsoleScreenBufferType object for stdin.
        :param buffer_height: The buffer height for this window (for testing only).
        :param old_out: The original win32console PyConsoleScreenBufferType object for stdout
            that should be restored on exit.
        :param old_in: The original stdin state that should be restored on exit.
        :param unicode_aware: Whether this Screen can use unicode or not.
        """
        # Save off the screen details and set up the scrolling pad.
        info = stdout.GetConsoleScreenBufferInfo()['Window']
        width = info.Right - info.Left + 1
        height = info.Bottom - info.Top + 1

        # Detect UTF-8 if needed and then construct the Screen.

        # Save off the console details.
        self._stdout = stdout
        self._stdin = stdin
        self._last_width = width
        self._last_height = height
        self._old_out = old_out
        self._old_in = old_in

        # Set of keys currently pressed.
        self._keys = set()

        # start line
        self._last_start_line = 0

        # tracking of current cursor position - used in screen refresh.
        self._cur_x = 0
        self._cur_y = 0

        # Create screen buffers.
        self.height = height
        self.width = width
        self.colours = 0
        self._start_line = 0
        self._x = None
        self._y = None

        # color shit
        self.attr = 0
        self.colour = 7
        self.bg = 0

        # Reset the screen ready to go...
        self.buffer = _DoubleBuffer(self.height, self.width)

    def get_event(self):
        """
        Check for any event without waiting.
        """
        # Look for a new event and consume it if there is one.
        while len(self._stdin.PeekConsoleInput(1)) > 0:
            event = self._stdin.ReadConsoleInput(1)[0]
            if event.EventType == win32console.KEY_EVENT:
                # Pasting unicode text appears to just generate key-up
                # events (as if you had pressed the Alt keys plus the
                # keypad code for the character), but the rest of the
                # console input simply doesn't
                # work with key up events - e.g. misses keyboard repeats.
                #
                # We therefore allow any key press (i.e. KeyDown) event and
                # _any_ event that appears to have popped up from nowhere
                # as long as the Alt key is present.
                key_code = ord(event.Char)
                if (event.KeyDown or
                        (key_code > 0 and key_code not in self._keys and
                            event.VirtualKeyCode == win32con.VK_MENU)):
                    # Record any keys that were pressed.
                    if event.KeyDown:
                        self._keys.add(key_code)

                    # Translate keys into a KeyboardEvent object.
                    if event.VirtualKeyCode in const.KEY_MAP:
                        key_code = const.KEY_MAP[event.VirtualKeyCode]

                    # Sadly, we are limited to Linux terminal input and so
                    # can't return modifier states in a cross-platform way.
                    # If the user decided not to be cross-platform, so be
                    # it, otherwise map some standard bindings for extended
                    # keys.

                        if (event.VirtualKeyCode == win32con.VK_TAB and
                                event.ControlKeyState &
                                win32con.SHIFT_PRESSED):
                            key_code = -302  # back tab

                    # Don't return anything if we didn't have a valid
                    # mapping.
                    if key_code:
                        return const.KeyboardEvent(key_code)
                else:
                    # Tidy up any key that was previously pressed.  At
                    # start-up, we may be mid-key, so can't assume this must
                    # always match up.
                    if key_code in self._keys:
                        self._keys.remove(key_code)

            elif event.EventType == win32console.MOUSE_EVENT:
                # Translate into a MouseEvent object.
                button = 0
                if event.EventFlags == 0:
                    # Button pressed - translate it.
                    if (event.ButtonState &
                            win32con.FROM_LEFT_1ST_BUTTON_PRESSED != 0):
                        button |= const.MouseEvent.LEFT_CLICK
                    if (event.ButtonState &
                            win32con.RIGHTMOST_BUTTON_PRESSED != 0):
                        button |= const.MouseEvent.RIGHT_CLICK
                elif event.EventFlags & win32con.DOUBLE_CLICK != 0:
                    button |= const.MouseEvent.DOUBLE_CLICK

                return const.MouseEvent(event.MousePosition.X,
                                        event.MousePosition.Y,
                                        button)

        # If we get here, we've fully processed the event queue and found
        # nothing interesting.
        return None

    def refresh(self):
        """
        Refresh the screen.
        """

        # Now draw any deltas to the scrolled screen.  Note that CJK character sets sometimes
        # use double-width characters, so don't try to draw the next 2nd char (of 0 width).
        for y, x in self.buffer.deltas(0, self.height):
            new_cell = self.buffer.get(x, y)
            if new_cell[4] > 0:
                self._change_colours(new_cell[1], new_cell[2], new_cell[3])
                # We can throw temporary errors on resizing, so catch and ignore
                # them on the assumption that we'll resize shortly.
                try:
                    # Move the cursor if necessary
                    if x != self._cur_x or y != self._cur_y:
                        self._stdout.SetConsoleCursorPosition(
                            win32console.PyCOORDType(x, y))

                    # Print the text at the required location and update the current
                    # position.
                    self._stdout.WriteConsole(new_cell[0])
                    self._cur_x = x + new_cell[4]
                    self._cur_y = y
                # unused pylint: disable=no-member
                except pywintypes.error:
                    pass

        # Resynch for next refresh.
        self.buffer.sync()

    def _change_colours(self, colour, attr, bg):
        """
        Change current colour if required.

        :param colour: New colour to use.
        :param attr: New attributes to use.
        :param bg: New background colour to use.
        """
        # Change attribute first as this will reset colours when swapping
        # modes.
        if colour != self.colour or attr != self.attr or self.bg != bg:
            new_attr = const.ATTRIBUTES[attr](
                const.COLOURS[colour] + const.BG_COLOURS[bg])
            self._stdout.SetConsoleTextAttribute(new_attr)
            self.attr = attr
            self.colour = colour
            self.bg = bg

    def print_at(self, text, x, y, colour=7, attr=0, bg=0):
        """
        Print the text at the specified location using the specified colour and attributes.

        :param text: The (single line) text to be printed.
        :param x: The column (x coord) for the start of the text.
        :param y: The line (y coord) for the start of the text.
        :param colour: The colour of the text to be displayed.
        :param attr: The cell attribute of the text to be displayed.
        :param bg: The background colour of the text to be displayed.
        :param transparent: Whether to print spaces or not, thus giving a
            transparent effect.

        The colours and attributes are the COLOUR_xxx and A_yyy constants
        defined in the Screen class.
        """
        # Convert to the logically visible window that our double-buffer provides
        y -= self._start_line

        text = str(text)
        if len(text) > 0:
            if x + len(text) > self.width:
                text = text[:self.width - x]
            self.buffer.set(slice(x, x + len(text)), y,
                            [(chr, colour, attr, bg, 1) for chr in text])

    def set_title(self, title):
        """
        Set the title for this terminal/console session.  This will
        typically change the text displayed in the window title bar.

        :param title: The title to be set.
        """
        win32console.SetConsoleTitle(title)


screen = _Screen(
    const.win_out, const.win_in, const.old_out_def, const.in_mode)


def screenWr(func):
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)
    return wrapper
