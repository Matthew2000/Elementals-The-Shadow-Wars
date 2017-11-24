#!/usr/bin/python3
import locale
import sys

from BaseClasses.NPC import *
from BaseClasses.Player import *
from Functions import Load
from Globals import *
from Maps.Environment import *

locale.setlocale(locale.LC_ALL, '')
code = "utf-8"

# initiates some required variables
save = {"all_NPCs": [], "player": {}, "current_map": "Maps/map1.json"}
map_save = {}
error = open('RPGErrorLog.txt', 'w')
sys.stderr = error
Key = -1
player_name = "Matthew"
Quest.load_all_quests()


def new_game(enemies, npcs):
    Load.load_npcs_for_new_game(npcs)
    Func.set_all_stats(enemies, npcs)
    DebugLog.write('NPCs loaded: ' + str(len(npcs)) + "\n\n")
    DebugLog.write("############\nGame loaded\n############\n\n")


try:

    # hides the cursor
    curses.curs_set(0)
    curses.noecho()

    MAP.border()
    MAP.keypad(True)
    journal.keypad(True)

    # gets the dimensions of the map
    screen_dims = screen.getmaxyx()

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
        current_map = save["current_map"]
        DebugLog.write("############\nGame loaded\n############\n\n")
    else:
        new_game(Character.all_enemies, Character.all_NPCs)

    map1.change_map(current_map)
    map1.show_map()
    map1.load_common_npcs()

    spawn_character(MAP, player1, player1.location[0], player1.location[1])

    screen.refresh()
    MAP.refresh()

    journal.addstr(1, 1, "game start")

    player1.begin_play()

    for npc in Character.all_NPCs:
        npc.begin_play()

    while Key != ord("q"):

        Func.update_player_location(player1, MAP, map1)
        current_map = map1.directory
        Func.update_npc_locations(Character.all_NPCs, map1)

        screen.refresh()
        MAP.refresh()
        MAP.border()

        Func.update_game(player1, journal)

        Func.player_dead(player1, MAP, journal)

        DebugLog.flush()

        Key = MAP.getch()  # gets the player input

        if Key == curses.KEY_RESIZE:
            screen_dims = screen.getmaxyx()
            screen.erase()
            curses.doupdate()
            Func.update_player_location(player1, MAP, map1)
            Func.update_npc_locations(Character.all_NPCs, map1)
            player1.update_player_status()
            journal.resize(50, 65)
            MAP.resize(35, 100)
            journal.refresh()
            conversation = curses.newwin(10, 20, 38, 84)
            player1.make_player_stat_win()
            continue

        player1.tick(Key, map1)

        for npc in Character.all_NPCs:
            if npc.on_map(map1):
                npc.tick(Key, player1)

        DebugLog.flush()

        Func.respawn_enemies(Character.all_NPCs)

        Func.update_game(player1, journal)

        Func.update_npc_locations(Character.all_NPCs, map1)

        screen.refresh()
        MAP.refresh()
        Func.update_game(player1, journal)
    else:
        DebugLog.write("\n############\nGame Closed\n############\n\n")

    Func.update_npc_locations(Character.all_NPCs, map1)
    DebugLog.write("\n############\nSave start\n############\n\n")
    save_player(player1, save)
    save_npcs(save, Character.all_NPCs)
    save["current_map"] = current_map
    DebugLog.write("\n############\nGame saved\n############")
except:
    DebugLog.write(str(sys.exc_info()))
finally:
    if os.path.exists('save.json'):
        temp = open("save.json", "r")
        temp_save = json.load(temp)
        if "total_exp" in temp_save["player"]:
            os.rename('save.json', 'save.json.bak')
        temp.close()
    if "total_exp" in save["player"]:
        with open('save.json', 'w') as f:
            json.dump(save, f, sort_keys=True, indent=2)
    f.close()
    DebugLog.close()
    error.close()
    curses.endwin()
