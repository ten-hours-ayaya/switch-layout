#!/usr/bin/env python3
import subprocess

from pynput import keyboard

MONITORED_KEYS = {keyboard.Key.ctrl, keyboard.Key.shift}

# How many layouts do you have?
LAYOUTS_COUNT = 2

# If you're having troubles configuring SWITCH_SHORTCUTS, set this to True.
# Script will output pressed keys so you could copy-paste them.
DEBUG = False


def format_key(key):
    """
    Formats a key the way it should be written in SWITCH_SHORTCUTS list.
    """
    if isinstance(key, keyboard.Key):
        return "keyboard.Key.{}".format(key.name)
    else:
        return "keyboard.KeyCode({})".format(key.vk)


class Switcher:
    def __init__(self):
        self.current_keys = set()
        self.is_ready_to_change = False
        self.current_layout = 0

    def on_press(self, key):
        if DEBUG:
            print("Pressed: {}".format(format_key(key)))

        if key not in MONITORED_KEYS:
            self.current_keys.clear()
            self.is_ready_to_change = False
            return

        self.current_keys.add(key)
        self.is_ready_to_change = len(MONITORED_KEYS.difference(self.current_keys)) == 0

    def on_release(self, key):
        if DEBUG:
            print("Released: {}".format(format_key(key)))
        
        if key not in MONITORED_KEYS:
            return
        
        if key in self.current_keys:
            self.current_keys.remove(key)

        if self.is_ready_to_change:
            self.on_switch()
            self.is_ready_to_change = False

    def on_switch(self):
        self.current_layout += 1
        if self.current_layout >= LAYOUTS_COUNT:
            self.current_layout = 0

        command = [
            "gsettings",
            "set",
            "org.gnome.desktop.input-sources",
            "current",
            str(self.current_layout),
        ]
        _exitcode = subprocess.call(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def main():
    switcher = Switcher()

    with keyboard.Listener(
            on_press=switcher.on_press,
            on_release=switcher.on_release) as listener:
        listener.join()


if __name__ == '__main__':
    main()

