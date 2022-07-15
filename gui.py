from PyQt5.QtWidgets import QApplication, QMainWindow, QHeaderView, QTableWidgetItem, QComboBox
from functools import partial
from ctypes import windll
from ImageTest import image_processing
from PIL import ImageGrab
import game_info_table
import virtual_input_service
import iCafe_Automation_Tool
import class_define
import time
import os
import sys
import ctypes
import tkinter
import datetime
from threading import Thread
import threading

# Global variable define
version = 'v1.0'
global_setting = class_define.GlobalSettings()
app = QApplication(sys.argv)
MainWindow = QMainWindow()
UI = iCafe_Automation_Tool.Ui_MainWindow()
UI.setupUi(MainWindow)
path = str(os.getcwd() + '\\scripts\\')
IQA_path = str(os.getcwd() + '\\failed_images\\')
default_script_name = 'default_script.txt'
fraps_window_name = 'FRAPS fps'
max_range = 10
supported_range = []
root = tkinter.Tk()
screen_size_x = root.winfo_screenwidth()
screen_size_y = root.winfo_screenheight()
pos_x = screen_size_x / 2
pos_y = screen_size_y / 2
default_IQA_threshold_min = '100'
default_IQA_threshold_max = '3000'
min_threshold = 0
max_threshold = 10000
IQA_threshold_range = []
stop_flag = 1
lock = threading.Lock()

for num in range(min_threshold, max_threshold+1):
    IQA_threshold_range.append(str(num))

for num in range(0, max_range):
    supported_range.append(str(num))
    supported_range.append(str(num) + '.5')


def status_check(ui):
    addr, offset = global_setting.setting_table.get('script_name')
    global_script_name = addr[offset]
    addr, offset = global_setting.setting_table.get('game_name')
    global_game_name = addr[offset]
    addr, offset = global_setting.setting_table.get('input_mode')
    global_input_mode = addr[offset]
    current_script_name = ui.lineEdit_Script_Name.text()
    current_game_name = ui.comboBox_Game_Name.currentText()
    current_input_mode = ui.comboBox_2_Input_Mode.currentText()
    if global_script_name != current_script_name:
        return 'script_name_not_save'
    elif global_input_mode != current_input_mode:
        return 'input_mode_not_save'
    elif global_game_name != current_game_name:
        return 'game_name_not_save'
    else:
        return 0


# Read script file in the folder
def operation_list_generator(ui, start_step):
    operation_list = []
    total_line = ui.tableWidget_Script_Display.rowCount()

    for i in range(start_step - 1, total_line):
        step = ui.tableWidget_Script_Display.item(i, 0).text()
        operation = ui.tableWidget_Script_Display.cellWidget(i, 1).currentText()
        execution_time = ui.tableWidget_Script_Display.item(i, 2).text()
        repeat_times = ui.tableWidget_Script_Display.item(i, 3).text()
        # Check unfilled attributes
        if execution_time == '' or repeat_times == '':
            msg = str('[op_gene]: step %s has no execution time or repeat time! please retry!' % step)
            ui.msg_print(msg)
            return -1
        # Check value in support range
        elif execution_time not in supported_range or repeat_times not in supported_range:
            msg = str('[op_gene]: step %s execution time or repeat time is not supported! please retry!' % step)
            ui.msg_print(msg)
            return -1
        else:
            operation_list.append(class_define.Operation(step, operation, execution_time, repeat_times))

    return operation_list


