from PyQt5.QtWidgets import QTableWidgetItem, QComboBox, QMessageBox
from configs import init_config, global_setting
import os
import game_info_table

script_path = init_config.get("script_path")
script_type = init_config.get("script_type")


def game_name_changed_check(ui, main_window):
    addr = global_setting.setting_table.get('game_name')[0]
    offset = global_setting.setting_table.get('game_name')[1]
    current_game_name = addr[offset]
    if ui.comboBox_Game_Name.currentText() == current_game_name:
        return 0
    else:
        result = QMessageBox.warning(main_window, "Warning", "Target game will be changed, continue?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if result == QMessageBox.Yes:
            update_target_game(ui)
        elif result == QMessageBox.No:
            for i in range(0, ui.comboBox_Game_Name.count()):
                if current_game_name == ui.comboBox_Game_Name.itemText(i):
                    ui.comboBox_Game_Name.setCurrentIndex(i)
                    break
    return 0


def input_mode_changed_check(ui, main_window):
    addr = global_setting.setting_table.get('input_mode')[0]
    offset = global_setting.setting_table.get('input_mode')[1]
    current_input_mode = addr[offset]
    if ui.comboBox_2_Input_Mode.currentText() == current_input_mode:
        return 0
    else:
        result = QMessageBox.warning(main_window, "Warning", "Input mode will be changed, continue?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if result == QMessageBox.Yes:
            update_input_mode(ui)
        elif result == QMessageBox.No:
            for i in range(0, ui.comboBox_2_Input_Mode.count()):
                if current_input_mode == ui.comboBox_2_Input_Mode.itemText(i):
                    ui.comboBox_2_Input_Mode.setCurrentIndex(i)
                    break
    return 0


def script_changed_check(ui, main_window):
    addr = global_setting.setting_table.get('current_script')[0]
    offset = global_setting.setting_table.get('current_script')[1]
    current_script = addr[offset]
    if ui.comboBox_Select_Script.currentText() == current_script:
        return 0
    else:
        result = QMessageBox.warning(main_window, "Warning", "All unsaved changes will be lost, continue to load new script? ", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if result == QMessageBox.Yes:
            script_load(ui)
        elif result == QMessageBox.No:
            for i in range(0, ui.comboBox_Select_Script.count()):
                if current_script == ui.comboBox_Select_Script.itemText(i):
                    ui.comboBox_Select_Script.setCurrentIndex(i)
                    break
    return 0


def update_target_game(ui):
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
            elif j == ui.tableWidget_Script_Display.cellWidget(i, 1).count() - 1:
                ui.tableWidget_Script_Display.cellWidget(i, 1).addItem('un-supported operation')
                ui.tableWidget_Script_Display.cellWidget(i, 1).setCurrentIndex(j + 1)


def update_input_mode(ui):
    input_mode = ui.comboBox_2_Input_Mode.currentText()
    global_setting.edit_setting('input_mode', input_mode)


def script_folder_refresh(ui):
    # clear current script list and re-scan script folder
    current_script = ui.comboBox_Select_Script.currentText()
    ui.comboBox_Select_Script.clear()
    ui.comboBox_Select_Script.addItem('<Not Selected>')
    result = os.path.exists(script_path)
    if result == 0:  # create script folder if not exist
        os.mkdir(script_path)
    file_list = os.listdir(script_path)
    for filename in file_list:
        if os.path.splitext(filename)[-1] == script_type:
            ui.comboBox_Select_Script.addItem(os.path.splitext(filename)[0])

    for i in range(0, ui.comboBox_Select_Script.count()):  # if current selected script still exist, set it as default
        if current_script == ui.comboBox_Select_Script.itemText(i):
            ui.comboBox_Select_Script.setCurrentIndex(i)
            break
        elif i == ui.comboBox_Select_Script.count() - 1:
            ui.comboBox_Select_Script.setCurrentIndex(0)


def script_load(ui):
    script_file_name = str(script_path + ui.comboBox_Select_Script.currentText() + script_type)
    if ui.comboBox_Select_Script.currentText() == '<Not Selected>':
        msg = str('[load]: please choose a script!')
        ui.msg_print(msg)
        return 0
    # Check file still exists:
    results = os.path.exists(str(script_path + ui.comboBox_Select_Script.currentText() + script_type))
    if results == 0:
        msg = str("[load]: selected file don't exists! please press refresh button to check!")
        ui.msg_print(msg)
        return 0
    # clear current loaded script
    ui.tableWidget_Script_Display.setRowCount(0)
    # load new script
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
            ui.msg_print(msg)
    for i in range(0, ui.comboBox_2_Input_Mode.count()):
        if input_mode == ui.comboBox_2_Input_Mode.itemText(i):
            ui.comboBox_2_Input_Mode.setCurrentIndex(i)
            break
        elif i == ui.comboBox_Game_Name.count() - 1:
            msg = str("[load]: unsupported input mode: " + input_mode)
            ui.msg_print(msg)

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
            global_setting.edit_setting("current_script", ui.comboBox_Select_Script.currentText())
            ui.lineEdit_Start_Step.setText('1')
            ui.lineEdit_Stop_Step.setText('')
            break


def script_add_line(ui):
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
        ui.msg_print(msg)
        return 0
    for column in range(0, 4):
        # clear the last line
        ui.tableWidget_Script_Display.setItem(total_line - 1, column, QTableWidgetItem(''))
    total_line = total_line - 1
    ui.tableWidget_Script_Display.setRowCount(total_line)


def script_insert(ui):
    total_line = ui.tableWidget_Script_Display.rowCount()
    if total_line == 0:
        script_add_line(ui)
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
    msg = str("[save]: now saving script file...")
    ui.msg_print(msg)
    # save setting part
    script_name = ui.lineEdit_Script_Name.text()
    if os.path.splitext(script_name)[-1] != script_type:
        script_name = script_name + script_type
    game_name = ui.comboBox_Game_Name.currentText()
    input_mode = ui.comboBox_2_Input_Mode.currentText()
    with open(str(script_path + script_name), 'w') as f:
        f.write(str('script_name = ' + os.path.splitext(script_name)[0] + '\n'))
    with open(str(script_path + script_name), 'a') as f:
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
        if operation == 'un-supported operation':
            msg = str('[save] step %s operation is not supported, please choose a supported one and retry!' % step)
            ui.msg_print(msg)
            return 0
        if execution_time == '' or repeat_times == '':
            msg = str('[save]: step %s has no execution time or repeat time! please retry!' % step)
            ui.msg_print(msg)
            return 0
        with open(str(script_path + script_name), 'a') as f:
            f.write(str(step + ',' + operation + ',' + execution_time + ',' + repeat_times + '\n'))

    msg = str("[save]: script file save complete!")
    ui.msg_print(msg)
    msg = str("[save]: now reload script file %s" % script_name)
    ui.msg_print(msg)

    # refresh and reload current script
    script_folder_refresh(ui)
    state = 0
    for i in range(0, ui.comboBox_Select_Script.count()):
        if os.path.splitext(script_name)[0] == ui.comboBox_Select_Script.itemText(i):
            ui.comboBox_Select_Script.setCurrentIndex(i)
            state = 1
            break
    if state == 0:
        msg = ("[save]: reload failed! script: %s not found!" % os.path.splitext(script_name)[0])
        ui.msg_print(msg)
        msg = "[save]: please re-try!"
        ui.msg_print(msg)
        return 0
    script_load(ui)
