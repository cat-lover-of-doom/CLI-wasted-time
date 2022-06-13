import ctypes
from ctypes import c_long, c_ulong
import os
import sys
import time
# make metaclass and abstract calss to serve as main loop, instead of a function, a list of all frames created automaticaly to switch between frame instances
# https://i.stack.imgur.com/KTSQa.png for colors
# ==== GLOBAL VARIABLES ======================

# torry is mid lol


class _buffer:
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

    def set_string(self, string, x, y, fg, bg, attr):
        if x + len(string) > self.width or y > self.height:
            raise Exception

        for index,  char in enumerate(string):
            self.set(x + index, y, (char, fg, bg, attr))


class ball:
    def __init__(self, height, width, buffer, pos=None, card=None) -> None:
        self.buffer = buffer
        self.field = (width, height)
        self.pos = pos if pos is not None else [0, 0]
        self.card = card if card is not None else [1, 1]

    def main(self):
        self.buffer.set(self.pos[0], self.pos[1], '0')
        self.pos[0] += self.card[0]
        self.pos[1] += self.card[1]
        self.check()

    def check(self):
        temp = []
        for card, boundry, position in zip(self.card, self.field, self.pos):
            if position >= boundry - abs(card) or position <= 0:
                card = -card
            temp.append(card)
        self.card = temp


buff = _buffer()
b = ball(buff.height, buff.width, buff)
b1 = ball(buff.height, buff.width, buff, pos=[100, 10], card=[1, -1])
os.system('cls')
while True:
    b.main()
    b1.main()
    buff.flush()
    buff.clear()
    time.sleep(0.01)
