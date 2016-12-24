#!/usr/bin/python3
import sys
import os.path
import locale
from Character import *
import curses
import json


def create_player(name: str, character: chr, race: Races):
	temp_player = Player(name, character, race)
	temp_player.location = [int(dims[0]/2), int(dims[1]/2)]
	return temp_player


def load_player():
	player1.name = save["player"]["name"]
	log.write(player1.name + " ")
	player1.location = save["player"]["location"]
	player1.prevlocation = save["player"]["prevlocation"]
	player1.health = save["player"]["health"]
	player1.character = save["player"]["character"]
	player1.inventory = save["player"]["inventory"]
	player1.max_health = save["player"]["max_health"]
	player1.quests = save["player"]["quests"]
	player1.race = Races(save["player"]["race"])
	player1.level = save["player"]["level"]
	player1.total_exp = save["player"]["total_exp"]
	player1.exp_for_next_level = save["player"]["exp_for_next_level"]
	player1.exp_to_next_level = save["player"]["exp_to_next_level"]
	player1.strength = save["player"]["strength"]
	log.write("Race: " + str(player1.race)[6:] + "\r\n")
	log.write("load player" + "\r\n")


def save_player():
	save["player"] = player1.__dict__
	save["player"]["race"] = save["player"]["race"].value
	log.write("player saved" + "\r\n")


def create_enemy(ID, name, character, race: Races):  # this function must be assigned to an object
	var = False
	for x in all_enemies:
		if ID == x.ID:
			var = True
			log.write(x.ID + " is already there" + "\r\n")
	if not var:
		all_enemies.append(Enemy(ID, name, character, race))
	return all_enemies[len(all_enemies) - 1]


def save_enemies():
	enemies = all_enemies[:]
	all_enemies.clear()
	for enemy in enemies:
		temp_enemy = enemy.__dict__
		temp_enemy["race"] = temp_enemy["race"].value
		all_enemies.append(temp_enemy)
	save["all_enemies"].clear()
	save["all_enemies"] = all_enemies[:]
	log.write("save enemies" + "\r\n")


def load_enemies(save):
	all_enemies.clear()
	for enemy in save["all_enemies"]:
		log.write(enemy["name"] + " ")
		temp_enemy = create_enemy(enemy["ID"], enemy["name"], enemy["character"], Races(enemy["race"]))
		temp_enemy.location = enemy["location"]
		temp_enemy.prevlocation = enemy["prevlocation"]
		temp_enemy.health = enemy["health"]
		temp_enemy.max_health = enemy["max_health"]
		temp_enemy.character = enemy["character"]
		temp_enemy.inventory = enemy["inventory"]
		temp_enemy.level = enemy["level"]
		temp_enemy.total_exp = enemy["total_exp"]
		temp_enemy.exp_for_next_level = enemy["exp_for_next_level"]
		temp_enemy.exp_to_next_level = enemy["exp_to_next_level"]
		temp_enemy.strength = enemy["strength"]
		temp_enemy.increase_exp_by = enemy["increase_exp_by"]
		log.write("Race: " + str(temp_enemy.race)[6:] + "\r\n")
	log.write("load enemies" + "\r\n")


def create_npc(name, character, race: Races):  # this function must be assigned to an object
	var = False
	for x in all_NPCs:
		if name == x.name:  # name must be the same as the object name
			var = True
			log.write(x.name + " is already there" + "\r\n")
	if not var:
		all_NPCs.append(NPC(name, character, race))
	return all_NPCs[len(all_NPCs) - 1]


def save_npcs():
	NPCs = all_NPCs[:]
	all_NPCs.clear()
	for npc in NPCs:
		temp_npc = npc.__dict__
		temp_npc["race"] = temp_npc["race"].value
		all_NPCs.append(temp_npc)
	save["all_NPCs"].clear()
	save["all_NPCs"] = all_NPCs[:]
	log.write("save NPCs" + "\r\n")


