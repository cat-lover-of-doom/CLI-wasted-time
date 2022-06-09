"""
Some classes that make working with cli's a bit easier.

This module is meant to be imported and used in the creation of any cli
regarding asciimatics

  Typical usage example:

  import asciiclasses
"""


class Button:
    """it defines the coordinates to consider a button.

    it stores a certain rectangle of coordinates on screen that can be
    considered a button

    Args:
        x_pos -> int: the horizontal value of left corner of the button
        y_pos -> int: the vertical position of the left corner of the button
        text -> string: the text the user will see

    Returns:
        None
    Raises:
        None
    """

    def __init__(self, screen, x_pos: int, y_pos: int, text: str = '') -> None:
        self.screen = screen
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.length = len(text)
        self.text = text
        self.inverse = False
        self.onpress = None
        self.ispressed = False

    def show(self, color_in: int = 7, bg_in: int = 0) -> None:
        """
        Renders the button into the screen.

        Args:
            screen -> object: the screen to print to

        Returns:
            None
        Raises:
            None
        """
        if self.inverse:
            self.screen.print_at(
                self.text,
                int(self.x_pos),
                int(self.y_pos),
                colour=bg_in,
                bg=color_in
            )
        else:
            self.screen.print_at(
                self.text,
                int(self.x_pos),
                int(self.y_pos),
                colour=color_in,
                bg=bg_in
            )

        if self.ispressed and self.onpress is not None:
            # unused pylint: disable=not-callable
            self.onpress()

    def coords(self) -> tuple:
        """
        returns the coordinates of the button.

        Args:
            None

        Returns:
            x_pos -> int: the horizontal value of left corner of the button
            y_pos -> int: the vertical position of the left corner of the button
            lenght -> int: the lenght of the string of the button
        Raises:
            None
        """

        return (self.x_pos, self.y_pos, self.length)

    def highlight(self, high_command: bool) -> None:
        """
        updates the state of the button to be highlighted or not.

        Args:
            high_command -> bool: whether the button should be highlighted

        Returns:
            None
        Raises:
            None
        """

        self.inverse = high_command

    def toggle(self):
        self.ispressed = not self.ispressed


class Cursor:
    """
    It is used for the user to interact with the ui.

    it is an object which coordinates are controlled by the user, it
    is used to check which object the user is currently interacting with
    it is controled by the keyboard

    Args:
        x_pos -> int: the horizontal value of left corner of the cursor
        y_pos -> int: the vertical position of the left corner of the cursor

    Returns:
        None
    Raises:
        None
    """

    def __init__(self, screen, x_pos: int, y_pos: int) -> None:
        self.x_pos = int(x_pos)
        self.y_pos = int(y_pos)
        self.screen = screen

    def move(self, x_pos: int, y_pos: int) -> None:
        """
        changes the vertical and horizontal position of the cursor.

        Args:
            x_pos -> int: the horizontal position of the cursor
            y_pos -> int: the vertical position of the cursor

        Returns:
            None
        Raises:
            None
        """

        self.x_pos += int(x_pos)
        self.y_pos += int(y_pos)

    def move_to(self, x_pos: int, y_pos: int = 0) -> None:
        """
        move the cursor to a certain coordinate.

        Args:
            x_pos: the horizontal position of the cursor
            y_pos: the vertical position of the cursor

        Returns:
            None
        Raises:
            None
        """
        self.x_pos = int(x_pos)
        self.y_pos = int(y_pos)

    def show(self) -> None:
        """
        changes the vertical and horizontal position of the cursor.

        Args:
            screen -> object: the screen to print to
            x_pos -> int: the horizontal value of left corner of the cursor
            y_pos -> int: the vertical position of the left corner of the cursor

        Returns:
            None
        Raises:
            None
        """

        self.screen.print_at('', self.x_pos, self.y_pos)


class Frame:
    def __init__(self, screen) -> None:
        self.screen = screen
        self.cursor = Cursor(self.screen, 0, 0)
        self.ui_elements = []
        self.index = 0

    def post_init(self) -> None:
        pass

    def __call__(self, *args: any, **kwds: any) -> any:
        pass

    def __repr__(self) -> str:
        pass

    def mainloop(self) -> None:
        pass
