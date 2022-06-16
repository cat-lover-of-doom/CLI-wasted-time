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


class Buffer():
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
        size = os.get_terminal_size()
        self.height: int = size.lines
        self.width: int = size.columns

        self.current_x_pos: int = 0
        self.current_y_pos: int = 0

        self.cells_to_print: list = []
        self.cells_to_clear: list = []

    def clear(self):
        """
        writes empty charaters in all the places in which characters have been written
        this is used to clear the screen and remove unwanted characters from it
        """
        self.flush(True)
        self.cells_to_clear = []

    def flush(self, clear_buffer: bool = False):
        """
        this part does the actual printing and goes through a list of 'cells' generating an 
        ansi code for them and printing them, this is usefull to see characters, if this 
        method is not called the screen will not refresh
        """
        if clear_buffer:
            cell_list = self.cells_to_clear
        else:
            cell_list = self.cells_to_print

        for set_tupple in cell_list:
            if set_tupple[0] != self.current_x_pos or set_tupple[1] != self.current_y_pos:
                move_cursor(set_tupple[0], set_tupple[1])

            sys.stdout.write(coloring_toddler(*set_tupple[2]))

            sys.stdout.flush()

            self.current_x_pos = set_tupple[0] + 1
            self.current_y_pos = set_tupple[1]

        self.cells_to_print = []

    def set(self, x_target_coordinate: int, y_target_coordinate: int, character_tupple: int):
        """apends a tuple of coordinates and character into the to_print and to_delete list"""
        self.cells_to_print.append(
            (x_target_coordinate, y_target_coordinate, character_tupple))
        self.cells_to_clear.append(
            (x_target_coordinate, y_target_coordinate, (' ')))

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
