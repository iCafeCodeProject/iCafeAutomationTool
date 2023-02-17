import serial.tools.list_ports
import time
import game_info_table
from configs import global_setting
target_device_manufacturer = "Arduino LLC (www.arduino.cc)"
bps = 9600
timeout_count = 25
timeout_time = 1
timer_flag = 0
# data = bytearray([4, 10, 5, 10])
TRANSFER_COMPLETE_FLAG = b'\xff'
EXECUTION_COMPLETE_FLAG = b'\xfe'
EXECUTION_START_FLAG = b'\xfd'
EXECUTION_TIMEOUT_FLAG = b'\xfb'
ALL_COMPLETE_FLAG = b'\xf7'
SERIAL_BUFFER_CLEAR_FLAG = b'\xef'

current_step = bytearray([0])
total_steps = 0


key_code_list = {
  'KEY_A':       4,
  'KEY_B':      5,
  'KEY_C':       6,
  'KEY_D':       7,
  'KEY_E':       8,
  'KEY_F':       9,
  'KEY_G':       10,
  'KEY_H':       11,
  'KEY_I':      12,
  'KEY_J':      13,
  'KEY_K':       14,
  'KEY_L':       15,
  'KEY_M':       16,
  'KEY_N':       17,
  'KEY_O':       18,
  'KEY_P':       19,
  'KEY_Q':       20,
  'KEY_R':       21,
  'KEY_S':       22,
  'KEY_T':       23,
  'KEY_U':       24,
  'KEY_V':       25,
  'KEY_W':       26,
  'KEY_X':       27,
  'KEY_Y':       28,
  'KEY_Z':       29,
  'KEY_1':       30,
  'KEY_2':       31,
  'KEY_3':       32,
  'KEY_4':       33,
  'KEY_5':       34,
  'KEY_6':       35,
  'KEY_7':       36,
  'KEY_8':       37,
  'KEY_9':       38,
  'KEY_0':       39,
  'KEY_ENTER':   40,
  'KEY_ESCAPE':  41,
  'KEY_BACKSPACE':  42,
  'KEY_TAB':     43,
  'KEY_SPACE':   44,
  'KEY_MINUS':   45,
  'KEY_EQUALS':  46,
  'KEY_LBRACKET': 47,
  'KEY_RBRACKET': 48,
  'KEY_BACKSLASH': 49,
  'KEY_NONUS_NUMBER': 50,
  'KEY_SEMICOLON': 51,
  'KEY_QUOTE':   52,
  'KEY_TILDE':   53,
  'KEY_COMMA':   54,
  'KEY_PERIOD':  55,
  'KEY_SLASH':   56,
  'KEY_CAPSLOCK': 57,

  'KEY_F1':      58,
  'KEY_F2':      59,
  'KEY_F3':      60,
  'KEY_F4':      61,
  'KEY_F5':      62,
  'KEY_F6':      63,
  'KEY_F7':      64,
  'KEY_F8':      65,
  'KEY_F9':      66,
  'KEY_F10':     67,
  'KEY_F11':     68,
  'KEY_F12':     69,

  'KEY_PRNTSCRN':    70,
  'KEY_SCROLLLOCK':  71,
  'KEY_PAUSE':       72,
  'KEY_INSERT':      73,
  'KEY_HOME':        74,
  'KEY_PAGEUP':      75,
  'KEY_DELETE':      76,
  'KEY_END':         77,
  'KEY_PAGEDOWN':    78,
  'KEY_RIGHT_ARROW': 79,
  'KEY_LEFT_ARROW':  80,
  'KEY_DOWN_ARROW':  81,
  'KEY_UP_ARROW':    82,

  'KEY_NUM_LOCK':    83,

  'KEY_NUM_DIV':     84,
  'KEY_NUM_MUL':     85,
  'KEY_NUM_SUB':     86,
  'KEY_NUM_ADD':     87,

  'KEY_NUM_ENTER':   88,
  'KEY_NUM_1':       89,
  'KEY_NUM_2':       90,
  'KEY_NUM_3':       91,
  'KEY_NUM_4':       92,
  'KEY_NUM_5':       93,
  'KEY_NUM_6':       94,
  'KEY_NUM_7':       95,
  'KEY_NUM_8':       96,
  'KEY_NUM_9':       97,
  'KEY_NUM_0':       98,
  'KEY_NUM_DOT':     99,
  'KEY_ARROW_LEFT': 0x50,

}


