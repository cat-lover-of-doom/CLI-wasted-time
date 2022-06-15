import asciiclasses
import arrays

# unused pylint: disable=no-member
BUFFER = arrays.Buffer()


class frame:
    def __call__(self, *args, **kwargs) -> any:
        return self.main()

    def __init__(self) -> None:
        self.buffer = BUFFER
        self.button1 = asciiclasses.Button(self.buffer, 5, 5, 'hellow world')
        self.button1.onpress = self.hello

    def hello(self) -> None:
        self.buffer.set_string(
            int(self.buffer.width/2), int(self.buffer.height/2), 'hello', foreground_color=14, background_color=1, attribute_value=4)

    @BUFFER.main_loop
    def main(self):

        self.button1.show()
        self.buffer.flush()


f = frame()
f()
