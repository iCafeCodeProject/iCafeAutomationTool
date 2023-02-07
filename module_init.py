from PyQt5.QtWidgets import QHeaderView
from configs import init_config, global_setting
from module_script_editor import script_load
import game_info_table
import module_hid_input_service
import os
import ctypes


# Initialize GUI settings
def gui_init(ui):
    basic_widget_init(ui)
    check_script_path(ui)
    check_iqa_path(ui)
    msg = str("----------------Welcome--------------")
    ui.msg_print(msg)
    version = init_config.get('version')
    msg = str("iCafe Automation Tool %s\n" % version)
    ui.msg_print(msg)


def check_script_path(ui):
    # Check if default script path exists
    script_path = init_config.get("script_path")
    result = os.path.exists(script_path)
    if result == 0:
        os.mkdir(script_path)
        msg = str("[path_check]: No script folder founded! Creating new folder...")
        ui.msg_print(msg)
        ui.comboBox_Select_Script.clear()
        ui.comboBox_Select_Script.addItem('<Not Selected>')
        ui.comboBox_Select_Script.setCurrentIndex(0)
        return 0

    # Check existing script files and load default script
    default_script_name = init_config.get("default_script_name")
    script_type = init_config.get("script_type")
    ui.comboBox_Select_Script.clear()
    ui.comboBox_Select_Script.addItem('<Not Selected>')
    file_list = os.listdir(script_path)
    for filename in file_list:
        if os.path.splitext(filename)[-1] == script_type:
            ui.comboBox_Select_Script.addItem(os.path.splitext(filename)[0])
    for i in range(0, ui.comboBox_Select_Script.count()):
        if ui.comboBox_Select_Script.itemText(i) == default_script_name:
            msg = str("[path_check]: default script exist, now loading...")
            ui.msg_print(msg)
            ui.comboBox_Select_Script.setCurrentIndex(i)
            script_load(ui)
            break
        elif i == ui.comboBox_Select_Script.count() - 1:
            ui.comboBox_Select_Script.setCurrentIndex(0)
    return 0


def check_iqa_path(ui):
    iqa_path = init_config.get("iqa_path")
    default_iqa_threshold_min = init_config.get("default_iqa_threshold_min")
    default_iqa_threshold_max = init_config.get("default_iqa_threshold_max")

    result = os.path.exists(iqa_path)
    if result == 0:
        os.mkdir(iqa_path)

    #ui.comboBox_Select_IQA.addItem('Enable')
    #ui.comboBox_Select_IQA.addItem('Disable')
    #ui.comboBox_Select_IQA.setCurrentIndex(1)

    ui.lineEdit_Threshold_Min.setText(default_iqa_threshold_min)
    ui.lineEdit_Threshold_Max.setText(default_iqa_threshold_max)


def basic_widget_init(ui):
    for key in game_info_table.supported_game_list:
        ui.comboBox_Game_Name.addItem(key)
    for key in module_hid_input_service.supported_input_methods:
        ui.comboBox_2_Input_Mode.addItem(key)
    default_script_name = init_config.get("default_script_name")
    ui.lineEdit_Script_Name.setText(default_script_name)
    game_name = ui.comboBox_Game_Name.currentText()
    input_mode = ui.comboBox_2_Input_Mode.currentText()
    global_setting.edit_setting("game_name", game_name)
    global_setting.edit_setting("input_mode", input_mode)
    global_setting.edit_setting("script_name", default_script_name)

    dll_h = ctypes.windll.kernel32
    local_language_code = hex(dll_h.GetSystemDefaultUILanguage())

    global_setting.edit_setting("sys_language", local_language_code)
    ui.lineEdit_Start_Step.setText('1')
    ui.lineEdit_Target_Step.setText('0')
    ui.tableWidget_Script_Display.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    ui.tableWidget_Script_Display.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
    ui.tableWidget_Script_Display.setColumnCount(4)
    ui.progressBar.setRange(0, 0)