# Main execution function
def operation_execution(operation_list, pos_x, pos_y):
    global stop_flag
    # Read global settings
    addr, offset = global_setting.setting_table.get('game_name')
    game_name = addr[offset]
    addr, offset = global_setting.setting_table.get('input_mode')
    input_mode = addr[offset]
    game_info = game_info_table.supported_game_list.get(game_name, 'unsupported game')

    # Get current OS language and look up game window name
    dll_h = ctypes.windll.kernel32
    local_language_code = hex(dll_h.GetSystemDefaultUILanguage())
    game_window_name = game_info.game_window_name.get(local_language_code, 'unsupported language!')
    if game_window_name == 'unsupported language':
        msg = str("[op_exec]: local language is unsupported! execution aborted!")
        UI.msg_print(msg)
        stop_flag = 0
        return 1

    total_steps = len(operation_list)
    UI.progressBar.setRange(0, total_steps)

    for i in range(0, total_steps):
        msg = str("[op_exec]: start execute step %s" % operation_list[i].step)
        UI.msg_print(msg)
        key = game_info.game_op_dict.get(operation_list[i].op_name, 'unsupported operation')
        repeat = int(operation_list[i].repeat)
        # mouse_move need special path to set target position
        if key == 'mouse_move':
            # use GUI execution time and repeat value to set target cursor position
            block_x = int(operation_list[i].time)
            block_y = repeat
            if block_x > 4 or block_y > 4:
                msg = str("[op_exec]: step %s failed! unsupported cursor position" % operation_list[i].step)
                UI.msg_print(msg)
                stop_flag = 0
                return -1
            pos_x = (block_x - 1) * screen_size_x/4 + screen_size_x/8
            pos_y = (block_y - 1) * screen_size_y/4 + screen_size_y/8
            result = virtual_input_service.key_strike_generator(key, '', input_mode, game_window_name, UI, pos_x, pos_y)
            if result != 0:
                msg = str("[op_exec]: step %s failed!" % operation_list[i].step)
                UI.msg_print(msg)
                stop_flag = 0
                return -1

        # Normal keyboard and mouse click path
        else:
            while repeat > 0:
                lock.acquire()
                result = virtual_input_service.key_strike_generator(key, 'press', input_mode, game_window_name, UI, pos_x, pos_y)
                if result != 0:
                    msg = str("[op_exec]: step %s failed!" % operation_list[i].step)
                    UI.msg_print(msg)
                    stop_flag = 0
                    lock.release()
                    return -1
                if operation_list[i].time not in supported_range:
                    msg = str("[op_exec]: step %s failed! unsupported execution time!" % operation_list[i].step)
                    UI.msg_print(msg)
                    stop_flag = 0
                    lock.release()
                    return -1
                time.sleep(float(operation_list[i].time))
                result = virtual_input_service.key_strike_generator(key, 'release', input_mode, game_window_name, UI, pos_x, pos_y)
                if result != 0:
                    msg = str("[op_exec]: step %s failed!" % operation_list[i].step)
                    UI.msg_print(msg)
                    stop_flag = 0
                    lock.release()
                    return -1
                repeat = repeat - 1
            msg = str("[op_exec]: step: %s complete!" % operation_list[i].step)
            UI.msg_print(msg)
            UI.progressBar.setValue(int(operation_list[i].step))
            QApplication.processEvents()
            lock.release()
    lock.acquire()
    stop_flag = 0
    lock.release()
    return 0


def IQA_image_process(threshold_min, threshold_max):
    global stop_flag
    im_num = 0
    lock.acquire()
    addr, offset = global_setting.setting_table.get('game_name')
    game_name = addr[offset]
    lock.release()
    run_path = IQA_path + str(game_name + '_'+datetime.datetime.now().strftime('%m-%d-%H-%M-%S') + '\\')
    os.mkdir(run_path)
    while stop_flag:
        image = ImageGrab.grab()
        result = image_processing(threshold_min, threshold_max, image, UI)
        if result == 1:
            msg = str("[IQA]: Image %d fail detected!" % im_num)
            UI.msg_print(msg)
            image.save(run_path + str(im_num) + ".png")
            im_num = im_num + 1
        time.sleep(1)
    return 0


