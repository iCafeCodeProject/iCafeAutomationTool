from PyQt5.QtWidgets import QApplication
from configs import init_config, global_setting
import module_hid_input_service
import class_define
import game_info_table
from ctypes import windll
import time

min_threshold = init_config.get("min_iqa_threshold")
max_threshold = init_config.get("max_iqa_threshold")
IQA_threshold_range = []
for num in range(min_threshold, max_threshold+1):
    IQA_threshold_range.append(str(num))

max_range = init_config.get("max_range")
supported_range = []
for num in range(0, max_range):
    supported_range.append(str(num))
    supported_range.append(str(num) + '.5')


# Read script file in the folder
def operation_list_generator(ui, start_step, stop_step):
    operation_list = []
    for i in range(start_step - 1, stop_step-1):
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
def operation_execution(ui, operation_list):
    # Read global settings
    addr, offset = global_setting.setting_table.get('game_name')
    game_name = addr[offset]
    addr, offset = global_setting.setting_table.get('input_mode')
    input_mode = addr[offset]
    game_info = game_info_table.supported_game_list.get(game_name, 'unsupported game')
    addr, offset = global_setting.setting_table.get('sys_language')
    local_language_code = addr[offset]
    game_window_name = game_info.game_window_name.get(local_language_code, 'unsupported language!')
    if game_window_name == 'unsupported language':
        msg = str("[op_exec]: local language is unsupported! execution aborted!")
        ui.msg_print(msg)
        return 1

    # HW keyboard and mouse click path
    if input_mode == 'hw_simulator':
        result = module_hid_input_service.key_strike_generator('key', 'press', input_mode, game_window_name, operation_list, ui)
        return result

    # SW keyboard and mouse click path
    total_steps = len(operation_list)
    ui.progressBar.setRange(0, total_steps)
    for i in range(0, total_steps):
        msg = str("[op_exec]: start execute step %s" % operation_list[i].step)
        ui.msg_print(msg)
        key = game_info.game_op_dict.get(operation_list[i].op_name, 'unsupported operation')
        repeat = int(operation_list[i].repeat)
        if 1:
            while repeat > 0:
                result = module_hid_input_service.key_strike_generator(key, 'press', input_mode, game_window_name, operation_list, ui)
                if result != 0:
                    msg = str("[op_exec]: step %s failed!" % operation_list[i].step)
                    ui.msg_print(msg)
                    
                    return -1
                if operation_list[i].time not in supported_range:

                    msg = str("[op_exec]: step %s failed! unsupported execution time!" % operation_list[i].step)
                    ui.msg_print(msg)
                    
                    return -1
                time.sleep(float(operation_list[i].time))
                result = module_hid_input_service.key_strike_generator(key, 'release', input_mode, game_window_name, operation_list, ui)
                if result != 0:

                    msg = str("[op_exec]: step %s failed!" % operation_list[i].step)
                    ui.msg_print(msg)
                    return -1
                repeat = repeat - 1
            msg = str("[op_exec]: step: %s complete!" % operation_list[i].step)
            ui.msg_print(msg)
            ui.progressBar.setValue(int(operation_list[i].step))
            QApplication.processEvents()
    return 0


def script_run(ui):
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
    if ui.lineEdit_Start_Step.text() not in target_range:
        msg = str('[run]: invalid start step %s' % ui.lineEdit_Target_Step.text())
        ui.msg_print(msg)
        return 0
    start_step = int(ui.lineEdit_Start_Step.text())

    if ui.lineEdit_Stop_Step.text() == '':
        msg = str('[run]: Will run to last step')
        ui.msg_print(msg)
        ui.lineEdit_Stop_Step.setText(str(total_line))
    if ui.lineEdit_Stop_Step.text() not in target_range:
        msg = str('[run]: invalid start step %s' % ui.lineEdit_Target_Step.text())
        ui.msg_print(msg)
        return 0
    stop_step = int(ui.lineEdit_Stop_Step.text())+1

    script_file_name = ui.lineEdit_Script_Name.text()
    operation_list = operation_list_generator(ui, start_step, stop_step)

    if operation_list == -1:
        msg = str("[run]: script: %s execution failed!" % script_file_name)
        ui.msg_print(msg)
        return 0
    # if ui.comboBox_Select_IQA.currentText() == 'Enable':
    if 0:
         global stop_flag
        # stop_flag = 1
        # IQA_threshold_max = ui.lineEdit_Threshold_Max.text()
        # IQA_threshold_min = ui.lineEdit_Threshold_Min.text()
        # if IQA_threshold_max not in IQA_threshold_range or IQA_threshold_min not in IQA_threshold_range:
        #     msg = str("[run]: unsupported IQA parameter! min: %s max: %s" % (IQA_threshold_min, IQA_threshold_max))
        #     ui.msg_print(msg)
        #     return 0
        # else:
        #     result = operation_execution(ui, operation_list)
        #     if result != 0:
        #         msg = str("[run]: script: %s execution failed!" % script_file_name)
        #         ui.msg_print(msg)
        #         return 0
        #     msg = str("[run]: script %s execution complete!" % script_file_name)
        #     ui.msg_print(msg)
    else:
        result = operation_execution(ui, operation_list)
        if result != 0:
            msg = str("[run]: script: %s execution failed!" % script_file_name)
            ui.msg_print(msg)
            return 0
        msg = str("[run]: script %s execution complete!" % script_file_name)
        ui.msg_print(msg)
        tool_window_name = init_config.get("tool_window_name")
        handle = windll.user32.FindWindowW(None, tool_window_name)
        #win32gui.SetForegroundWindow(handle)
    return 0


def single_step_run(ui):
    total_line = ui.tableWidget_Script_Display.rowCount()
    if total_line == 0:
        msg = str('[single_run]: Nothing to remove, please add or load a script!')
        ui.msg_print(msg)
        return 0
    target_range = []
    for i in range(1, total_line + 1):
        target_range.append(str(i))
    if ui.lineEdit_Target_Step.text() == '':
        msg = str('[single_run]: Please set a target step!')
        ui.msg_print(msg)
        return 0
    if ui.lineEdit_Target_Step.text() not in target_range:
        msg = str('[single_run]: invalid target step %s' % ui.lineEdit_Target_Step.text())
        ui.msg_print(msg)
        return 0
    target_step = int(ui.lineEdit_Target_Step.text())
    start_step = target_step
    stop_step = start_step + 1
    operation_list = operation_list_generator(ui, start_step, stop_step)
    result = operation_execution(ui, operation_list)
    if result != 0:
        msg = str("[single_run]: step: %d execution failed!" % target_step)
        ui.msg_print(msg)
        return 0
    else:
        msg = str("[single_run]: step %d execution complete!" % target_step)
        ui.msg_print(msg)
        return 0
