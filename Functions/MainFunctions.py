from Functions.EnemyFunctions import *
from Functions.NPCFunctions import *
from BaseClasses.Player import *
from Maps.Environment import *
import string


def create_player(name: str, character: chr, race: Races, spawn_point):
	temp_player = Player(name, character, race, spawn_point)
	temp_player.location = temp_player.spawn_location
	return temp_player


def load_player(player, save, log):
	"""loads all player stats from the save file"""
	player.name = save["player"]["name"]
	log.write(player.name + " ")
	player.location = save["player"]["location"]
	player.prevlocation = player.location[:]
	player.health = save["player"]["health"]
	player.character = save["player"]["character"]
	player.max_health = save["player"]["max_health"]
	player.quests = load_quests(save["player"]["quests"], log)
	player.race = Races(save["player"]["race"])
	player.level = save["player"]["level"]
	player.total_exp = save["player"]["total_exp"]
	player.exp_for_next_level = save["player"]["exp_for_next_level"]
	player.exp_to_next_level = save["player"]["exp_to_next_level"]
	player.strength = save["player"]["strength"]
	player.endurance = save["player"]["endurance"]
	player.defense = save["player"]["defense"]
	player.coins = save["player"]["coins"]
	log.write("Race: " + str(player.race)[6:] + "\r\n")
	log.write("load player" + "\r\n")


def load_player_equipment(player, save):
	"""loads the player's equipped items from the save file"""
	equipped_item = save["player"]["equipped"]
	for weapon in all_weapons:
		if equipped_item["weapon"] is not None:
			if equipped_item["weapon"] == weapon.name:
				player.equipped["weapon"] = weapon
		else:
			player.equipped["weapon"] = None

	for armour in all_armours:
		if equipped_item["helmet"] is not None:
			if equipped_item["helmet"] == armour.name:
				player.equipped["helmet"] = armour
		if equipped_item["chest"] is not None:
			if equipped_item["chest"] == armour.name:
				player.equipped["chest"] = armour
		if equipped_item["gloves"] is not None:
			if equipped_item["gloves"] == armour.name:
				player.equipped["gloves"] = armour
		if equipped_item["belt"] is not None:
			if equipped_item["belt"] == armour.name:
				player.equipped["belt"] = armour
		if equipped_item["pants"] is not None:
			if equipped_item["pants"] == armour.name:
				player.equipped["pants"] = armour
		if equipped_item["shoes"] is not None:
			if equipped_item["shoes"] == armour.name:
				player.equipped["shoes"] = armour


def load_player_inventory(player, save):
	"""loads the player inventory from the save file"""
	player.inventory = save["player"]["inventory"]
	for inv_item in player.inventory[0]:
		index = player.inventory[0].index(inv_item)
		for item in all_items:
			if inv_item == item.name:
				player.inventory[0][index] = item


def save_player(player, save, log):
	"""converts the player object into a dictionary
	and then saves it in the save file
	"""
	save["player"] = player.save_character(log)
	"""del player.inventory_win
	del player.player_status
	del player.quest_log_win
	save["player"] = player.__dict__
	save["player"]["race"] = save["player"]["race"].value
	equipped_item = save["player"]["equipped"]
	if equipped_item["helmet"] is not None:
		equipped_item["helmet"] = equipped_item["helmet"].__dict__
		equipped_item["helmet"] = equipped_item["helmet"]["name"]
	if equipped_item["chest"] is not None:
		equipped_item["chest"] = equipped_item["chest"].__dict__
		equipped_item["chest"] = equipped_item["chest"]["name"]
	if equipped_item["gloves"] is not None:
		equipped_item["gloves"] = equipped_item["gloves"].__dict__
		equipped_item["gloves"] = equipped_item["gloves"]["name"]
	if equipped_item["belt"] is not None:
		equipped_item["belt"] = equipped_item["belt"].__dict__
		equipped_item["belt"] = equipped_item["belt"]["name"]
	if equipped_item["pants"] is not None:
		equipped_item["pants"] = equipped_item["pants"].__dict__
		equipped_item["pants"] = equipped_item["pants"]["name"]
	if equipped_item["shoes"] is not None:
		equipped_item["shoes"] = equipped_item["shoes"].__dict__
		equipped_item["shoes"] = equipped_item["shoes"]["name"]
	if equipped_item["weapon"] is not None:
		equipped_item["weapon"] = equipped_item["weapon"].__dict__
		equipped_item["weapon"] = equipped_item["weapon"]["name"]
	for item in save["player"]["inventory"][0]:
		index = save["player"]["inventory"][0].index(item)
		if isinstance(save["player"]["inventory"][0][index], Item):
			save["player"]["inventory"][0][index] = save["player"]["inventory"][0][index].name"""
	log.write("player saved" + "\r\n")