# Initialize GUI settings
def gui_init(ui):
    msg = str("----------------Welcome--------------")
    UI.msg_print(msg)
    msg = str("iCafe Automation Tool %s\n" % version)
    UI.msg_print(msg)
    for key in game_info_table.supported_game_list:
        ui.comboBox_Game_Name.addItem(key)
    for key in virtual_input_service.supported_input_methods:
        ui.comboBox_2_Input_Mode.addItem(key)
    ui.lineEdit_Script_Name.setText(default_script_name)
    ui.lineEdit_Start_Step.setText('1')
    ui.lineEdit_Target_Step.setText('0')

    global_setting.edit_setting('game_name', ui.comboBox_Game_Name.currentText())
    global_setting.edit_setting('input_mode', ui.comboBox_2_Input_Mode.currentText())
    global_setting.edit_setting('script_name', ui.lineEdit_Script_Name.text())

    ui.tableWidget_Script_Display.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    ui.tableWidget_Script_Display.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
    ui.tableWidget_Script_Display.setColumnCount(4)
    ui.progressBar.setRange(0, 0)

    result = os.path.exists(path)
    ui.comboBox_Select_Script.addItem('<Not Selected>')
    if result == 0:
        os.mkdir(path)
    file_list = os.listdir(path)
    for filename in file_list:
        if filename.split('.')[1] == 'txt':
            ui.comboBox_Select_Script.addItem(filename)
    for i in range(0, ui.comboBox_Select_Script.count()):
        if ui.comboBox_Select_Script.itemText(i) == default_script_name:
            msg = str("[init]: default script exist, now loading...")
            UI.msg_print(msg)
            ui.comboBox_Select_Script.setCurrentIndex(i)
            script_load(UI)
        elif i == ui.comboBox_Select_Script.count()-1:
            ui.comboBox_Select_Script.setCurrentIndex(0)

    result = os.path.exists(IQA_path)
    if result == 0:
        os.mkdir(IQA_path)
    ui.comboBox_Select_IQA.addItem('Enable')
    ui.comboBox_Select_IQA.addItem('Disable')
    ui.comboBox_Select_IQA.setCurrentIndex(0)

    ui.lineEdit_Threshold_Min.setText(default_IQA_threshold_min)
    ui.lineEdit_Threshold_Max.setText(default_IQA_threshold_max)


def script_load(ui):
    # clear current loaded script
    ui.tableWidget_Script_Display.setRowCount(0)
    # load new script
    script_file_name = str(path + ui.comboBox_Select_Script.currentText())
    if ui.comboBox_Select_Script.currentText() == '<Not Selected>':
        msg = str('[load]: please choose a script!')
        ui.msg_print(msg)
        return 0
    script = open(script_file_name).readlines()
    if len(script) == 0:
        msg = str('[load]: empty file: %s ! please choose another one' % ui.comboBox_Select_Script.currentText())
        ui.msg_print(msg)
        return 0
    # load script setting part
    count = 0
    for lines in script:
        if lines.rstrip() == 'setting part end':
            break
        setting_name = lines.rstrip().split(" = ")[0]
        setting_value = lines.rstrip().split(" = ")[1]
        global_setting.edit_setting(setting_name, setting_value)
        count = count + 1
    addr = global_setting.setting_table.get('script_name')[0]
    offset = global_setting.setting_table.get('script_name')[1]
    script_name = addr[offset]
    addr = global_setting.setting_table.get('game_name')[0]
    offset = global_setting.setting_table.get('game_name')[1]
    game_name = addr[offset]
    addr = global_setting.setting_table.get('input_mode')[0]
    offset = global_setting.setting_table.get('input_mode')[1]
    input_mode = addr[offset]

    # change current script name
    ui.lineEdit_Script_Name.setText(script_name)
    for i in range(0, ui.comboBox_Game_Name.count()):
        if game_name == ui.comboBox_Game_Name.itemText(i):
            ui.comboBox_Game_Name.setCurrentIndex(i)
            break
        elif i == ui.comboBox_Game_Name.count() - 1:
            msg = str("[load]: unsupported game: " + game_name)
            UI.msg_print(msg)
    for i in range(0, ui.comboBox_2_Input_Mode.count()):
        if input_mode == ui.comboBox_2_Input_Mode.itemText(i):
            ui.comboBox_2_Input_Mode.setCurrentIndex(i)
            break
        elif i == ui.comboBox_Game_Name.count() - 1:
            msg = str("[load]: unsupported game: " + input_mode)
            UI.msg_print(msg)

    total_steps = len(script) - count - 1
    ui.tableWidget_Script_Display.setRowCount(total_steps)
    game_info = game_info_table.supported_game_list.get(game_name)

    row = 0 - count
    state = 0

    for lines in script:
        # loop until setting part end
        if lines.rstrip() == 'setting part end':
            state = 1
            continue
        if state == 0:
            row = row + 1
            continue
        # start read script steps
        line_data = lines.rstrip().split(',')
        # skip blank lines
        if line_data[0] == '':
            total_steps = total_steps - 1
            ui.tableWidget_Script_Display.setRowCount(total_steps)
            continue

        for column in range(0, 4):
            if column == 1:
                locals()['op_combobox' + str(row)] = QComboBox()
                for key in game_info.game_op_dict:
                    locals()['op_combobox' + str(row)].addItem(key)
                ui.tableWidget_Script_Display.setCellWidget(row, column, locals()['op_combobox' + str(row)])
                for i in range(0, locals()['op_combobox' + str(row)].count()):
                    if line_data[column] == locals()['op_combobox' + str(row)].itemText(i):
                        locals()['op_combobox' + str(row)].setCurrentIndex(i)
            ui.tableWidget_Script_Display.setItem(row, column, QTableWidgetItem(line_data[column]))
        row = row + 1
        if row == total_steps:
            msg = str("[load]: script: %s load complete!" % script_name)
            ui.msg_print(msg)
            break


