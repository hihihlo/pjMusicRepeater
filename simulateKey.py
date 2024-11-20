# How to generate keyboard events? - Stack Overflow
#   https://stackoverflow.com/questions/13564851/how-to-generate-keyboard-events
#   ref author : "object-Object"

from ctypes import *
from time import sleep

"""
< --- CTRL by [object Object] --- >
Only works on windows.
Some characters only work with a US standard keyboard.
Some parts may also only work in python 32-bit.
"""

class KeySm:
    delay = 0.010

    cancel = 0x03
    backspace = 0x08
    tab = 0x09
    enter = 0x0D
    shift = 0x10
    ctrl = 0x11
    alt = 0x12
    capslock = 0x14
    esc = 0x1B
    space = 0x20
    pgup = 0x21
    pgdown = 0x22
    end = 0x23
    home = 0x24
    leftarrow = 0x26
    uparrow = 0x26
    rightarrow = 0x27
    downarrow = 0x28
    select = 0x29
    print = 0x2A
    execute = 0x2B
    printscreen = 0x2C
    insert = 0x2D
    delete = 0x2E
    help = 0x2F
    num0 = 0x30
    num1 = 0x31
    num2 = 0x32
    num3 = 0x33
    num4 = 0x34
    num5 = 0x35
    num6 = 0x36
    num7 = 0x37
    num8 = 0x38
    num9 = 0x39
    A = 0x41
    B = 0x42
    C = 0x43
    D = 0x44
    E = 0x45
    F = 0x46
    G = 0x47
    H = 0x48
    I = 0x49
    J = 0x4A
    K = 0x4B
    L = 0x4C
    M = 0x4D
    N = 0x4E
    O = 0x4F
    P = 0x50
    Q = 0x51
    R = 0x52
    S = 0x53
    T = 0x54
    U = 0x55
    V = 0x56
    W = 0x57
    X = 0x58
    Y = 0x59
    Z = 0x5A
    leftwin = 0x5B
    rightwin = 0x5C
    apps = 0x5D
    sleep = 0x5F
    numpad0 = 0x60
    numpad1 = 0x61
    numpad3 = 0x63
    numpad4 = 0x64
    numpad5 = 0x65
    numpad6 = 0x66
    numpad7 = 0x67
    numpad8 = 0x68
    numpad9 = 0x69
    multiply = 0x6A
    add = 0x6B
    seperator = 0x6C
    subtract = 0x6D
    decimal = 0x6E
    divide = 0x6F
    F1 = 0x70
    F2 = 0x71
    F3 = 0x72
    F4 = 0x73
    F5 = 0x74
    F6 = 0x75
    F7 = 0x76
    F8 = 0x77
    F9 = 0x78
    F10 = 0x79
    F11 = 0x7A
    F12 = 0x7B
    F13 = 0x7C
    F14 = 0x7D
    F15 = 0x7E
    F16 = 0x7F
    F17 = 0x80
    F19 = 0x82
    F20 = 0x83
    F21 = 0x84
    F22 = 0x85
    F23 = 0x86
    F24 = 0x87
    numlock = 0x90
    scrolllock = 0x91
    leftshift = 0xA0
    rightshift = 0xA1
    leftctrl = 0xA2
    rightctrl = 0xA3
    leftmenu = 0xA4
    rightmenu = 0xA5
    browserback = 0xA6
    browserforward = 0xA7
    browserrefresh = 0xA8
    browserstop = 0xA9
    browserfavories = 0xAB
    browserhome = 0xAC
    volumemute = 0xAD
    volumedown = 0xAE
    volumeup = 0xAF
    nexttrack = 0xB0
    prevoustrack = 0xB1
    stopmedia = 0xB2
    playpause = 0xB3
    launchmail = 0xB4
    selectmedia = 0xB5
    launchapp1 = 0xB6
    launchapp2 = 0xB7
    semicolon = 0xBA
    equals = 0xBB
    comma = 0xBC
    dash = 0xBD
    period = 0xBE
    slash = 0xBF
    accent = 0xC0
    openingsquarebracket = 0xDB
    backslash = 0xDC
    closingsquarebracket = 0xDD
    quote = 0xDE
    play = 0xFA
    zoom = 0xFB
    PA1 = 0xFD
    clear = 0xFE

    # Category variables
    __letters = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM"
    __shiftSymbols = "~!@#$%^&*()_+QWERTYUIOP{}|ASDFGHJKL:\"ZXCVBNM<>?"

    user32 = windll.user32
    # kernel32 = windll.kernel32

    # Presses and releases the key, and optional modifiers
    # ex : KeySm.press(KeySm.F)                # press_single_key
    # ex : KeySm.press(KeySm.F, [KeySm.alt])   # Alt+f : hold_modifier + press_single_key + release_modifier
    # ex : argKey = ord('F');  KeySm.press(argKey, [KeySm.alt])
    @classmethod
    def press(cls, key, lModifier = None):
        if lModifier:
            for m in lModifier:
                cls.user32.keybd_event(m, 0, 0, 0)  # hold modifier key
            sleep(cls.delay)
        cls.user32.keybd_event(key, 0, 0, 0)
        sleep(cls.delay)
        cls.user32.keybd_event(key, 0, 2, 0)
        if lModifier:
            for m in lModifier:
                cls.user32.keybd_event(m, 0, 2, 0)  # release modifier key
        sleep(cls.delay)

    # Holds a key
    @classmethod
    def hold(cls, key):
        cls.user32.keybd_event(key, 0, 0, 0)
        sleep(cls.delay)

    # Releases a key
    @classmethod
    def release(cls, key):
        cls.user32.keybd_event(key, 0, 2, 0)
        sleep(cls.delay)

    # Types out a string
    @classmethod
    def typeStr(cls, sentence):
        for letter in sentence:
            shift = letter in cls.__shiftSymbols
            fixedletter = "space"
            if letter == "`" or letter == "~":
                fixedletter = "accent"
            elif letter == "1" or letter == "!":
                fixedletter = "num1"
            elif letter == "2" or letter == "@":
                fixedletter = "num2"
            elif letter == "3" or letter == "#":
                fixedletter = "num3"
            elif letter == "4" or letter == "$":
                fixedletter = "num4"
            elif letter == "5" or letter == "%":
                fixedletter = "num5"
            elif letter == "6" or letter == "^":
                fixedletter = "num6"
            elif letter == "7" or letter == "&":
                fixedletter = "num7"
            elif letter == "8" or letter == "*":
                fixedletter = "num8"
            elif letter == "9" or letter == "(":
                fixedletter = "num9"
            elif letter == "0" or letter == ")":
                fixedletter = "num0"
            elif letter == "-" or letter == "_":
                fixedletter = "dash"
            elif letter == "=" or letter == "+":
                fixedletter = "equals"
            elif letter in cls.__letters:
                fixedletter = letter.lower()
            elif letter == "[" or letter == "{":
                fixedletter = "openingsquarebracket"
            elif letter == "]" or letter == "}":
                fixedletter = "closingsquarebracket"
            elif letter == "\\" or letter == "|":
                fixedletter = "backslash"
            elif letter == ";" or letter == ":":
                fixedletter = "semicolon"
            elif letter == "'" or letter == "\"":
                fixedletter = "quote"
            elif letter == "," or letter == "<":
                fixedletter = "comma"
            elif letter == "." or letter == ">":
                fixedletter = "period"
            elif letter == "/" or letter == "?":
                fixedletter = "slash"
            elif letter == "\n":
                fixedletter = "enter"
            keytopress = eval("KeySm." + str(fixedletter))
            if shift:
                cls.hold(KeySm.shift)
                cls.press(keytopress)
                cls.release(KeySm.shift)
            else:
                cls.press(keytopress)

class MouseSm:
    delay = 0.010
    left = [0x0002, 0x0004]
    right = [0x0008, 0x00010]
    middle = [0x00020, 0x00040]

    user32 = windll.user32
    # kernel32 = windll.kernel32

    @classmethod
    # Moves mouse to a position
    def move(cls, x, y):
        cls.user32.SetCursorPos(x, y)

    @classmethod
    # Presses and releases mouse
    def click(cls, button):
        cls.user32.mouse_event(button[0], 0, 0, 0, 0)
        sleep(cls.delay)
        cls.user32.mouse_event(button[1], 0, 0, 0, 0)
        sleep(cls.delay)

    @classmethod
    # Holds a mouse button
    def holdClick(cls, button):
        cls.user32.mouse_event(button[0], 0, 0, 0, 0)
        sleep(cls.delay)

    @classmethod
    # Releases a mouse button
    def releaseClick(cls, button):
        cls.user32.mouse_event(button[1])
        sleep(cls.delay)
