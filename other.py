"""
An example implementation to my cli library.

This module is meant to be imported and used in the creation of any cli
regarding asciimatics

  Typical usage example:

  import asciiclasses
"""
import CLI_MOD
SCREEN = CLI_MOD.screen


def element_selctor(cardinality: int, list_in: list, current: int) -> int:
    """
    changes the index of the selection to select a new item.

    Args:
        cardinality -> int: the direction in which to move the selection
        list_in -> list: the list to be iterated over
        current -> int: the current selected element
    Returns:
        new_element_index: the index of the new selected element
    Raises:
        None
    """
    current += cardinality

    if current >= len(list_in):
        new_element_index = 0
    else:
        new_element_index = current

    return new_element_index


def hello():
    SCREEN.print_at('hello', int(SCREEN.width/2), int(SCREEN.height/2))


def hello2():
    SCREEN.print_at('hello2', int(SCREEN.width/2), int(SCREEN.height/2))


def demo() -> None:
    """
    The mainloop for the ui, it is passed to the renderer.

    The main loop of the program is located here, all the calculations
    are done here

    Args:
        None
    Returns:
        None
    Raises:
        None
    """

    i, j = 0, SCREEN.height/2
    option1 = CLI_MOD.asciiclasses.Button(SCREEN, i, j, 'option1')
    option2 = CLI_MOD.asciiclasses.Button(SCREEN, i, j+1, 'option2')
    option1.onpress = hello
    option2.onpress = hello2
    cursor = CLI_MOD.asciiclasses.Cursor(SCREEN, 0, 0)
    ui_elements = [option1, option2]
    current_index = 0
    elem = ui_elements[current_index]
    elem.highlight(True)
    cursor.move_to(elem.x_pos + elem.length, elem.y_pos)

    while True:

        event = SCREEN.get_event()

        if isinstance(event, CLI_MOD.const.KeyboardEvent):

            if event.key_code == ord('q'):
                return

            if event.key_code == -206:
                current_index = element_selctor(
                    -1, ui_elements, current_index)
                elem = ui_elements[current_index]

                cursor.move_to(elem.x_pos + elem.length, elem.y_pos)

            elif event.key_code == -204:
                current_index = element_selctor(
                    1, ui_elements, current_index)
                elem = ui_elements[current_index]

                cursor.move_to(elem.x_pos + elem.length, elem.y_pos)

            elif event.key_code == 13:
                elem = ui_elements[current_index]
                elem.toggle()

        elif isinstance(event, CLI_MOD.const.MouseEvent):

            if event.buttons == 1:
                return

        for element in ui_elements:
            if element == elem:
                element.highlight(True)
            else:
                element.highlight(False)

        cursor.show()
        option1.show()
        option2.show()
        SCREEN.refresh()
        SCREEN.buffer.clear(7, 0, 0)


if __name__ == '__main__':
    demo()
