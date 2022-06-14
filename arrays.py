import ctypes
from ctypes import c_long, c_ulong
import os
import sys
# make metaclass and abstract calss to serve as main loop, instead of a function, a list of all frames created automaticaly to switch between frame instances
# https://i.stack.imgur.com/KTSQa.png for colors
# ==== GLOBAL VARIABLES ======================

# torry is mid lol


class Buffer:
    def __init__(self) -> None:

        self.ATTRIBG = {'normal': 1, 'underline': 4, 'reverse': 7, }
        self.gHandle = ctypes.windll.kernel32.GetStdHandle(c_long(-11))
        size = os.get_terminal_size()

        self.height = size.lines
        self.width = size.columns
        self.double_buffer = None
        line = [(' ', 15, 0, 1) for _ in range(self.width)]
        self.screen_buffer = [line[:] for _ in range(self.height)]
        self.curr_x = 0
        self.curr_y = 0

        self.clear()

    def clear(self, fg=15, bg=0, attr=1):
        line = [(' ', fg, bg, attr) for _ in range(self.width)]
        self.double_buffer = [line[:] for _ in range(self.height)]

    def deltas(self):
        for y in range(self.height):
            for x in range(self.width):
                old_cell = self.screen_buffer[y][x]
                new_cell = self.double_buffer[y][x]
                if old_cell != new_cell:
                    yield x, y

    def sync(self):
        self.screen_buffer = [row[:] for row in self.double_buffer]

    def move_cursor(self, x, y):
        """Move cursor to position indicated by x and y."""
        value = x + (y << 16)
        ctypes.windll.kernel32.SetConsoleCursorPosition(
            self.gHandle, c_ulong(value))

    def set_title(self, title):
        os.system(f'title {title}')

    def coloring_toddler(self, text, fg=15, bg=0, attr=1):
        return_string = f'\033[{attr};38;5;{fg};48;5;{bg}m{text}\033[?25l'
        return return_string

    def flush(self):
        for x, y in self.deltas():
            new_cell = self.double_buffer[y][x]

            if x != self.curr_x or y != self.curr_y:
                self.move_cursor(x, y)

            sys.stdout.write(self.coloring_toddler(*new_cell))
            sys.stdout.flush()

            self.curr_x = x + 1
            self.curr_y = y

        self.sync()

    def set(self, x, y, char_tupple):
        self.double_buffer[y][x] = char_tupple

    def set_string(self, x, y, string, fg=15, bg=0, attr=1):
        if x + len(string) > self.width or y > self.height:
            pass
        for index,  char in enumerate(string):
            self.set(x + index, y, (char, fg, bg, attr))

    def main_loop(self, func):
        def wrapper(*args, **kwargs):
            os.system('cls')
            try:
                while True:
                    func(*args, **kwargs)
            finally:
                os.system('cls')
                print('\033[0m')
        return wrapper
