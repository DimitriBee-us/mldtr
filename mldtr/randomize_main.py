import struct
import random
from mldtr import randomize_repack
from mnllib.n3ds import fs_std_code_bin_path
from mnllib.dt import load_enemy_stats, save_enemy_stats

#input_folder = 'C:/Users/Dimit/AppData/Roaming/Azahar/load/mods/00040000000D5A00'
#stat_mult = [5, 5]

def get_spot_type(spot):
    if spot[2] == 0x0012 or spot[2] == 0x0013:
        return 5
    elif spot[5] == 0:
        return 1
    elif (spot[6] == 74 or spot[6] == 312 or (303 <= spot[6] <= 306) or
          spot[6] == 312 or  spot[6] == 1522 or spot[6] == 1524 or
          spot[6] == 1581 or (1543 <= spot[6] <= 1545) or spot[6] == 1549 or
          spot[6] == 1567 or (1673 <= spot[6] <= 1675) or spot[6] == 2125 or
          spot[6] == 2398):
        return 3
    return 0

def find_index_in_2d_list(arr, target_value):
    for row_index, row in enumerate(arr):
        for col_index, element in enumerate(row):
            if element == target_value:
                return (row_index, col_index)
    return None  # Return None if the element is not found

def is_available(logic, key):
    #Sets up the variables to check the logic
    available = True
    was_true = False
    multi = [0, 0]
    for d in range(len(logic)-1):
        #Updates hammers if mini or mole mario have been grabbed, along with updating the other if one has been grabbed multiple times
        if (logic[d+1] == 1 or logic[d+1] == 2) and key[logic[d+1]] == 1:
            if key[0] < 1:
                key[0] += 1
                key[logic[d+1]] -= 1
            if key[logic[d+1]] > 1:
                if logic[d+1] == 1:
                    key[2] += 1
                    key[1] -= 1
                else:
                    key[1] += 1
                    key[2] -= 1

        #Updates the tornado if a progressive spin has been grabbed
        if logic[d+1] == 4 and key[logic[d+1]] == 1:
            if key[3] < 1:
                key[3] += 1
                key[4] -= 1

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
            multi = [0, 0]
    if was_true:
        available = True
    return available