def script_add_line(ui):
    status = status_check(UI)
    if status == 'game_name_not_save':
        msg = str('[check]: game name changed, please click "refresh" and retry!')
        ui.msg_print(msg)
        return 0
    addr = global_setting.setting_table.get('game_name')[0]
    offset = global_setting.setting_table.get('game_name')[1]
    game_name = addr[offset]

    game_info = game_info_table.supported_game_list.get(game_name)
    total_line = ui.tableWidget_Script_Display.rowCount()
    total_line = total_line + 1
    ui.tableWidget_Script_Display.setRowCount(total_line)
    for column in range(0, 4):
        if column == 0:
            ui.tableWidget_Script_Display.setItem(total_line - 1, column, QTableWidgetItem(str(total_line)))
        elif column == 1:
            locals()['op_combobox' + str(total_line)] = QComboBox()
            for key in game_info.game_op_dict:
                locals()['op_combobox' + str(total_line)].addItem(key)
            ui.tableWidget_Script_Display.setCellWidget(total_line - 1, column, locals()['op_combobox' + str(total_line)])
        else:
            ui.tableWidget_Script_Display.setItem(total_line - 1, column, QTableWidgetItem(''))


def script_delete_line(ui):
    total_line = ui.tableWidget_Script_Display.rowCount()
    if total_line == 0:
        msg = str("[delete]: nothing to delete here!")
        UI.msg_print(msg)
        return 0
    for column in range(0, 4):
        # clear the last line
        ui.tableWidget_Script_Display.setItem(total_line - 1, column, QTableWidgetItem(''))
    total_line = total_line - 1
    ui.tableWidget_Script_Display.setRowCount(total_line)


