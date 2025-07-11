import itertools
import struct
import random
from mldtr import randomize_repack
from mnllib.n3ds import fs_std_code_bin_path, fs_std_romfs_path
from mnllib.dt import FMAPDAT_OFFSET_TABLE_LENGTH_ADDRESS, FMAPDAT_PATH, NUMBER_OF_ROOMS, \
    determine_version_from_code_bin, load_enemy_stats, save_enemy_stats, FEventScriptManager, \
    FMAPDAT_REAL_WORLD_OFFSET_TABLE_LENGTH_ADDRESS, FMAPDAT_DREAM_WORLD_OFFSET_TABLE_LENGTH_ADDRESS


#input_folder = 'C:/Users/Dimit/AppData/Roaming/Azahar/load/mods/00040000000D5A00'
#stat_mult = [5, 5]

def fix_offsets(fmapdat, code_bin, room, new_len, spot, next_room):
    do_once = False
    version_pair = determine_version_from_code_bin(code_bin)
    for i in range(next_room - room):
        r = room + i
        code_bin.seek(FMAPDAT_OFFSET_TABLE_LENGTH_ADDRESS[version_pair] + 16 + r*8)
        room_pos, room_len = struct.unpack('<II', code_bin.read(4 * 2))
        if not do_once:
            do_once = True
            room_len = 0x68
            old_len = 0
            for c in range(13):
                fmapdat.seek(room_pos + c*8)
                chunk_pos, chunk_len = struct.unpack('<II', fmapdat.read(4 * 2))
                chunk_next_pos = struct.unpack('<I', fmapdat.read(4))
                if c == spot:
                    fmapdat.seek(room_pos + c*8 + 4)
                    fmapdat.write(new_len.to_bytes(4, "little"))
                    old_len = chunk_len
                    chunk_len = new_len
                room_len += chunk_len
                if (chunk_len == 0 or c == 11) and chunk_next_pos[0] - chunk_pos + (old_len - new_len) != 0:
                    padding = 0
                    fmapdat.seek(room_pos + chunk_pos + chunk_len)
                    chunk_type = int.from_bytes(fmapdat.read(1))
                    while chunk_type == 0 or (chunk_type == 0xFF and c == 11):
                        padding += 1
                        fmapdat.seek(room_pos + chunk_pos + chunk_len + padding)
                        chunk_type = int.from_bytes(fmapdat.read(1))
                    if padding % 4 != 2 or c > 7:
                        chunk_len += padding
                        room_len += padding
                    else:
                        test = 0
                if chunk_pos + chunk_len != chunk_next_pos[0] and c != 12:
                    new_chunk_pos = chunk_pos + chunk_len
                    fmapdat.seek(room_pos + c*8 + 8)
                    fmapdat.write(new_chunk_pos.to_bytes(4, "little"))
        room_next_pos = struct.unpack('<I', code_bin.read(4))
        code_bin.seek(FMAPDAT_REAL_WORLD_OFFSET_TABLE_LENGTH_ADDRESS[version_pair] + 16 + 4 + r*8)
        code_bin.write(room_len.to_bytes(4, "little"))
        code_bin.seek(FMAPDAT_DREAM_WORLD_OFFSET_TABLE_LENGTH_ADDRESS[version_pair] + 16 + 4 + r*8)
        code_bin.write(room_len.to_bytes(4, "little"))
        if r == NUMBER_OF_ROOMS:
            room_len += 0x64
        if room_pos + room_len != room_next_pos[0]:
            room_next_pos = room_pos + room_len
            code_bin.seek(FMAPDAT_REAL_WORLD_OFFSET_TABLE_LENGTH_ADDRESS[version_pair] + 16 + 8 + r*8)
            code_bin.write(room_next_pos.to_bytes(4, "little"))
            code_bin.seek(FMAPDAT_DREAM_WORLD_OFFSET_TABLE_LENGTH_ADDRESS[version_pair] + 16 + 8 + r*8)
            code_bin.write(room_next_pos.to_bytes(4, "little"))

def get_room(id):
    if 0x000 <= id <= 0x00C or id == 0x00F or id == 0x018 or id == 0x1C8 or 0x050 <= id <= 0x055:
        return "Mushrise Park"
    elif id == 0x00E or 0x010 <= id <= 0x017 or id == 0x019 or id == 0x01A or id == 0x05D or 0x60 <= id <= 0x62 or id == 0x0AF or 0x101 <= id <= 0x104 or id == 0x138 or id == 0x1DC or id == 0x28A:
        return "Dozing Sands"
    elif id == 0x01B or id == 0x01C or 0x056 <= id <= 0x05C or id == 0x063 or id == 0x064 or id == 0x1DE:
        return "Blimport"
    elif 0x01D <= id <= 0x030 or id == 0x032 or id == 0x0B0 or id == 0x09D or 0x0F1 <= id <= 0x0F3 or id == 0x199 or id == 0x19A or id == 0x1CD or id == 0x1CE:
        return "Dreamy Mushrise Park"
    elif 0x033 <= id <= 0x037 or id == 0x039 or 0x03C <= id <= 0x044 or 0x108 <= id <= 0x10A or id == 0x288:
        return "Wakeport"
    elif id == 0x038 or id == 0x03A or id == 0x03B or 0x045 <= id <= 0x04F:
        return "Driftwood Shores"
    elif 0x066 <= id <= 0x081 or id == 0x100 or id == 0x10B or id == 0x10C:
        return "Mount Pajamaja"
    elif id == 0x082 or 0x084 <= id <= 0x09B or 0x136 <= id <= 0x13B or id == 0x1D8:
        return "Pi'illo Castle"
    elif 0x0A1 <= id <= 0x0AE or 0x0D8 <= id <= 0x0DE or 0x0F4 <= id <= 0x0FA:
        return "Dreamy Pi'illo Castle"
    elif 0x0B1 <= id <= 0x0C7 or 0x0E4 <= id <= 0x0F0 or 0x13C <= id <= 0x13E or id == 0x1D6:
        return "Dreamy Dozing Sands"
    elif 0x0D2 <= id <= 0x0D6 or 0x161 <= id <= 0x182 or id == 0x1C9 or id == 0x1CA:
        return "Dreamy Driftwood Shores"
    elif id == 0x106 or 0x10D <= id <= 0x134 or id == 0x12B or id == 0x12C or id == 0x1CF or id == 0x1E1 or id == 0x294 or id == 0x295:
        return "Dreamy Wakeport"
    else:
        return "Unknown"

def get_spot_type(spot):
    if spot[2] == 0x0012 or spot[2] == 0x0013:
        return 5
    return 0

def find_index_in_2d_list(arr, target_value):
    for row_index, row in enumerate(arr):
        for col_index, element in enumerate(row):
            if element == target_value:
                return (row_index, col_index)
    return None  # Return None if the element is not found

def is_available(logic, key, settings):
    #Sets up the variables to check the logic
    available = True
    was_true = False
    for d in range(len(logic)-1):
        #Checks if you have the items needed for the check
        if key[logic[d+1]] < 1:
            available = False
        #If it's an or statement, it resets the generation for the next statement
        #while setting wasTrue depending on whether the chunk was true or not
        if logic[d+1] < 0:
            if not available:
                available = True
            else:
                was_true = True
    if was_true:
        available = True
    return available

