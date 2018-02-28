#!/usr/bin/python3
import locale
import sys

from BaseClasses.NpcClass import *
from BaseClasses.PlayerClass import *
from Functions import Load
from Globals import *
from Maps.Environment import *

locale.setlocale(locale.LC_ALL, 'en-US')
code = "utf-8"

# initiates some required variables
save = {"all_NPCs": [], "player": {}, "current_map": "Maps/map1.json"}
map_save = {}
error = open('RPGErrorLog.txt', 'w')
sys.stderr = error
Key = -1
player_name = "Matthew"
QuestClass.load_all_quests()

global current_map_path


def new_game(enemies, npcs):
    Load.load_npcs_for_new_game()
    Func.set_all_stats(enemies, npcs)
    DebugLog.write('NPCs loaded: ' + str(len(npcs)) + "\n\n")
    DebugLog.write("############\nGame loaded\n############\n\n")


try:

    # hides the cursor
    curses.curs_set(0)
    curses.noecho()

    curses.wborder(map_window)
    curses.keypad(map_window, True)
    curses.keypad(journal, True)

    # gets the dimensions of the map
    screen_dims = curses.getmaxyx(stdscr)

    player1 = create_player("Matthew", "@", Race.Human, [23, 71])

    # loads the save if it exits.
    # if there is no save it makes a new game
    if os.path.exists('save.json'):
        with open('save.json', 'r') as f:
            save = json.load(f)
            f.close()

        load_player(player1, save)
        player1.inventory = Func.load_inventory(save["player"]["inventory"])
        load_player_equipment(player1, save)
        Load.load_npcs(save, Character.all_NPCs)
        current_map_path = save["current_map"]
        DebugLog.write("############\nGame loaded\n############\n\n")
    else:
        new_game(Character.all_enemies, Character.all_NPCs)

    map1.change_map(current_map_path)
    map1.show_map()
    map1.load_common_npcs()

    spawn_character(map_window, player1, player1.location[0], player1.location[1])

    curses.wrefresh(stdscr)
    curses.wrefresh(map_window)

    curses.mvwaddstr(journal, 1, 1, "game start")

    player1.begin_play()

    for npc in Character.all_NPCs:
        npc.begin_play()

    while Key != ord("q"):

        curses.wclear(map_window)
        map1.show_map()

        Func.update_player_location(player1, map1)
        current_map_path = map1.directory
        Func.update_npc_locations(Character.all_NPCs, map1)

        curses.wrefresh(stdscr)
        curses.wrefresh(map_window)
        curses.wborder(map_window)

        Func.update_game(player1)

        Func.player_dead(player1)

        DebugLog.flush()

        Key = curses.wgetch(map_window)  # gets the player input

        if Key == curses.KEY_RESIZE:
            screen_dims = curses.getmaxyx(stdscr)
            stdscr.erase()
            curses.doupdate()
            Func.update_player_location(player1, map1)
            Func.update_npc_locations(Character.all_NPCs, map1)
            player1.update_player_status()
            journal.resize(50, 65)
            map_window.resize(35, 100)
            curses.wrefresh(journal)
            conversation = curses.newwin(10, 20, 38, 84)
            player1.make_player_stat_win()
            continue

        player1.tick(Key, map1)

        for npc in Character.all_NPCs:
            if Func.on_map(map1, npc.name, npc.id):
                npc.tick(Key, player1)

        DebugLog.flush()

        Func.respawn_enemies(Character.all_NPCs)

        Func.update_game(player1)

        curses.wrefresh(stdscr)
        curses.wrefresh(map_window)
        Func.update_game(player1)
    else:
        DebugLog.write("\n############\nGame Closed\n############\n\n")

    Func.update_npc_locations(Character.all_NPCs, map1)
    DebugLog.write("\n############\nSave start\n############\n\n")
    save_player(player1, save)
    save_npcs(save, Character.all_NPCs)
    save["current_map"] = current_map_path
    DebugLog.write("\n############\nGame saved\n############")
except:
    DebugLog.write(str(sys.exc_info()))
finally:
    if os.path.exists('save.json'):
        temp = open("save.json", "r")
        temp_save = json.load(temp)
        temp.close()
        if "total_exp" in temp_save["player"]:
            os.remove("save.json.bak")
            os.rename('save.json', 'save.json.bak')
    if "total_exp" in save["player"]:
        with open('save.json', 'w') as f:
            json.dump(save, f, sort_keys=True, indent=2)
            f.close()
    DebugLog.close()
    error.close()
    curses.endwin()