def load_npcs(save):
	all_NPCs.clear()
	for npc in save["all_NPCs"]:
		log.write(npc["name"] + " ")
		temp_npc = create_npc(npc["name"], npc["character"], Races(npc["race"]))
		temp_npc.location = npc["location"]
		temp_npc.prevlocation = npc["prevlocation"]
		temp_npc.health = npc["health"]
		temp_npc.max_health = npc["max_health"]
		temp_npc.character = npc["character"]
		temp_npc.inventory = npc["inventory"]
		temp_npc.has_quest = npc["has_quest"]
		temp_npc.level = npc["level"]
		temp_npc.total_exp = npc["total_exp"]
		temp_npc.exp_for_next_level = npc["exp_for_next_level"]
		temp_npc.exp_to_next_level = npc["exp_to_next_level"]
		temp_npc.strength = npc["strength"]
		log.write("Race: " + str(temp_npc.race)[6:] + "\r\n")
	log.write("load NPCs" + "\r\n")


def spawn_character(win, character, y, x):
	character.location[0] = y
	character.location[1] = x
	character.prevlocation[0] = y
	character.prevlocation[1] = x
	win.addch(y, x, ord(character.character))


def spawn_npc(name, character, race: Races, y, x):
	for npc in all_NPCs:
		if npc.name == name:
			break
	else:
		create_npc(name, character, race)
		spawn_character(Main_Window, all_NPCs[len(all_NPCs) - 1], y, x)


def spawn_enemy(name, character, race: Races, y, x):
	for enemy in all_enemies:
		if enemy.name == name:
			break
	else:
		create_enemy(name, character, race)
		spawn_character(Main_Window, all_enemies[len(all_enemies) - 1], y, x)


def update_inventory():
	x = 1
	inventory.clear()
	inventory.border()
	inventory.addstr(0, 1, "Inventory")
	for item in player1.inventory:
		inventory.addstr(x, 1, item + ": " + str(player1.inventory[item]))
		x += 1
	inventory.refresh()


def update_player_status():
	player_status.clear()
	player_status.border()
	player_status.addstr(0, 1, "Player Stats")
	player_status.addstr(1, 1, "Health: " + str(player1.health))
	player_status.addstr(2, 1, "Strength: " + str(player1.strength))
	player_status.addstr(3, 1, "Race: " + str(player1.race)[6:])
	player_status.addstr(4, 1, "Level: " + str(player1.level))
	player_status.addstr(5, 1, "exp needed: " + str(player1.exp_to_next_level-player1.exp_for_next_level)[:len(str(player1.exp_to_next_level-player1.exp_for_next_level))-2])
	player_status.refresh()


def update_enemy_status():
	enemy_status.clear()
	for enemy in all_enemies:
		if enemy.allow_movement is False:
			enemy_status.border()
			enemy_status.addstr(0, 1, enemy.name + "'s Stats")
			enemy_status.addstr(1, 1, "Race: " + str(enemy.race)[6:])
			enemy_status.addstr(2, 1, "Health: " + str(enemy.health))
			enemy_status.addstr(3, 1, "Level: " + str(enemy.level))
			enemy_status.addstr(4, 1, "Strength: " + str(enemy.strength))
	enemy_status.refresh()


def update_journal():
	journal.border()
	journal.refresh()


def update_conversation():
	conversation.clear()
	for npc in all_NPCs:
		if npc.talking is True:
			conversation.border()
			conversation.addstr(0, 1, "Conversation")
			conversation.addstr(2, 1, "1 - Talk")
			conversation.addstr(3, 1, "2 - Quest")
			conversation.addstr(4, 1, "3 - Trade")
			conversation.addstr(5, 1, "4 - Leave")
	conversation.refresh()


def update_game():
	update_player_status()
	update_inventory()
	update_journal()


def are_enemies_dead():
	for enemy in all_enemies:
		if enemy.is_dead():
			if Main_Window.inch(enemy.location[0], enemy.location[1]) == ord(enemy.character):
				enemy.death(player1)
				Main_Window.addch(enemy.prevlocation[0], enemy.prevlocation[1], " ")
				print_to_journal(enemy.name + " is dead")
				enemy.prevlocation = enemy.location[:]
				enemy.location = [0, 0]
				log.write("player exp is: " + str(player1.total_exp) + "\r\n")
				print_to_journal("you gained " + str(enemy.increase_exp_by) + " exp")


