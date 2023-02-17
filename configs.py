import os
import class_define
init_config = {
    'version': 'v0.2',
    'script_path': str(os.getcwd() + '\\scripts\\'),
    'iqa_path': str(os.getcwd() + '\\failed_images\\'),
    'default_script_name': 'default_script',
    'max_range': 10,
    'default_iqa_threshold_min': '200',
    'default_iqa_threshold_max': '2000',
    'min_iqa_threshold': 0,
    'max_iqa_threshold': 100000,
    'script_type': '.txt',
    'tool_window_name': 'iCafe Automation Tool'
}
global_setting = class_define.GlobalSettings()
