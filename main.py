from PyQt5.QtWidgets import QMainWindow, QApplication
from functools import partial
from ctypes import windll
from module_init import *
from module_script_editor import *
from module_script_run import *
from module_IQA_test import *
import iCafe_Automation_Tool
import class_define
import sys


if __name__ == '__main__':
    if not windll.shell32.IsUserAnAdmin():
        windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, __file__, None, 1)
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    UI = iCafe_Automation_Tool.Ui_MainWindow()
    UI.setupUi(MainWindow)
    if windll.shell32.IsUserAnAdmin():
        MainWindow.show()

    gui_init(UI)

    # Define single thread push buttons
    UI.pushButton_Load_Script.clicked.connect(partial(script_changed_check, UI, MainWindow))
    UI.pushButton_4_Add_Script.clicked.connect(partial(script_add_line, UI))
    UI.pushButton_5_Delete_Script.clicked.connect(partial(script_delete_line, UI))
    UI.pushButton_2_Save_Script.clicked.connect(partial(script_save, UI))
    UI.pushButton_Refresh.clicked.connect(partial(script_folder_refresh, UI))
    UI.pushButton_Insert.clicked.connect(partial(script_insert, UI))
    UI.pushButton_Remove.clicked.connect(partial(script_remove, UI))
    UI.pushButton_IQA_test_start.clicked.connect(partial(iqa_test, UI))

    # Define multi thread push buttons
    pushButton_3_Run_clicked_response = class_define.ClickResponse(script_run, UI)
    UI.pushButton_3_Run.clicked.connect(partial(script_run, UI))
    pushButton_Run_Single_Step_clicked_response = class_define.ClickResponse(single_step_run, UI)
    UI.pushButton_Run_Single_Step.clicked.connect(partial(single_step_run, UI))

    # Define signals
    UI.comboBox_Game_Name.currentIndexChanged.connect(partial(game_name_changed_check, UI, MainWindow))
    UI.comboBox_2_Input_Mode.currentIndexChanged.connect(partial(input_mode_changed_check, UI, MainWindow))

    sys.exit(app.exec_())

