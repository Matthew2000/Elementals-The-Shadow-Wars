#!/usr/bin/python3
import sys
import locale
from Character import *
import curses
from Functions.MainFunctions import *


locale.setlocale(locale.LC_ALL, '')
code = "utf-8"
save = {"all_enemies": [], "all_NPCs": [], "player": {"character": "@", "health": 100, "inventory": {"Coins": 100}, "location": [2, 5], "max_health": 100, "name": "Matthew", "prevlocation": [3, 5]}}
log = open('RPGLog.txt', 'w')
error = open('RPGErrorLog.txt', 'w')
sys.stderr = error
Key = -1
player_name = "Matthew"
all_enemies = []
all_NPCs = []

try:
	screen = curses.initscr()
	Main_Window = curses.newwin(35, 100, 2, 3)
	inventory = curses.newwin(10, 20, 38, 30)
	player_status = curses.newwin(10, 20, 38, 3)
	enemy_status = curses.newwin(10, 20, 38, 57)
	journal = curses.newwin(50, 65, 2, 110)
	conversation = curses.newwin(10, 20, 38, 84)

	curses.curs_set(0)
	curses.noecho()
	Main_Window.border()
	Main_Window.keypad(True)

	dims = Main_Window.getmaxyx()
	dims2 = inventory.getmaxyx()

	player1 = create_player("Matthew", "@", Races.Human, dims)

	if os.path.exists('save.json'):
		with open('save.json', 'r') as f:
			save = json.load(f)
			f.close()

		player = save["player"].keys()
		inventory_items = save["player"]["inventory"].keys()

		load_player(player1, save, log)
		load_player_equipment(player1, save)
		load_enemies(save, all_enemies, log)
		load_npcs(save, all_NPCs, log)
		load_npc_dialogue(all_NPCs, log)
	else:
		new_game(save, all_enemies, all_NPCs, log)

	spawn_character(Main_Window, player1, player1.location[0], player1.location[1])
	place_enemies(all_enemies, Main_Window)
	place_npcs(all_NPCs, Main_Window)

	screen.refresh()
	Main_Window.refresh()

	player_turn = True
	number_of_turns = 0

	journal.addstr(1, 1, "game start")

	while Key != ord("q"):

		screen.refresh()
		Main_Window.refresh()
		Main_Window.border()

		update_game(player1, player_status, inventory, journal)

		player_dead(player1, Main_Window, journal)

		if player1.exp_is_enough():
			player1.level_up()

		Key = Main_Window.getch()

		number_of_turns += 1

		if Key is ord("r"):
			if player1.is_dead():
				player1.respawn(30, 50)
				spawn_character(Main_Window, player1, player1.location[0], player1.location[1])

		if player_turn:
			player1.update_quests(all_enemies, all_NPCs, journal)
			if not player1.is_dead():
				player1.move(Key, dims)
				result = enemy_at_location(all_enemies, player1.location[0], player1.location[1], enemy_status)
				if result["result"] is True:
					enemy1 = result["enemy"]
					enter_combat(player1, enemy1, Key, Main_Window, enemy_status, player_status, log, journal)
				else:
					player_health_regen(player1)
					update_player_status(player1, player_status)
				result = npc_at_location(player1.location[0], player1.location[1], all_NPCs)
				if result["result"] is True:
					NPC = result["npc"]
					NPC.interact(journal, conversation, Key, player1, log, all_enemies, all_NPCs)
					update_journal(journal)
					update_player_status(player1, player_status)
					while Key is not ord("4"):
						Key = Main_Window.getch()
						NPC.interact(journal, conversation, Key, player1, log, all_enemies, all_NPCs)
						update_journal(journal)
					else:
						NPC.talking = False
						conversation.clear()
						conversation.refresh()
				update_player_location(player1, Main_Window)
			player1.update_quests(all_enemies, all_NPCs, journal)
			player_turn = False

		player_dead(player1, Main_Window, journal)

		if not player_turn:
			move_enemies(all_enemies, player1, dims, log, enemy_status, Main_Window, player_status, journal)
			enemy_health_regen(all_enemies)
			player_turn = True

		log.flush()

		if player1.exp_is_enough():
			player1.level_up()

		respawn_enemies(all_enemies)

		update_game(player1, player_status, inventory, journal)

		update_enemy_locations(all_enemies, Main_Window)
		update_npc_locations(all_NPCs, Main_Window)

		screen.refresh()
		Main_Window.refresh()
		update_game(player1, player_status, inventory, journal)
	update_enemy_locations(all_enemies, Main_Window)
	update_npc_locations(all_NPCs, Main_Window)
	save_player(player1, save, log)
	save_npc_dialogue(all_NPCs, log)
	save_npcs(save, all_NPCs, log)
	save_enemies(save, all_enemies, log)
except:
	log.write(str(sys.exc_info()))
finally:
	if os.path.exists('save.json.bak') and os.path.exists('save.json'):
		os.remove('save.json.bak')
		os.rename('save.json', 'save.json.bak')
	with open('save.json', 'w') as f:
		json.dump(save, f, sort_keys=True, indent=4)
	f.close()
	log.close()
	error.close()
	curses.endwin()