def update_journal(journal):
	journal.border()
	#journal.addstr(0, 1, "Journal")
	journal.refresh()


def update_game(player, journal):
	player.update_player_status()
	update_journal(journal)


def update_player_location(player, map, log):
	if player.prevlocation.__ne__(player.location):  # moves the Enemy
		if map.inch(player.location[0], player.location[1]) == ord(
				" "):  # stops Enemy from moving if there's a enemy there
			map.addch(player.location[0], player.location[1], ord(player.character))
			map.addch(player.prevlocation[0], player.prevlocation[1], " ")
			player.prevlocation = player.location[:]
		else:
			global current_map
			if map.inch(player.location[0], player.location[1]) == ord("∨"):
				current_map = current_map.go_to_map("north", log)
				current_map.show_map(map)
			if map.inch(player.location[0], player.location[1]) == ord("^"):
				current_map = current_map.go_to_map("south", log)
				current_map.show_map(map)
			if map.inch(player.location[0], player.location[1]) == ord(">"):
				current_map = current_map.go_to_map("west", log)
				current_map.show_map(map)
			if map.inch(player.location[0], player.location[1]) == ord("<"):
				current_map = current_map.go_to_map("east", log)
				current_map.show_map(map)
			player.location = player.prevlocation[:]  # keeps the Enemy at its current location
	if map.inch(player.location[0], player.location[1]) == ord(" "):
		map.addch(player.location[0], player.location[1], ord(player.character))


def print_to_journal(journal, message):
	journal.insertln()
	journal.addstr(1, 1, message)


def player_at_location(player, location):
	if player.location[0] is location[0] and player.location[1] is location[1]:
		return True
	else:
		return False


def player_dead(player, map, journal):
	if player.is_dead():
		if map.inch(player.location[0], player.location[1]) == ord(player.character):
			player.on_death()
			map.addch(player.prevlocation[0], player.prevlocation[1], " ")
			print_to_journal(journal, player.name + " is dead")


def print_combat_intro_text(journal):
	print_to_journal(journal, 'Press "1" to attack or "2" to leave')
	print_to_journal(journal, "Battle has started")
	update_journal(journal)


def set_all_stats(npcs, enemies):
	for npc in npcs:
		npc.set_stats_by_level_and_race()
	for enemy in enemies:
		enemy.set_stats_by_level_and_race()
		enemy.increase_exp_by = int((enemy.level**2)/.4) + 5


def new_game(enemies, npcs, log):
	with open('NewGame.json', 'r') as f:
		save = json.load(f)
		f.close()
	load_enemies(save, enemies, log)
	load_npcs(save, npcs, log)
	set_all_stats(enemies, npcs)
	load_npc_dialogue(npcs, log)
	log.write('len: ' + str(len(npcs)) + "\r\n")


def is_enemy_dead(enemy, player, map, journal):
	if enemy.is_dead():
		if map.inch(enemy.location[0], enemy.location[1]) == ord(enemy.character):
			enemy.on_death(player)
			map.addch(enemy.prevlocation[0], enemy.prevlocation[1], " ")
			print_to_journal(journal, enemy.name + " is dead")
			enemy.prevlocation = enemy.location[:]
			enemy.location = [0, 0]
			print_to_journal(journal, "you gained " + str(enemy.increase_exp_by) + " exp")