def randomize_data(input_folder, stat_mult, settings, seed):
    print("Initializing...")
    #Sets the seed to what it was in main
    random.seed = seed

    # Opens code.bin for enemy stat randomization
    code_bin_path = fs_std_code_bin_path(data_dir=input_folder)
    enemy_stats = load_enemy_stats(code_bin=code_bin_path)
    enemy_stats_rand = []
    dream_enemy_stats_rand = []
    boss_stats_rand = []
    dream_boss_stats_rand = []
    filler_stats_rand = []
    for enemy in range(len(enemy_stats)):
        if stat_mult[0] > -1:
            enemy_stats[enemy].power *= stat_mult[0]
            if enemy_stats[enemy].power > 0xFFFF:
                enemy_stats[enemy].power = 0xFFFF
        else:
            enemy_stats[enemy].power = 0xFFFF
        if stat_mult[1] > 0:
            enemy_stats[enemy].exp *= stat_mult[1]
            if enemy_stats[enemy].exp > 0xFFFF:
                enemy_stats[enemy].exp = 0xFFFF
        if (enemy > 12 and not(14 <= enemy <= 16) and enemy != 20 and
                enemy != 22 and enemy != 24 and enemy != 26 and
                enemy != 28 and enemy != 32 and enemy != 34 and
                enemy != 40 and enemy != 43 and enemy != 44 and
                enemy != 48 and enemy != 51 and not(53 <= enemy <= 56) and
                enemy != 63 and enemy != 83 and enemy != 97 and
                enemy != 103 and enemy != 105 and enemy != 114 and
                enemy != 132 and not(134 <= enemy <= 136) and enemy < 139):
            #Appends data to enemy array if it's an enemy
            if (enemy == 13 or enemy == 18 or enemy == 25 or
                    enemy == 27 or enemy == 29 or enemy == 38 or
                    enemy == 39 or enemy == 41 or (58 <= enemy <= 61) or
                    (68 <= enemy <= 71) or (85 <= enemy <= 94) or
                    (100 <= enemy <= 102) or enemy == 104 or enemy == 106 or
                    enemy == 113 or (115 <= enemy <= 120)):
                enemy_stats_rand.append([enemy, enemy_stats[enemy].hp, enemy_stats[enemy].power, enemy_stats[enemy].defense,
                                         enemy_stats[enemy].speed, enemy_stats[enemy].exp, enemy_stats[enemy].coins, enemy_stats[enemy].coin_rate,
                                         enemy_stats[enemy].item_chance, enemy_stats[enemy].item_type, enemy_stats[enemy].rare_item_chance, enemy_stats[enemy].rare_item_type, enemy_stats[enemy].level])
            #Appends data to boss array if it's a boss
            elif (enemy == 17 or enemy == 30 or enemy == 42 or
                  enemy == 62 or enemy == 95 or enemy == 96 or
                  enemy == 107 or enemy == 108):
                boss_stats_rand.append([enemy, enemy_stats[enemy].hp, enemy_stats[enemy].power, enemy_stats[enemy].defense,
                                         enemy_stats[enemy].speed, enemy_stats[enemy].exp, enemy_stats[enemy].coins, enemy_stats[enemy].coin_rate,
                                         enemy_stats[enemy].item_chance, enemy_stats[enemy].item_type, enemy_stats[enemy].rare_item_chance, enemy_stats[enemy].rare_item_type, enemy_stats[enemy].level])
            #Appends data to dream enemy array if it's a dream enemy
            elif (enemy == 19 or enemy == 21 or enemy == 31 or
                  enemy == 33 or enemy == 35 or enemy == 45 or
                  enemy == 46 or enemy == 47 or enemy == 49 or
                  enemy == 50 or (64 <= enemy <= 67) or (72 <= enemy <= 78) or
                  enemy == 84 or enemy == 98 or enemy == 99 or
                  (110 <= enemy <= 112) or (121 <= enemy <= 125) or enemy == 133):
                dream_enemy_stats_rand.append([enemy, enemy_stats[enemy].hp, enemy_stats[enemy].power, enemy_stats[enemy].defense,
                                         enemy_stats[enemy].speed, enemy_stats[enemy].exp, enemy_stats[enemy].coins, enemy_stats[enemy].coin_rate,
                                         enemy_stats[enemy].item_chance, enemy_stats[enemy].item_type, enemy_stats[enemy].rare_item_chance, enemy_stats[enemy].rare_item_type, enemy_stats[enemy].level])
            #Appends data to dream boss array if it's a dream boss
            elif (enemy == 23 or enemy == 36 or enemy == 52 or
                  (79 <= enemy <= 81) or (126 <= enemy <= 131) or enemy == 137):
                dream_boss_stats_rand.append([enemy, enemy_stats[enemy].hp, enemy_stats[enemy].power, enemy_stats[enemy].defense,
                                         enemy_stats[enemy].speed, enemy_stats[enemy].exp, enemy_stats[enemy].coins, enemy_stats[enemy].coin_rate,
                                         enemy_stats[enemy].item_chance, enemy_stats[enemy].item_type, enemy_stats[enemy].rare_item_chance, enemy_stats[enemy].rare_item_type, enemy_stats[enemy].level])
            #Appends data to filler array if it's a "filler" enemy (one used in bosses that only exists for spectacle)
            else:
                filler_stats_rand.append([enemy, enemy_stats[enemy].hp, enemy_stats[enemy].power, enemy_stats[enemy].defense,
                                         enemy_stats[enemy].speed, enemy_stats[enemy].exp, enemy_stats[enemy].coins, enemy_stats[enemy].coin_rate,
                                         enemy_stats[enemy].item_chance, enemy_stats[enemy].item_type, enemy_stats[enemy].rare_item_chance, enemy_stats[enemy].rare_item_type, enemy_stats[enemy].level])

    #Logic for real world enemies
    if settings[1][0] == 0 and settings[1][1] == 0:
        enemy_logic = [[13], [18, 15, 5, -1, 15, 6], [25, 15, 0], [27, 15, 0], [29, 15, 0],
                       [38, 15, 16], [39, 15, 16], [41, 15, 16, 5, -1, 15, 16, 17, 2],
                       [58, 1], [59, 1], [60, 23, 1, -1, 1, 5], [61, 23, 1, 4, 6, -1, 1, 5],
                       [68, 15, 16, 1, -1, 15, 16, 5], [69, 15, 16, 1, -1, 15, 16, 5], [70, 15, 16, 1, -1, 15, 16, 5],
                       [71, 15, 16, 1, -1, 15, 16, 5], [85, 15, -1, 1, 4, 5], [86, 15, -1, 1, 4, 5], [87, 15, -1, 1, 4, 5],
                       [88, 15, -1, 1, 4, 5], [89, 15, -1, 1, 4, 5], [90, 1, 4, 5], [91, 15, 16, 2, 4], [92, 15], [93, 15],
                       [94, 15, 16, 5], [100, 15, 1, 3, 5], [101, 15, 1, 5], [102, 15, 1, 5], [104, 15, 1, 5],
                       [106, 15, 1, 5], [113, 15, 27, 1, 5], [115, 15, 27, 1, 5],
                       [116, 15, 27, 1, 5], [117, 15, 27, 1, 4, 5], [118, 15, 27, 1, 4, 5], [119, 15, 27, 1, 4, 5], [120, 15, 27, 1, 4, 5],]
    elif settings[1][0] != 0 and settings[1][1] != 0:
        enemy_logic = [[13], [18, 15, 5, -1, 15, 6], [25, 15, 0], [27, 15, 0], [29, 15, 0],
                       [38, 15, 16], [39, 15, 16], [41, 15, 16, 17, 2],
                       [58], [59, 23], [60, 23], [61, 23, 4, 6],
                       [68, 15, 16], [69, 15, 16], [70, 15, 16],
                       [71, 15, 16], [85, 15, -1, 23, 4, 5], [86, 15, -1, 23, 4, 5], [87, 15, -1, 23, 4, 5],
                       [88, 15, -1, 23, 4, 5], [89, 15, -1, 23, 4, 5], [90, 23, 4, 5], [91, 15, 16, 2, 4], [92, 15], [93, 15],
                       [94, 15, 16, 17, 18, 19, 20, 21, 5], [100, 15, 3, 5], [101, 15, 5], [102, 15, 5], [104, 15, 5],
                       [106, 15, 5], [113, 15, 27, 5], [115, 15, 27, 5],
                       [116, 15, 27, 5], [117, 15, 27, 4, 5], [118, 15, 27, 4, 5], [119, 15, 27, 4, 5], [120, 15, 27, 4, 5],]
    elif settings[1][0] == 1:
        enemy_logic = [[13], [18, 15, 5, -1, 15, 6], [25, 15, 0], [27, 15, 0], [29, 15, 0],
                       [38, 15, 16], [39, 15, 16], [41, 15, 16, 5, -1, 15, 16, 17, 2],
                       [58], [59], [60, 23, -1, 5], [61, 23, 4, 6, -1, 5],
                       [68, 15, 16], [69, 15, 16], [70, 15, 16],
                       [71, 15, 16], [85, 15, -1, 4, 5], [86, 15, -1, 4, 5], [87, 15, -1, 4, 5],
                       [88, 15, -1, 4, 5], [89, 15, -1, 4, 5], [90, 4, 5], [91, 15, 16, 2, 4], [92, 15], [93, 15],
                       [94, 15, 16, 5], [100, 15, 3, 5], [101, 15, 5], [102, 15, 5], [104, 15, 5],
                       [106, 15, 5], [113, 15, 27, 5], [115, 15, 27, 5],
                       [116, 15, 27, 5], [117, 15, 27, 4, 5], [118, 15, 27, 4, 5], [119, 15, 27, 4, 5], [120, 15, 27, 4, 5],]
    else:
        enemy_logic = [[13], [18, 15, 5, -1, 15, 6], [25, 15, 0], [27, 15, 0], [29, 15, 0],
                       [38, 15, 16], [39, 15, 16], [41, 15, 16, 17, 2],
                       [58, 1], [59, 23, 1], [60, 23, 1], [61, 23, 1, 4, 6],
                       [68, 15, 16, 1, -1, 15, 16, 5], [69, 15, 16, 1, -1, 15, 16, 5], [70, 15, 16, 1, -1, 15, 16, 5],
                       [71, 15, 16, 1, -1, 15, 16, 5], [85, 15, -1, 23, 1, 4, 5], [86, 15, -1, 23, 1, 4, 5], [87, 15, -1, 23, 1, 4, 5],
                       [88, 15, -1, 23, 1, 4, 5], [89, 15, -1, 23, 1, 4, 5], [90, 23, 1, 4, 5], [91, 15, 16, 2, 4], [92, 15], [93, 15],
                       [94, 15, 16, 17, 18, 19, 20, 21, 5], [100, 15, 1, 3, 5], [101, 15, 1, 5], [102, 15, 1, 5], [104, 15, 1, 5],
                       [106, 15, 1, 5], [113, 15, 27, 1, 5], [115, 15, 27, 1, 5],
                       [116, 15, 27, 1, 5], [117, 15, 27, 1, 4, 5], [118, 15, 27, 1, 4, 5], [119, 15, 27, 1, 4, 5], [120, 15, 27, 1, 4, 5],]

    #Logic for dream world enemies
    if settings[1][0] == 0 and settings[1][1] == 0:
        dream_enemy_logic = [[19], [21], [31, 15, 6], [33, 15, 6], [35, 15, 6], [45, 15, 16, 6], [46, 15, 16, 6], [47, 15, 16, 17, 6, -1, 15, 16, 5, 6],
                             [49, 15, 22, 6], [50, 15, 22, 6], [64, 23, 1, 6, -1, 1, 5, 6], [65, 23, 1, 4, 6, 10, -1, 1, 3, 5, 6, 10],
                             [66, 23, 1, 4, 6, 10, -1, 1, 3, 5, 6, 10], [67, 23, 1, 4, 6, 10, -1, 1, 3, 5, 6, 10],
                             [72, 15, 16, 1, 6, -1, 15, 16, 5, 6], [73, 15, 16, 1, 6, -1, 15, 16, 5, 6],
                             [74, 15, 16, 24, 1, 6, -1, 15, 16, 24, 5, 6], [75, 15, 16, 24, 1, 6, -1, 15, 16, 24, 5, 6],
                             [76, 15, 16, 24, 25, 1, 6, -1, 15, 16, 24, 25, 5, 6], [77, 15, 16, 1, 6, -1, 15, 16, 5, 6],
                             [78, 15, 16, 1, 6, -1, 15, 16, 5, 6], [84, 6], [98, 22, 1, 2, 4, 5, 6], [99, 22, 1, 2, 4, 5, 6],
                             [110, 15, 1, 3, 5, 6], [111, 15, 1, 3, 5, 6], [112, 15, 1, 2, 3, 5, 6],  [121, 15, 27, 1, 5, 6],
                             [122, 15, 27, 1, 4, 5, 6], [123, 15, 27, 1, 4, 5, 6], [124, 15, 27, 1, 5, 6], [125, 15, 27, 1, 5, 6], [133, 15, 27, 1, 4, 5, 6],]
    elif settings[1][0] == 1 and settings[1][1] == 1:
        dream_enemy_logic = [[19], [21, 15, 6], [31, 15, 6], [33, 15, 6], [35, 15, 6], [45, 15, 16, 6], [46, 15, 16, 6], [47, 15, 16, 17, 6],
                             [49, 15, 22, 6], [50, 15, 22, 6], [64, 23, 3, 6, -1, 23, 5, 6], [65, 23, 4, 6, 10],
                             [66, 23, 4, 6, 10], [67, 23, 4, 6, 10],
                             [72, 15, 16, 6], [73, 15, 16, 6],
                             [74, 15, 16, 24, 6], [75, 15, 16, 24, 6],
                             [76, 15, 16, 24, 25, 6], [77, 15, 16, 6],
                             [78, 15, 16, 6], [84, 6], [98, 22, 2, 4, 5, 6], [99, 22, 2, 4, 5, 6],
                             [110, 15, 3, 5, 6], [111, 15, 3, 5, 6], [112, 15, 2, 3, 5, 6],  [121, 15, 27, 5, 6],
                             [122, 15, 27, 4, 5, 6], [123, 15, 27, 4, 5, 6], [124, 15, 27, 5, 6], [125, 15, 27, 5, 6], [133, 15, 27, 4, 5, 6],]
    elif settings[1][0] == 1:
        dream_enemy_logic = [[19], [21], [31, 15, 6], [33, 15, 6], [35, 15, 6], [45, 15, 16, 6], [46, 15, 16, 6], [47, 15, 16, 17, 6, -1, 15, 16, 5, 6],
                             [49, 15, 22, 6], [50, 15, 22, 6], [64, 23, 6, -1, 5, 6], [65, 23, 4, 6, 10, -1, 3, 5, 6, 10],
                             [66, 23, 4, 6, 10, -1, 3, 5, 6, 10], [67, 23, 4, 6, 10, -1, 3, 5, 6, 10],
                             [72, 15, 16, 6], [73, 15, 16, 6],
                             [74, 15, 16, 24, 6], [75, 15, 16, 24, 6],
                             [76, 15, 16, 24, 25, 6], [77, 15, 16, 6],
                             [78, 15, 16, 6], [84, 6], [98, 22, 2, 4, 5, 6], [99, 22, 2, 4, 5, 6],
                             [110, 15, 3, 5, 6], [111, 15, 3, 5, 6], [112, 15, 2, 3, 5, 6],  [121, 15, 27, 5, 6],
                             [122, 15, 27, 4, 5, 6], [123, 15, 27, 4, 5, 6], [124, 15, 27, 5, 6], [125, 15, 27, 5, 6], [133, 15, 27, 4, 5, 6],]
    else:
        dream_enemy_logic = [[19], [21], [31, 15, 6], [33, 15, 6], [35, 15, 6], [45, 15, 16, 6], [46, 15, 16, 6], [47, 15, 16, 17, 6, -1, 15, 16, 5, 6],
                             [49, 15, 22, 6], [50, 15, 22, 6], [64, 23, 1, 6], [65, 23, 1, 4, 6, 10],
                             [66, 23, 1, 4, 6, 10], [67, 23, 1, 4, 6, 10],
                             [72, 15, 16, 1, 6, -1, 15, 16, 5, 6], [73, 15, 16, 1, 6, -1, 15, 16, 5, 6],
                             [74, 15, 16, 24, 1, 6, -1, 15, 16, 24, 5, 6], [75, 15, 16, 24, 1, 6, -1, 15, 16, 24, 5, 6],
                             [76, 15, 16, 24, 25, 1, 6, -1, 15, 16, 24, 25, 5, 6], [77, 15, 16, 1, 6, -1, 15, 16, 5, 6],
                             [78, 15, 16, 1, 6, -1, 15, 16, 5, 6], [84, 6], [98, 22, 1, 2, 4, 5, 6], [99, 22, 1, 2, 4, 5, 6],
                             [110, 15, 1, 3, 5, 6], [111, 15, 1, 3, 5, 6], [112, 15, 1, 2, 3, 5, 6],  [121, 15, 27, 1, 5, 6],
                             [122, 15, 27, 1, 4, 5, 6], [123, 15, 27, 1, 4, 5, 6], [124, 15, 27, 1, 5, 6], [125, 15, 27, 1, 5, 6], [133, 15, 27, 1, 4, 5, 6],]

    #Logic for bosses
    boss_logic = [[17, 14], [30, 15], [42, 15, 16, 17, 18, 19, 20, 21], [62, 23, 1, 4, 6, -1, 1, 5],
                  [95, 15, 22, 5], [96, 15, 22, 5], [107, 15, 1, 2, 4, 5, 6], [108, 15, 1, 2, 4, 5, 6],]

    #Logic for dream world bosses
    dream_boss_logic = [[23], [36, 15, 6], [52, 15, 22, 6], [79, 15, 16, 24, 25, 26, 1, 4, 6, -1, 15, 16, 24, 25, 26, 4, 5, 6],
                        [80, 15, 16, 24, 25, 26, 1, 4, 6, -1, 15, 16, 24, 25, 26, 4, 5, 6], [81, 15, 16, 24, 25, 26, 1, 4, 6, -1, 15, 16, 24, 25, 26, 4, 5, 6],
                        [126, 15, 27, 1, 5, 6], [127, 15, 27, 1, 4, 5, 6], [128, 15, 27, 1, 4, 5, 6], [129, 15, 27, 1, 4, 5, 6], [130, 15, 27, 1, 4, 5, 6],
                        [131, 15, 27, 1, 4, 5, 6], [137, 15, 27, 1, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],]

    #Logic for "filler" enemies
    filler_logic = [[37, 15, 6], [57, 15, 22, 6], [82, 15, 16, 24, 25, 26, 1, 4, 6, -1, 15, 16, 24, 25, 26, 4, 5, 6],
                    [109, 15, 1, 2, 3, 5, 6], [138, 15, 27, 1, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],]

    #Initializes the item pool
    item_pool = []

    # Creates an item_data array with all the blocks and bean spots
    item_locals = []
    with (
        code_bin_path.open('rb+') as code_bin,
        fs_std_romfs_path(FMAPDAT_PATH, data_dir=input_folder).open('rb+') as fmapdat,
    ):
        # Updates the collision for Nerfed Ball Hop
        if settings[1][1] == 1:
            spot = [0x281A96C, 0x281A974, 0x281A97C, 0x281A984, 0x281A9A4, 0x281A9AC, 0x281A9B4, 0x281A9BC, 0x281AD24,
                    0x281AD2C, 0x281AD34, 0x281AD3C, 0x2B92B10, 0x2B92B18, 0x2B92B20, 0x2B92B80, 0x2B92B88, 0x2B92B90,
                    0x2B92BB8, 0x2B92BC0, 0x2B92BC8, 0x2B92BF0, 0x2B92BF8, 0x2B92C00, 0x2B92C08, 0x2B92C28, 0x2B92C30,
                    0x2B92C38, 0x2B92C40, 0x2B92C60, 0x2B92C68, 0x2B92C70, 0x2B92C78, 0x2B92C98, 0x2B92CA0, 0x2B92CA8,
                    0x2B92CB0, 0x2B92CD0, 0x2B92CD8, 0x2B92CE0, 0x2B92CE8, 0x2B92D08, 0x2B92D10, 0x2B92D18, 0x2B92D20,
                    0x2B92D40, 0x2B92D48, 0x2B92D50, 0x2B92D58, 0x2B92F00, 0x2B92F08, 0x2B92F10, 0x2B93050, 0x2B93058,
                    0x2B93060, 0x2B93068, 0x2B932B8, 0x2B932C0, 0x2B932C8, 0x2B932D0, 0x2B932F0, 0x2B932F8, 0x2B93300,
                    0x2B93308, 0x2B93360, 0x2B93368, 0x2B93370, 0x2B93478, 0x2B93480, 0x2B93488, 0x2B93490, 0x2B934B0,
                    0x2B934B8, 0x2B934C0, 0x2B934C8, 0x2B934E8, 0x2B934F0, 0x2B934F8, 0x2B93500, 0x2B93520, 0x2B93528,
                    0x2B93530, 0x2B93538, 0x2B93558, 0x2B93560, 0x2B93568, 0x2B93570, 0x2B93590, 0x2B93598, 0x2B935A0,
                    0x2B935A8, 0x2B936E0, 0x2B936E8, 0x2B936F0, 0x2B936F8, 0x2B93B08, 0x2B93B10, 0x2B93B18, 0x2B93B20]
            for i in range(len(spot)):
                fmapdat.seek(spot[i])
                fmapdat.write(0x78.to_bytes())
            #with open("Dozing Edit.bin", 'rb') as new_model:
            #    fmapdat.seek(0)
            #    temp = bytearray(fmapdat.read())
            #    test = bytearray(new_model.read())
            #    temp[0x281C898:0x281C898+0x72A7B] = (test[:0x72A7B])
            #    temp[0x281C898+0x72A7B:0x281C898+0x72A7B] = test[0x72A7C:]
            #    fmapdat.seek(0)
            #    fmapdat.write(temp)
            #    fix_offsets(fmapdat, code_bin, 0x5D, len(test), 12)
            #del temp
            #del test
            fmapdat.seek(0)
        version_pair = determine_version_from_code_bin(code_bin)
        block_id = 3000
        rooms_to_init = [0x001, 0x004, 0x005, 0x010, 0x011, 0x012, 0x013, 0x014, 0x017, 0x019, 0x062]
        for room in range(NUMBER_OF_ROOMS):
            code_bin.seek(FMAPDAT_REAL_WORLD_OFFSET_TABLE_LENGTH_ADDRESS[version_pair] + 16 + room*8)
            fmapdat_chunk_offset, fmapdat_chunk_len = struct.unpack('<II', code_bin.read(4 * 2))
            fmapdat.seek(fmapdat_chunk_offset + 7 * 4 * 2)
            treasure_data_offset, treasure_data_len = struct.unpack('<II', fmapdat.read(4 * 2))
            treasure_data_absolute_offset = fmapdat_chunk_offset + treasure_data_offset
            #print(room)
            try:
                check_room = rooms_to_init.index(room)
                new_data = []
                fevent_manager = FEventScriptManager(input_folder)
                script = fevent_manager.parsed_script(room, 0)
                fmapdat.seek(0)
                temp = bytearray(fmapdat.read())
                if room == 0x001:
                    #Adds blocks in place of attack piece blocks and ability cutscenes
                    fmapdat.seek(0)
                    new_block = [0x10, 0x0, int(((script.header.triggers[4][0] % 0x10000) + (script.header.triggers[4][1] % 0x10000))/2) - 0x20,
                                 script.header.triggers[4][4] % 0x10000 + 0x55,
                                 int(((script.header.triggers[4][0] // 0x10000) + (script.header.triggers[4][1] // 0x10000)) / 2), block_id]
                    block_id += 1
                    for b in range(len(new_block)):
                        temp[treasure_data_absolute_offset+b*2:treasure_data_absolute_offset+b*2] = new_block[b].to_bytes(2, "little")
                    new_data.append([])
                elif room == 0x012:
                    fmapdat.seek(0)
                    new_block = [0x10, 0x0, int(((script.header.triggers[1][0] % 0x10000) + (script.header.triggers[1][1] % 0x10000))/2),
                                 script.header.triggers[1][5] % 0x10000 + 0x55,
                                 int(((script.header.triggers[1][0] // 0x10000) + (script.header.triggers[1][1] // 0x10000)) / 2), block_id]
                    block_id += 1
                    for b in range(len(new_block)):
                        temp[treasure_data_absolute_offset+b*2:treasure_data_absolute_offset+b*2] = new_block[b].to_bytes(2, "little")
                    new_data.append([])
                for a in range(len(script.header.actors)):
                    if script.header.actors[a][5] // 0x1000 == 0x748 and script.header.actors[a][5] % 0x100 == 0x43:
                        fmapdat.seek(0)
                        new_block = [0x10, 0x0, script.header.actors[a][0] % 0x10000, script.header.actors[a][0] // 0x10000,
                                     script.header.actors[a][0] % 0x10000, block_id]
                        block_id += 1
                        for b in range(len(new_block)):
                            temp[treasure_data_absolute_offset+b*2:treasure_data_absolute_offset+b*2] = new_block[b].to_bytes(2, "little")
                        new_data.append([])
                fmapdat.write(temp)
                if check_room < len(rooms_to_init) - 1:
                    fix_offsets(fmapdat, code_bin, room, len(new_data)*12 + treasure_data_len, 7, rooms_to_init[check_room + 1] + 1)
                else:
                    fix_offsets(fmapdat, code_bin, room, len(new_data)*12 + treasure_data_len, 7, 0x316)
                fmapdat.seek(fmapdat_chunk_offset + 7 * 4 * 2)
                treasure_data_offset, treasure_data_len = struct.unpack('<II', fmapdat.read(4 * 2))
            except ValueError:
                room = room
            fmapdat.seek(treasure_data_absolute_offset)
            treasure_data = fmapdat.read(treasure_data_len)
            for treasure_index, treasure in enumerate(itertools.batched(treasure_data, 12, strict=True)):
                treasure_type, item_id, x, y, z, treasure_id = struct.unpack('<HHHHHH', bytes(treasure))
                if (room != 0x00D and room != 0x015 and room != 0x016 and room != 0x01D and room != 0x037 and room != 0x04E and room != 0x052 and
                        room != 0x054 and treasure_type % 0x100 != 0x16 and treasure_type % 0x100 != 0x17
                        and treasure_id != 157 and treasure_id != 161):
                    item_locals.append([room, treasure_data_absolute_offset + treasure_index * 12, treasure_type, x, y, z, treasure_id])
                    if room < 0x10D:  # TODO
                        item_pool.append([treasure_type, item_id])

    #for item in item_locals:
    #   print(str(item) + "\n")

    item_logic_chunk = [[], [], [], [], [], [], [], [], [], [], [], []]
    #Logic for every single block and bean spot (The numbers after the ID point to their spots in the ability info)
    item_logic_chunk[0] = [[52, 15, 5], [53, 15, 5], [3000, 15], [54, 15], [55, 15, 0, -1, 15, 5], [56, 15, 0], [57, 15, 0], [58, 15], [59, 15, 2], [60, 15, 2],
                  [61, 15, 0, 2], [2388, 15, 2], [62, 15, 0], [63, 15, 0], [64, 15, 0], [65, 15, 0], [3004, 15, 0], [3003, 15, 0], [3002, 15, 0], [3001, 15, 0],
                  [66, 15, 0], [67, 15, 2, 3, -1, 15, 2, 5], [3008, 15, 0], [3007, 15, 0], [3006, 15, 0], [3005, 15, 0], [68, 15, 0], [69, 15, 0], [70, 15, 0],
                  [71, 15, 0], [72, 15], [73, 15], [74, 15, 16, 1], [75, 15, 16, 2], [76, 15, 2], [77, 15, 2],
                  [78, 15, 0], [79, 15], [80, 15], [81, 15], [82, 15, 2], [83, 15, 2], [84, 15, 2], [85, 15, 2, 3, 0, 15, 2, 5], [86, 15, 4],
                  [87, 15], [88, 15], [89, 15, 4], [90, 15, 2], [91, 15, 0], [92, 15, 0, 1, 5, -1, 15, 0, 1, 3], [2389, 15, 0, 4, 5], [94, 15, 0, 4, 5],
                  [95, 15, 0, 4, 5], [96, 15, 0, 4, 5], [97, 15, 0, 4, 5], [98, 15, 0, 4, 5], [99, 15, 0, 2, 4, 5], [100, 15, 0, 2, 4, 5],
                  [101, 15, 0, 2, 4, 5], [102, 15, 0, 2, 4, 5], [103, 15], [104, 15], [107, 15], [2390, 15, 0], [2391, 15, 0],
                  [108, 15, 0, 2], [109, 15, 0, 2], [110, 15, 0, 2], [111, 15, 0, 2], [112, 15, 0], [113, 15, 0], [114, 15, 0]]
    if settings[1][1] != 1:
        item_logic_chunk[1] = [[253, 15, 16, 2], [3010, 15, 16, 1, 5], [3009, 15, 16, 17, 1, -1, 15, 16, 1, 5], [271, 15, 16, 17, 2, -1, 15, 16, 2, 5], [272, 15, 16, 17, 2, -1, 15, 16, 2, 5], [273, 15, 16, 17, 2, -1, 15, 16, 2, 5],
                  [274, 15, 16, 17, 2, -1, 15, 16, 2, 5], [275, 15, 16, 17, 2, -1, 15, 16, 2, 5], [3011, 15, 16, 17, 1, -1, 15, 16, 1, 5], [276, 15, 16, 17, 2, -1, 15, 16, 2, 5], [969, 15, 16, 17, 2, -1, 15, 16, 2, 5],
                  [277, 15, 16, 17, -1, 15, 16, 5], [278, 15, 16, 17, -1, 15, 16, 5], [3015, 15, 16, 2], [3014, 15, 16, 2], [3013, 15, 16, 2], [3012, 15, 16], [279, 15, 16, 2], [281, 15, 16, 2],
                  [282, 15, 16, 1], [283, 15, 16, 17, -1, 15, 16, 5], [284, 15, 16, 2], [3017, 15, 16, 17, 1, -1, 15, 16, 1, 5], [3016, 15, 16, 17, 1, -1, 15, 16, 1, 5],
                  [285, 15, 16, 17, 2, -1, 15, 16, 2, 5], [286, 15, 16, 17, 2, -1, 15, 16, 2, 5],
                  [287, 15, 16, 17, 2, -1, 15, 16, 2, 5, -1, 15, 16, 17, 1, -1, 15, 16, 1, 5], [288, 15, 16, 17, 2, -1, 15, 16, 2, 5, -1, 15, 16, 17, 1, -1, 15, 16, 1, 5],
                  [289, 15, 16, 17, 2, -1, 15, 16, 2, 5, -1, 15, 16, 17, 1, -1, 15, 16, 1, 5], [290, 15, 16, 17, 2, -1, 15, 16, 2, 5, -1, 15, 16, 17, 1, -1, 15, 16, 1, 5],
                  [291, 15, 16, 17, 2, -1, 15, 16, 2, 5, -1, 15, 16, 17, 1, -1, 15, 16, 1, 5], [3019, 15, 16, 17, 1, -1, 15, 16, 1, 5], [3018, 15, 16, 17, 1, -1, 15, 16, 1, 5], [292, 15, 16, 17, 2, -1, 15, 16, 2, 5],
                  [293, 15, 16, 17, 2, -1, 15, 16, 2, 5, -1, 15, 16, 17, 1, -1, 15, 16, 1, 5], [294, 15, 16, 17, 2, -1, 15, 16, 2, 5],
                  [295, 15, 16, 17, 2, -1, 15, 16, 2, 5], [296, 15, 16, 17, 2, -1, 15, 16, 2, 5], [2373, 15, 16, 17, 2, -1, 15, 16, 2, 5, -1, 15, 16, 17, 1, -1, 15, 16, 1, 5],
                  [3021, 15, 16, 17, 1, -1, 15, 16, 1, 5], [3020, 15, 16, 17, 1, -1, 15, 16, 1, 5], [303, 15, 16, 17, 1, -1, 15, 16, 1, 5], [304, 15, 16, 17, 1, -1, 15, 16, 1, 5],
                  [305, 15, 16, 17, 1, -1, 15, 16, 1, 5], [306, 15, 16, 17, 1, -1, 15, 16, 1, 5],
                  [115, 15, 0], [116, 15, 0, 5], [3024, 15, 16, 17, 1, -1, 15, 16, 1, 5], [3023, 15, 16, 17, 1, -1, 15, 16, 1, 5],
                  [3022, 15, 16, 17, 1, -1, 15, 16, 1, 5], [307, 15, 16, 17, 2, -1, 15, 16, 2, 5],
                  [308, 15, 16, 1, 5, -1, 15, 16, 2, 5], [309, 15, 16, 17, 2, -1, 15, 16, 2, 5],
                  [310, 15, 16, 17, 2, -1, 15, 16, 2, 5, -1, 15, 16, 17, 1, -1, 15, 16, 1, 5],
                  [311, 15, 16, 17, 2, -1, 15, 16, 2, 5, -1, 15, 16, 17, 1, -1, 15, 16, 1, 5],
                  [312, 15, 16, 17, 1, -1, 15, 16, 1, 5], [2374, 15, 16, 1, 5, -1, 15, 16, 2, 5],
                  [313, 15, 16, 3, 5], [314, 15, 16, 3, 5], [15], [16, 2]]
    else:
        item_logic_chunk[1] = [[253, 15, 16, 2], [3010, 15, 16, 17, 1, 5], [3009, 15, 16, 17, 1], [271, 15, 16, 17, 2], [272, 15, 16, 17, 2], [273, 15, 16, 17, 2],
                      [274, 15, 16, 17, 2], [275, 15, 16, 17, 2], [3011, 15, 16, 17, 1], [276, 15, 16, 17, 2], [969, 15, 16, 17, 2],
                      [277, 15, 16, 17], [278, 15, 16, 17], [3015, 15, 16, 2], [3014, 15, 16, 2], [3013, 15, 16, 2], [3012, 15, 16],
                      [279, 15, 16, 2], [281, 15, 16, 2], [282, 15, 16, 1], [283, 15, 16, 17], [284, 15, 16, 2], [3017, 15, 16, 17, 1], [3016, 15, 16, 17, 1],
                      [285, 15, 16, 17, 2], [286, 15, 16, 17, 2], [287, 15, 16, 17, 1], [288, 15, 16, 17, 1],
                      [289, 15, 16, 17, 1], [290, 15, 16, 17, 1], [291, 15, 16, 17, 1], [3019, 15, 16, 17, 1], [3018, 15, 16, 17, 1], [292, 15, 16, 17, 2],
                      [293, 15, 16, 17, 1], [294, 15, 16, 17, 2], [295, 15, 16, 17, 2], [296, 15, 16, 17, 2], [2373, 15, 16, 17, 1], [3021, 15, 16, 17, 1], [3020, 15, 16, 17, 1],
                      [303, 15, 16, 17, 1], [304, 15, 16, 17, 1], [305, 15, 16, 17, 1], [306, 15, 16, 17, 1],
                      [115, 15, 0], [116, 15, 0, 5], [3024, 15, 16, 17, 1], [3023, 15, 16, 17, 1], [3022, 15, 16, 17, 1], [307, 15, 16, 17, 2],
                      [308, 15, 16, 17, 1, 5, -1, 15, 16, 17, 2, 5], [309, 15, 16, 17, 2],
                      [310, 15, 16, 17, 2, -1, 15, 16, 17, 1], [311, 15, 16, 17, 2, -1, 15, 16, 17, 1],
                      [312, 15, 16, 17, 1], [2374, 15, 16, 17, 1, 5, -1, 15, 16, 17, 2, 5], [313, 15, 16, 17, 3, 5], [314, 15, 16, 17, 3, 5], [15], [16, 2]]

    item_logic_chunk[2] = [[119, 15, 6], [121, 15, 6], [123, 15, 6], [125, 15, 6], [127, 15, 6], [129, 15, 6], [131, 15, 6], [132, 15, 6], [2392, 15, 6],
                  [141, 15, 6], [142, 15, 6], [2393, 15, 6], [144, 15, 6], [145, 15, 6], [146, 15, 6], [147, 15, 6], [152, 15, 6], [2394, 15, 6], [2395, 15, 6], [151, 15, 6]]

    if settings[1][0] != 1:
        item_logic_chunk[3] = [[1511, 15, 3], [1512, 15, 2, 3], [1513, 15, 2, 3], [1514, 15, 22], [1515, 15, 22, 2], [1516, 15, 22, 2, 5],
                  [1517, 15, 22, 2], [1518, 15, 22, 2], [1519, 15, 22], [1520, 15, 22, 2], [1521, 15, 22, 2], [1522, 15, 22, 1], [1523, 15, 22],
                  [1524, 15, 22, 1], [1525, 15, 22, 2], [1549, 15, 16, 1], [1550, 15, 16], [1551, 15, 16, 1], [1552, 15, 16, 2], [1527, 15, 22],
                  [1528, 15, 22], [1529, 15, 22], [1530, 15, 22], [1531, 15, 22], [1532, 15, 22], [1553, 15, 16, 1], [1554, 15, 16, 1, 3],
                  [2331, 15, 16, 1, 3], [2332, 15, 16, 1, 3], [1562, 15, 16, 1, 3], [1539, 15, 22, 3], [1540, 15, 22],
                  [1541, 15, 22], [1542, 15, 22], [1566, 15, 16, 1, 3,], [1567, 15, 16, 1, 3], [1568, 15, 16, 1, 3],
                  [1569, 15, 16, 1, 3], [1570, 15, 16, 1, 3, 5], [1571, 15, 16, 1, 2, 3],
                  [1572, 15, 16, 1, 2, 3], [1543, 15, 16, 1], [1544, 15, 16, 1], [1545, 15, 16, 1], [2398, 15, 16, 1], [2399, 15, 16],
                  [1547, 15, 16], [1548, 15, 16, 2], [1555, 15, 16, 1, 4], [1556, 15, 16, 1, 4], [1557, 15, 16, 1, 2, 4],
                  [2400, 15, 16, 1, 2, 4], [1558, 15, 16, 1, 3], [1559, 15, 16, 1, 3], [1560, 15, 16, 1, 2, 3],
                  [1561, 15, 16, 1, 2, 3], [2401, 15, 16, 1, 2, 3], [1563, 15, 16, 1, 4, -1, 15, 16, 3, 5],
                  [1564, 15, 16, 1, 4, -1, 15, 16, 3, 5,], [1565, 15, 16, 1, 2, 4, -1, 15, 16, 2, 4, 5],
                  [988, 15, 16, 1, 2, 4, -1, 15, 16, 2, 3, 5]]
    else:
        item_logic_chunk[3] = [[1511, 15, 3], [1512, 15, 2, 3], [1513, 15, 2, 3], [1514, 15, 22], [1515, 15, 22, 2],
                      [1516, 15, 22, 2, 5],
                      [1517, 15, 22, 2], [1518, 15, 22, 2], [1519, 15, 22], [1520, 15, 22, 2], [1521, 15, 22, 2],
                      [1522, 15, 22, 1], [1523, 15, 22],
                      [1524, 15, 22, 1], [1525, 15, 22, 2], [1549, 15, 16, 1], [1550, 15, 16], [1551, 15, 16],
                      [1552, 15, 16, 2], [1527, 15, 22],
                      [1528, 15, 22], [1529, 15, 22], [1530, 15, 22], [1531, 15, 22], [1532, 15, 22], [1553, 15, 16],
                      [1554, 15, 16, 3],
                      [2331, 15, 16, 3], [2332, 15, 16, 3], [1562, 15, 16, 3], [1539, 15, 22, 3], [1540, 15, 22],
                      [1541, 15, 22], [1542, 15, 22], [1566, 15, 16, 3, ], [1567, 15, 16, 3], [1568, 15, 16, 3],
                      [1569, 15, 16, 3], [1570, 15, 16, 3, 5], [1571, 15, 16, 2, 3],
                      [1572, 15, 16, 2, 3], [1543, 15, 16, 1], [1544, 15, 16, 1], [1545, 15, 16, 1], [2398, 15, 16, 1],
                      [2399, 15, 16],
                      [1547, 15, 16], [1548, 15, 16, 2], [1555, 15, 16, 4], [1556, 15, 16, 4], [1557, 15, 16, 2, 4],
                      [2400, 15, 16, 2, 4], [1558, 15, 16, 3], [1559, 15, 16, 3], [1560, 15, 16, 2, 3],
                      [1561, 15, 16, 2, 3], [2401, 15, 16, 2, 3], [1563, 15, 16, 4, -1, 15, 16, 3, 5],
                      [1564, 15, 16, 4, -1, 15, 16, 3, 5, ], [1565, 15, 16, 2, 4, -1, 15, 16, 2, 4, 5],
                      [988, 15, 16, 2, 4, -1, 15, 16, 2, 3, 5]]

    item_logic_chunk[4] = [[7], [8], [9], [10], [11], [12], [13], [14], [17], [18, 2], [19], [20, 2], [21, 2], [22, 2], [23, 2]]

    if settings[1][1] != 1:
        item_logic_chunk[5] = [[254, 15, 16, 2], [255, 15, 16, 17, 18, 19, 20, 21, 1, 2, -1, 15, 16, 5], [256, 15, 16], [257, 15, 16], [258, 15, 16],
                  [259, 15, 16, 17, 2, -1, 15, 16, 2, 5], [260, 15, 16, 17, -1, 15, 16, 5], [261, 15, 16, 5], [262, 15, 16, 5],
                  [263, 15, 16, 2, 5], [264, 15, 16, 2, 5], [3025, 15, 16], [268, 15, 16, 2], [269, 15, 16], [270, 15, 16],]
    else:
        item_logic_chunk[5] = [[254, 15, 16, 2], [255, 15, 16, 17, 18, 19, 20, 21, 1], [256, 15, 16], [257, 15, 16], [258, 15, 16],
                      [259, 15, 16, 17, 2], [260, 15, 16, 17], [261, 15, 16, 5], [262, 15, 16, 5],
                      [263, 15, 16, 2, 5], [264, 15, 16, 2, 5], [3025, 15, 16], [268, 15, 16, 2], [269, 15, 16], [270, 15, 16],]

    if settings[1][0] != 1 and settings[1][1] != 1:
        item_logic_chunk[6] = [[1573, 1], [1574, 1], [1575, 1], [1576, 23, 1, -1, 1, 5], [1577, 23, 1, -1, 1, 5], [1578, 23, 1, 3, -1, 1, 5], [1579, 23, 1, 2, 3, -1, 1, 2, 3, 5],
                      [1580, 23, 1, 2, 3, -1, 1, 2, 3, 5], [1581, 23, 1, -1, 1, 5], [1582, 23, 1, -1, 1, 5], [1583, 23, 1, 2, 4, -1, 1, 2, 4, 5], [2402, 23, 1, 2, 4, -1, 1, 2, 4, 5],
                      [1584, 23, 1, -1, 1, 5], [1585, 23, 1, 2, 3, -1, 1, 2, 3, 5], [1586, 23, 1, 3, -1, 1, 5], [1587, 23, 1, 3, -1, 1, 3, 5], [1588, 23, 1, -1, 1, 5],
                      [1589, 23, 1, -1, 1, 5], [1590, 23, 1, -1, 1, 5], [1591, 23, 1, 2, 3, -1, 1, 2, 3, 5], [1592, 23, 1, 3, -1, 1, 3, 5], [2403, 23, 1, 3, -1, 1, 5],
                      [1593, 23, 1, 2, 3, -1, 1, 2, 3, 5], [1594, 23, 1, 2, 3, -1, 1, 2, 3, 5], [1595, 23, 1, 3, 6, -1, 1, 3, 5, 6], [1596, 23, 1, 3, -1, 1, 3, 5],
                      [1597, 23, 1, 3, -1, 1, 3, 5], [1598, 1, 3, 5], [1599, 1, 3, 5], [2333, 23, 1, 3, -1, 1, 3, 5], [1546, 23, 1, 3, -1, 1, 3, 5], [2219, 23, 1, 3, -1, 1, 3, 5],
                      [1600, 23, 1, 2, 3, -1, 1, 2, 3, 5], [1601, 23, 1, 2, 3, -1, 1, 2, 3, 5], [2334, 23, 1, 2, 3, -1, 1, 2, 3, 5], [1602, 23, 1, 4, 6, 8, 10, -1, 1, 4, 5],
                      [1603, 23, 1, 4, 6, 8, 10, -1, 1, 4, 5], [1604, 23, 1, 4, 6, 8, 10, -1, 1, 4, 5, 6], [1605, 23, 1, 4, 6, 8, 10, -1, 1, 4, 5], [1606, 23, 1, 4, 6, 8, 10, -1, 1, 5],
                      [1607, 23, 1, 2, 4, 6, 8, 10, -1, 1, 2, 5], [1608, 23, 1, 4, 6, 8, 10, -1, 1, 4, 5], [1609, 23, 1, 4, 6, 8, 10, -1, 1, 4, 5], [1610, 23, 1, 4, 6, 8, 10, -1, 1, 4, 5],
                      [2359, 23, 1, 2, 4, 6, 8, 10, -1, 1, 2, 4, 5], [2360, 23, 1, 2, 4, 6, 8, 10, -1, 1, 2, 4, 5], [2375, 23, 1, 4, 6, 8, 10, -1, 1, 4, 5], [1611, 1, 4, 5],
                      [1612, 1, 4, 5], [1613, 1, 2, 4, 5], [1614, 23, 1, 4, 6, 8, 10, -1, 1, 4, 5], [1615, 23, 1, 4, 6, 8, 10, -1, 1, 4, 5], [1616, 23, 1, 4, 6, 8, 10, -1, 1, 4, 5],
                      [1617, 23, 1, 4, 6, 8, 10, -1, 1, 4, 5], [1618, 23, 1, 2, 4, 6, 8, 10, -1, 1, 2, 4, 5], [2361, 23, 1, 2, 4, 6, 8, 10, -1, 1, 2, 4, 5], [2362, 1, 3, 5],
                      [1619, 23, 1, 2, 4, 6, 8, 10, -1, 1, 2, 3, 5], [1620, 23, 1, 2, 4, 6, 8, 10, -1, 1, 2, 3, 5], [1621, 1, 3, 5], [2296, 1, 2, 3, 5], [1623, 1, 3, 5],]
    elif settings[1][0] == 1 and settings[1][1] == 1:
        item_logic_chunk[6] = [[1573], [1574], [1575], [1576, 23, 1], [1577, 23], [1578, 23, 3, -1, 23, 5], [1579, 23, 2, 3],
                      [1580, 23, 2, 3], [1581, 23], [1582, 23], [1583, 23, 2, 4], [2402, 23, 2, 4],
                      [1584, 23], [1585, 23, 2, 3], [1586, 23, 3], [1587, 23, 3], [1588, 23],
                      [1589, 23], [1590, 23], [1591, 23, 2, 3], [1592, 23, 3], [2403, 23, 3, -1, 23, 5],
                      [1593, 23, 2, 3], [1594, 23, 2, 3], [1595, 23, 3, 6], [1596, 23, 3],
                      [1597, 23, 3], [1598, 23, 3, 5], [1599, 23, 3, 5], [2333, 23, 3], [1546, 23, 3], [2219, 23, 3],
                      [1600, 23, 2, 3], [1601, 23, 2, 3], [2334, 23, 2, 3], [1602, 23, 4, 6, 8, 10],
                      [1603, 23, 4, 6, 8, 10], [1604, 23, 4, 6, 8, 10], [1605, 23, 4, 6, 8, 10], [1606, 23, 4, 6, 8, 10],
                      [1607, 23, 2, 4, 6, 8, 10], [1608, 23, 4, 6, 8, 10], [1609, 23, 4, 6, 8, 10], [1610, 23, 4, 6, 8, 10],
                      [2359, 23, 2, 4, 6, 8, 10], [2360, 23, 2, 4, 6, 8, 10], [2375, 23, 4, 6, 8, 10], [1611, 4, 5],
                      [1612, 23, 4, 5], [1613, 23, 2, 4, 5], [1614, 23, 4, 6, 8, 10], [1615, 23, 4, 6, 8, 10], [1616, 23, 4, 6, 8, 10],
                      [1617, 23, 4, 6, 8, 10], [1618, 23, 2, 4, 6, 8, 10], [2361, 23, 2, 4, 6, 8, 10], [2362, 23, 3, 5],
                      [1619, 23, 2, 4, 6, 8, 10], [1620, 23, 2, 4, 6, 8, 10], [1621, 23, 3, 5], [2296, 23, 2, 3, 5], [1623, 23, 3, 5],]
    elif settings[1][1] == 1:
        item_logic_chunk[6] = [[1573, 1], [1574, 1], [1575, 1], [1576, 23, 1], [1577, 23, 1], [1578, 23, 1, 3, -1, 1, 23, 5], [1579, 23, 1, 2, 3],
                      [1580, 23, 1, 2, 3], [1581, 23, 1], [1582, 23, 1], [1583, 23, 1, 2, 4], [2402, 23, 1, 2, 4],
                      [1584, 23, 1], [1585, 23, 1, 2, 3], [1586, 23, 1, 3], [1587, 23, 1, 3], [1588, 23, 1],
                      [1589, 23, 1], [1590, 23, 1], [1591, 23, 1, 2, 3], [1592, 23, 1, 3], [2403, 23, 1, 3],
                      [1593, 23, 1, 2, 3], [1594, 23, 1, 2, 3], [1595, 23, 1, 3, 6], [1596, 23, 1, 3],
                      [1597, 23, 1, 3], [1598, 23, 1, 3, 5], [1599, 23, 1, 3, 5], [2333, 23, 1, 3], [1546, 23, 1, 3], [2219, 23, 1, 3],
                      [1600, 23, 1, 2, 3], [1601, 23, 1, 2, 3], [2334, 23, 1, 2, 3], [1602, 23, 1, 4, 6, 8, 10],
                      [1603, 23, 1, 4, 6, 8, 10], [1604, 23, 1, 4, 6, 8, 10], [1605, 23, 1, 4, 6, 8, 10], [1606, 23, 1, 4, 6, 8, 10],
                      [1607, 23, 1, 2, 4, 6, 8, 10], [1608, 23, 1, 4, 6, 8, 10], [1609, 23, 1, 4, 6, 8, 10], [1610, 23, 1, 4, 6, 8, 10],
                      [2359, 23, 1, 2, 4, 6, 8, 10], [2360, 23, 1, 2, 4, 6, 8, 10], [2375, 23, 1, 4, 6, 8, 10], [1611, 23, 1, 4, 5],
                      [1612, 23, 1, 4, 5], [1613, 23, 1, 2, 4, 5], [1614, 23, 1, 4, 6, 8, 10], [1615, 23, 1, 4, 6, 8, 10], [1616, 23, 1, 4, 6, 8, 10],
                      [1617, 23, 1, 4, 6, 8, 10], [1618, 23, 1, 2, 4, 6, 8], [2361, 23, 1, 2, 4, 6, 8, 10], [2362, 23, 1, 3, 5],
                      [1619, 23, 1, 2, 4, 6, 8, 10], [1620, 23, 1, 2, 4, 6, 8, 10], [1621, 23, 1, 3, 5], [2296, 23, 1, 2, 3, 5], [1623, 23, 1, 3, 5],]
    else:
        item_logic_chunk[6] = [[1573], [1574], [1575], [1576, 23, 1, -1, 1, 5], [1577, 23, -1, 5], [1578, 23, 3, -1, 5], [1579, 23, 2, 3, -1, 2, 3, 5],
                      [1580, 23, 2, 3, -1, 2, 3, 5], [1581, 23, -1, 5], [1582, 23, -1, 5], [1583, 23, 2, 4, -1, 2, 4, 5], [2402, 23, 2, 4, -1, 2, 4, 5],
                      [1584, 23, -1, 5], [1585, 23, 2, 3, -1, 2, 3, 5], [1586, 23, 3, -1, 5], [1587, 23, 3, -1, 3, 5], [1588, 23, -1, 5],
                      [1589, 23, -1, 5], [1590, 23, -1, 5], [1591, 23, 2, 3, -1, 2, 3, 5], [1592, 23, 3, -1, 3, 5], [2403, 23, 3, -1, 5],
                      [1593, 23, 2, 3, -1, 2, 3, 5], [1594, 23, 2, 3, -1, 2, 3, 5], [1595, 23, 3, 6, -1, 3, 5, 6], [1596, 23, 3, -1, 3, 5],
                      [1597, 23, 3, -1, 3, 5], [1598, 3, 5], [1599, 3, 5], [2333, 23, 3, -1, 3, 5], [1546, 23, 3, -1, 3, 5], [2219, 23, 3, -1, 3, 5],
                      [1600, 23, 2, 3, -1, 2, 3, 5], [1601, 23, 2, 3, -1, 2, 3, 5], [2334, 23, 2, 3, -1, 2, 3, 5], [1602, 23, 4, 6, 8, 10, -1, 4, 5],
                      [1603, 23, 4, 6, 8, 10, -1, 4, 5], [1604, 23, 4, 6, 8, 10, -1, 4, 5, 6], [1605, 23, 4, 6, 8, 10, -1, 4, 5], [1606, 23, 4, 6, 8, 10, -1, 5],
                      [1607, 23, 2, 4, 6, 8, 10, -1, 2, 5], [1608, 23, 4, 6, 8, 10, -1, 4, 5], [1609, 23, 4, 6, 8, 10, -1, 4, 5], [1610, 23, 4, 6, 8, 10, -1, 4, 5],
                      [2359, 23, 2, 4, 6, 8, 10, -1, 2, 4, 5], [2360, 23, 2, 4, 6, 8, 10, -1, 2, 4, 5], [2375, 23, 4, 6, 8, 10, -1, 4, 5], [1611, 4, 5],
                      [1612, 4, 5], [1613, 2, 4, 5], [1614, 23, 4, 6, 8, 10, -1, 4, 5], [1615, 23, 4, 6, 8, 10, -1, 4, 5], [1616, 23, 4, 6, 8, 10, -1, 4, 5],
                      [1617, 23, 4, 6, 8, 10, -1, 4, 5], [1618, 23, 2, 4, 6, 8, 10, -1, 2, 4, 5], [2361, 23, 2, 4, 6, 8, 10, -1, 2, 4, 5], [2362, 3, 5],
                      [1619, 23, 2, 4, 6, 8, 10, -1, 2, 3, 5], [1620, 23, 2, 4, 6, 8, 10, -1, 2, 3, 5], [1621, 3, 5], [2296, 2, 3, 5], [1623, 3, 5],]

    item_logic_chunk[7] = [[24], [25], [26], [27, 3, -1, 5], [28], [29], [30], [31, 15], [32, 15], [33], [34, 15], [35, 15], [158], [159], [162], [163], [164], [165], [167, 6],
    [168, 6], [169, 6], [171, 6], [173, 6], [175, 6], [177, 6], [1643, 6], [265, 16, 17, 2, -1, 2, 5], [266, 16, 17, 2, -1, 2, 5], [267, 16, 17, -1, 5], [148, 15, 6],]

    if settings[1][1] == 0:
        item_logic_chunk[8] = [[413, 16, 2, 6], [414, 16, 2, 6], [452, 16, 17, 1, 6, -1, 16, 1, 5, 6], [461, 16, 17, 1, 6, -1, 16, 1, 5, 6], [462, 16, 17, 1, 6, -1, 16, 1, 5, 6], [463, 16, 17, 1, 6, -1, 16, 1, 5, 6],
        [464, 16, 17, 2, 6, -1, 16, 2, 5, 6], [450, 16, 17, 2, 6, -1, 16, 2, 5, 6], [486, 16, 17, 2, 6, -1, 16, 2, 5, 6], [512, 16, 17, 18, 19, 20, 21, 6, -1, 16, 5, 6], [513, 16, 17, 18, 19, 20, 21, 6, -1, 16, 5, 6],
        [523, 16, 17, 18, 19, 20, 21, 6, -1, 16, 5, 6], [529, 16, 17, 18, 19, 20, 21, 6, -1, 16, 5, 6], [545, 16, 17, 18, 19, 20, 21, 6, 9, -1, 16, 5, 6, 9], [546, 16, 17, 18, 19, 20, 21, 6, 9, -1, 16, 5, 6, 9],]
    else:
        item_logic_chunk[8] = [[413, 16, 2, 6], [414, 16, 2, 6], [452, 16, 17, 1, 6], [461, 16, 17, 1, 6], [462, 16, 17, 1, 6], [463, 16, 17, 1, 6],
        [464, 16, 17, 2, 6], [450, 16, 17, 2, 6], [486, 16, 17, 2, 6], [512, 16, 17, 18, 19, 20, 21, 6], [513, 16, 17, 18, 19, 20, 21, 6],
        [523, 16, 17, 18, 19, 20, 21, 6], [529, 16, 17, 18, 19, 20, 21, 6], [545, 16, 17, 18, 19, 20, 21, 6, 9], [546, 16, 17, 18, 19, 20, 21, 6, 9],]

    if settings[1][0] == 0:
        item_logic_chunk[9] = [[1243, 16, 24, 1, 3, 6], [1250, 16, 24, 1, 3, 6], [1251, 16, 24, 1, 3, 6], [1252, 16, 24, 1, 3, 6], [184, 15, 6], [185, 15, 6], [186, 15, 6], [187, 15, 6], [188, 15, 6], [189, 15, 6], [191, 15, 6],
        [193, 15, 6], [195, 15, 6], [197, 15, 6], [199, 15, 6], [201, 15, 6], [203, 15, 6], [205, 15, 6], [207, 15, 6], [209, 15, 6], [211, 15, 6], [213, 15, 6], [215, 15, 6], [217, 15, 6], [219, 15, 6],
        [221, 15, 6], [223, 15, 6], [225, 15, 6], [227, 15, 6], [229, 15, 6], [231, 15, 6], [233, 15, 6], [235, 15, 6], [236, 15, 6], [237, 15, 6], [238, 15, 6], [245, 15, 6], [246, 15, 6],]
    else:
        item_logic_chunk[9] = [[1243, 16, 24, 3, 6], [1250, 16, 24, 3, 6], [1251, 16, 24, 3, 6], [1252, 16, 24, 3, 6], [184, 15, 6], [185, 15, 6], [186, 15, 6], [187, 15, 6], [188, 15, 6], [189, 15, 6], [191, 15, 6],
        [193, 15, 6], [195, 15, 6], [197, 15, 6], [199, 15, 6], [201, 15, 6], [203, 15, 6], [205, 15, 6], [207, 15, 6], [209, 15, 6], [211, 15, 6], [213, 15, 6], [215, 15, 6], [217, 15, 6], [219, 15, 6],
        [221, 15, 6], [223, 15, 6], [225, 15, 6], [227, 15, 6], [229, 15, 6], [231, 15, 6], [233, 15, 6], [235, 15, 6], [236, 15, 6], [237, 15, 6], [238, 15, 6], [245, 15, 6], [246, 15, 6],]

    if settings[1][1] == 0:
        item_logic_chunk[10] = [[568, 16, 17, 18, 19, 20, 21, 6, 9, -1, 16, 5, 6, 9], [569, 16, 17, 18, 19, 20, 21, 6, 9, -1, 16, 5, 6, 9], [577, 16, 4, 5, 6], [578, 16, 4, 5, 6], [579, 16, 4, 5, 6], [580, 16, 4, 5, 6],
        [581, 16, 17, 18, 19, 20, 21, 6, -1, 16, 5, 6], [582, 16, 17, 18, 19, 20, 21, 6, -1, 16, 5, 6], [583, 16, 17, 1, 6, -1, 16, 1, 5, 6], [584, 16, 17, 2, 6, -1, 16, 2, 5, 6], [585, 16, 17, 2, 6, -1, 16, 2, 5, 6],
        [861, 6, 7, 12, 13], [862, 6, 7, 12, 13], [2081, 15, 2, 4, 5, 6, 8],]
    else:
        item_logic_chunk[10] = [[568, 16, 17, 18, 19, 20, 21, 6, 9], [569, 16, 17, 18, 19, 20, 21, 6, 9], [577, 16, 4, 5, 6], [578, 16, 4, 5, 6], [579, 16, 4, 5, 6], [580, 16, 4, 5, 6],
        [581, 16, 17, 18, 19, 20, 21, 6], [582, 16, 17, 18, 19, 20, 21, 6], [583, 16, 17, 1, 6], [584, 16, 17, 2, 6], [585, 16, 17, 2, 6],
        [861, 6, 7, 12, 13], [862, 6, 7, 12, 13], [2081, 15, 2, 4, 5, 6, 8],]

    if settings[1][0] == 0 and settings[1][1] == 0:
        item_logic_chunk[11] = [[1624, 1, 4, 5], [2404, 1, 4, 5], [315, 16, 17, 2, -1, 16, 2, 5], [316, 16, 17, 2, -1, 16, 2, 5], [317, 16, 17, 18, 19, 20, 21, 2, -1, 16, 2, 5], [318, 16, 5], [2396, 16, 4, 5], [2330, 16, 2, 4, 5],
        [323, 16, 4, 5], [324, 16, 4, 5], [325, 16, 4, 5], [326, 16, 4, 5], [1506, 15, 1], [1507, 15, 3], [1508, 15, 3, 5], [1509, 15, 5], [1510, 15, 2], [1533, 15, 16, 2, 4, 5, 6], [1534, 15, 16, 2, 4, 5, 6],
        [2337, 15, 16, 2, 4, 5, 6], [2338, 15, 16, 2, 4, 5, 6], [2339, 15, 16, 2, 4, 5, 6], [1535, 15, 16, 22, 2, 4, 5, 6], [1536, 15, 16, 22, 2, 4, 5, 6], [1537, 15, 16, 22, 2, 4, 5, 6], [1538, 15, 16, 22, 2, 4, 5, 6],
        [1625, 1, 4, 5], [1626, 1, 4, 5], [1627, 1, 4, 5], [1628, 2, 4, 5], [1629, 2, 4, 5]]
    elif settings[1][0] != 0 and settings[1][1] != 0:
        item_logic_chunk[11] = [[1624, 4, 5], [2404, 4, 5], [315, 16, 17, 2], [316, 16, 17, 2], [317, 16, 17, 18, 19, 20, 21, 2], [318, 16, 5], [2396, 16, 4, 5], [2330, 16, 2, 4, 5],
        [323, 16, 4, 5], [324, 16, 4, 5], [325, 16, 4, 5], [326, 16, 4, 5], [1506, 15, 1], [1507, 15, 3], [1508, 15, 3, 5], [1509, 15, 5], [1510, 15, 2], [1533, 15, 16, 2, 4, 5, 6], [1534, 15, 16, 2, 4, 5, 6],
        [2337, 15, 16, 2, 4, 5, 6], [2338, 15, 16, 2, 4, 5, 6], [2339, 15, 16, 2, 4, 5, 6], [1535, 15, 16, 22, 2, 4, 5, 6], [1536, 15, 16, 22, 2, 4, 5, 6], [1537, 15, 16, 22, 2, 4, 5, 6], [1538, 15, 16, 22, 2, 4, 5, 6],
        [1625, 1, 4, 5], [1626, 1, 4, 5], [1627, 1, 4, 5], [1628, 2, 4, 5], [1629, 2, 4, 5]]
    elif settings[1][0] == 1:
        item_logic_chunk[11] = [[1624, 4, 5], [2404, 4, 5], [315, 16, 17, 2, -1, 16, 2, 5], [316, 16, 17, 2, -1, 16, 2, 5], [317, 16, 17, 18, 19, 20, 21, 2, -1, 16, 2, 5], [318, 16, 5], [2396, 16, 4, 5], [2330, 16, 2, 4, 5],
        [323, 16, 4, 5], [324, 16, 4, 5], [325, 16, 4, 5], [326, 16, 4, 5], [1506, 15, 1], [1507, 15, 3], [1508, 15, 3, 5], [1509, 15, 5], [1510, 15, 2], [1533, 15, 16, 2, 4, 5, 6], [1534, 15, 16, 2, 4, 5, 6],
        [2337, 15, 16, 2, 4, 5, 6], [2338, 15, 16, 2, 4, 5, 6], [2339, 15, 16, 2, 4, 5, 6], [1535, 15, 16, 22, 2, 4, 5, 6], [1536, 15, 16, 22, 2, 4, 5, 6], [1537, 15, 16, 22, 2, 4, 5, 6], [1538, 15, 16, 22, 2, 4, 5, 6],
        [1625, 1, 4, 5], [1626, 1, 4, 5], [1627, 1, 4, 5], [1628, 2, 4, 5], [1629, 2, 4, 5]]
    else:
        item_logic_chunk[11] = [[1624, 1, 4, 5], [2404, 1, 4, 5], [315, 16, 17, 2], [316, 16, 17, 2], [317, 16, 17, 18, 19, 20, 21, 2], [318, 16, 5], [2396, 16, 4, 5], [2330, 16, 2, 4, 5],
        [323, 16, 4, 5], [324, 16, 4, 5], [325, 16, 4, 5], [326, 16, 4, 5], [1506, 15, 1], [1507, 15, 3], [1508, 15, 3, 5], [1509, 15, 5], [1510, 15, 2], [1533, 15, 16, 2, 4, 5, 6], [1534, 15, 16, 2, 4, 5, 6],
        [2337, 15, 16, 2, 4, 5, 6], [2338, 15, 16, 2, 4, 5, 6], [2339, 15, 16, 2, 4, 5, 6], [1535, 15, 16, 22, 2, 4, 5, 6], [1536, 15, 16, 22, 2, 4, 5, 6], [1537, 15, 16, 22, 2, 4, 5, 6], [1538, 15, 16, 22, 2, 4, 5, 6],
        [1625, 1, 4, 5], [1626, 1, 4, 5], [1627, 1, 4, 5], [1628, 2, 4, 5], [1629, 2, 4, 5]]

    item_logic = []
    for c in range(len(item_logic_chunk)):
        for l in range(len(item_logic_chunk[c])):
            item_logic.append(item_logic_chunk[c][l])

    #for item in range(len(item_logic)):
    #    if item_locals[item][6] == item_logic[item][0]:
    #        print(item_locals[item][6])

    #Creates an array with the ability info
    key_item_info = [-1, 0x06C, 0x075, 0x10C, 0x13D, 0x0F5, 0x0C6, -1, 0x1E7, 0x1F8, 0x0F6, 0x0FA,
                     -1, -1, -1, 0x13E, 0x0B2, 0x0B5, 0x0B6, 0x0B7, -1, -1, 0x177, 0x17A, 0x17D, -1]

    #Creates an item pool for the key items
    key_item_pool = [[0xE002, 0], [0xE002, 1], [0xE002, 2], [0xE004, 3], [0xE004, 4], [0xE005, 5], [0xE00A, 6], [0xE00D, 7],
                     [0xE00E, 8], [0xE00F, 9], [0xE010, 10], [0xE011, 11], [0xE012, 12], [0xE013, 13], [0xE075, 14], [0xC369, 15],
                     [0xCABF, 16], [0xE0A0, 17], [0xC343, 18], [0xC344, 19], [0xC345, 20], [0xC346, 21], [0xC960, 22], [0xC3B9, 23],
                     [0xB0F7, 24], [0xB0F7, 25], [0xB0F7, 26], [0xC47E, 27]]

    #Checked array for the key items
    key_item_check = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    #Removes items from the key item pool depending on the settings
    for l in range(len(settings)):
        if settings[0][l] == 1.0:
            s = find_index_in_2d_list(key_item_pool, l)
            key_item_check[s[0]] += 1
            del key_item_pool[s[0]]

    #Creates an array with the key item logic
    key_item_logic = [[-1], [0x06C, 0, 23, -1, 0, 5], [0x075, 0, 23, 3, 10, -1, 0, 5, 10],
                      [0x10C, 0, 4, 23, -1, 0, 4, 5], [0x13D, 15, 16], [0x0F5, 6], [0x0C6, 15, 16, 17, 18, 19, 20, 21, 6, -1, 15, 16, 5, 6],
                      [-1], [0x1E7, 23, 0, 6, -1, 0, 5, 6], [0x1F8, 23, 0, 4, 6, 10, -1, 23, 0, 3, 5, 6, 10], [0x0F6, 6, 7], [0x0FA, 6, 7, 12],
                      [-1], [-1], [-1], [0x13E, 15, 16, 6], [0x0B2, 15, 16, 17, -1, 15, 16, 5], [0x0B5, 15, 16, 17, 1, -1, 15, 16, 1, 5, -1, 15, 16, 17, 2, -1, 15, 16, 2, 5],
                      [0x0B6, 15, 16, 17, 2, -1, 15, 16, 2, 5], [0x0B7, 15, 16, 17, 1, -1, 15, 16, 1, 5, -1, 15, 16, 17, 2, -1, 15, 16, 2, 5],
                      [-1], [-1], [0x177, 15, 16, 1, 2, 4, 6], [0x17A, 15, 16, 1, 4, 6], [0x17D, 15, 16, 1, 4, 6], [-1]]

    #Creates an item pool with the attack pieces
    attack_piece_pool = [[[0x01, 0xB030], [0x02, 0xB030], [0x04, 0xB030], [0x08, 0xB030], [0x10, 0xB030], [0x01, 0xB031],
                         [0x02, 0xB031], [0x04, 0xB031], [0x08, 0xB031], [0x10, 0xB031]], [[0x01, 0xB059], [0x02, 0xB059],
                         [0x04, 0xB059], [0x08, 0xB059], [0x10, 0xB059], [0x01, 0xB05A], [0x02, 0xB05A], [0x04, 0xB05A],
                         [0x08, 0xB05A], [0x10, 0xB05A]], [[0x01, 0xB037], [0x02, 0xB037], [0x04, 0xB037], [0x08, 0xB037],
                         [0x10, 0xB037], [0x01, 0xB038], [0x02, 0xB038], [0x04, 0xB038], [0x08, 0xB038], [0x10, 0xB038]]]

    #Logic for the key items, so they only spawn when others are already in the pool
    logic_logic = [[0], [1, 0], [2, 1], [3], [4, 15, 16, 3, -1, 23, 1, 3, -1, 1, 3, 5], [5], [6, 15, -1, 23, 1, 3], [7, 6], [8, 6], [9, 6], [10, 15, 3, 6, -1, 23, 1, 3, 6], [11, 10],
                   [12, 7], [13, 7], [14], [15], [16, 15], [17, 15, 16], [18, 15, 16], [19, 15, 16], [20, 15, 16], [21, 15, 16], [22, 15], [23, 1],
                   [24, 1, 3, 6], [25, 24], [26, 25], [27, 15, 1]]

    print("Randomizing...")
    new_item_locals = []

    #[Trigger type, Room ID, X Pos, Y Pos, Z Pos, Collectible/Cutscene ID, Ability/Item/Key Item/Attack(, Attack Piece ID/Coin Amount/Item Cutscene/Hammer or Spin Cutscene, Coin Cutscene)]
    repack_data = []
    itemcut = 0
    attackcut = 0
    key_item_pool_checked = []
    new_enemy_stats = []
    attack = random.randint(0, len(attack_piece_pool) - 1)

    while len(item_pool) + len(key_item_pool) + len(attack_piece_pool) > 0:
        prevlen = len(item_pool) + len(key_item_pool) + len(attack_piece_pool)
        item_logic_len = len(item_logic)
        for i in range(item_logic_len):
            try:
                if len(item_logic) > 0:
                    if is_available(item_logic[i], key_item_check, settings):
                        rand_array = random.randint(0, 1)
                        if rand_array == 0 and len(item_pool) > 0:
                            #Code for randomizing blocks and bean spots with just eachother
                            nitem = random.randint(0, len(item_pool) - 1)
                            narray = [item_locals[i][0], item_locals[i][1], item_locals[i][2], item_pool[nitem][1],
                                        item_locals[i][3], item_locals[i][4], item_locals[i][5], item_locals[i][6]]
                            new_item_locals.append(narray)
                            del item_pool[nitem]
                            del item_locals[i]
                            del item_logic[i]
                        elif len(attack_piece_pool) > 0:
                            #Code for putting attacks in blocks and bean spots
                            if len(attack_piece_pool[attack]) == 0:
                                del attack_piece_pool[attack]
                                if len(attack_piece_pool) > 0:
                                    attack = random.randint(0, len(attack_piece_pool) - 1)
                            nitem = random.randint(0, len(attack_piece_pool[attack]) - 1)
                            narray = [item_locals[i][0], item_locals[i][1], item_locals[i][2], 0,
                                    item_locals[i][3], item_locals[i][4], item_locals[i][5], item_locals[i][6]]
                            new_item_locals.append(narray)
                            spottype = get_spot_type(item_locals[i])
                            repack_data.append([spottype, item_locals[i][0], item_locals[i][3], item_locals[i][4], item_locals[i][5], item_locals[i][6] + 0xD000,
                                                attack_piece_pool[attack][nitem][1], attack_piece_pool[attack][nitem][0], 0xCD20 + attackcut])
                            attackcut += 1
                            del attack_piece_pool[attack][nitem]
                            del item_locals[i]
                            del item_logic[i]
                        i -= 1
            except IndexError:
                break
        for i in range(len(key_item_logic)):
            if len(key_item_logic) > 0:
                try:
                    if key_item_info[i] > -1:
                        if is_available(key_item_logic[i], key_item_check, settings):
                            rand_array = random.randint(0, 1)
                            if rand_array == 0 and len(item_pool) > 0:
                                # Code for if a block or bean spot's contents are in an ability cutscene
                                nitem = random.randint(0, len(item_pool) - 1)
                                if (item_pool[nitem][1] != 0x0000 and item_pool[nitem][1] != 0x0002 and
                                        item_pool[nitem][1] != 0x0004 and item_pool[nitem][1] != 0x0006 and item_pool[nitem][1] != 0x0008):
                                    repack_data.append(
                                        [6, key_item_info[i], 0, 0, 0, 0xCDA0 + itemcut, item_pool[nitem][1],
                                         0xCDA0 + itemcut])
                                else:
                                    repack_data.append(
                                        [6, key_item_info[i], 0, 0, 0, 0xCDA0 + itemcut, item_pool[nitem][1], 1 + 9 * (item_pool[nitem][0] // 0xA0 % 2),
                                         0xCDA0 + itemcut])
                                itemcut += 1
                                del item_pool[nitem]
                                del key_item_info[i]
                                del key_item_logic[i]
                            elif len(attack_piece_pool) > 0:
                                # Code for if an attack is in an ability cutscene
                                if len(attack_piece_pool[attack]) == 0:
                                    del attack_piece_pool[attack]
                                    attack = random.randint(0, len(attack_piece_pool) - 1)
                                nitem = random.randint(0, len(attack_piece_pool[attack]) - 1)
                                repack_data.append(
                                    [6, key_item_info[i], 0, 0, 0, 0xCD20 + attackcut, attack_piece_pool[attack][nitem][1],
                                     attack_piece_pool[attack][nitem][0], 0xCD20 + attackcut])
                                attackcut += 1
                                del attack_piece_pool[attack][nitem]
                                del key_item_info[i]
                                del key_item_logic[i]
                            i -= 1
                except IndexError:
                    break
        #Checks if more items can be randomized
        if prevlen <= len(item_pool) + len(key_item_pool) + len(attack_piece_pool) and len(key_item_pool) > 0 and len(new_item_locals) > 0:
            if len(key_item_pool) > 0:
                can_key = False
                for i in range(len(new_item_locals)):
                    if new_item_locals[i][3] != 0 or find_index_in_2d_list(repack_data, new_item_locals[i][7] + 0xD000) is not None:
                        can_key = True
                if can_key:
                    old_spot = random.randint(0, len(new_item_locals) - 1)
                    while new_item_locals[old_spot][3] == 0:
                        old_spot = random.randint(0, len(new_item_locals) - 1)
                    item_locals.append([new_item_locals[old_spot][0], new_item_locals[old_spot][1],
                                        new_item_locals[old_spot][2], new_item_locals[old_spot][4],
                                        new_item_locals[old_spot][5], new_item_locals[old_spot][6],
                                        new_item_locals[old_spot][7]])
                    item_pool.append([new_item_locals[old_spot][2], new_item_locals[old_spot][3]])
                    i = -1

                    # Code for putting key items in blocks and bean spots
                    nitem = random.randint(0, len(key_item_pool) - 1)
                    while not is_available(logic_logic[key_item_pool[nitem][1]], key_item_check, settings):
                        nitem = random.randint(0, len(key_item_pool) - 1)
                    narray = [item_locals[i][0], item_locals[i][1], item_locals[i][2], 0,
                              item_locals[i][3], item_locals[i][4], item_locals[i][5], item_locals[i][6]]
                    new_item_locals[old_spot] = narray
                    spottype = get_spot_type(item_locals[i])
                    if key_item_pool[nitem][0] < 0xE000 or key_item_pool[nitem][0] > 0xE004:
                        repack_data.append(
                            [spottype, item_locals[i][0], item_locals[i][3], item_locals[i][4], item_locals[i][5],
                             item_locals[i][6] + 0xD000, key_item_pool[nitem][0]])
                    elif key_item_pool[nitem][0] != 0xE000:
                        repack_data.append(
                            [spottype, item_locals[i][0], item_locals[i][3], item_locals[i][4], item_locals[i][5],
                             item_locals[i][6] + 0xD000, key_item_pool[nitem][0], 0xCDA0 + itemcut])
                        itemcut += 1
                    else:
                        repack_data.append(
                            [spottype, item_locals[i][0], item_locals[i][3], item_locals[i][4], item_locals[i][5],
                             item_locals[i][6] + 0xD000, key_item_pool[nitem][0] + key_item_pool[nitem][1],
                             0xCDA0 + itemcut])
                        itemcut += 1
                    key_item_check[key_item_pool[nitem][1]] += 1
                    key_item_pool_checked.append(key_item_pool[nitem])
                    del key_item_pool[nitem]
                    del item_locals[i]
                else:
                    attack_spot = find_index_in_2d_list(repack_data, new_item_locals[0][7] + 0xD000)
                    if attack_spot is not None:
                        if len(repack_data[attack_spot[0]]) > 7 and repack_data[attack_spot[0]][6] < 0xC000:
                            attack_piece_pool.append([repack_data[attack_spot[0]][7], repack_data[attack_spot[0]][6]])
                        else:
                            key_spot = find_index_in_2d_list(key_item_pool_checked, repack_data[attack_spot[0]][6])
                            if key_spot is not None:
                                key_item_pool.append(key_item_pool_checked[key_spot[0]])
                                del key_item_pool_checked[key_spot[0]]
                                key_item_check[key_item_pool[-1][1]] -= 1
                        del repack_data[attack_spot[0]]
                    else:
                        item_pool.append([new_item_locals[0][2], new_item_locals[0][3]])
                    item_locals[len(item_logic)] = [new_item_locals[0][0], new_item_locals[0][1], new_item_locals[0][2],
                                        new_item_locals[0][4], new_item_locals[0][5], new_item_locals[0][6],
                                        new_item_locals[0][7]]
                    item_logic.append([0])
                    del new_item_locals[0]

        #Randomizes enemy stats
        for i in range(len(enemy_logic)):
            if len(enemy_logic) > 0:
                try:
                    if is_available(enemy_logic[i], key_item_check, settings):
                        temp = enemy_stats_rand[i]
                        for n in range(len(enemy_stats_rand[0])-1):
                            enemy_stats_rand[i][n+1] = enemy_stats_rand[0][n+1]
                            for j in range(i-1):
                                enemy_stats_rand[j][n+1] = enemy_stats_rand[j+1][n+1]
                            if i > 0:
                                enemy_stats_rand[i-1][n+1] = temp[n+1]
                        new_enemy_stats.append(enemy_stats_rand[i])
                        del enemy_stats_rand[i]
                        del enemy_logic[i]
                        i -= 1
                except IndexError:
                    break
        for i in range(len(boss_logic)):
            if len(boss_logic) > 0:
                try:
                    if is_available(boss_logic[i], key_item_check, settings):
                        temp = boss_stats_rand[i]
                        for n in range(len(boss_stats_rand[0])-1):
                            boss_stats_rand[i][n+1] = boss_stats_rand[0][n+1]
                            for j in range(i-1):
                                boss_stats_rand[j][n+1] = boss_stats_rand[j+1][n+1]
                            if i > 0:
                                boss_stats_rand[i-1][n+1] = temp[n+1]
                        new_enemy_stats.append(boss_stats_rand[i])
                        del boss_stats_rand[i]
                        del boss_logic[i]
                        i -= 1
                except IndexError:
                    break
        for i in range(len(dream_enemy_logic)):
            if len(dream_enemy_logic) > 0:
                try:
                    if is_available(dream_enemy_logic[i], key_item_check, settings):
                        temp = dream_enemy_stats_rand[i]
                        for n in range(len(dream_enemy_stats_rand[0])-1):
                            dream_enemy_stats_rand[i][n+1] = dream_enemy_stats_rand[0][n+1]
                            for j in range(i-1):
                                dream_enemy_stats_rand[j][n+1] = dream_enemy_stats_rand[j+1][n+1]
                            if i > 0:
                                dream_enemy_stats_rand[i-1][n+1] = temp[n+1]
                        new_enemy_stats.append(dream_enemy_stats_rand[i])
                        del dream_enemy_stats_rand[i]
                        del dream_enemy_logic[i]
                        i -= 1
                except IndexError:
                    break
        for i in range(len(dream_boss_logic)):
            if len(dream_boss_logic) > 0:
                try:
                    if is_available(dream_boss_logic[i], key_item_check, settings):
                        temp = dream_boss_stats_rand[i]
                        for n in range(len(dream_boss_stats_rand[0])-1):
                            dream_boss_stats_rand[i][n+1] = dream_boss_stats_rand[0][n+1]
                            for j in range(i-1):
                                dream_boss_stats_rand[j][n+1] = dream_boss_stats_rand[j+1][n+1]
                            if i > 0:
                                dream_boss_stats_rand[i-1][n+1] = temp[n+1]
                        new_enemy_stats.append(dream_boss_stats_rand[i])
                        del dream_boss_stats_rand[i]
                        del dream_boss_logic[i]
                        i -= 1
                except IndexError:
                    break
        for i in range(len(filler_logic)):
            if len(filler_logic) > 0:
                try:
                    if is_available(filler_logic[i], key_item_check, settings):
                        temp = filler_stats_rand[i]
                        for n in range(len(filler_stats_rand[0])-1):
                            filler_stats_rand[i][n+1] = filler_stats_rand[0][n+1]
                            for j in range(i-1):
                                filler_stats_rand[j][n+1] = filler_stats_rand[j+1][n+1]
                            if i > 0:
                                filler_stats_rand[i-1][n+1] = temp[n+1]
                        new_enemy_stats.append(filler_stats_rand[i])
                        del filler_stats_rand[i]
                        del filler_logic[i]
                        i -= 1
                except IndexError:
                    break

        #Swaps a coin with whatever is left in the item pool
        if (len(item_pool) > 0 or len(attack_piece_pool) > 0) and len(item_logic) == 0:
            item = 0
            while new_item_locals[item][3] != 0 or find_index_in_2d_list(repack_data, new_item_locals[item][7] + 0xD000) is not None:
                item += 1
                if item == len(new_item_locals):
                    item -= 1
                    break
            item_locals[len(item_logic)] = [new_item_locals[item][0], new_item_locals[item][1], new_item_locals[item][2], new_item_locals[item][4], new_item_locals[item][5], new_item_locals[item][6], new_item_locals[item][7]]
            item_logic.append([0])
            del new_item_locals[item]

    #hammer_local = find_index_in_2d_list(repack_data, 0xC369)
    #print(repack_data[hammer_local[0]])

    print("Generating spoiler log...")
    #Names for all the locations
    item_local_names = ["Entrance", "Hammer Room", "West Hammer Room", "River Rocks",
                        "Upper Attack Piece Room", "Lower Attack Piece Room", "Gate Room",
                        "Fountain Room", "Lower Rock Room", "Right of Hammer Room", "Right Rock Room", "Maintenance Hut", "Many Enemy Room",
                        "Early Hammer Room", "Outside", "Mushrise Treeboard Room", "Western Track Room",
                        "Drill Machine Tutorial Room", "Mini/Mole Mario Tutorial Room", "Middle Track Room", "Lower Track Room",
                        "Upper Track Room", "Early First Track Room", "Early Main Track Room", "Mini Mario Room",
                        "Underground", "Bottom Right Track Room", "East of Dreamstone", "West of Pi'illo Castle",
                        "In Front of Pi'illo Castle", "Test Room", "Eldream Room 1",
                        "Eldream Room 2", "Eldream Room 3", "Eldream Room 4",
                        "Eldream Room 5", "Eldream Item Detour Room", "Eldream Fountain Room",
                        "Eldream Room 7", "Eldream Bouncy Flower Room", "Eldream Pipe to Sewers",
                        ""]

    #Names for items
    item_names = [["Coin", "5 Coins", "10 Coins", "50 Coins", "100 Coins"],

                  ["Mushroom", "Super Mushroom", "Ultra Mushroom", "Max Mushroom", "Nut", "Super Nut", "Ultra Nut", "Max Nut", "Syrup Jar", "Supersyrup Jar", "Ultrasyrup Jar", "Max Syrup Jar",
                   "Candy", "Super Candy", "Ultra Candy", "Max Candy", "1-Up Mushroom", "1-Up Deluxe", "Refreshing Herb", "Heart Bean", "Bros. Bean", "Power Bean", "Defense Bean", "Speed Bean",
                   "Stache Bean", "Taunt Ball", "Shock Bomb", "Boo Biscuit", "Secret Box", "Heart Bean DX", "Bros Bean DX", "Power Bean DX", "Defense Bean DX", "Speed Bean DX", "Stache Bean DX"],

                  ["Starter Badge", "Master Badge", "Expert Badge", "Bronze Badge", "Silver Badge", "Gold Badge", "Mush Badge", "Strike Badge", "Guard Badge", "Virus Badge", "Risk Badge", "Miracle Badge"],

                  ["Run-Down Boots", "Discount Boots", "So-So Boots", "Sandwich Boots", "Bare Boots", "Iron-Ball Boots", "Trusty Boots", "Snare Boots", "Coin Boots", "Super Boots", "EXP Boots",
                   "Knockout Boots", "Heart Boots", "Elite Boots", "Anti-air Boots", "Action Boots", "Bros. Boots", "Singular Boots", "Glass Boots", "Coin Boots DX", "Iron-Ball Boots DX", "VIP Boots",
                   "EXP Boots DX", "Anti-air Boots DX", "Bare Boots DX", "Star Boots", "Dark Boots", "Crystal Boots", "Wellington Boots", "Pro Boots", "Supreme Boots", "Challenge Boots", "Hiking Boots",
                   "DoB Boots", "MINI Boots", "Run-Down Hammer", "Discount Hammer", "So-So Hammer", "Picnic Hammer", "Bare Hammer", "Iron-Ball Hammer", "Steady Hammer", "Fighter Hammer", "Sap Hammer",
                   "Super Hammer", "Soft Hammer", "Knockout Hammer", "Flame Hammer", "Elite Hammer", "Blunt Hammer", "Action Hammer", "Spin Hammer", "Singular Hammer", "Glass Hammer", "Sap Hammer DX",
                   "Iron-Ball Hammer DX", "VIP Hammer", "Flame Hammer DX", "Blunt Hammer DX", "Bare Hammer DX", "Star Hammer", "Dark Hammer", "Crystal Hammer", "Soft Hammer DX", "Pro Hammer", "Supreme Hammer",
                   "Challenge Hammer", "Golden Hammer", "DoB Hammer", "MINI Hammer", "Thin Wear", "Picnic Wear", "Cozy Wear", "So-So Wear", "Retribution Wear", "Singular Wear", "Rally Wear", "Filler Wear",
                   "Super Wear", "Fighter Wear", "Koopa Troopa Wear", "VIP Wear", "Counter Wear", "Safety Wear", "Fancy Wear", "Hero Wear", "Bros. Wear", "Metal Wear", "Snare Wear", "Heart Wear", "Boost Wear",
                   "Star Wear", "Ironclad Wear", "King Wear", "Angel Wear", "Pro Wear", "Legendary Wear", "Challenge Wear", "Golden Wear", "DoB Wear", "Thick Gloves", "Shell Gloves", "Metal Gloves", "HP Gloves",
                   "HP Gloves DX", "BP Gloves", "BP Gloves DX", "POW Gloves", "POW Gloves DX", "Speed Gloves", "Stache Gloves", "Lucky Gloves", "Lucky Gloves DX", "Gift Gloves", "Gift Gloves DX", "Filler Gloves",
                   "Filler Gloves DX", "Strike Gloves", "Mushroom Gloves", "1-Up Gloves", "Pro Gloves", "Rookie Gloves", "Perfect POW Gloves", "Perfect Bro Gloves", "Coin Bro Gloves", "Coin Bro Gloves DX", "EXP Bro Gloves",
                   "EXP Bro Gloves DX", "Bottomless Gloves", "MINI Gloves", "HP Scarf", "HP Scarf DX", "BP Scarf", "BP Scarf DX", "POW Scarf", "POW Scarf DX", "Speed Scarf", "Stache Scarf", "Bros. Ring", "HP Bangle",
                   "HP Bangle DX", "BP Bangle", "BP Bangle DX", "Angel Bangle", "HP Knockout Bangle", "BP Knockout Bangle", "Healthy Ring", "Guard Shell", "Guard Shell DX", "Rally Belt", "Counter Belt", "POW Mush Jam",
                   "DEF Mush Jam", "Duplex Crown", " -- ", "Mushroom Amulet", "DoB Ring", "Mini Ring", "Silver Statue", "Gold Statue"]]

    #Names for key items
    key_item_names = ["Progressive Hammers", "Progressive Hammers", "Progressive Hammers", "Progressive Spin", "Progressive Spin", "Ball Hop", "Luiginary Works", "Luiginary Ball", "Luiginary Stack High Jump",
                      "Luiginary Stack Ground Pound", "Luiginary Cone Jump", "Luiginary Cone Storm", "Luiginary Ball Hookshot", "Luiginary Ball Throw", "Deep Pi'illo Castle", "Blimport Bridge", "Mushrise Park Gate",
                      "First Dozite", "Dozite 1", "Dozite 2", "Dozite 3", "Dozite 4", "Access to Wakeport", "Access to Mount Pajamaja", "Dream Egg 1", "Dream Egg 2", "Dream Egg 3", "Access to Neo Bowser Castle"]

    #Names for attack pieces
    attack_piece_names = ["Mushrise Park", "Dreamy Mushrise Park", "Dozing Sands", "Dreamy Dozing Sands", "Wakeport", "Mount Pajamaja", "Dreamy Mount Pajamaja", "Driftwood Shores", "Dreamy Driftwood Shores",
                          "Mount Pajamaja Summit", "Dreamy Wakeport", "Somnom Woods", "Dreamy Somnom Woods", "Mushrise Park Caves", "Neo Bowser Castle"]

    #Names for the different kinds of checks
    check_names = ["Block", "Block", "Rotated Block", "Mini Mario Block", "High Up Block", "Bean Spot", "Key Item Spot", "Attack Piece Block", "Rotated Block", "Rotated Block"]

    #Sorts the new item locals array in order of room ID and spot ID
    new_item_locals = sorted(new_item_locals, key=lambda local: local[0])
    repack_data = sorted(repack_data, key=lambda key: key[1])
    rooms = []
    areas = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
    temp = []
    for i in range(len(new_item_locals)):
        if i > 0:
            if new_item_locals[i][0] == new_item_locals[i-1][0]:
                rooms.append(new_item_locals[i])
            else:
                rooms = sorted(rooms, key=lambda local: local[7])
                if get_room(rooms[-1][0]) == "Mushrise Park":
                    room = 3
                elif get_room(rooms[-1][0]) == "Dozing Sands":
                    room = 5
                elif get_room(rooms[-1][0]) == "Blimport":
                    room = 0
                elif get_room(rooms[-1][0]) == "Dreamy Mushrise Park":
                    room = 4
                elif get_room(rooms[-1][0]) == "Wakeport":
                    room = 7
                elif get_room(rooms[-1][0]) == "Driftwood Shores":
                    room = 11
                elif get_room(rooms[-1][0]) == "Mount Pajamaja":
                    room = 9
                elif get_room(rooms[-1][0]) == "Pi'illo Castle":
                    room = 1
                elif get_room(rooms[-1][0]) == "Dreamy Pi'illo Castle":
                    room = 2
                elif get_room(rooms[-1][0]) == "Dreamy Dozing Sands":
                    room = 6
                elif get_room(rooms[-1][0]) == "Dreamy Driftwood Shores":
                    room = 12
                else:
                    room = 17
                if len(areas[room]) > 1:
                    spot = 1
                    while areas[room][spot-1][0] < areas[room][spot][0]:
                        spot += 1
                        if spot == len(areas[room]):
                            break
                    areas[room].insert(spot, rooms)
                else:
                    if len(areas[room]) == 0:
                        areas[room].append(rooms)
                    else:
                        if areas[room][0][0] <= areas[room][-1][0]:
                            areas[room].append(rooms)
                        else:
                            areas[room].insert(0, rooms)
                rooms = []
                rooms.append(new_item_locals[i])
        else:
            rooms.append(new_item_locals[i])

    rooms = sorted(rooms, key=lambda local: local[7])
    if get_room(rooms[-1][0]) == "Mushrise Park":
        room = 3
    elif get_room(rooms[-1][0]) == "Dozing Sands":
        room = 5
    elif get_room(rooms[-1][0]) == "Blimport":
        room = 0
    elif get_room(rooms[-1][0]) == "Dreamy Mushrise Park":
        room = 4
    elif get_room(rooms[-1][0]) == "Wakeport":
        room = 7
    elif get_room(rooms[-1][0]) == "Driftwood Shores":
        room = 11
    elif get_room(rooms[-1][0]) == "Mount Pajamaja":
        room = 9
    elif get_room(rooms[-1][0]) == "Pi'illo Castle":
        room = 1
    elif get_room(rooms[-1][0]) == "Dreamy Pi'illo Castle":
        room = 2
    elif get_room(rooms[-1][0]) == "Dreamy Dozing Sands":
        room = 6
    elif get_room(rooms[-1][0]) == "Dreamy Driftwood Shores":
        room = 12
    elif get_room(rooms[-1][0]) == "Dreamy Wakeport":
        room = 8
    else:
        room = 17
    if len(areas[room]) > 1:
        spot = 1
        while areas[room][spot - 1][0] < areas[room][spot][0]:
            spot += 1
            if spot == len(areas[room]):
                break
        areas[room].insert(spot, rooms)
    else:
        if len(areas[room]) == 0:
            areas[room].append(rooms)
        else:
            if areas[room][0][0] <= areas[room][-1][0]:
                areas[room].append(rooms)
            else:
                areas[room].insert(0, rooms)
    rooms = []
    for r in range(len(areas)):
        for p in range(len(areas[r])):
            for i in range(len(areas[r][p])):
                temp.append(areas[r][p][i])
    new_item_locals = temp

    #Creates a spoiler log
    spoiler_log = open(input_folder + "/Spoiler Log.txt", "w")
    room_check = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
    for s in range(len(new_item_locals)):
        if s > 0:
            if get_room(new_item_locals[s][0]) != get_room(new_item_locals[s-1][0]):
                spoiler_log.write("\n--" + get_room(new_item_locals[s][0]) + "--\n\n")
        else:
            spoiler_log.write("--Blimport--\n\n")
        check_type = ""
        if len(room_check) < new_item_locals[s][0] + 1:
            while len(room_check) < new_item_locals[s][0] + 1:
                room_check.append([0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        room_check[new_item_locals[s][0]][get_spot_type(new_item_locals[s])] += 1
        number = str(room_check[new_item_locals[s][0]][get_spot_type(new_item_locals[s])])
        k = find_index_in_2d_list(repack_data, new_item_locals[s][7] + 0xD000)
        if k is None:
            item = item_names[new_item_locals[s][3] // 0x2000][int(new_item_locals[s][3] / 2) % 0x100]
            check_type = check_names[get_spot_type(new_item_locals[s])]
        else:
            check_type = check_names[repack_data[k[0]][0]]
            ab = find_index_in_2d_list(key_item_pool_checked, repack_data[k[0]][6])
            if ab is None:
                if repack_data[k[0]][6] < 0xB037:
                    item = attack_piece_names[int((repack_data[k[0]][6] - 0xB030) / 2)]
                    offset = 0
                elif repack_data[k[0]][6] < 0xB059:
                    item = attack_piece_names[int((repack_data[k[0]][6] - 0xB037) / 2) + 2]
                    offset = 1
                else:
                    item = attack_piece_names[int((repack_data[k[0]][6] - 0xB059) / 2) + 13]
                    offset = 1
                item += " Attack Piece " + str(((repack_data[k[0]][7] >> 0x2) + 1) * ((repack_data[k[0]][6] + offset) % 2 + 1))
            else:
                item = key_item_names[key_item_pool_checked[ab[0]][1]]
        if new_item_locals[s][0] < len(item_local_names):
            room_name = item_local_names[new_item_locals[s][0]]
        else:
            room_name = hex(new_item_locals[s][0])
        spoiler_log.write(room_name + " " + check_type + " " + number + " - " + item + "\n")

    print("Repacking enemy stats...")
    #Repackages randomized enemy stats
    for enemy in range(len(new_enemy_stats)):
        enemy_stats[new_enemy_stats[enemy][0]].hp = new_enemy_stats[enemy][1]
        enemy_stats[new_enemy_stats[enemy][0]].power = new_enemy_stats[enemy][2]
        enemy_stats[new_enemy_stats[enemy][0]].defense = new_enemy_stats[enemy][3]
        enemy_stats[new_enemy_stats[enemy][0]].speed = new_enemy_stats[enemy][4]
        enemy_stats[new_enemy_stats[enemy][0]].exp = new_enemy_stats[enemy][5]
        enemy_stats[new_enemy_stats[enemy][0]].coins = new_enemy_stats[enemy][6]
        enemy_stats[new_enemy_stats[enemy][0]].coin_rate = new_enemy_stats[enemy][7]
        enemy_stats[new_enemy_stats[enemy][0]].item_chance = new_enemy_stats[enemy][8]
        enemy_stats[new_enemy_stats[enemy][0]].item_type = new_enemy_stats[enemy][9]
        enemy_stats[new_enemy_stats[enemy][0]].rare_item_chance = new_enemy_stats[enemy][10]
        enemy_stats[new_enemy_stats[enemy][0]].rare_item_type = new_enemy_stats[enemy][11]
        enemy_stats[new_enemy_stats[enemy][0]].level = new_enemy_stats[enemy][12]
        #print(new_enemy_stats[enemy])
    #Packs enemy stats
    save_enemy_stats(enemy_stats, code_bin=code_bin_path)

    print("Repacking FMap...")
    newlen = 0
    rooms_to_fix = []
    items_to_delete = []
    with fs_std_romfs_path(FMAPDAT_PATH, data_dir=input_folder).open('r+b') as f:
        b = 0
        while b < len(new_item_locals):
            try:
                if new_item_locals[b][3] < 0xC000:
                    f.seek(new_item_locals[b][1])
                    f.write(struct.pack('<HHHHHH', *new_item_locals[b][2:8]))
                if b > 0:
                    if new_item_locals[b-1][0] != new_item_locals[b][0]:
                        if newlen > 0:
                            rooms_to_fix.append([items_to_delete[-1][0], newlen*12])
                        newlen = 0
                if find_index_in_2d_list(repack_data, new_item_locals[b][-1] + 0xD000) is not None:
                    x, y = find_index_in_2d_list(repack_data, new_item_locals[b][-1] + 0xD000)
                    if repack_data[x][0] == 0:
                        items_to_delete.append([new_item_locals[b][0], new_item_locals[b][7]])
                        newlen += 1
                b += 1
            except IndexError:
                break
        t = 0
        for r in range(len(rooms_to_fix)):
            with (
                code_bin_path.open('rb+') as code_bin,
            ):
                version_pair = determine_version_from_code_bin(code_bin)
                code_bin.seek(FMAPDAT_REAL_WORLD_OFFSET_TABLE_LENGTH_ADDRESS[version_pair] + 16 + rooms_to_fix[r][0]*8)
                room_pos = struct.unpack('<I', code_bin.read(4))
                f.seek(room_pos[0] + 7 * 8)
                treasure_pos = struct.unpack('<I', f.read(4))
                treasure_len = struct.unpack('<I', f.read(4))
                while rooms_to_fix[r][0] == items_to_delete[t][0]:
                    p = 0
                    f.seek(room_pos[0] + treasure_pos[0] + 10)
                    f.seek(room_pos[0] + treasure_pos[0] + 10)
                    while struct.unpack('<H', f.read(2))[0] != items_to_delete[t][1]:
                        p += 1
                        f.seek(room_pos[0] + treasure_pos[0] + p*12 + 10)
                    f.seek(room_pos[0] + treasure_pos[0] + p*12 + 12)
                    the_rest = f.read()
                    f.seek(room_pos[0] + treasure_pos[0] + p*12)
                    f.write(the_rest)
                    t += 1
                    if t == len(items_to_delete):
                        break
                if r < len(rooms_to_fix) - 1:
                    if rooms_to_fix[r+1][0] > rooms_to_fix[r][0]:
                        fix_offsets(f, code_bin, rooms_to_fix[r][0], treasure_len[0] - rooms_to_fix[r][1], 7, rooms_to_fix[r+1][0])
                    else:
                        fix_offsets(f, code_bin, rooms_to_fix[r][0], treasure_len[0] - rooms_to_fix[r][1], 7, 0x316)
                else:
                    fix_offsets(f, code_bin, rooms_to_fix[r][0], treasure_len[0] - rooms_to_fix[r][1], 7, 0x316)

    randomize_repack.pack(input_folder, repack_data, settings)

#randomize_data(input_folder, stat_mult)
