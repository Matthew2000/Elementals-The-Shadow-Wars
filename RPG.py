#!/usr/bin/python3
import sys
import os.path
import locale
from Character import *
import curses
import json


def load_player():
	player1.name = save["player"]["name"]
	player1.location = save["player"]["location"]
	player1.prevlocation = save["player"]["prevlocation"]
	player1.health = save["player"]["health"]
	player1.character = save["player"]["character"]
	player1.inventory = save["player"]["inventory"]
	player1.max_health = save["player"]["max_health"]
	log.write("load player" + "\r\n")


def save_player():
	save["player"] = player1.__dict__


def create_enemy(name, character):  # this function must be assigned to an object
	var = False
	for x in all_enemies:
		if name == x.name:  # name must be the same as the object name
			var = True
			log.write(x.name + " is already there" + "\r\n")
	if not var:
		name = Enemy(name, character)
		all_enemies.append(name)
	return var


def save_enemies():
	enemies = all_enemies[:]
	all_enemies.clear()
	for enemy in enemies:
		all_enemies.append(enemy.__dict__)
	save["all_enemies"].clear()
	save["all_enemies"] = all_enemies[:]
	log.write("save enemies" + "\r\n")


def load_enemies():
	all_enemies.clear()
	x = 0
	for enemy in save["all_enemies"]:
		name = enemy["name"]
		log.write(name + "\r\n")
		create_enemy(name, enemy["character"])
		all_enemies[x].name = save["all_enemies"][x]["name"]
		all_enemies[x].location = save["all_enemies"][x]["location"]
		all_enemies[x].prevlocation = save["all_enemies"][x]["prevlocation"]
		all_enemies[x].health = save["all_enemies"][x]["health"]
		all_enemies[x].max_health = save["all_enemies"][x]["max_health"]
		all_enemies[x].character = save["all_enemies"][x]["character"]
		all_enemies[x].inventory = save["all_enemies"][x]["inventory"]
		x += 1
	log.write("load enemies" + "\r\n")


def create_npc(name, character):  # this function must be assigned to an object
	var = False
	for x in all_NPCs:
		if name == x.name:  # name must be the same as the object name
			var = True
			log.write(x.name + " is already there" + "\r\n")
	if not var:
		name = NPC(name, character)
		all_NPCs.append(name)
	return var


def save_npcs():
	NPCs = all_NPCs[:]
	all_NPCs.clear()
	for npc in NPCs:
		all_NPCs.append(npc.__dict__)
	save["all_NPCs"].clear()
	save["all_NPCs"] = all_NPCs[:]
	log.write("save NPCs" + "\r\n")


def load_npcs():
	all_NPCs.clear()
	x = 0
	for npc in save["all_NPCs"]:
		name = npc["name"]
		log.write(name + "\r\n")
		create_npc(name, npc["character"])
		all_NPCs[x].name = save["all_NPCs"][x]["name"]
		all_NPCs[x].location = save["all_NPCs"][x]["location"]
		all_NPCs[x].prevlocation = save["all_NPCs"][x]["prevlocation"]
		all_NPCs[x].health = save["all_NPCs"][x]["health"]
		all_NPCs[x].max_health = save["all_NPCs"][x]["max_health"]
		all_NPCs[x].character = save["all_NPCs"][x]["character"]
		all_NPCs[x].inventory = save["all_NPCs"][x]["inventory"]
		x += 1
	log.write("load NPCs" + "\r\n")


def spawn_character(win, character, y, x):
	character.location[0] = y
	character.location[1] = x
	character.prevlocation[0] = y
	character.prevlocation[1] = x
	win.addch(y, x, ord(character.character))


def spawn_enemy(name, character, y, x):
	if not create_enemy(name, character):
		spawn_character(Main_Window, all_enemies[len(all_enemies) - 1], y, x)


def spawn_npc(name, character, y, x):
	if not create_npc(name, character):
		spawn_character(Main_Window, all_NPCs[len(all_NPCs) - 1], y, x)


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
	player_status.refresh()


def update_enemy_status():
	enemy_status.clear()
	for enemy in all_enemies:
		if enemy.allow_movement is False:
			enemy_status.border()
			enemy_status.addstr(0, 1, enemy.name + "'s Stats")
			enemy_status.addstr(1, 1, "Health: " + str(enemy.health))
	enemy_status.refresh()


def update_journal():
	journal.border()
	journal.refresh()


