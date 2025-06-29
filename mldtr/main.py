# Imports the necessary modules
import os.path
import functools
from mldtr import randomize_music, randomize_main

#Import modules for later use
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo

def get_folder(window):
    # Grabs a folder
    window.romfs = fd.askdirectory(
        title='Open Dumped Game Directory',
        initialdir='/', )

    # Either allows the options to work, or says they can't
    if os.path.isfile(window.romfs + "/exefs/code.bin"):
        window.option_2.config(state="normal")
        window.songdir_button.config(state="normal")
        window.generate.config(state="normal")
    else:
        showinfo(
            "Whoops!",
            "Couldn't find your exefs"
        )
        window.option_2.config(state="disabled")
        window.option_3.config(state="disabled")
        window.songdir_button.config(state="disabled")


def get_song_folder(window):
    # Grabs a folder
    songdir = fd.askdirectory(
        title='Open Custom Song Folder',
        initialdir='/', )

    # Adds all .rsd files into the array
    for root, _, files in os.walk(songdir):
        for file in files:
            file_path = os.path.join(root, file)
            if file_path[len(file_path) - 4:len(file_path)] == ".rsd":
                if file[0:5] == "AREA_":
                    window.all_songs[0].append(file_path)
                elif file[0:7] == "BATTLE_":
                    window.all_songs[1].append(file_path)
                elif file[0:9] == "CUTSCENE_":
                    window.all_songs[2].append(file_path)
                elif file[0:5] == "MENU_":
                    window.all_songs[3].append(file_path)
                elif file[0:9] == "MINIGAME_":
                    window.all_songs[4].append(file_path)
                elif not (file[0:13] == "STRBGM_JINGLE"):
                    window.all_songs[5].append(file_path)

    # Either allows the options to work, or says they can't
    if (len(window.all_songs[0]) + len(window.all_songs[1]) + len(window.all_songs[2])
            + len(window.all_songs[3]) + len(window.all_songs[4]) + len(window.all_songs[5]) >= 52):
        window.option_3.config(state="normal")
    else:
        showinfo(
            "Whoops!",
            "Couldn't find enough .rsd files.\nYou need at least 52 to use this."
        )
        window.option_3.config(state="disabled")


def can_check(window):
    # Checks if the checkbox is available or not
    if (window.option.get() == 0 or (
            window.option.get() == 2 and (len(window.all_songs[0]) < 25 or len(window.all_songs[1]) < 6
                                          or len(window.all_songs[2]) < 15 or len(window.all_songs[3]) < 5 or len(
                window.all_songs[4]) < 1))):
        window.category_check.config(state="disabled")
        window.categorize.set(False)
    else:
        window.category_check.config(state="normal")


def help():
    # Idk why I had to make this but ok, sure
    showinfo("Categorize Help",
             "You can't categorize with no randomization.\n" +
             "Also, if your custom song directory can't be categorized, you need:\n" +
             "- At least 25 songs beginning in \"AREA_\"\n" +
             "- At least 6 songs beginning in \"BATTLE_\"\n" +
             "- At least 15 songs beginning in \"CUTSCENE_\"\n" +
             "- At least 5 songs beginning in \"MENU_\"\n" +
             "- At least one song beginning in \"MINIGAME_\"")


def randomize(window):
    # Sets enemy stats to what you selected
    window.enemy_stats[0] = 1
    if window.attack_mode.get() == "0.5x - Easy":
        window.enemy_stats[0] = 0.5
    if window.attack_mode.get() == "1x - Normal":
        window.enemy_stats[0] = 1
    if window.attack_mode.get() == "2x - Hard":
        window.enemy_stats[0] = 2
    if window.attack_mode.get() == "3x - Very Hard":
        window.enemy_stats[0] = 3
    if window.attack_mode.get() == "5x - Good Luck":
        window.enemy_stats[0] = 5
    if window.attack_mode.get() == "Maxed Out - The Perfect Run":
        window.enemy_stats[0] = -1

    window.enemy_stats[1] = 2
    if window.exp_mode.get() == "0.5x - Grinder's Delight":
        window.enemy_stats[1] = 0.5
    if window.exp_mode.get() == "1x - Normal":
        window.enemy_stats[1] = 1
    if window.exp_mode.get() == "2x - Quick Level":
        window.enemy_stats[1] = 2
    if window.exp_mode.get() == "5x - Rapid Level":
        window.enemy_stats[1] = 5
    if window.exp_mode.get() == "10x - Enemies are Overrated":
        window.enemy_stats[1] = 10

    # Begins randomization
    randomize_main.randomize_data(window.romfs, window.enemy_stats)
    if window.option.get() == 2:
        print("Randomizing custom music...")
        randomize_music.import_random(5, window.romfs, window.all_songs, window.categorize.get())
    if window.option.get() == 1:
        print("Randomizing music...")
        randomize_music.shuffle(window.romfs, window.categorize.get())
    print("Done!")
    showinfo("Yay!", "Success!")


