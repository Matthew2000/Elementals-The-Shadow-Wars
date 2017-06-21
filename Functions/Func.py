import string
import json
import os

import Items

#modified from https://gist.github.com/seanh/93666
def sanitize_filename(file_name):
	valid_chars = "-_.%s%s" % (string.ascii_letters, string.digits)
	filename = ''.join(c for c in file_name if c in valid_chars)
	return filename


def load_inventory(inventory):
	"""loads the player inventory from the save file"""
	new_inv = [[], []]
	temp_inv = inventory
	for inv_item in temp_inv[0]:
		index = temp_inv[0].index(inv_item)
		for item in Items.all_items:
			if inv_item == item.name:
				new_inv[0].append(item)
				new_inv[1].append(temp_inv[1][index])
	return new_inv


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


##############################################################


def is_enemy_dead(enemy, player, map, journal):
	if enemy.is_dead():
		if map.inch(enemy.location[0], enemy.location[1]) == ord(enemy.character):
			enemy.on_death(player)
			map.addch(enemy.prevlocation[0], enemy.prevlocation[1], " ")
			print_to_journal(journal, enemy.name + " is dead")
			enemy.prevlocation = enemy.location[:]
			enemy.location = [0, 0]
			print_to_journal(journal, "you gained " + str(enemy.increase_exp_by) + " exp")


def update_enemy_status(enemy, enemy_stat_win):
	enemy_stat_win.clear()
	if enemy.allow_movement is False:
		enemy_stat_win.border()
		enemy_stat_win.addstr(0, 1, enemy.name + "'s Stats")
		enemy_stat_win.addstr(1, 1, "Race: " + str(enemy.race)[6:])
		enemy_stat_win.addstr(2, 1, "Health: " + str(enemy.health))
		enemy_stat_win.addstr(3, 1, "Level: " + str(enemy.level))
		enemy_stat_win.addstr(4, 1, "Strength: " + str(enemy.strength))
		enemy_stat_win.addstr(5, 1, "Defense: " + str(enemy.defense))
	enemy_stat_win.refresh()


def update_enemy_locations(enemies, map):
	for enemy in enemies:
		if enemy.prevlocation.__ne__(enemy.location):  # moves the Enemy
			if map.inch(enemy.location[0], enemy.location[1]) == ord(
					" "):  # stops Enemy from moving if there's a enemy there
				map.addch(enemy.location[0], enemy.location[1], ord(enemy.character))
				map.addch(enemy.prevlocation[0], enemy.prevlocation[1], " ")
				enemy.prevlocation = enemy.location[:]
			else:
				enemy.location = enemy.prevlocation[:]  # keeps the Enemy at its current location
		if map.inch(enemy.location[0], enemy.location[1]) == ord(" "):
			map.addch(enemy.location[0], enemy.location[1], ord(enemy.character))


def enemy_at_location(enemies, location, enemy_stat_win):
	for enemy in enemies:
		if enemy.location[0] is location[0] and enemy.location[1] is location[1]:
			update_enemy_status(enemy, enemy_stat_win)
			enemy.allow_movement = False
			return {"result": True, "enemy": enemy}
	else:
		return {"result": False}


def follow_the_player(enemies, player):
	for enemy in enemies:
		enemy.follow_player(player)


def respawn_enemies(enemies):
	for enemy in enemies:
		if enemy.is_dead():
			if enemy.respawnable:
				enemy.respawn_counter += 1
				if enemy.respawn_counter == 20:
					enemy.respawn_counter = 0
					enemy.respawn()