def script_insert(ui):
    total_line = ui.tableWidget_Script_Display.rowCount()
    if total_line == 0:
        script_add_line(UI)
        return 0
    target_range = []
    for i in range(0, total_line + 1):
        target_range.append(str(i))
    if ui.lineEdit_Target_Step.text() == '':
        msg = str('[insert]: Please set a target step!')
        ui.msg_print(msg)
        return 0
    if ui.lineEdit_Target_Step.text() not in target_range:
        msg = str('[insert]: invalid target step %s' % ui.lineEdit_Target_Step.text())
        ui.msg_print(msg)
        return 0
    target_step = int(ui.lineEdit_Target_Step.text())

    status = status_check(UI)
    if status == 'game_name_not_save':
        msg = str('[check]: game name changed, please click "refresh" and retry!')
        ui.msg_print(msg)
        return 0
    addr = global_setting.setting_table.get('game_name')[0]
    offset = global_setting.setting_table.get('game_name')[1]
    game_name = addr[offset]
    game_info = game_info_table.supported_game_list.get(game_name)
    total_line = total_line + 1
    ui.tableWidget_Script_Display.setRowCount(total_line)
    for i in range(1, total_line - target_step + 1):
        if i == total_line - target_step:
            for column in range(0, 4):
                if column == 0:
                    ui.tableWidget_Script_Display.setItem(total_line - i, column, QTableWidgetItem(str(total_line - i + 1)))
                elif column == 1:
                    locals()['op_combobox' + str(total_line - i)] = QComboBox()
                    locals()['op_combobox' + str(total_line - i)].clear()
                    for key in game_info.game_op_dict:
                        locals()['op_combobox' + str(total_line - i)].addItem(key)
                    ui.tableWidget_Script_Display.setCellWidget(total_line - i, column, locals()['op_combobox' + str(total_line - i)])
                else:
                    ui.tableWidget_Script_Display.setItem(total_line - i, column, QTableWidgetItem(''))
        elif i == 1:
            for column in range(0, 4):
                if column == 0:
                    ui.tableWidget_Script_Display.setItem(total_line - i, column, QTableWidgetItem(str(total_line - i + 1)))
                elif column == 1:
                    locals()['op_combobox' + str(total_line - i)] = QComboBox()
                    locals()['op_combobox' + str(total_line - i)].clear()
                    for key in game_info.game_op_dict:
                        locals()['op_combobox' + str(total_line - i)].addItem(key)
                    ui.tableWidget_Script_Display.setCellWidget(total_line - i, column, locals()['op_combobox' + str(total_line - i)])
                    index = ui.tableWidget_Script_Display.cellWidget(total_line - i - 1, column).currentIndex()
                    ui.tableWidget_Script_Display.cellWidget(total_line - i, column).setCurrentIndex(index)
                elif column == 2:
                    exec_time = ui.tableWidget_Script_Display.item(total_line - i - 1, column).text()
                    ui.tableWidget_Script_Display.setItem(total_line - i, column, QTableWidgetItem(exec_time))
                elif column == 3:
                    repeat = ui.tableWidget_Script_Display.item(total_line - i - 1, column).text()
                    ui.tableWidget_Script_Display.setItem(total_line - i, column, QTableWidgetItem(repeat))

        else:
            for column in range(0, 4):
                if column == 0:
                    ui.tableWidget_Script_Display.setItem(total_line - i, column, QTableWidgetItem(str(total_line - i + 1)))
                elif column == 1:
                    index = ui.tableWidget_Script_Display.cellWidget(total_line - i - 1, column).currentIndex()
                    ui.tableWidget_Script_Display.cellWidget(total_line - i, column).setCurrentIndex(index)
                elif column == 2:
                    exec_time = ui.tableWidget_Script_Display.item(total_line - i - 1, column).text()
                    ui.tableWidget_Script_Display.setItem(total_line - i, column, QTableWidgetItem(exec_time))
                elif column == 3:
                    repeat = ui.tableWidget_Script_Display.item(total_line - i - 1, column).text()
                    ui.tableWidget_Script_Display.setItem(total_line - i, column, QTableWidgetItem(repeat))


def script_remove(ui):
    total_line = ui.tableWidget_Script_Display.rowCount()
    if total_line == 0:
        msg = str('[remove]: Nothing to remove, please add or load a script!')
        ui.msg_print(msg)
        return 0
    target_range = []
    for i in range(1, total_line + 1):
        target_range.append(str(i))
    if ui.lineEdit_Target_Step.text() == '':
        msg = str('[remove]: Please set a target step!')
        ui.msg_print(msg)
        return 0
    if ui.lineEdit_Target_Step.text() not in target_range:
        msg = str('[remove]: invalid target step %s' % ui.lineEdit_Target_Step.text())
        ui.msg_print(msg)
        return 0
    target_step = int(ui.lineEdit_Target_Step.text())

    for i in range(target_step - 1, total_line - 1):
        for column in range(0, 4):
            if column == 0:
                ui.tableWidget_Script_Display.setItem(i, column, QTableWidgetItem(str(i + 1)))
            elif column == 1:
                index = ui.tableWidget_Script_Display.cellWidget(i + 1, column).currentIndex()
                ui.tableWidget_Script_Display.cellWidget(i, column).setCurrentIndex(index)
            elif column == 2:
                exec_time = ui.tableWidget_Script_Display.item(i + 1, column).text()
                ui.tableWidget_Script_Display.setItem(i, column, QTableWidgetItem(exec_time))
            elif column == 3:
                repeat = ui.tableWidget_Script_Display.item(i + 1, column).text()
                ui.tableWidget_Script_Display.setItem(i, column, QTableWidgetItem(repeat))

    total_line = total_line - 1
    ui.tableWidget_Script_Display.setRowCount(total_line)