# Shows credits
def credit():
    # Credits for the license and my peers who helped me
    showinfo("Categorize Help",
             "This program is made under the GNU General Public License v3.0.\n" +
             "UI design and general coding: Dimitri Bee\n" +
             "FMap data and some cutscene flags: Pixiuchu\n" +
             "Mnlscript and some pointers: DimiDimit\n\n")

def main():
    # Create the window
    window = tk.Tk()
    window.title("MLDT Randomizer")
    window.resizable(False, False)
    window.geometry("450x450")

    # Initialize some variables
    window.romfs = tk.StringVar()
    window.option = tk.IntVar()
    nubValues = ["No Randomization", 0,
                 "Base Game Songs Only", 1,
                 "Songs from Directory", 2]
    window.all_songs = [[], [], [], [], [], []]
    window.categorize = tk.BooleanVar()
    window.enemy_stats = [1, 2]
    window.attack_mode = tk.StringVar()
    window.attack_mode.set("1x - Normal")
    window.attack_options = ["0.5x - Easy", "1x - Normal", "2x - Hard", "3x - Very Hard", "5x - Good Luck",
                             "Maxed Out - The Perfect Run"]
    window.exp_mode = tk.StringVar()
    window.exp_mode.set("2x - Quick Level")
    window.exp_options = ["0.5x - Grinder's Delight", "1x - Normal", "2x - Quick Level", "5x - Rapid Level",
                          "10x - Enemies are Overrated"]
    #Creates tabs
    window.menu = ttk.Notebook(window)
    tabMain = ttk.Frame(window.menu)
    tabEnemy = ttk.Frame(window.menu)
    tabMusic = ttk.Frame(window.menu)

    #Names tabs
    window.menu.add(tabMain, text = "Main")
    window.menu.add(tabEnemy, text = "Enemy")
    window.menu.add(tabMusic, text = "Music")
    window.menu.pack(expand = 1, fill = "both", pady=40)

    # Press button to open RomFS
    window.romfs_button = ttk.Button(
        window,
        text='Open Dump',
        command = functools.partial(get_folder, window)
    )
    window.romfs_button.place(x=10, y=10)

    # Generates the file
    window.generate = ttk.Button(
        window,
        text = 'Generate',
        command = functools.partial(randomize, window),
        state = "disabled"
    )
    window.generate.place(x=185, y=410)

    #Shows credits if clicked on
    window.show_credits = ttk.Button(
        window,
        text = 'Credits',
        command = credit
    )
    window.show_credits.place(x=360, y=10)

    #Lets you decide options for enemy attack
    window.enemy_attack = ttk.OptionMenu(
        tabEnemy,
        window.attack_mode,
        window.attack_options[1],
        *window.attack_options
    )
    window.enemy_attack.place(x=160, y=100)

    #Lets you decide options for experience gained in battle
    window.enemy_exp = ttk.OptionMenu(
        tabEnemy,
        window.exp_mode,
        window.exp_options[2],
        *window.exp_options
    )
    window.enemy_exp.place(x=160, y=150)

    # Press button to open songs
    window.songdir_button = ttk.Button(
        tabMusic,
        text='Open Custom Song Folder',
        command = functools.partial(get_song_folder, window),
        state = "disabled"
    )
    window.songdir_button.place(x=240, y=130)

    #Press dot for randomization option
    window.option_1 = ttk.Radiobutton(
        tabMusic,
        text = nubValues[0],
        variable = window.option,
        value = nubValues[1],
        command = functools.partial(can_check, window)
    )
    window.option_1.place(x=50, y=30)

    window.option_2 = ttk.Radiobutton(
        tabMusic,
        text = nubValues[2],
        variable = window.option,
        value = nubValues[3],
        command = functools.partial(can_check, window)
    )
    window.option_2.place(x=50, y=80)

    window.option_3 = ttk.Radiobutton(
        tabMusic,
        text = nubValues[4],
        variable = window.option,
        value = nubValues[5],
        command = functools.partial(can_check, window),
        state = "disabled"
    )
    window.option_3.place(x=50, y=130)

    #Checkmark for whether the randomized songs should be categorized or not
    window.category_check = ttk.Checkbutton(
        tabMusic,
        text = "Categorize",
        variable = window.categorize,
        onvalue = True,
        offvalue = False,
        state = "disabled"
    )
    window.category_check.place(x=180, y=195)

    #Explains how the custom music categorization works
    window.category_info = ttk.Button(
        tabMusic,
        text = '?',
        command = help
    )
    window.category_info.place(x=185, y=220)

    window.mainloop()