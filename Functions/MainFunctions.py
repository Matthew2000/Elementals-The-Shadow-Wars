from Functions.EnemyFunctions import *
from Functions.NPCFunctions import *
import string

def create_player(name: str, character: chr, race: Races, area):
	temp_player = Player(name, character, race)
	temp_player.location = [int(area[0]/2), int(area[1]/2)]
	return temp_player


def load_player(player, save, log):
	player.name = save["player"]["name"]
	log.write(player.name + " ")
	player.location = save["player"]["location"]
	player.prevlocation = save["player"]["prevlocation"]
	player.health = save["player"]["health"]
	player.character = save["player"]["character"]
	player.inventory = save["player"]["inventory"]
	player.max_health = save["player"]["max_health"]
	player.quests = save["player"]["quests"]
	player.race = Races(save["player"]["race"])
	player.level = save["player"]["level"]
	player.total_exp = save["player"]["total_exp"]
	player.exp_for_next_level = save["player"]["exp_for_next_level"]
	player.exp_to_next_level = save["player"]["exp_to_next_level"]
	player.strength = save["player"]["strength"]
	player.endurance = save["player"]["endurance"]
	player.defense = save["player"]["defense"]
	log.write("Race: " + str(player.race)[6:] + "\r\n")
	log.write("load player" + "\r\n")


def load_player_equipment(player, save):
	equipped_item = save["player"]["equipped"]
	for weapon in all_weapons:
		if equipped_item["weapon"] is not None:
			if equipped_item["weapon"] == weapon.name:
				player.equipped["weapon"] = weapon

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


def save_player(player, save, log):
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
	log.write("player saved" + "\r\n")


def update_inventory(player, inventory):
	x = 1
	inventory.clear()
	inventory.border()
	inventory.addstr(0, 1, "Inventory")
	for item in player.inventory:
		inventory.addstr(x, 1, item + ": " + str(player.inventory[item]))
		x += 1
	inventory.refresh()


def update_player_status(player, player_stat_win):
	player_stat_win.clear()
	player_stat_win.border()
	player_stat_win.addstr(0, 1, "Player Stats")
	player_stat_win.addstr(1, 1, "Health: " + str(player.health))
	player_stat_win.addstr(2, 1, "Strength: " + str(player.strength))
	player_stat_win.addstr(3, 1, "Defense: " + str(player.defense))
	player_stat_win.addstr(4, 1, "Race: " + str(player.race)[6:])
	player_stat_win.addstr(5, 1, "Level: " + str(player.level))
	player_stat_win.addstr(6, 1, "exp needed: " + str(player.exp_to_next_level - player.exp_for_next_level)[:len(str(player.exp_to_next_level - player.exp_for_next_level)) - 2])
	player_stat_win.refresh()


def update_journal(journal):
	journal.border()
	journal.refresh()


def update_game(player, player_stat_win, inventory, journal):
	update_player_status(player, player_stat_win)
	update_inventory(player, inventory)
	update_journal(journal)


def update_player_location(player, map):
	if player.prevlocation.__ne__(player.location):  # moves the Enemy
		if map.inch(player.location[0], player.location[1]) == ord(
				" "):  # stops Enemy from moving if there's a enemy there
			map.addch(player.location[0], player.location[1], ord(player.character))
			map.addch(player.prevlocation[0], player.prevlocation[1], " ")
		else:
			player.location = player.prevlocation[:]  # keeps the Enemy at its current location


def print_to_journal(journal, message):
	journal.insertln()
	journal.addstr(1, 1, message)


def player_at_location(player, y, x):
	if player.location[0] is y and player.location[1] is x:
		return True
	else:
		return False


def player_dead(player, map, journal):
	if player.is_dead():
		if map.inch(player.location[0], player.location[1]) == ord(player.character):
			player.death()
			map.addch(player.prevlocation[0], player.prevlocation[1], " ")
			print_to_journal(journal, player.name + " is dead")


def enter_combat(player, enemy, key, map, enemy_stat_win, player_stat_win, log, journal):
	print_to_journal(journal, 'Press "1" to attack or "2" to leave')
	print_to_journal(journal, "Battle has started")
	update_journal(journal)
	update_enemy_status(enemy, enemy_stat_win)
	update_player_status(player, enemy_stat_win)
	while key is not ord("2"):
		update_enemy_status(enemy, enemy_stat_win)
		update_player_status(player, player_stat_win)
		if enemy.health <= 0:
			is_enemy_dead(enemy, player, map, journal, log)
			enemy.allow_movement = True
			update_enemy_status(enemy, enemy_stat_win)
			break
		if player.health <= 0:
			if player.is_dead():
				player_dead(player, map, journal)
				update_player_location(player, map)
			enemy.allow_movement = True
			update_enemy_status(enemy, enemy_stat_win)
			break
		key = map.getch()
		if key is ord("1"):
			player.attack(enemy)
		enemy.attack(player)
	else:
		enemy.allow_movement = True
		print_to_journal(journal, "You have left combat")


def set_all_stats(npcs, enemies):
	for npc in npcs:
		npc.set_stats_by_level_and_race()
	for enemy in enemies:
		enemy.set_stats_by_level_and_race()
		enemy.increase_exp_by = int((enemy.level**2)/.4) + 5


def new_game(save, enemies, npcs, log):
	with open('NewGame.json', 'r') as f:
		save = json.load(f)
		f.close()
	load_enemies(save, enemies, log)
	load_npcs(save, npcs, log)
	set_all_stats(enemies, npcs)
	load_npc_dialogue(npcs, log)
	log.write('len: ' + str(len(npcs)))


def player_health_regen(player):
	if not (player.health >= player.max_health):
		player.health += player.health_regen
		if player.health >= player.max_health:
			player.health = player.max_health


def is_enemy_dead(enemy, player, map, journal, log):
	if enemy.is_dead():
		if map.inch(enemy.location[0], enemy.location[1]) == ord(enemy.character):
			enemy.death(player)
			map.addch(enemy.prevlocation[0], enemy.prevlocation[1], " ")
			print_to_journal(journal, enemy.name + " is dead")
			enemy.prevlocation = enemy.location[:]
			enemy.location = [0, 0]
			log.write("player exp is: " + str(player.total_exp) + "\r\n")
			print_to_journal(journal, "you gained " + str(enemy.increase_exp_by) + " exp")


def move_enemies(enemies, player, area, log, enemy_stat_win, map, player_stat_win, journal):
	for enemy in enemies:
		if not enemy.is_dead():
			enemy.move(area, player)
			if player_at_location(player, enemy.location[0], enemy.location[1]):
				enemy.allow_movement = False
				enter_combat(player, enemy, -1, map, enemy_stat_win, player_stat_win, log, journal)
