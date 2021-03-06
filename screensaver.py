import pstats
import cProfile
import time
import os

import screen


class ball:
    def __init__(self, height, width, buffer, pos=None, card=None, text='0', fg=15, bg=0, attr=1) -> None:
        self.buffer = buffer
        self.field = (width, height)
        self.pos = pos if pos is not None else [0, 0]
        self.card = card if card is not None else [1, 1]
        self.text = (text, fg, bg, attr)

    def main(self):
        self.buffer.set_string(self.pos[0], self.pos[1], *self.text)
        self.pos[0] += self.card[0]
        self.pos[1] += self.card[1]
        self.check()

    def check(self):
        temp = []
        count = 0
        for card, boundry, position in zip(self.card, self.field, self.pos):
            if count == 0:
                boundry -= len(self.text[0])

            if position >= boundry - abs(card) or position <= 0:
                card = -card
                self.colision()

            temp.append(card)
            count += 1

        self.card = temp

    def colision(self):
        tup = self.text[:]
        self.text = (tup[0], tup[2], tup[1], tup[3])


def main():
    buff = screen.Buffer()
    b1 = ball(buff.height, buff.width, buff, pos=[
        10, 10], card=[1, -1], text='amogos')
    os.system('cls')
    i = 0
    try:
        while i < 1000:
            b1.main()
            buff.flush()
            screen.set_title('normal')
            # time.sleep(0.03)
            buff.clear()
            i += 1
    finally:
        print('\033[0m')


if __name__ == '__main__':
    with cProfile.Profile() as pr:
        main()
        stats = pstats.Stats(pr)
        stats.sort_stats(pstats.SortKey.TIME)
        stats.print_stats()