def script_save(ui):
    status = status_check(UI)
    if status == 'game_name_not_save':
        msg = str('[check]: game name changed, please click "refresh" and retry!')
        ui.msg_print(msg)
        return 0
    msg = str("[save]: now saving script file...")
    ui.msg_print(msg)
    # save setting part
    script_name = ui.lineEdit_Script_Name.text()
    game_name = ui.comboBox_Game_Name.currentText()
    input_mode = ui.comboBox_2_Input_Mode.currentText()
    with open(str(path + script_name), 'w') as f:
        f.write(str('script_name = ' + script_name + '\n'))
    with open(str(path + script_name), 'a') as f:
        f.write(str('game_name = ' + game_name + '\n'))
        f.write(str('input_mode = ' + input_mode + '\n'))
        f.write('setting part end\n')

    # save script part
    total_line = ui.tableWidget_Script_Display.rowCount()
    for i in range(0, total_line):
        step = str(i + 1)
        operation = ui.tableWidget_Script_Display.cellWidget(i, 1).currentText()
        execution_time = ui.tableWidget_Script_Display.item(i, 2).text()
        repeat_times = ui.tableWidget_Script_Display.item(i, 3).text()
        if execution_time == '' or repeat_times == '':
            msg = str('[save]: step %s has no execution time or repeat time! please retry!' % step)
            ui.msg_print(msg)
            return 0
        with open(str(path + script_name), 'a') as f:
            f.write(str(step + ',' + operation + ',' + execution_time + ',' + repeat_times + '\n'))

    msg = str("[save]: script file save complete!")
    ui.msg_print(msg)
    msg = str("[save]: now reload script file %s" % script_name)
    ui.msg_print(msg)

    # refresh and reload current script
    script_refresh(ui)
    state = 0
    for i in range(0, ui.comboBox_Select_Script.count()):
        if script_name == ui.comboBox_Select_Script.itemText(i):
            ui.comboBox_Select_Script.setCurrentIndex(i)
            state = 1
            break
    if state == 0:
        msg = ("[save]: reload failed! script: %s not found!" % script_name)
        ui.msg_print(msg)
        msg = ("[save]: please re-try!" % script_name)
        ui.msg_print(msg)
        return 0
    script_load(ui)


def script_run(ui):
    status = status_check(UI)
    if status == 'script_name_not_save':
        msg = str('[check]: script file name changed, please click "save script" and retry!')
        ui.msg_print(msg)
        return 0
    elif status == 'input_mode_not_save':
        msg = str('[check]: input mode changed, please click "save script" and retry!')
        ui.msg_print(msg)
        return 0
    elif status == 'game_name_not_save':
        msg = str('[check]: game name changed, please click "refresh" and retry!')
        ui.msg_print(msg)
        return 0
    # create operation list from current script and run
    total_line = ui.tableWidget_Script_Display.rowCount()
    if total_line == 0:
        msg = str('[run]: nothing to run, please add or load a script!')
        ui.msg_print(msg)
        return 0
    target_range = []
    for i in range(1, total_line + 1):
        target_range.append(str(i))
    if ui.lineEdit_Start_Step.text() == '':
        msg = str('[run]: run from step 1')
        ui.msg_print(msg)
        ui.lineEdit_Start_Step.setText('1')
        return 0
    if ui.lineEdit_Start_Step.text() not in target_range:
        msg = str('[run]: invalid start step %s' % ui.lineEdit_Target_Step.text())
        ui.msg_print(msg)
        return 0
    start_step = int(ui.lineEdit_Start_Step.text())

    script_file_name = ui.lineEdit_Script_Name.text()
    operation_list = operation_list_generator(UI, start_step)

    if operation_list == -1:
        msg = str("[run]: script: %s execution failed!" % script_file_name)
        ui.msg_print(msg)
        return 0
    if ui.comboBox_Select_IQA.currentText() == 'Enable':
        global stop_flag
        stop_flag = 1
        IQA_threshold_max = ui.lineEdit_Threshold_Max.text()
        IQA_threshold_min = ui.lineEdit_Threshold_Min.text()
        if IQA_threshold_max not in IQA_threshold_range or IQA_threshold_min not in IQA_threshold_range:
            msg = str("[run]: unsupported IQA parameter! min: %s max: %s" % (IQA_threshold_min, IQA_threshold_max))
            UI.msg_print(msg)
            return 0
        else:
            IQA_thread = Thread(target=IQA_image_process, args=(int(IQA_threshold_min), int(IQA_threshold_max)))
            IQA_thread.start()
            result = operation_execution(operation_list, pos_x, pos_y)
            if result != 0:
                msg = str("[run]: script: %s execution failed!" % script_file_name)
                UI.msg_print(msg)
                return 0
            msg = str("[run]: script %s execution complete!" % script_file_name)
            UI.msg_print(msg)
    else:
        result = operation_execution(operation_list, pos_x, pos_y)
        if result != 0:
            msg = str("[run]: script: %s execution failed!" % script_file_name)
            UI.msg_print(msg)
            return 0
        msg = str("[run]: script %s execution complete!" % script_file_name)
        UI.msg_print(msg)
    return 0


