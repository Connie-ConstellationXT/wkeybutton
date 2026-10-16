# wkeybutton

A sane, always-available on-screen keyboard for **KWin on Wayland**.

Requirements:

- Full desktop keyboard: function row, modifiers, navigation, arrows and numpad.
- A floating, resizable window with KWin's Meta + mouse gestures.
- Modifier latches: tap Shift/Ctrl/Alt/Meta, then the next key. Tap again to cancel. Multiple modifiers can be combined.
- Remains usable with a physical keyboard connected; no tablet-mode or text-field activation requirement.

## Run with Nix

```sh
nix-shell
wkeybutton
```

The shell includes Python, PySide6, evdev, Qt Wayland plugins and the launcher; no pip or virtual environment is needed. Use `wkeybutton --dry-run` to preview without device access.

If `/dev/uinput` is not accessible, run this once per boot/device recreation:

```sh
sudo modprobe uinput
sudo setfacl -m "u:$(id -un):rw" /dev/uinput
```

## First prototype

Python + PySide6 provide the ordinary desktop window. Linux `uinput` delivers physical key events through the compositor. This is a Wayland desktop application, but input injection uses a kernel virtual device rather than a compositor-specific input-method protocol. It does not grab or read physical keyboards.

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
QT_QPA_PLATFORM=wayland wkeybutton --dry-run
```

Dry run prints events and requires no device permissions. Omit `--dry-run` for actual typing after granting access to `/dev/uinput`.

### Device access

Load the kernel module with `sudo modprobe uinput` if `/dev/uinput` is absent. Your user needs write access to that device. For a temporary test on a personal machine, grant just your current user access:

```sh
sudo setfacl -m "u:$(id -un):rw" /dev/uinput
QT_QPA_PLATFORM=wayland wkeybutton
```

This ACL lasts until the device is recreated; persistent installation policy is not included yet. Access permits input injection across the session. Do not run the GUI as root or make the device world-writable.

### KWin window behavior

In System Settings → Window Management → Window Behavior → Window Actions, select Meta as the modifier, left button to Move, and right button to Resize. These are compositor-controlled bindings; the app does not override your KWin configuration.

The window requests no keyboard focus and stays on top. If clicking it takes focus on your Plasma version, add a window rule matching `wkeybutton` (use Detect Window Properties), with **Accept focus → Force → No**. Verify that clicking keys leaves your editor focused.

### Current limits

This is an initial implementation, not yet verified in a live KWin session. Key labels show US ANSI positions; output follows the compositor's keyboard layout. Caps/Num Lock indicators, layout discovery, key repeat, held keys, persistent modifier locks, touch interaction, and remembered window geometry are future work. Modifier latches emit only with the next key, so latching Meta does not hold Meta down globally. The numpad follows normal Num Lock behavior.

## Verification

```sh
python3 -m unittest discover -s tests -v
```

Manual acceptance on KWin Wayland:

1. Keep a physical keyboard attached and focus a text editor.
2. Launch wkeybutton and type by clicking; the editor must retain focus.
3. Latch Shift and click A: get one uppercase A, then lowercase on the next click.
4. Latch Ctrl and Shift together and verify a shortcut; both latches clear afterward.
5. Cancel a latch by clicking it twice.
6. Move with physical Meta + left-drag and resize with Meta + right-drag.
7. Check function, navigation and numpad keys, then close the keyboard and confirm physical typing still works.

## References

- [Linux uinput documentation](https://docs.kernel.org/input/uinput.html)
- [KWin Window Rules](https://docs.kde.org/stable_kf6/en/kwin/kcontrol/windowspecific/)
- [KWin Window Behavior](https://docs.kde.org/trunk_kf6/en/kwin/kcontrol/windowbehaviour/index.html)