def update_game():
	update_player_status()
	update_inventory()
	update_journal()


def are_enemies_dead():
	for enemy in all_enemies:
		if enemy.is_dead():
			if Main_Window.inch(enemy.location[0], enemy.location[1]) == ord(enemy.character):
				enemy.death()
				Main_Window.addch(enemy.prevlocation[0], enemy.prevlocation[1], " ")
				print_to_journal(enemy.name + " is dead")


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
	x = 0
	for enemy in all_enemies:
		spawn_character(Main_Window, all_enemies[x], all_enemies[x].location[0], all_enemies[x].location[1])
		x += 1


def place_npcs():
	x = 0
	for npc in all_NPCs:
		spawn_character(Main_Window, all_NPCs[x], all_NPCs[x].location[0], all_NPCs[x].location[1])
		x += 1


def move_enemies():
	for enemy in all_enemies:
		enemy.move(dims)


def interact_npc(input_key, log):
	for npc in all_NPCs:
		npc.interact(player1, input_key, log)


def print_to_journal(message):
	journal.insertln()
	journal.addstr(1, 1, message)


def attack_enemies():
	for enemy in all_enemies:
		player1.attack(enemy)


def enemy_at_location(y, x):
	for enemy in all_enemies:
		if enemy.location[0] is y and enemy.location[1] is x:
			update_enemy_status()
			enemy.allow_movement = False
			return {"result": True, "enemy": enemy}
	else:
		return {"result": False}


locale.setlocale(locale.LC_ALL, '')
code = "utf-8"
save = {"all_enemies": [], "player": {"character": "@", "health": 100, "inventory": {"Coins": 100}, "location": [2, 5], "max_health": 100, "name": "Matthew", "prevlocation": [3, 5]}}
log = open('RPGLog.txt', 'w')
Key = -1
player_name = "Matthew"
all_enemies = []
all_NPCs = []

try:
	screen = curses.initscr()
	Main_Window = curses.newwin(35, 100, 2, 3)
	inventory = curses.newwin(10, 20, 38, 33)
	player_status = curses.newwin(10, 20, 38, 3)
	enemy_status = curses.newwin(10, 20, 38, 63)
	journal = curses.newwin(50, 65, 2, 110)

	curses.curs_set(0)
	curses.noecho()
	Main_Window.border()
	Main_Window.keypad(True)

	dims = Main_Window.getmaxyx()
	dims2 = inventory.getmaxyx()

	if os.path.exists('save.json'):
		with open('save.json', 'r') as f:
			save = json.load(f)
			f.close()

	player = save["player"].keys()
	inventory_items = save["player"]["inventory"].keys()

	player1 = Player("Matthew", "@")
	log.write("player made" + "\r\n")

	load_player()
	load_enemies()
	load_npcs()

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

		Key = Main_Window.getch()

		if Key is ord("a"):
			attack_enemies()

		interact_npc(Key, journal)

		if Key is ord("s"):
			spawn_enemy("Zack", "Z", dims[0]-2, 1)

		if Key is ord("r"):
			if player1.is_dead():
				player1.respawn(20, 20)
				spawn_character(Main_Window, player1, player1.location[0], player1.location[1])
				save_player()

		are_enemies_dead()

		if player_turn:
			if not player1.is_dead():
				player1.move(Key, dims)
				result = enemy_at_location(player1.location[0], player1.location[1])
				if result["result"] is True:
					enemy = result["enemy"]
					print_to_journal('Press "a" to attack or "e" to leave')
					print_to_journal("Battle has started")
					update_journal()
					while Key is not ord("e"):
						update_enemy_status()
						Key = Main_Window.getch()
						if Key is ord("a"):
							player1.attack(enemy)
						if enemy.health <= 0:
							are_enemies_dead()
							enemy.allow_movement = True
							update_enemy_status()
							break
					else:
						enemy.allow_movement = True
						print_to_journal("You have left combat")
				update_player_location()
				save_player()
			player_turn = False

		if not player_turn:
			move_enemies()
			player_turn = True

		log.flush()

		update_enemy_locations()
		update_npc_locations()

		screen.refresh()
		Main_Window.refresh()
		update_game()
	update_enemy_locations()
	update_npc_locations()
	save_npcs()
	save_enemies()
except:
	log.write(str(sys.exc_info()))
finally:
	with open('save.json', 'w') as f:
		json.dump(save, f, sort_keys=True, indent=4)
	f.close()
	log.close()
	curses.endwin()
