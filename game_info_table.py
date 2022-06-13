from class_define import GameInfo

# Genshin Impact game info
# Please update supported game table after add new game!
genshin_impact = GameInfo()
genshin_impact.game_name = genshin_impact
genshin_impact.game_op_dict = {
    'idle': 0,
    'forward': 'w',
    'backward': 's',
    'left': 'a',
    'right': 'd',
    'jump': 'space',
    'dash': 'lshift',  # please use 'lshift'(left shift) or rshift(right shift) instead of 'shift'
    'left_click': 'mouse_left',
    'mouse_move': 'mouse_move',
    'elemental_skill': 'e',
    'elemental_burst': 'q',
    'aim_mode': 'r',
    'pick_up': 'f',
    'switch_member_1': '1',
    'switch_member_2': '2',
    'switch_member_3': '3',
    'switch_member_4': '4',
}
genshin_impact.game_window_name = {
    '0x804': "原神",
    '0x409': "Genshin Impact"
}

# Crossfire game info
# Please update supported game table after add new game!
crossfire = GameInfo()
crossfire.game_name = crossfire
crossfire.game_op_dict = {
    'idle': 0,
    'forward': 'w',
    'backward': 's',
    'left': 'a',
    'right': 'd',
    'jump': 'space',
}
crossfire.game_window_name = {
    '0x804': "穿越火线",
    '0x409': "crossfire"
}


supported_game_list = {
    'genshin_impact': genshin_impact,
    'crossfire': crossfire,
}
