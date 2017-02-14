#!/usr/bin/python3
import sys
import locale
from Character import *
import curses
from Functions.MainFunctions import *


locale.setlocale(locale.LC_ALL, '')
code = "utf-8"
save = {"all_NPCs": [], "all_enemies": [], "player": {}}
DebugLog = open('RPGLog.txt', 'w')
error = open('RPGErrorLog.txt', 'w')
sys.stderr = error
Key = -1
player_name = "Matthew"
all_enemies = []
all_NPCs = []


def start_combat(player, enemy):
	global Key
	print_combat_intro_text(journal)
	update_enemy_status(enemy, enemy_status)
	player.update_player_status()
	while Key is not ord("2"):
		update_enemy_status(enemy, enemy_status)
		player.update_player_status()
		if enemy.health <= 0:
			is_enemy_dead(enemy, player, MAP, journal)
			enemy.allow_movement = True
			update_enemy_status(enemy, enemy_status)
			break
		if player.health <= 0:
			if player.is_dead():
				player_dead(player, MAP, journal)
				update_player_location(player, MAP)
			enemy.allow_movement = True
			update_enemy_status(enemy, enemy_status)
			break
		Key = MAP.getch()
		if ord("1") <= Key >= ord("2"):
			continue
		if Key is ord("1"):
			player.attack(enemy)
		enemy.attack(player)
	else:
		enemy.allow_movement = True
		print_to_journal(journal, "You have left combat")

try:
	screen = curses.initscr()
	MAP = curses.newwin(35, 100, 2, 3)
	inventory_win = curses.newwin(10, 20, 38, 30)
	player_status = curses.newwin(10, 20, 38, 3)
	enemy_status = curses.newwin(10, 20, 38, 57)
	journal = curses.newwin(50, 65, 2, 110)
	conversation = curses.newwin(10, 20, 38, 84)

	curses.curs_set(0)
	curses.noecho()
	MAP.border()
	MAP.keypad(True)
	journal.keypad(True)

	dims = MAP.getmaxyx()

	player1 = create_player("Matthew", "@", Races.Human, dims)

	if os.path.exists('save.json'):
		with open('save.json', 'r') as f:
			save = json.load(f)
			f.close()

		inventory_items = save["player"]["inventory"].keys()

		load_player(player1, save, DebugLog)
		load_player_equipment(player1, save)
		load_enemies(save, all_enemies, DebugLog)
		load_npcs(save, all_NPCs, DebugLog)
		load_npc_dialogue(all_NPCs, DebugLog)
	else:
		new_game(save, all_enemies, all_NPCs, DebugLog)

	spawn_character(MAP, player1, player1.location[0], player1.location[1])
	place_enemies(all_enemies, MAP)
	place_npcs(all_NPCs, MAP)

	screen.refresh()
	MAP.refresh()

	player_turn = True
	number_of_turns = 0

	journal.addstr(1, 1, "game start")

	while Key != ord("q"):

		screen.refresh()
		MAP.refresh()
		MAP.border()

		update_game(player1, journal)

		player_dead(player1, MAP, journal)

		if player1.exp_is_enough():
			player1.level_up()

		Key = MAP.getch()

		number_of_turns += 1

		if Key is ord("r"):
			if player1.is_dead():
				player1.respawn(30, 50)
				spawn_character(MAP, player1, player1.location[0], player1.location[1])

		if player_turn:
			player1.update_quests(all_enemies, all_NPCs, journal)
			if not player1.is_dead():
				player1.move(Key, dims)
				result = enemy_at_location(all_enemies, player1.location, enemy_status)
				if result["result"] is True:
					enemy1 = result["enemy"]
					start_combat(player1, enemy1)
				else:
					player1.regenerate_health()
					player1.update_player_status()
				result = npc_at_location(player1.location, all_NPCs)
				if result["result"] is True:
					NPC = result["npc"]
					NPC.interact(journal, conversation, Key, player1, DebugLog, all_enemies, all_NPCs)
					update_journal(journal)
					player1.update_player_status()
					while Key is not ord("4"):
						Key = MAP.getch()
						NPC.interact(journal, conversation, Key, player1, DebugLog, all_enemies, all_NPCs)
						update_journal(journal)
					else:
						NPC.talking = False
						conversation.clear()
						conversation.refresh()
				update_player_location(player1, MAP)
			player1.update_quests(all_enemies, all_NPCs, journal)
			player_turn = False

		player_dead(player1, MAP, journal)

		if not player_turn:
			for enemy in all_enemies:
				if not enemy.is_dead():
					enemy.move(dims, player1)
					enemy.regenerate_health()
					if player_at_location(player1, enemy.location):
						enemy.location= enemy.prevlocation[:]
						enemy.allow_movement = False
						start_combat(player1, enemy)
			player_turn = True

		DebugLog.flush()

		if player1.exp_is_enough():
			player1.level_up()

		respawn_enemies(all_enemies)

		update_game(player1, journal)

		update_enemy_locations(all_enemies, MAP)
		update_npc_locations(all_NPCs, MAP)

		screen.refresh()
		MAP.refresh()
		update_game(player1, journal)
	update_enemy_locations(all_enemies, MAP)
	update_npc_locations(all_NPCs, MAP)
	save_player(player1, save, DebugLog)
	save_npc_dialogue(all_NPCs, DebugLog)
	save_npcs(save, all_NPCs, DebugLog)
	save_enemies(save, all_enemies, DebugLog)
except:
	DebugLog.write(str(sys.exc_info()))
finally:
	if os.path.exists('save.json.bak') and os.path.exists('save.json'):
		os.remove('save.json.bak')
		os.rename('save.json', 'save.json.bak')
	with open('save.json', 'w') as f:
		json.dump(save, f, sort_keys=True, indent=4)
	f.close()
	DebugLog.close()
	error.close()
	curses.endwin()