def randomize_data(input_folder, stat_mult):
    print("Initializing...")
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
                                         enemy_stats[enemy].item_chance, enemy_stats[enemy].item_type, enemy_stats[enemy].rare_item_chance, enemy_stats[enemy].rare_item_type])
            #Appends data to boss array if it's a boss
            elif (enemy == 17 or enemy == 30 or enemy == 42 or
                  enemy == 62 or enemy == 95 or enemy == 96 or
                  enemy == 107 or enemy == 108):
                boss_stats_rand.append([enemy, enemy_stats[enemy].hp, enemy_stats[enemy].power, enemy_stats[enemy].defense,
                                         enemy_stats[enemy].speed, enemy_stats[enemy].exp, enemy_stats[enemy].coins, enemy_stats[enemy].coin_rate,
                                         enemy_stats[enemy].item_chance, enemy_stats[enemy].item_type, enemy_stats[enemy].rare_item_chance, enemy_stats[enemy].rare_item_type])
            #Appends data to dream enemy array if it's a dream enemy
            elif (enemy == 19 or enemy == 21 or enemy == 31 or
                  enemy == 33 or enemy == 35 or enemy == 45 or
                  enemy == 46 or enemy == 47 or enemy == 49 or
                  enemy == 50 or (64 <= enemy <= 67) or (72 <= enemy <= 78) or
                  enemy == 84 or enemy == 98 or enemy == 99 or
                  (110 <= enemy <= 112) or (121 <= enemy <= 125) or enemy == 133):
                dream_enemy_stats_rand.append([enemy, enemy_stats[enemy].hp, enemy_stats[enemy].power, enemy_stats[enemy].defense,
                                         enemy_stats[enemy].speed, enemy_stats[enemy].exp, enemy_stats[enemy].coins, enemy_stats[enemy].coin_rate,
                                         enemy_stats[enemy].item_chance, enemy_stats[enemy].item_type, enemy_stats[enemy].rare_item_chance, enemy_stats[enemy].rare_item_type])
            #Appends data to dream boss array if it's a dream boss
            elif (enemy == 23 or enemy == 36 or enemy == 52 or
                  (79 <= enemy <= 81) or (126 <= enemy <= 131) or enemy == 137):
                dream_boss_stats_rand.append([enemy, enemy_stats[enemy].hp, enemy_stats[enemy].power, enemy_stats[enemy].defense,
                                         enemy_stats[enemy].speed, enemy_stats[enemy].exp, enemy_stats[enemy].coins, enemy_stats[enemy].coin_rate,
                                         enemy_stats[enemy].item_chance, enemy_stats[enemy].item_type, enemy_stats[enemy].rare_item_chance, enemy_stats[enemy].rare_item_type])
            #Appends data to filler array if it's a "filler" enemy (one used in bosses that only exists for spectacle)
            else:
                filler_stats_rand.append([enemy, enemy_stats[enemy].hp, enemy_stats[enemy].power, enemy_stats[enemy].defense,
                                         enemy_stats[enemy].speed, enemy_stats[enemy].exp, enemy_stats[enemy].coins, enemy_stats[enemy].coin_rate,
                                         enemy_stats[enemy].item_chance, enemy_stats[enemy].item_type, enemy_stats[enemy].rare_item_chance, enemy_stats[enemy].rare_item_type])

    #Logic for real world enemies
    enemy_logic = [[13], [18, 15, 5, -1, 15, 6], [25, 15, 0], [27, 15, 0], [29, 15, 0],
                   [38, 15, 16], [39, 15, 16], [41, 15, 16, 5, -1, 15, 16, 17, 2],
                   [48, 15, 22], [51, 1], [58, 1], [59, 1], [60, 23, 1, -1, 1, 5], [61, 23, 1, 4, 6, -1, 1, 5],
                   [68, 15, 16, 1, -1, 15, 16, 5], [69, 15, 16, 1, -1, 15, 16, 5], [70, 15, 16, 1, -1, 15, 16, 5],
                   [71, 15, 16, 1, -1, 15, 16, 5], [85, 15, -1, 1, 4, 5], [86, 15, -1, 1, 4, 5], [87, 15, -1, 1, 4, 5],
                   [88, 15, -1, 1, 4, 5], [89, 15, -1, 1, 4, 5], [90, 1, 4, 5], [91, 15, 16, 2, 4], [92, 15], [93, 15],
                   [94, 15, 16, 5], [100, 15, 1, 3, 5], [101, 15, 1, 5], [102, 15, 1, 5], [104, 15, 1, 5],
                   [106, 15, 1, 5], [113, 15, 27, 1, 5], [115, 15, 27, 1, 5],
                   [116, 15, 27, 1, 5], [117, 15, 27, 1, 4, 5], [118, 15, 27, 1, 4, 5], [119, 15, 27, 1, 4, 5], [120, 15, 27, 1, 4, 5],]

    #Logic for dream world enemies
    dream_enemy_logic = [[19], [21], [31, 15, 6], [33, 15, 6], [35, 15, 6], [45, 15, 16], [46, 15, 16], [47, 15, 16, 17],
                         [49, 15, 22, 6], [50, 15, 22, 6], [64, 23, 1, 6, -1, 1, 5, 6], [65, 23, 1, 4, 6, 10, -1, 1, 3, 5, 6, 10],
                         [66, 23, 1, 4, 6, 10, -1, 1, 3, 5, 6, 10], [67, 23, 1, 4, 6, 10, -1, 1, 3, 5, 6, 10],
                         [72, 15, 16, 1, 6, -1, 15, 16, 5, 6], [73, 15, 16, 1, 6, -1, 15, 16, 5, 6],
                         [74, 15, 16, 24, 1, 6, -1, 15, 16, 24, 5, 6], [75, 15, 16, 24, 1, 6, -1, 15, 16, 24, 5, 6],
                         [76, 15, 16, 24, 25, 1, 6, -1, 15, 16, 24, 25, 5, 6], [77, 15, 16, 1, 6, -1, 15, 16, 5, 6],
                         [78, 15, 16, 1, 6, -1, 15, 16, 5, 6], [84, 6], [98, 22, 1, 2, 4, 5, 6], [99, 22, 1, 2, 4, 5, 6],
                         [110, 15, 1, 3, 5, 6], [111, 15, 1, 3, 5, 6], [112, 15, 1, 2, 3, 5, 6],  [121, 15, 27, 1, 5, 6],
                         [122, 15, 27, 1, 4, 5, 6], [123, 15, 27, 1, 4, 5, 6], [124, 15, 27, 1, 5, 6], [125, 15, 27, 1, 5, 6], [133, 15, 27, 1, 4, 5, 6],]

    #Logic for bosses
    boss_logic = [[17, 14], [30, 15], [42, 15, 16, 17, 18, 19, 20, 21], [62, 23, 1, 4, 6, -1, 1, 5],
                  [95, 15, 22, 5], [96, 15, 22, 5], [107, 15, 1, 2, 3, 5, 6], [108, 15, 1, 2, 3, 5, 6],]

    #Logic for dream world bosses
    dream_boss_logic = [[23], [36, 15, 6], [52, 15, 22, 6], [79, 15, 16, 24, 25, 26, 1, 4, 6, -1, 15, 16, 24, 25, 26, 4, 5, 6],
                        [80, 15, 16, 24, 25, 26, 1, 4, 6, -1, 15, 16, 24, 25, 26, 4, 5, 6], [81, 15, 16, 24, 25, 26, 1, 4, 6, -1, 15, 16, 24, 25, 26, 4, 5, 6],
                        [126, 15, 27, 1, 5, 6], [127, 15, 27, 1, 4, 5, 6], [128, 15, 27, 1, 4, 5, 6], [129, 15, 27, 1, 4, 5, 6], [130, 15, 27, 1, 4, 5, 6],
                        [131, 15, 27, 1, 4, 5, 6], [137, 15, 27, 1, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],]

    #Logic for "filler" enemies
    filler_logic = [[37, 15, 6], [57, 15, 22, 6], [82, 15, 16, 24, 25, 26, 1, 4, 6, -1, 15, 16, 24, 25, 26, 4, 5, 6],
                    [109, 15, 1, 2, 3, 5, 6], [138, 15, 27, 1, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],]

    # Opens the FMapDat.dat file
    with open(input_folder + '/romfs/FMap/FMapDat.dat', 'rb') as f:
        itemdata = f.read()

    #Initializes the item pool
    item_pool = []

    # Creates an item_data array with all the blocks and bean spots
    item_locals = []
    for i in range(2216):
        offset = 0
        room = 0
        if i < 2:
            offset = 0x00002964
            room = 0x000
        elif i < 11:
            offset = 0x00069D70 - 24
            room = 0x001
        elif i < 13:
            offset = 0x00152B30 - (12 * 11)
            room = 0x002
        elif i < 15:
            offset = 0x001DED24 - (12 * 13)
            room = 0x003
        elif i < 17:
            offset = 0x002366C8 - (12 * 15)
            room = 0x004
        elif i < 21:
            offset = 0x002C2AC0 - (12 * 17)
            room = 0x005
        elif i < 27:
            offset = 0x00364A34 - (12 * 21)
            room = 0x006
        elif i < 35:
            offset = 0x003E5E30 - (12 * 27)
            room = 0x007
        elif i < 40:
            offset = 0x004C3044 - (12 * 35)
            room = 0x008
        elif i < 42:
            offset = 0x0054794C - (12 * 40)
            room = 0x009
        elif i < 52:
            offset = 0x005EFC20 - (12 * 42)
            room = 0x00A
        elif i < 61:
            offset = 0x00692DB0 - (12 * 52)
            room = 0x00B
        elif i < 64:
            offset = 0x0074123C - (12 * 61)
            room = 0x00C
        elif i < 65:
            offset = 0x0082C2AC - (12 * 64)
            room = 0x00E
        elif i < 70:
            offset = 0x008DFAAC - (12 * 65)
            room = 0x010
        elif 73 < i < 81:
            offset = 0x00A4C790 - (12 * 74)
            room = 0x013
        elif i < 87:
            offset = 0x00B121B4 - (12 * 81)
            room = 0x014
        elif i < 93:
            offset = 0x00B87490 - (12 * 87)
            room = 0x015
        elif i < 97:
            offset = 0x00CD32B0 - (12 * 93)
            room = 0x017
        elif i < 99:
            offset = 0x00D2BAA8 - (12 * 97)
            room = 0x018
        elif i < 106:
            offset = 0x00E0160C - (12 * 99)
            room = 0x019
        elif i < 108:
            offset = 0x00EC3010 - (12 * 106)
            room = 0x01A
        elif i < 110:
            offset = 0x00EF951C - (12 * 108)
            room = 0x01B
        elif i < 114:
            offset = 0x01087128 - (12 * 110)
            room = 0x020
        elif i < 116:
            offset = 0x010C0524 - (12 * 114)
            room = 0x021
        elif i < 117:
            offset = 0x010F5358 - (12 * 116)
            room = 0x022
        elif i < 119:
            offset = 0x0112A494 - (12 * 117)
            room = 0x023
        elif i < 127:
            offset = 0x01144664 - (12 * 119)
            room = 0x024
        elif i < 128:
            offset = 0x0119A374 - (12 * 127)
            room = 0x025
        elif i < 130:
            offset = 0x01251ED0 - (12 * 128)
            room = 0x028
        elif i < 131:
            offset = 0x012C7254 - (12 * 130)
            room = 0x029
        elif i < 132:
            offset = 0x0131D2E8 - (12 * 131)
            room = 0x02A
        elif i < 133:
            offset = 0x0134AE68 - (12 * 132)
            room = 0x02B
        elif i < 134:
            offset = 0x01385D10 - (12 * 133)
            room = 0x02C
        elif i < 136:
            offset = 0x013BB514 - (12 * 134)
            room = 0x02D
        elif i < 137:
            offset = 0x013D267C - (12 * 136)
            room = 0x02E
        elif i < 140:
            offset = 0x0144311C - (12 * 137)
            room = 0x031
        elif i < 143:
            offset = 0x014D2594 - (12 * 140)
            room = 0x033
        elif i < 145:
            offset = 0x015409A4 - (12 * 143)
            room = 0x034
        elif i < 149:
            offset = 0x0161BB40 - (12 * 145)
            room = 0x035
        elif i < 155:
            offset = 0x017074D8 - (12 * 149)
            room = 0x036
        elif 156 < i < 160:
            offset = 0x0189E470 - (12 * 156)
            room = 0x038
        elif i < 166:
            offset = 0x0196F0D8 - (12 * 160)
            room = 0x039
        elif i < 170:
            offset = 0x01A47D68 - (12 * 166)
            room = 0x03A
        elif i < 171:
            offset = 0x01ADED58 - (12 * 170)
            room = 0x03B
        elif i < 172:
            offset = 0x01B5592C - (12 * 171)
            room = 0x03C
        elif i < 173:
            offset = 0x01B8A054 - (12 * 172)
            room = 0x03D
        elif i < 174:
            offset = 0x01BA8738 - (12 * 173)
            room = 0x03E
        elif i < 175:
            offset = 0x01BDD62C - (12 * 174)
            room = 0x03F
        elif i < 179:
            offset = 0x01DE1220 - (12 * 175)
            room = 0x047
        elif i < 180:
            offset = 0x01E8EA9C - (12 * 179)
            room = 0x048
        elif i < 182:
            offset = 0x01F3DD88 - (12 * 180)
            room = 0x049
        elif i < 186:
            offset = 0x02000448 - (12 * 182)
            room = 0x04A
        elif i < 189:
            offset = 0x0207802C - (12 * 186)
            room = 0x04B
        elif i < 194:
            offset = 0x02114498 - (12 * 189)
            room = 0x04C
        elif i < 198:
            offset = 0x021CE2CC - (12 * 194)
            room = 0x04D
        elif i < 202:
            offset = 0x022ADA10 - (12 * 198)
            room = 0x04F
        elif i < 220:
            offset = 0x024F1410 - (12 * 216)
            room = 0x56
        elif i < 224:
            offset = 0x025A9B58 - (12 * 220)
            room = 0x58
        elif i < 226:
            offset = 0x027170E4 - (12 * 224)
            room = 0x5B
        elif i < 231:
            offset = 0x027860F0 - (12 * 226)
            room = 0x5C
        elif i < 236:
            offset = 0x0281BB18 - (12 * 231)
            room = 0x5D
        if i < 236 and (i < 70 or i > 73) and i != 154 and (i < 202 or i > 215):
            offset = offset + (i * 12)
            item_locals.append([room, offset, itemdata[offset + 0x1] * 0x100 + itemdata[offset],
                                itemdata[offset + 0x5] * 0x100 + itemdata[offset + 0x4],
                                itemdata[offset + 0x7] * 0x100 + itemdata[offset + 0x6],
                                itemdata[offset + 0x9] * 0x100 + itemdata[offset + 0x8],
                                itemdata[offset + 0xB] * 0x100 + itemdata[offset + 0xA]])

            item_pool.append([itemdata[offset + 0x1] * 0x100 + itemdata[offset],
                             itemdata[offset + 0x3] * 0x100 + itemdata[offset + 0x2]])

    #for item in item_locals:
    #   print(str(item) + "\n")

    #Logic for every single block and bean spot (The numbers after the ID point to their spots in the ability info)
    item_logic = [[52, 15, 5], [53, 15, 5], [54, 15], [55, 15, 0, -1, 15, 5], [56, 15, 0], [57, 15, 0], [58, 15], [59, 15, 2], [60, 15, 2],
                  [61, 15, 0, 2], [2388, 15, 2], [62, 15, 0], [63, 15, 0], [64, 15, 0], [65, 15, 0], [66, 15, 0], [67, 15, 2, 3, -1, 15, 2, 5],
                  [68, 15, 0], [69, 15, 0], [70, 15, 0], [71, 15, 0], [72, 15], [73, 15], [74, 15, 16, 1], [75, 15, 16, 2], [76, 15, 2], [77, 15, 2],
                  [78, 15, 0], [79, 15], [80, 15], [81, 15], [82, 15, 2], [83, 15, 2], [84, 15, 2], [85, 15, 2, 3, 0, 15, 2, 5], [86, 15, 4],
                  [87, 15], [88, 15], [89, 15, 4], [90, 15, 2], [91, 15, 0], [92, 15, 0, 1, 5, -1, 15, 0, 1, 3], [2389, 15, 0, 4, 5], [94, 15, 0, 4, 5],
                  [95, 15, 0, 4, 5], [96, 15, 0, 4, 5], [97, 15, 0, 4, 5], [98, 15, 0, 4, 5], [99, 15, 0, 2, 4, 5], [100, 15, 0, 2, 4, 5],
                  [101, 15, 0, 2, 4, 5], [102, 15, 0, 2, 4, 5], [103, 15], [104, 15], [107, 15], [2390, 15, 0], [2391, 15, 0],
                  [108, 15, 0, 2], [109, 15, 0, 2], [110, 15, 0, 2], [111, 15, 0, 2], [112, 15, 0], [113, 15, 0], [114, 15, 0],

                  [253, 15, 16, 2], [271, 15, 16, 17, 2, -1, 15, 16, 2, 5], [272, 15, 16, 17, 2, -1, 15, 16, 2, 5], [273, 15, 16, 17, 2, -1, 15, 16, 2, 5],
                  [274, 15, 16, 17, 2, -1, 15, 16, 2, 5], [275, 15, 16, 17, 2, -1, 15, 16, 2, 5], [285, 15, 16, 17, 2, -1, 15, 16, 2, 5], [286, 15, 16, 17, 2, -1, 15, 16, 2, 5],
                  [287, 15, 16, 17, 2, -1, 15, 16, 2, 5, -1, 15, 16, 17, 1, -1, 15, 16, 1, 5], [288, 15, 16, 17, 2, -1, 15, 16, 2, 5, -1, 15, 16, 17, 1, -1, 15, 16, 1, 5],
                  [289, 15, 16, 17, 2, -1, 15, 16, 2, 5, -1, 15, 16, 17, 1, -1, 15, 16, 1, 5], [290, 15, 16, 17, 2, -1, 15, 16, 2, 5, -1, 15, 16, 17, 1, -1, 15, 16, 1, 5],
                  [291, 15, 16, 17, 2, -1, 15, 16, 2, 5, -1, 15, 16, 17, 1, -1, 15, 16, 1, 5], [292, 15, 16, 17, 2, -1, 15, 16, 2, 5],
                  [293, 15, 16, 17, 2, -1, 15, 16, 2, 5, -1, 15, 16, 17, 1, -1, 15, 16, 1, 5], [294, 15, 16, 17, 2, -1, 15, 16, 2, 5],
                  [295, 15, 16, 17, 2, -1, 15, 16, 2, 5], [296, 15, 16, 17, 2, -1, 15, 16, 2, 5], [2373, 15, 16, 17, 2, -1, 15, 16, 2, 5, -1, 15, 16, 17, 1, -1, 15, 16, 1, 5],
                  [297, 15, 16, 17, 2, -1, 15, 16, 2, 5], [298, 15, 16, 17, 2, -1, 15, 16, 2, 5], [299, 15, 16, 17, 2, -1, 15, 16, 2, 5],
                  [300, 15, 16, 17, 2, -1, 15, 16, 2, 5, -1, 15, 16, 17, 1, -1, 15, 16, 1, 5], [301, 15, 16, 17, 2, -1, 15, 16, 2, 5, -1, 15, 16, 17, 1, -1, 15, 16, 1, 5],
                  [302, 15, 16, 17, 1, -1, 15, 16, 1, 5], [303, 15, 16, 17, 1, -1, 15, 16, 1, 5], [304, 15, 16, 17, 1, -1, 15, 16, 1, 5],
                  [305, 15, 16, 17, 1, -1, 15, 16, 1, 5], [306, 15, 16, 17, 1, -1, 15, 16, 1, 5],

                  [115, 15, 0], [116, 15, 0, 3], [307, 15, 16, 17, 2, -1, 15, 16, 2, 5], [308, 15, 16, 1, 5, -1, 15, 16, 2, 5], [309, 15, 16, 17, 2, -1, 15, 16, 2, 5],
                  [310, 15, 16, 17, 2, -1, 15, 16, 2, 5, -1, 15, 16, 17, 1, -1, 15, 16, 1, 5], [311, 15, 16, 17, 2, -1, 15, 16, 2, 5, -1, 15, 16, 17, 1, -1, 15, 16, 1, 5],
                  [312, 15, 16, 17, 1, -1, 15, 16, 1, 5], [2374, 15, 16, 1, 5, -1, 15, 16, 2, 5], [313, 15, 16, 3, 5], [314, 15, 16, 3, 5], [15], [16, 2],

                  [119, 15, 6], [121, 15, 6], [123, 15, 6], [125, 15, 6], [127, 15, 6], [129, 15, 6], [131, 15, 6], [132, 15, 6], [2392, 15, 6],
                  [134, 15, 6], [135, 15, 6], [136, 15, 6], [137, 15, 6], [138, 15, 6], [139, 15, 6], [140, 15, 6], [141, 15, 6], [142, 15, 6],
                  [2393, 15, 6], [144, 15, 6], [145, 15, 6], [146, 15, 6], [147, 15, 6], [152, 15, 6], [2394, 15, 6], [2395, 15, 6], [151, 15, 6],
                  [153, 15, 27, 1, 6, 7], [154, 15, 27, 1, 6, 7], [155, 15, 27, 1, 6, 7],

                  [1511, 15, 3], [1512, 15, 2, 3], [1513, 15, 2, 3], [1514, 15, 22], [1515, 15, 22, 2], [1516, 15, 22, 2, 5],
                  [1517, 15, 22, 2], [1518, 15, 22, 2], [1519, 15, 22], [1520, 15, 22, 2], [1521, 15, 22, 2], [1522, 15, 22, 1], [1523, 15, 22],
                  [1524, 15, 22, 1], [1525, 15, 22, 2], [1549, 15, 16, 1], [1550, 15, 16], [1551, 15, 16, 1], [1552, 15, 16, 2], [1527, 15, 22],
                  [1528, 15, 22], [1529, 15, 22], [1530, 15, 22], [1531, 15, 22], [1532, 15, 22], [1553, 15, 16, 1], [1554, 15, 16, 1, 3],
                  [2331, 15, 16, 1, 3], [2332, 15, 16, 1, 3], [1562, 15, 16, 1, 3], [1539, 15, 22, 3], [1540, 15, 22], [1541, 15, 22], [1542, 15, 22],
                  [1566, 15, 16, 1, 3], [1567, 15, 16, 1, 3], [1568, 15, 16, 1, 3], [1569, 15, 16, 1, 3], [1570, 15, 16, 1, 3, 5], [1571, 15, 16, 1, 2, 3],
                  [1572, 15, 16, 1, 2, 3], [1543, 15, 16, 1], [1544, 15, 16, 1], [1545, 15, 16, 1], [2398, 15, 16, 1], [2399, 15, 16],
                  [1547, 15, 16], [1548, 15, 16, 2], [1555, 15, 16, 1, 4], [1556, 15, 16, 1, 4], [1557, 15, 16, 1, 2, 4], [2400, 15, 16, 1, 2, 4],
                  [1558, 15, 16, 1, 3], [1559, 15, 16, 1, 3], [1560, 15, 16, 1, 2, 3], [1561, 15, 16, 1, 2, 3], [2401, 15, 16, 1, 2, 3],
                  [1563, 15, 16, 1, 4, -1, 15, 16, 3, 5], [1564, 15, 16, 1, 4, -1, 15, 16, 3, 5], [1565, 15, 16, 1, 2, 4, -1, 15, 16, 2, 4, 5],
                  [988, 15, 16, 1, 2, 4, -1, 15, 16, 2, 3, 5],

                  [7], [8], [9], [10], [11], [12], [13], [14], [17], [18, 2], [19], [20, 2], [21, 2], [22, 2], [23, 2],

                  [254, 15, 16, 2], [255, 15, 16, 17, 18, 19, 20, 21, 1, 2, -1, 15, 16, 5], [256, 15, 16], [257, 15, 16], [258, 15, 16],]

    #Creates an array with the ability info
    key_item_info = [0x001, 0x012, -1, 0x06C, 0x075, 0x10C, 0x13D, 0x0F5, 0x0C6, -1, 0x1E7, 0x1F8, 0x0F6, 0x0FA,
                     -1, -1, -1, 0x13E, 0x0B2, 0x0B5, 0x0B6, 0x0B7, -1, -1, 0x177, 0x17A, 0x17D, -1]

    #Creates an item pool for the key items
    key_item_pool = [[0xE000, random.randint(1, 2)], [0xE001, 1], [0xE002, 2], [0xE004, 4], [0xE004, 4], [0xE005, 5], [0xE00A, 6], [0xE00D, 7],
                     [0xE00E, 8], [0xE00F, 9], [0xE010, 10], [0xE011, 11], [0xE012, 12], [0xE013, 13], [0xE075, 14], [0xC369, 15],
                     [0xCABF, 16], [0xE0A0, 17], [0xC343, 18], [0xC344, 19], [0xC345, 20], [0xC346, 21], [0xC960, 22], [0xC3B9, 23],
                     [0xB0F7, 24], [0xB0F7, 25], [0xB0F7, 26], [0xC47E, 27]]

    #Checked array for the key items
    key_item_check = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    #Creates an array with the key item logic
    key_item_logic = [[0x001, 15], [0x012, 15, 16], [-1], [0x06C, 0, 23, -1, 0, 5], [0x075, 0, 23, 3, 10, -1, 0, 5, 10],
                      [0x10C, 0, 4, 23, -1, 0, 4, 5], [0x13D, 15, 16], [0x0F5, 6], [0x0C6, 15, 16, 17, 18, 19, 20, 21, 6, -1, 15, 16, 5, 6],
                      [-1], [0x1E7, 23, 0, 6, -1, 0, 5, 6], [0x1F8, 23, 0, 4, 6, 10, -1, 23, 0, 3, 5, 6, 10], [0x0F6, 6, 7], [0x0FA, 6, 7, 12],
                      [-1], [-1], [-1], [0x13E, 15, 16, 6], [0x0B2, 15, 16, 17, -1, 15, 16, 5], [0x0B5, 15, 16, 17, 1, -1, 15, 16, 1, 5, -1, 15, 16, 17, 2, -1, 15, 16, 2, 5],
                      [0x0B6, 15, 16, 17, 2, -1, 15, 16, 2, 5], [0x0B7, 15, 16, 17, 1, -1, 15, 16, 1, 5, -1, 15, 16, 17, 2, -1, 15, 16, 2, 5],
                      [-1], [-1], [0x177, 15, 16, 1, 2, 4, 6], [0x17A, 15, 16, 1, 4, 6], [0x17D, 15, 16, 1, 4, 6], [-1]]

    #Creates an array with the attack piece info
    attack_piece_info = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1,]

    attack_piece_logic = [[0x004, 0x02, 15, 0], [0x004, 0x04, 15, 0], [0x004, 0x08, 15, 0], [0x004, 0x0F, 15, 0],
                         [0x005, 0x01, 15, 0], [0x005, 0x02, 15, 0], [0x005, 0x04, 15, 0], [0x005, 0x08, 15, 0],]

    #Creates an item pool with the attack pieces
    attack_piece_pool = [[0x01, 0xB030], [0x02, 0xB030], [0x04, 0xB030], [0x08, 0xB030], [0x10, 0xB030], [0x01, 0xB031],
                         [0x02, 0xB031], [0x04, 0xB031], [0x08, 0xB031], [0x10, 0xB031]]

    print("Randomizing...")
    new_item_locals = []

    #[Trigger type, Room ID, X Pos, Y Pos, Z Pos, Collectible/Cutscene ID, Ability/Item/Key Item/Attack(, Attack Piece ID/Coin Amount/Item Cutscene/Hammer or Spin Cutscene, Coin Cutscene)]
    repack_data = []
    itemcut = 0
    attackcut = 0
    key_item_pool_checked = []
    new_enemy_stats = []

    while len(item_pool) + len(key_item_pool) + len(attack_piece_pool) > 0:
        prevlen = len(item_pool) + len(key_item_pool) + len(attack_piece_pool)
        item_logic_len = len(item_logic)
        for i in range(item_logic_len):
            try:
                if len(item_locals) > 0:
                    if is_available(item_logic[i], key_item_check):
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
                            nitem = random.randint(0, len(attack_piece_pool) - 1)
                            narray = [item_locals[i][0], item_locals[i][1], item_locals[i][2], 0,
                                    item_locals[i][3], item_locals[i][4], item_locals[i][5], item_locals[i][6]]
                            new_item_locals.append(narray)
                            spottype = get_spot_type(item_locals[i])
                            repack_data.append([spottype, item_locals[i][0], item_locals[i][3], item_locals[i][4], item_locals[i][5], item_locals[i][6] + 0xD000,
                                                attack_piece_pool[nitem][1], attack_piece_pool[nitem][0], 0xCD20 + attackcut])
                            attackcut += 1
                            del attack_piece_pool[nitem]
                            del item_locals[i]
                            del item_logic[i]
            except IndexError:
                break
        for i in range(len(key_item_info)):
            if len(key_item_info) > 0:
                try:
                    if key_item_info[i] > -1:
                        if is_available(key_item_logic[i], key_item_check):
                            rand_array = random.randint(0, 1)
                            if rand_array == 0 and len(item_pool) > 0:
                                # Code for if a block or bean spot's contents are in an ability cutscene
                                nitem = random.randint(0, len(item_pool) - 1)
                                if (item_pool[nitem][1] != 0x0000 and item_pool[nitem][1] != 0x0002 and
                                        item_pool[nitem][1] != 0x0004 and item_pool[nitem][1] != 0x0006 and item_pool[nitem][1] != 0x0008):
                                    repack_data.append(
                                        [6, key_item_info[i], 0, 0, 0, 0xC0A0 + itemcut, item_pool[nitem][1],
                                         0xC0A0 + itemcut])
                                else:
                                    repack_data.append(
                                        [6, key_item_info[i], 0, 0, 0, 0xC0A0 + itemcut, item_pool[nitem][1], 1 + 9 * (item_pool[nitem][0] // 0xA0 % 2),
                                         0xC0A0 + itemcut])
                                itemcut += 1
                                del item_pool[nitem]
                                del key_item_info[i]
                                del key_item_logic[i]
                            elif len(attack_piece_pool) > 0:
                                # Code for if an attack is in an ability cutscene
                                nitem = random.randint(0, len(attack_piece_pool) - 1)
                                repack_data.append(
                                    [6, key_item_info[i], 0, 0, 0, 0xCD20 + attackcut, attack_piece_pool[nitem][1],
                                     attack_piece_pool[nitem][0], 0xCD20 + attackcut])
                                attackcut += 1
                                del attack_piece_pool[nitem]
                                del key_item_info[i]
                                del key_item_logic[i]
                except IndexError:
                    break
        #Randomizes enemy stats
        for i in range(len(enemy_logic)):
            if len(enemy_logic) > 0:
                try:
                    if is_available(enemy_logic[i], key_item_check):
                        temp = enemy_stats_rand[i]
                        for n in range(len(enemy_stats_rand[0])-1):
                            enemy_stats_rand[i][n+1] = enemy_stats_rand[0][n+1]
                            enemy_stats_rand[0][n+1] = temp[n+1]
                        new_enemy_stats.append(enemy_stats_rand[i])
                        del enemy_stats_rand[i]
                        del enemy_logic[i]
                except IndexError:
                    break
        for i in range(len(boss_logic)):
            if len(boss_logic) > 0:
                try:
                    if is_available(boss_logic[i], key_item_check):
                        temp = boss_stats_rand[i]
                        for n in range(len(boss_stats_rand[0])-1):
                            boss_stats_rand[i][n+1] = boss_stats_rand[0][n+1]
                            boss_stats_rand[0][n+1] = temp[n+1]
                        new_enemy_stats.append(boss_stats_rand[i])
                        del boss_stats_rand[i]
                        del boss_logic[i]
                except IndexError:
                    break
        for i in range(len(dream_enemy_logic)):
            if len(dream_enemy_logic) > 0:
                try:
                    if is_available(dream_enemy_logic[i], key_item_check):
                        temp = dream_enemy_stats_rand[i]
                        for n in range(len(dream_enemy_stats_rand[0])-1):
                            dream_enemy_stats_rand[i][n+1] = dream_enemy_stats_rand[0][n+1]
                            dream_enemy_stats_rand[0][n+1] = temp[n+1]
                        new_enemy_stats.append(dream_enemy_stats_rand[i])
                        del dream_enemy_stats_rand[i]
                        del dream_enemy_logic[i]
                except IndexError:
                    break
        for i in range(len(dream_boss_logic)):
            if len(dream_boss_logic) > 0:
                try:
                    if is_available(dream_boss_logic[i], key_item_check):
                        temp = dream_boss_stats_rand[i]
                        for n in range(len(dream_boss_stats_rand[0])-1):
                            dream_boss_stats_rand[i][n+1] = dream_boss_stats_rand[0][n+1]
                            dream_boss_stats_rand[0][n+1] = temp[n+1]
                        new_enemy_stats.append(dream_boss_stats_rand[i])
                        del dream_boss_stats_rand[i]
                        del dream_boss_logic[i]
                except IndexError:
                    break
        for i in range(len(filler_logic)):
            if len(filler_logic) > 0:
                try:
                    if is_available(filler_logic[i], key_item_check):
                        temp = filler_stats_rand[i]
                        for n in range(len(filler_stats_rand[0])-1):
                            filler_stats_rand[i][n+1] = filler_stats_rand[0][n+1]
                            filler_stats_rand[0][n+1] = temp[n+1]
                        new_enemy_stats.append(filler_stats_rand[i])
                        del filler_stats_rand[i]
                        del filler_logic[i]
                except IndexError:
                    break
        # Checks if more items can be randomized
        if prevlen <= len(item_pool) + len(key_item_pool) + len(attack_piece_pool) and len(key_item_pool) > 0 and len(new_item_locals) > 0:
            if len(key_item_pool) > 0:
                can_key = False
                for i in range(len(new_item_locals)):
                    if new_item_locals[i][3] != 0:
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
                        del repack_data[attack_spot[0]]
                    else:
                        item_pool.append([new_item_locals[0][2], new_item_locals[0][3]])
                    item_locals.append([new_item_locals[0][0], new_item_locals[0][1], new_item_locals[0][2],
                                        new_item_locals[0][4], new_item_locals[0][5], new_item_locals[0][6],
                                        new_item_locals[0][7]])
                    item_logic.append([0])
                    del new_item_locals[0]

        #Swaps a coin with whatever is left in the item pool
        if (len(item_pool) > 0 or len(attack_piece_pool) > 0) and len(item_locals) == 0:
            item = 0
            while new_item_locals[item][3] != 0:
                item += 1
            item_locals.append([new_item_locals[item][0], new_item_locals[item][1], new_item_locals[item][2], new_item_locals[item][4], new_item_locals[item][5], new_item_locals[item][6], new_item_locals[item][7]])
            item_logic.append([0, 0])

    #hammer_local = find_index_in_2d_list(repack_data, 0xE001)
    #print(repack_data[hammer_local[0]])

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
    #Packs enemy stats
    save_enemy_stats(enemy_stats, code_bin=code_bin_path)

    print("Repacking FMap...")
    for b in new_item_locals:
        if b[3] < 0xC000:
            itemdata = itemdata[:b[1]] + struct.pack('<HHHHHH',b[2], b[3], b[4], b[5], b[6], b[7]) + itemdata[b[1]+12:]

    with open(input_folder + '/romfs/FMap/FMapDat.dat', 'wb') as f:
        f.write(itemdata)

    randomize_repack.pack(input_folder, repack_data)

#randomize_data(input_folder, stat_mult)