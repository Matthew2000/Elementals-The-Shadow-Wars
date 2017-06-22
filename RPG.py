#!/usr/bin/python3
import locale
import sys

from BaseClasses.NPC import *
from BaseClasses.Player import *
from Maps.Environment import *
from Functions import Load

locale.setlocale(locale.LC_ALL, '')
code = "utf-8"

# initiates some required variables
save = {"all_NPCs": [], "player": {}}
DebugLog = open('RPGLog.txt', 'w')
error = open('RPGErrorLog.txt', 'w')
sys.stderr = error
Key = -1
player_name = "Matthew"
all_enemies = []
all_NPCs = []


def new_game(enemies, npcs, log):
	Load.load_npcs_for_new_game(npcs, log)
	Func.set_all_stats(enemies, npcs)
	load_npc_dialogue(npcs, log)
	log.write('len: ' + str(len(npcs)) + "\r\n")


def start_combat(player, enemy):
	global Key
	Func.print_combat_intro_text(journal)
	Func.update_enemy_status(enemy, enemy_status)
	player.update_player_status()
	while Key is not ord("2"):
		Func.update_enemy_status(enemy, enemy_status)
		player.update_player_status()
		if enemy.health <= 0:
			Func.is_enemy_dead(enemy, player, MAP, journal)
			enemy.allow_movement = True
			Func.update_enemy_status(enemy, enemy_status)
			break
		if player.health <= 0:
			if player.is_dead():
				Func.player_dead(player, MAP, journal)
				Func.update_player_location(player, MAP, DebugLog)
			enemy.allow_movement = True
			Func.update_enemy_status(enemy, enemy_status)
			break
		Key = MAP.getch()
		if ord("1") <= Key >= ord("2"):
			continue
		if Key is ord("1"):
			player.attack(enemy)
		enemy.attack(player)
	else:
		enemy.allow_movement = True
		Func.print_to_journal(journal, "You have left combat")

