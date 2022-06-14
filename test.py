import asciiclasses
import arrays

BUFFER = arrays.Buffer()


class frame:
    def __call__(self, *args, **kwargs) -> any:
        return self.main()

    def __init__(self) -> None:
        self.buffer = BUFFER
        self.button1 = asciiclasses.Button(self.buffer, 5, 5, 'hellow world')

    @BUFFER.main_loop
    def main(self):

        self.button1.show()
        self.buffer.flush()


f = frame()
f()
