import unittest
from wkeybutton.keyboard import Keyboard


class Sink:
    def __init__(self):
        self.events = []

    def key(self, code, value):
        self.events.append((code, value))


class KeyboardTests(unittest.TestCase):
    def test_chord_consumes_latches_and_releases_in_reverse_order(self):
        sink = Sink()
        keyboard = Keyboard(sink)
        keyboard.toggle(42)
        keyboard.toggle(29)
        self.assertEqual(sink.events, [])
        keyboard.tap(30)
        self.assertEqual(sink.events, [(29, 1), (42, 1), (30, 1), (30, 0), (42, 0), (29, 0)])
        keyboard.tap(48)
        self.assertEqual(sink.events[-2:], [(48, 1), (48, 0)])

    def test_second_modifier_tap_cancels_latch(self):
        keyboard = Keyboard(Sink())
        keyboard.toggle(42)
        keyboard.toggle(42)
        self.assertFalse(keyboard.latched)

    def test_failed_key_press_releases_modifiers(self):
        class FailingSink(Sink):
            def key(self, code, value):
                if code == 30 and value == 1:
                    raise OSError("disconnected")
                super().key(code, value)
        sink = FailingSink()
        keyboard = Keyboard(sink)
        keyboard.toggle(42)
        with self.assertRaises(OSError):
            keyboard.tap(30)
        self.assertEqual(sink.events, [(42, 1), (42, 0)])
        self.assertFalse(keyboard.latched)


if __name__ == "__main__":
    unittest.main()