def update_enemy_locations():
	for enemy in all_enemies:
		if enemy.prevlocation.__ne__(enemy.location):  # moves the Enemy
			if Main_Window.inch(enemy.location[0], enemy.location[1]) == ord(
					" "):  # stops Enemy from moving if there's a enemy there
				Main_Window.addch(enemy.location[0], enemy.location[1], ord(enemy.character))
				Main_Window.addch(enemy.prevlocation[0], enemy.prevlocation[1], " ")
			else:
				enemy.location = enemy.prevlocation[:]  # keeps the Enemy at its current location


def update_player_location():
	if player1.prevlocation.__ne__(player1.location):  # moves the Enemy
		if Main_Window.inch(player1.location[0], player1.location[1]) == ord(
				" "):  # stops Enemy from moving if there's a enemy there
			Main_Window.addch(player1.location[0], player1.location[1], ord(player1.character))
			Main_Window.addch(player1.prevlocation[0], player1.prevlocation[1], " ")
		else:
			player1.location = player1.prevlocation[:]  # keeps the Enemy at its current location


def update_npc_locations():
	for npc in all_NPCs:
		if npc.prevlocation.__ne__(npc.location):  # moves the NPC
			if Main_Window.inch(npc.location[0], npc.location[1]) == ord(
					" "):  # stops NPC from moving if there's a character there
				Main_Window.addch(npc.location[0], npc.location[1], ord(npc.character))
				Main_Window.addch(npc.prevlocation[0], npc.prevlocation[1], " ")
			else:
				npc.location = npc.prevlocation[:]  # keeps the NPC at its current location


def place_enemies():
	for enemy in all_enemies:
		spawn_character(Main_Window, enemy, enemy.location[0], enemy.location[1])


def place_npcs():
	for npc in all_NPCs:
		spawn_character(Main_Window, npc, npc.location[0], npc.location[1])


def move_enemies():
	for enemy in all_enemies:
		if not enemy.is_dead():
			enemy.move(dims, player1)
			if player_at_location(enemy.location[0], enemy.location[1]):
				enemy.allow_movement = False
				enter_combat(player1, enemy, -1)


def interact_npc(input_key, log):
	for npc in all_NPCs:
		npc.interact(player1, input_key, log, all_enemies, all_NPCs)


def print_to_journal(message):
	journal.insertln()
	journal.addstr(1, 1, message)


def enemy_at_location(y, x):
	for enemy in all_enemies:
		if enemy.location[0] is y and enemy.location[1] is x:
			update_enemy_status()
			enemy.allow_movement = False
			return {"result": True, "enemy": enemy}
	else:
		return {"result": False}


def player_at_location(y, x):
	if player1.location[0] is y and player1.location[1] is x:
		update_enemy_status()
		return True
	else:
		return False


def npc_at_location(y, x):
	for npc in all_NPCs:
		if npc.location[0] is y and npc.location[1] is x:
			return {"result": True, "npc": npc}
	else:
		return {"result": False}


def load_npc_dialogue():
	for npc in all_NPCs:
		if os.path.exists('Dialogue/' + npc.name + '.json'):
			with open('Dialogue/' + npc.name + '.json', 'r') as a:
				npc.dialogue = json.load(a)
				a.close()


def save_npc_dialogue():
	for npc in all_NPCs:
		with open('Dialogue/' + npc.name + '.json', 'w') as a:
			json.dump(npc.dialogue, a, sort_keys=True, indent=4)
			a.close()
	log.write("dialogue save" + "\r\n")


def player_dead():
	if player1.is_dead():
		if Main_Window.inch(player1.location[0], player1.location[1]) == ord(player1.character):
			player1.death()
			Main_Window.addch(player1.prevlocation[0], player1.prevlocation[1], " ")
			print_to_journal(player1.name + " is dead")


def follow_the_player():
	for enemy in all_enemies:
		enemy.follow_player(player1)


