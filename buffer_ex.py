"""
A CLI engine with ctypes that moves the cursor arround and sutff.

This module is meant to be imported and used to handle the output to
the terminal

  Typical usage example:

  import arrays

  BUFFER = arrays.Buffer()
  BUFFER.set_string(5,5, 'hello')
  BUUFER.flush()
"""
import ctypes
from ctypes import c_long, c_ulong
import os
import sys
# make metaclass and abstract calss to serve as main loop, instead of a function,
#  a list of all frames created automaticaly to switch between frame instances
# https://i.stack.imgur.com/KTSQa.png for colors
# ==== GLOBAL VARIABLES ======================


G_HANDLE = ctypes.windll.kernel32.GetStdHandle(c_long(-11))


def move_cursor(x_target_position: int, y_target_position: int):
    """
    Move cursor to position indicated by x and y.
    usefull for the flush function so that only diferent characters
    are printed
    """

    value = x_target_position + (y_target_position << 16)
    ctypes.windll.kernel32.SetConsoleCursorPosition(G_HANDLE, c_ulong(value))


def coloring_toddler(text: str, fg_color: int = 15, bg_color: int = 0, attr_val: int = 1):
    """
    this function generates an escape sequence that is used to color the text
    purely for aestethics
    """

    return_string = f'\033[{attr_val};38;5;{fg_color};48;5;{bg_color}m{text}\033[?25l'
    return return_string


def set_title(title: str):
    """sets the tile of the window aparently"""

    os.system(f'title {title}')


class Buffer:
    """
    the buffer class is meant to be used to interact with the terminal.

    atributes:
    - the atribute list serves the purpose of reminding me which atributes work, it should be unused

    - the height and width are simpy the size of the terminal

    - the screen_buffer is the buffer that is used to store the characters while the double
      buffer is the one that the user changes and that is used to contrast what is on the screen
      (buffer) to what is sheduled to be on it (double buffer)

    - the current pos values are used to keep track of the cursor position
      which is needed in the flush function which writes to the stdout
    """

    def __init__(self) -> None:

        self.attribute_list: dict = {
            'normal': 1, 'underline': 4, 'reverse': 7, }
        size = os.get_terminal_size()

        self.current_x_pos: int = 0
        self.current_y_pos: int = 0
        self.height: int = size.lines
        self.width: int = size.columns

        self.double_buffer: list = None
        line: list = [(' ', 15, 0, 1) for _ in range(self.width)]
        self.screen_buffer: list = [line[:] for _ in range(self.height)]

        self.clear()

    def clear(self, fg_color: int = 15, bg_color: int = 0, attr_val: int = 1):
        """
        sets all cells to the none or ' '
        this is done so that the buffer is not filled with ghost characters
        """
        line: int = [(' ', fg_color, bg_color, attr_val)
                     for _ in range(self.width)]
        self.double_buffer: list = [line[:] for _ in range(self.height)]

    def deltas(self):
        """
        this generator is used to find which characters are different between the buffers
        and yield the x and y coordinates of the different characters
        """

        for y_coord in range(self.height):
            for x_coord in range(self.width):
                old_cell = self.screen_buffer[y_coord][x_coord]
                new_cell = self.double_buffer[y_coord][x_coord]
                if old_cell != new_cell:
                    yield x_coord, y_coord

    def sync(self):
        """
        syncs the two buffers, this is used to reflect the current state of the terminal
        this means that if delta is called again it wont see the same characters as unchanged
        """

        self.screen_buffer = [row[:] for row in self.double_buffer]

    def flush(self):
        """
         get the deltas aka the parts where buffer and doublebuffer dont match
         this part of the script is what actually prints to the terminal
         dumping the buffer onto the stdout and then syncing the buffers

         the cell lists are generated depending on if the buffer is running in
         efficient mode or not, and if yes, if the flush is to print or unprint
         charcters
        """

        for x_coordinate, y_coordinate in self.deltas():
            new_cell = self.double_buffer[y_coordinate][x_coordinate]

            if x_coordinate != self.current_x_pos or y_coordinate != self.current_y_pos:
                move_cursor(x_coordinate, y_coordinate)

            sys.stdout.write(coloring_toddler(*new_cell))
            sys.stdout.flush()

            self.current_x_pos = x_coordinate + 1
            self.current_y_pos = y_coordinate

        self.sync()

    def set(self, x_target_coordinate: int, y_target_coordinate: int, character_tupple: int):
        """
        this method sets a value of a choordinate of the buffer
        this is necesary since the only actual way to print in
        the program is dumping the buffer, so to make an output
        it needs to be made in the buffer first.

        the efficient parameter is used to bypass the deltas method and
        get arround iterations in which case it creates a list of all characters
        that are set, and schedules them to be deleted
        """

        self.double_buffer[y_target_coordinate][x_target_coordinate] = character_tupple

    def set_string(self, x_target_coord: int, y_target_coord: int, string_to_set: str,
                   fg_color: int = 15, bg_color: int = 0, attr_val: int = 1):
        """
        this method sets a string of characters to a choordinate of the buffer
        helps so that the user doesnt need to call set multiple times
        it is to be noted that the value set to the buffer is not a character,
        but a tupple that contains the style info and the character
        """

        if x_target_coord + len(string_to_set) > self.width or y_target_coord > self.height:
            pass

        for index,  char in enumerate(string_to_set):
            self.set(x_target_coord + index,
                     y_target_coord, (char, fg_color, bg_color, attr_val))

    def main_loop(self, main_method: callable):
        """
        pre-release main loop that sets up the screen before the program
        it also makes shure that when the program exits the terminal is still usable
        this is made to work arround a frame OBJECT not a function,
        the func parameter is a method of the objects, the constants of a frame should
        be set in a different method
        """

        def wrapper(*args, **kwargs):
            os.system('cls')
            try:
                while True:
                    main_method(*args, **kwargs)
            finally:
                os.system('cls')
                print('\033[0m')
        return wrapper
