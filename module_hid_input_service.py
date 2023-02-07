from ctypes import windll
import string
import submodule_hw_simulator
import win32gui

VkCode = {
    "back":  0x08,
    "tab":  0x09,
    "return":  0x0D,
    "shift":  0x10,
    "control":  0x11,
    "menu":  0x12,
    "pause":  0x13,
    "capital":  0x14,
    "escape":  0x1B,
    "space":  0x20,
    "end":  0x23,
    "home":  0x24,
    "left":  0x25,
    "up":  0x26,
    "right":  0x27,
    "down":  0x28,
    "print":  0x2A,
    "snapshot":  0x2C,
    "insert":  0x2D,
    "delete":  0x2E,
    "lwin":  0x5B,
    "rwin":  0x5C,
    "numpad0":  0x60,
    "numpad1":  0x61,
    "numpad2":  0x62,
    "numpad3":  0x63,
    "numpad4":  0x64,
    "numpad5":  0x65,
    "numpad6":  0x66,
    "numpad7":  0x67,
    "numpad8":  0x68,
    "numpad9":  0x69,
    "multiply":  0x6A,
    "add":  0x6B,
    "separator":  0x6C,
    "subtract":  0x6D,
    "decimal":  0x6E,
    "divide":  0x6F,
    "f1":  0x70,
    "f2":  0x71,
    "f3":  0x72,
    "f4":  0x73,
    "f5":  0x74,
    "f6":  0x75,
    "f7":  0x76,
    "f8":  0x77,
    "f9":  0x78,
    "f10":  0x79,
    "f11":  0x7A,
    "f12":  0x7B,
    "numlock":  0x90,
    "scroll":  0x91,
    "lshift":  0xA0,
    "rshift":  0xA1,
    "lcontrol":  0xA2,
    "rcontrol":  0xA3,
    "lmenu":  0xA4,
    "rmenu":  0XA5
}

MsgID = {
    'press': 0x100,
    'release': 0x101,
    'mouse_move_': 0x0200,
    'mouse_left_press': 0x0201,
    'mouse_left_release': 0x202,
}
PostMessageW = windll.user32.PostMessageW
MapVirtualKeyW = windll.user32.MapVirtualKeyW
VkKeyScanA = windll.user32.VkKeyScanA


def get_window_handle(window_name, ui):
    handle = windll.user32.FindWindowW(None, window_name)
    if handle == 0:
        msg = str("[input]:Target window not found!: %s" % window_name)
        ui.msg_print(msg)
        print("[input]:Target window not found!: %s" % window_name)
        return -1
    return handle


def get_vk_code(key):
    if len(key) == 1 and key in string.printable:
        return VkKeyScanA(ord(key))
    else:
        return VkCode.get(key)


def key_strike_generator(key, movement, input_mode, window_name, operation_list, ui):
    func = supported_input_methods.get(input_mode, "Invalid mode")
    if func == 'Invalid mode':
        msg = str("[Input]: Invalid input mode: %s" % input_mode)
        ui.msg_print(msg)
        print("[Input]: Invalid input mode: %s" % input_mode)
    else:
        handle = get_window_handle(window_name, ui)
        if handle == -1:
            msg = str("[input]:generate input failed!")
            ui.msg_print(msg)
            print("[input]:generate input failed!")
            return -1
        else:
            win32gui.SetForegroundWindow(handle)
        return func(key, movement, handle, operation_list, ui)


def post_message(key, movement, handle, operation_list, ui):
    if key == 0:
        return 0
    else:
        hwnd = handle
        if key.find('mouse') != -1:
            movement = str(key+'_'+movement)
            msg = MsgID.get(movement)
            wparam = 0
            lparam = 0
            PostMessageW(hwnd, msg, wparam, lparam)
        else:
            msg = MsgID.get(movement)
            vk_code = get_vk_code(key)
            scan_code = MapVirtualKeyW(vk_code, 0)
            wparam = vk_code
            lparam = 0
            # lparam:
            # 0 - 15(16 bit): key repeat count
            # 16 - 23(8 bit): scan code
            # 24: extended flag
            # 25 - 28(4 bit): reserved
            # 29: context code, if ALT is pressed, 1 for pressed
            # 30: previous key state, 1 pressed, 0 released
            # 31: transaction state flag, 1 release, 0 press
            if msg == 0x100:
                lparam = (scan_code << 16) | 1  # set repeated count as 1
            elif msg == 0x101:
                lparam = (scan_code << 16) | 0xC0000001  # set previous key state and transaction state flag as 1
            PostMessageW(hwnd, msg, wparam, lparam)
        return 0


def hw_simulator(key, movement, handle, operation_list, ui):
    result = submodule_hw_simulator.hw_simulator_execution(operation_list, ui)
    return result


supported_input_methods = {
    'post_message': post_message,
    'hw_simulator': hw_simulator
}