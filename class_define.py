class GlobalSettings(object):
    def __init__(self):
        self.values = ['0' for i in range(10)]
        self.setting_table = {
            'script_name': [self.values, 0],
            'game_name': [self.values, 1],
            'input_mode': [self.values, 2]
        }

    def edit_setting(self, setting_name, setting_value):
        addr = self.setting_table.get(setting_name, 'invalid')[0]
        offset = self.setting_table.get(setting_name, 'invalid')[1]
        if addr == 'invalid':
            print("invalid setting found: %s = %s skip it!\n" % (setting_name, setting_value))
        addr[offset] = setting_value

    def print_settings(self):
        print("Current settings:\n")
        for name in self.setting_table:
            addr = self.setting_table.get(name)[0]
            offset = self.setting_table.get(name)[1]
            print("%s = %s\n" % (name, addr[offset]))


class Operation(object):
    def __init__(self, init_step, init_opname, init_time, init_repeat):
        self.step = init_step
        self.op_name = init_opname
        self.time = init_time
        self.repeat = init_repeat

    def print_settings(self):
        print("Current settings:\n")
        for name, value in vars(self).items():
            print("%s: %s\n" % (name, value))


class GameInfo(object):
    def __init__(self):
        self.game_name = 'init_game_name'
        self.game_op_dict = {}
        self.game_window_name = {
            0x804: 'init_CN_name',
            0x409: 'init_EN_name'
        }
