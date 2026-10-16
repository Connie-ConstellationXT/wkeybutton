import argparse
import sys

from .keyboard import Keyboard

# Physical US ANSI positions. The compositor's configured layout determines
# characters, just as for a hardware keyboard.
ROWS = [
    "ESC F1 F2 F3 F4 F5 F6 F7 F8 F9 F10 F11 F12 SYSRQ SCROLLLOCK PAUSE",
    "GRAVE 1 2 3 4 5 6 7 8 9 0 MINUS EQUAL BACKSPACE INSERT HOME PAGEUP NUMLOCK KPSLASH KPASTERISK KPMINUS",
    "TAB Q W E R T Y U I O P LEFTBRACE RIGHTBRACE BACKSLASH DELETE END PAGEDOWN KP7 KP8 KP9 KPPLUS",
    "CAPSLOCK A S D F G H J K L SEMICOLON APOSTROPHE ENTER KP4 KP5 KP6",
    "LEFTSHIFT Z X C V B N M COMMA DOT SLASH RIGHTSHIFT UP KP1 KP2 KP3 KPENTER",
    "LEFTCTRL LEFTMETA LEFTALT SPACE RIGHTALT RIGHTMETA COMPOSE RIGHTCTRL LEFT DOWN RIGHT KP0 KPDOT",
]
MODIFIERS = {
    "LEFTSHIFT", "RIGHTSHIFT", "LEFTCTRL", "RIGHTCTRL",
    "LEFTALT", "RIGHTALT", "LEFTMETA", "RIGHTMETA",
}
LABELS = {
    "GRAVE": "`", "MINUS": "-", "EQUAL": "=", "BACKSPACE": "Backspace",
    "LEFTBRACE": "[", "RIGHTBRACE": "]", "BACKSLASH": "\\",
    "SEMICOLON": ";", "APOSTROPHE": "'", "COMMA": ",", "DOT": ".",
    "SLASH": "/", "SPACE": "Space", "LEFTSHIFT": "Shift", "RIGHTSHIFT": "Shift",
    "LEFTCTRL": "Ctrl", "RIGHTCTRL": "Ctrl", "LEFTALT": "Alt", "RIGHTALT": "AltGr",
    "LEFTMETA": "Meta", "RIGHTMETA": "Meta", "CAPSLOCK": "Caps",
    "PAGEUP": "PgUp", "PAGEDOWN": "PgDn", "SYSRQ": "PrtSc",
    "SCROLLLOCK": "ScrLk", "NUMLOCK": "Num", "COMPOSE": "Menu",
    "KPSLASH": "Num /", "KPASTERISK": "Num *", "KPMINUS": "Num -",
    "KPPLUS": "Num +", "KPENTER": "Num Enter", "KPDOT": "Num .",
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Print events without injecting input")
    args = parser.parse_args()
    from evdev import UInput, ecodes
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QWidget

    class Sink:
        def __init__(self):
            self.device = None
            if not args.dry_run:
                codes = {ecodes.ecodes[f"KEY_{name}"] for row in ROWS for name in row.split()}
                self.device = UInput({ecodes.EV_KEY: sorted(codes)}, name="wkeybutton")

        def key(self, code, value):
            if self.device:
                self.device.write(ecodes.EV_KEY, code, value)
                self.device.syn()
            else:
                print(ecodes.KEY.get(code, code), value, flush=True)

        def close(self):
            if self.device:
                self.device.close()

    app = QApplication(sys.argv[:1])
    app.setApplicationName("wkeybutton")
    app.setDesktopFileName("wkeybutton")
    try:
        sink = Sink()
    except OSError as error:
        print(f"Cannot create virtual keyboard: {error}\nSee README.md for /dev/uinput setup; use --dry-run to preview.", file=sys.stderr)
        return 1
    keyboard = Keyboard(sink)
    window = QWidget()
    window.setWindowTitle("wkeybutton")
    window.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.WindowDoesNotAcceptFocus)
    window.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
    window.resize(1400, 420)
    window.setMinimumSize(850, 280)
    layout = QVBoxLayout(window)
    status = QLabel("Tap modifiers to latch; tap a key to consume. Meta + right-drag resizes via KWin.")
    layout.addWidget(status)
    buttons = []

    def activate(name, code):
        try:
            if name in MODIFIERS:
                keyboard.toggle(code)
            else:
                keyboard.tap(code)
            status.setText("Latched: " + (", ".join(LABELS[n] for n, c, _ in buttons if c in keyboard.latched) or "none"))
        except OSError as error:
            status.setText(f"Input error: {error}")
        for _, c, button in buttons:
            button.setChecked(c in keyboard.latched)

    for row in ROWS:
        line = QHBoxLayout()
        for name in row.split():
            code = ecodes.ecodes[f"KEY_{name}"]
            label = LABELS.get(name, "Num " + name[2:] if name.startswith("KP") else name.title())
            button = QPushButton(label)
            button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            button.setMinimumSize(0, 30)
            button.setCheckable(name in MODIFIERS)
            button.clicked.connect(lambda checked=False, n=name, c=code: activate(n, c))
            line.addWidget(button, 5 if name == "SPACE" else 2 if name in {"BACKSPACE", "ENTER", "LEFTSHIFT", "RIGHTSHIFT"} else 1)
            buttons.append((name, code, button))
        layout.addLayout(line, 1)
    window.setStyleSheet("QPushButton { padding: 5px; } QPushButton:checked { background: #3874cb; color: white; }")
    app.aboutToQuit.connect(sink.close)
    window.show()
    try:
        return app.exec()
    finally:
        sink.close()


if __name__ == "__main__":
    raise SystemExit(main())