def enter_combat(player, enemy, key):
	print_to_journal('Press "1" to attack or "2" to leave')
	print_to_journal("Battle has started")
	update_journal()
	update_enemy_status()
	update_player_status()
	while key is not ord("2"):
		update_enemy_status()
		update_player_status()
		if enemy.health <= 0:
			are_enemies_dead()
			enemy.allow_movement = True
			update_enemy_status()
			break
		if player1.health <= 0:
			if player.is_dead():
				player_dead()
				update_player_location()
			enemy.allow_movement = True
			update_enemy_status()
			break
		key = Main_Window.getch()
		if key is ord("1"):
			player.attack(enemy)
		enemy.attack(player)
	else:
		enemy.allow_movement = True
		print_to_journal("You have left combat")


def set_all_stats():
	for npc in all_NPCs:
		npc.set_stats()
	for enemy in all_enemies:
		enemy.set_stats()
		enemy.increase_exp_by = int((enemy.level**2)/.4)


def new_game(save):
	with open('NewGame.json', 'r') as f:
		save = json.load(f)
		f.close()
	load_enemies(save)
	load_npcs(save)
	set_all_stats()
	for npc in save["all_NPCs"]:
		with open('Dialogue/' + npc["name"] + '.json', 'w') as a:
			json.dump(npc["dialogue"], a, sort_keys=True, indent=4)
			a.close()
	load_npc_dialogue()

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

	player1 = create_player("Matthew", "@", Races.Human)

	if os.path.exists('save.json'):
		with open('save.json', 'r') as f:
			save = json.load(f)
			f.close()

		player = save["player"].keys()
		inventory_items = save["player"]["inventory"].keys()

		load_player()
		load_enemies(save)
		load_npcs(save)
		load_npc_dialogue()
	else:
		new_game(save)

	spawn_character(Main_Window, player1, player1.location[0], player1.location[1])
	place_enemies()
	place_npcs()

	screen.refresh()
	Main_Window.refresh()

	player_turn = True

	journal.addstr(1, 1, "game start")

	while Key != ord("q"):

		screen.refresh()
		Main_Window.refresh()
		Main_Window.border()

		update_game()
		update_enemy_status()

		are_enemies_dead()
		player_dead()

		if player1.exp_is_enough():
			player1.level_up()

		Key = Main_Window.getch()

		if Key is ord("g"):
			spawn_npc("Rainbow Tooth", "R", Races.Avaker, 1, int(dims[1])-1)

		if Key is ord("r"):
			if player1.is_dead():
				player1.respawn(20, 20)
				spawn_character(Main_Window, player1, player1.location[0], player1.location[1])

		if player_turn:
			player1.update_quests(all_enemies, all_NPCs, journal)
			if not player1.is_dead():
				player1.move(Key, dims)
				result = enemy_at_location(player1.location[0], player1.location[1])
				if result["result"] is True:
					enemy1 = result["enemy"]
					enter_combat(player1, enemy1, -1)
				result = npc_at_location(player1.location[0], player1.location[1])
				if result["result"] is True:
					NPC = result["npc"]
					NPC.interact(journal, conversation, Key, player1, log, all_enemies, all_NPCs)
					update_journal()
					update_player_status()
					while Key is not ord("4"):
						Key = Main_Window.getch()
						NPC.interact(journal, conversation, Key, player1, log, all_enemies, all_NPCs)
						update_journal()
					else:
						NPC.talking = False
						update_conversation()
				update_player_location()

			player1.update_quests(all_enemies, all_NPCs, journal)
			player_turn = False

		are_enemies_dead()
		player_dead()

		if not player_turn:
			move_enemies()
			player_turn = True

		log.flush()

		if player1.exp_is_enough():
			player1.level_up()

		update_game()

		update_enemy_locations()
		update_npc_locations()

		screen.refresh()
		Main_Window.refresh()
		update_game()
	update_enemy_locations()
	update_npc_locations()
	save_player()
	save_npc_dialogue()
	save_npcs()
	save_enemies()
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