try:
	# creates the screens and windows that are used in the game
	screen = curses.initscr()
	MAP = curses.newwin(35, 100, 2, 3)
	trade_win = curses.newwin(50, 65, 2, 110)
	enemy_status = curses.newwin(10, 20, 38, 57)
	journal = curses.newwin(50, 65, 2, 110)
	conversation = curses.newwin(10, 20, 38, 84)

	# hides the cursor
	curses.curs_set(0)
	curses.noecho()

	MAP.border()
	MAP.keypad(True)
	journal.keypad(True)

	# gets the dimensions of the map
	dims = MAP.getmaxyx()
	screen_dims = screen.getmaxyx()

	player1 = create_player("Matthew", "@", Races.Human, [23, 71])

	map1.show_map(MAP)

	# loads the save if it exits.
	# if there is no save it makes a new game
	if os.path.exists('save.json'):
		with open('save.json', 'r') as f:
			save = json.load(f)
			f.close()

		load_player(player1, save, DebugLog)
		player1.inventory = Func.load_inventory(save["player"]["inventory"])
		load_player_equipment(player1, save)
		Load.load_npcs(save, all_NPCs, DebugLog)
	else:
		new_game(all_enemies, all_NPCs, DebugLog)

	spawn_character(MAP, player1, player1.location[0], player1.location[1])
	place_npcs(all_NPCs, MAP)

	screen.refresh()
	MAP.refresh()

	player_turn = True
	number_of_turns = 0

	journal.addstr(1, 1, "game start")

	while Key != ord("q"):

		#current_map.show_map(MAP)
		update_npc_locations(all_NPCs, MAP)
		Func.update_enemy_locations(all_NPCs, MAP)
		Func.update_player_location(player1, MAP, DebugLog)

		screen.refresh()
		MAP.refresh()
		MAP.border()

		Func.update_game(player1, journal)

		Func.player_dead(player1, MAP, journal)

		if player1.exp_is_enough():
			player1.level_up()

		Key = MAP.getch()  # gets the player input

		if Key == curses.KEY_RESIZE:
			screen_dims = screen.getmaxyx()
			screen.erase()
			curses.doupdate()
			Func.update_player_location(player1, MAP, DebugLog)
			Func.update_enemy_locations(all_enemies, MAP)
			update_npc_locations(all_NPCs, MAP)
			player1.update_player_status()
			journal.resize(50, 65)
			MAP.resize(35, 100)
			journal.refresh()
			conversation = curses.newwin(10, 20, 38, 84)
			player1.make_player_stat_win()
			continue

		number_of_turns += 1

		# opens the player inventory
		if Key is ord("i"):
			conversation.border()
			conversation.addstr(1, 1, "1 - equip")
			conversation.addstr(2, 1, "2 - unequip")
			conversation.refresh()
			player1.open_inventory(DebugLog)
			conversation.clear()
			conversation.refresh()

		if Key is ord("l"):
			player1.open_quest_log()

		if Key is ord("r"):
			if player1.is_dead():
				player1.respawn(30, 50)
				spawn_character(MAP, player1, player1.location[0], player1.location[1])

		if player_turn:
			player1.update_quests(all_enemies, all_NPCs, journal)
			if not player1.is_dead():
				player1.move(Key, dims)

				# checks to see if the player moves unto an enemy
				# if so it starts combat
				# if not the player regenerates health and updates its status
				result = Func.enemy_at_location(all_enemies, player1.location, enemy_status)
				if result["result"] is True:
					enemy1 = result["enemy"]
					start_combat(player1, enemy1)
				else:
					player1.regenerate_health()
					player1.update_player_status()

				# checks to see if the player moves onto an NPC
				# if so it starts interacting with it
				result = npc_at_location(player1.location, all_NPCs)
				if result["result"] is True:
					NPC = result["npc"]
					if NPC.is_enemy():
						start_combat(player1, NPC)
					else:
						NPC.interact(journal, conversation, Key, player1, DebugLog, all_enemies, all_NPCs, trade_win)
						Func.update_journal(journal)
						player1.update_player_status()
					while Key is not ord("4"):
						Key = MAP.getch()
						NPC.interact(journal, conversation, Key, player1, DebugLog, all_enemies, all_NPCs, trade_win)
						Func.update_journal(journal)
					else:
						NPC.talking = False
						conversation.clear()
						conversation.refresh()

				# updates the quests that the player has then ends the player's turn
						Func.update_player_location(player1, MAP, DebugLog)

			player1.update_quests(all_enemies, all_NPCs, journal)
			player_turn = False

			Func.player_dead(player1, MAP, journal)

		# moves the enemies and regenerates their health
		# if the enemy moves unto the player, combat starts
		if not player_turn:
			for npc in all_NPCs:
				if not npc.is_dead():
					npc.move(dims, player1)
					npc.regenerate_health()
					if Func.player_at_location(player1, npc.location):
						if npc.is_enemy():
							npc.location = npc.prevlocation[:]
							npc.allow_movement = False
							start_combat(player1, npc)
			player_turn = True

		DebugLog.flush()

		if player1.exp_is_enough():
			player1.level_up()

			Func.respawn_enemies(all_enemies)

			Func.update_game(player1, journal)

			Func.update_enemy_locations(all_enemies, MAP)
		update_npc_locations(all_NPCs, MAP)

		screen.refresh()
		MAP.refresh()
		Func.update_game(player1, journal)

		Func.update_enemy_locations(all_enemies, MAP)
	update_npc_locations(all_NPCs, MAP)
	save_player(player1, save, DebugLog)
	save_npcs(save, all_NPCs, DebugLog)
except:
	DebugLog.write(str(sys.exc_info()))
finally:
	if os.path.exists('save.json'):
		temp = open("save.json", "r")
		temp_save = json.load(temp)
		if "total_exp" in temp_save["player"]:
			os.rename('save.json', 'save.json.bak')
		temp.close()
	with open('save.json', 'w') as f:
		json.dump(save, f, sort_keys=True, indent=2)
	f.close()
	DebugLog.close()
	error.close()
	curses.endwin()
