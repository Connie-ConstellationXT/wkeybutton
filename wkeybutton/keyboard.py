"""Input state independent of the UI and input transport."""


class Keyboard:
    def __init__(self, sink):
        self.sink = sink
        self.latched = set()

    def toggle(self, code):
        if code in self.latched:
            self.latched.remove(code)
        else:
            self.latched.add(code)

    def tap(self, code):
        # Latches are emitted only with the next key, so a latched Meta does
        # not interfere with KWin's physical Meta+mouse window gestures.
        pressed = []
        try:
            for modifier in sorted(self.latched):
                self.sink.key(modifier, 1)
                pressed.append(modifier)
            self.sink.key(code, 1)
            pressed.append(code)
        finally:
            try:
                for key in reversed(pressed):
                    self.sink.key(key, 0)
            finally:
                self.latched.clear()