# refresh script list and apply current settings
def script_refresh(ui):
    screen_size_x = root.winfo_screenwidth()
    screen_size_y = root.winfo_screenheight()
    # clear current script list and re-scan script folder
    current_script = ui.comboBox_Select_Script.currentText()
    ui.comboBox_Select_Script.clear()
    result = os.path.exists(path)
    if result == 0:  # create script folder if not exist
        os.mkdir(path)
    file_list = os.listdir(path)
    for filename in file_list:
        if filename.split('.')[1] == 'txt':
            ui.comboBox_Select_Script.addItem(filename)

    for i in range(0, ui.comboBox_Select_Script.count()):  # if current selected script still exist, set it as default
        if current_script == ui.comboBox_Select_Script.itemText(i):
            ui.comboBox_Select_Script.setCurrentIndex(i)
            break
        elif i == ui.comboBox_Select_Script.count() - 1:
            ui.comboBox_Select_Script.addItem('<Not Selected>')
            ui.comboBox_Select_Script.setCurrentIndex(i + 1)

    # apply game changes
    game_name = ui.comboBox_Game_Name.currentText()
    game_info = game_info_table.supported_game_list.get(game_name)
    global_setting.edit_setting('game_name', game_name)
    total_line = ui.tableWidget_Script_Display.rowCount()
    for i in range(0, total_line):
        current_op = ui.tableWidget_Script_Display.cellWidget(i, 1).currentText()
        ui.tableWidget_Script_Display.cellWidget(i, 1).clear()
        for key in game_info.game_op_dict:
            ui.tableWidget_Script_Display.cellWidget(i, 1).addItem(key)
        for j in range(0, ui.tableWidget_Script_Display.cellWidget(i, 1).count()):
            if current_op == ui.tableWidget_Script_Display.cellWidget(i, 1).itemText(j):
                ui.tableWidget_Script_Display.cellWidget(i, 1).setCurrentIndex(j)
                break
            # if current selected operation is unsupported by new game, change it to "unsupported operation"
            elif j == ui.tableWidget_Script_Display.cellWidget(i, 1).count()-1:
                ui.tableWidget_Script_Display.cellWidget(i, 1).addItem('un-supported operation')
                ui.tableWidget_Script_Display.cellWidget(i, 1).setCurrentIndex(j+1)


if __name__ == '__main__':
    if not windll.shell32.IsUserAnAdmin():
        windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, __file__, None, 1)
    if windll.shell32.IsUserAnAdmin():
        MainWindow.show()
    gui_init(UI)

    # Define push buttons
    UI.pushButton_Load_Script.clicked.connect(partial(script_load, UI))
    UI.pushButton_4_Add_Script.clicked.connect(partial(script_add_line, UI))
    UI.pushButton_5_Delete_Script.clicked.connect(partial(script_delete_line, UI))
    UI.pushButton_2_Save_Script.clicked.connect(partial(script_save, UI))
    UI.pushButton_3_Run.clicked.connect(partial(script_run, UI))
    UI.pushButton_Refresh.clicked.connect(partial(script_refresh, UI))
    UI.pushButton_Insert.clicked.connect(partial(script_insert, UI))
    UI.pushButton_Remove.clicked.connect(partial(script_remove, UI))

    sys.exit(app.exec_())