def serial_port_init():
    port_list = list(serial.tools.list_ports.comports())
    if len(port_list) == 0:
        print("No target port founded! Please check connection!")
        return -1
    else:
        for i in range(0, len(port_list)):
            if port_list[i].manufacturer == target_device_manufacturer:
                target_port = port_list[i].device
                return serial.Serial(target_port, bps, timeout=timeout_time)
            elif i == len(port_list) - 1:
                print("No target port founded! Please check connection")
                return -1


def serial_send(serial_port, data_array, ui):
    if not serial_port.isOpen():
        serial_port.open()
    for i in range(0, len(data_array)):
        current_step_data = data_array[i]
        for j in range(0, len(current_step_data)):
            current_data = bytearray([current_step_data[j]])
            for count in range(0, timeout_count+1):
                if count == timeout_count:
                    msg = str("[Serial_send]:Data send failed! Please check connection!")
                    ui.msg_print(msg)
                    return -1
                serial_port.write(current_data)
                #print(current_data)
                if serial_port.inWaiting() > 0:
                    temp = serial_port.read(1)
                    #print(temp)
                    if temp == current_data:
                        #print(current_data)
                        break
                time.sleep(timeout_time/timeout_count)

            for clear_count in range(0, timeout_count+1):
                if clear_count == timeout_count:
                    #print("Serial buffer clear timeout! please check connection or reset device!")
                    msg = str("[Serial_send]:Step %s serial buffer clear timeout! please check connection or reset device!" % (i + 1))
                    ui.msg_print(msg)
                    return -1
                if serial_port.inWaiting() > 0:
                    temp = serial_port.read(1)
                    #print(temp)
                    if temp == SERIAL_BUFFER_CLEAR_FLAG:
                        #print(SERIAL_BUFFER_CLEAR_FLAG)
                        break
                time.sleep(timeout_time/timeout_count)
        if i == len(data_array) - 1:
            break
        msg = str("[Serial_send]:step %s data send successful!" % (i + 1))
        ui.msg_print(msg)
    return 0


def serial_data_generator(operation_list):
    global total_steps
    addr, offset = global_setting.setting_table.get('game_name')
    game_name = addr[offset]
    game_info = game_info_table.supported_game_list.get(game_name, 'unsupported game')

    serial_data = []
    total_steps = len(operation_list)
    for i in range(0, total_steps):
        key = game_info.game_op_dict.get(operation_list[i].op_name, 'unsupported operation')
        if key == 0:
            key_code = 0
        else:
            key_code = key_code_list.get(str('KEY_'+key.upper()), 'unsupported key!')
        if key == 'unsupported key':
            return -1
        execution_time = int(operation_list[i].time)
        repeat = int(operation_list[i].repeat)
        serial_data.append(bytearray([key_code, execution_time, repeat]))
    serial_data.append(bytearray([255]))
    return serial_data


def hw_simulator_execution(operation_list, ui):
    global current_step
    target_port = serial_port_init()
    if target_port == -1:
        msg = str("[hw_siml]:no compatible device, please check connection!")
        ui.msg_print(msg)
        return -1
    data = serial_data_generator(operation_list)
    result = serial_send(target_port, data, ui)
    if result == 0:
        msg = str("[hw_siml]:All step data send successful!")
        ui.msg_print(msg)
        target_port.flushInput()
    elif result == -1:
        return -1

    while 1:
        if target_port.inWaiting() > 0:
            temp = target_port.read(1)
            if temp == EXECUTION_TIMEOUT_FLAG:
                msg = str("[hw_siml]:Execution timeout! please check connection!")
                ui.msg_print(msg)
                return -1
            elif temp == EXECUTION_START_FLAG:
                msg = str("[hw_siml]:Start executing!")
                ui.msg_print(msg)
            elif temp == EXECUTION_COMPLETE_FLAG:
                msg = str("[hw_siml]:Step %d execution complete!" % int.from_bytes(current_step, "little"))
                ui.msg_print(msg)
            elif temp == ALL_COMPLETE_FLAG:
                msg = str("[hw_siml]:All steps execution complete!")
                ui.msg_print(msg)
                return 0
            elif int.from_bytes(temp, "little") <= total_steps:
                current_step = temp
                msg = str("[hw_siml]:Start executing Step %d!" % int.from_bytes(current_step, "little"))
                ui.msg_print(msg)
























