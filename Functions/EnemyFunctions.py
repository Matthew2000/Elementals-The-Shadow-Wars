import os.path
from Character import *
import curses
import json


def create_enemy(ID, name, character, race: Races, enemies, log):  # this function must be assigned to an object
	var = False
	for x in enemies:
		if ID == x.ID:
			var = True
			log.write(x.ID + " is already there" + "\r\n")
	if not var:
		enemies.append(Enemy(ID, name, character, race))
	return enemies[len(enemies) - 1]


def save_enemies(save, enemies, log):
	all_enemies = enemies[:]
	enemies.clear()
	for enemy in all_enemies:
		temp_enemy = enemy.__dict__
		temp_enemy["race"] = temp_enemy["race"].value
		equipped_item = temp_enemy["equipped"]
		if temp_enemy["race"] == 6:
			pass
		else:
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
		enemies.append(temp_enemy)
	save["all_enemies"].clear()
	save["all_enemies"] = enemies[:]
	log.write("save enemies" + "\r\n")


def load_enemies(save, enemies, log):
	enemies.clear()
	for enemy in save["all_enemies"]:
		log.write(enemy["name"] + " ")
		temp_enemy = create_enemy(enemy["ID"], enemy["name"], enemy["character"], Races(enemy["race"]), enemies, log)
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
		temp_enemy.respawnable = enemy["respawnable"]
		temp_enemy.spawn_location = enemy["spawn_location"]
		temp_enemy.endurance = enemy["endurance"]
		temp_enemy.defence = enemy["defence"]
		# load equipped enemy items
		if temp_enemy.race is not Races.Wolf:
			equipped_item = enemy["equipped"]
			for weapon in all_weapons:
				if equipped_item["weapon"] is not None:
					if equipped_item["weapon"] == weapon.name:
						temp_enemy.equipped["weapon"] = weapon
			for armour in all_armours:
				if equipped_item["helmet"] is not None:
					if equipped_item["helmet"] == armour.name:
						temp_enemy.equipped["helmet"] = armour
				if equipped_item["chest"] is not None:
					if equipped_item["chest"] == armour.name:
						temp_enemy.equipped["chest"] = armour
				if equipped_item["gloves"] is not None:
					if equipped_item["gloves"] == armour.name:
						temp_enemy.equipped["gloves"] = armour
				if equipped_item["belt"] is not None:
					if equipped_item["belt"] == armour.name:
						temp_enemy.equipped["belt"] = armour
				if equipped_item["pants"] is not None:
					if equipped_item["pants"] == armour.name:
						temp_enemy.equipped["pants"] = armour
				if equipped_item["shoes"] is not None:
					if equipped_item["shoes"] == armour.name:
						temp_enemy.equipped["shoes"] = armour
		elif temp_enemy.race is Races.Wolf:
			temp_enemy.equipped = {}
		log.write("Race: " + str(temp_enemy.race)[6:] + "\r\n")
	log.write("load enemies" + "\r\n")


def update_enemy_status(enemy, enemy_stat_win):
	enemy_stat_win.clear()
	if enemy.allow_movement is False:
		enemy_stat_win.border()
		enemy_stat_win.addstr(0, 1, enemy.name + "'s Stats")
		enemy_stat_win.addstr(1, 1, "Race: " + str(enemy.race)[6:])
		enemy_stat_win.addstr(2, 1, "Health: " + str(enemy.health))
		enemy_stat_win.addstr(3, 1, "Level: " + str(enemy.level))
		enemy_stat_win.addstr(4, 1, "Strength: " + str(enemy.strength))
		enemy_stat_win.addstr(5, 1, "Defence: " + str(enemy.defence))
	enemy_stat_win.refresh()


def update_enemy_locations(enemies, map):
	for enemy in enemies:
		if enemy.prevlocation.__ne__(enemy.location):  # moves the Enemy
			if map.inch(enemy.location[0], enemy.location[1]) == ord(
					" "):  # stops Enemy from moving if there's a enemy there
				map.addch(enemy.location[0], enemy.location[1], ord(enemy.character))
				map.addch(enemy.prevlocation[0], enemy.prevlocation[1], " ")
			else:
				enemy.location = enemy.prevlocation[:]  # keeps the Enemy at its current location


def spawn_character(map, character, y, x):
	character.location[0] = y
	character.location[1] = x
	character.prevlocation[0] = y
	character.prevlocation[1] = x
	map.addch(y, x, ord(character.character))


def place_enemies(enemies, map):
	for enemy in enemies:
		spawn_character(map, enemy, enemy.location[0], enemy.location[1])


def enemy_at_location(enemies, y, x, enemy_stat_win):
	for enemy in enemies:
		if enemy.location[0] is y and enemy.location[1] is x:
			update_enemy_status(enemy, enemy_stat_win)
			enemy.allow_movement = False
			return {"result": True, "enemy": enemy}
	else:
		return {"result": False}


def player_at_location(player, y, x):
	if player.location[0] is y and player.location[1] is x:
		return True
	else:
		return False


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


def enemy_health_regen(enemies):
	for enemy in enemies:
		if not enemy.is_dead():
			if enemy.health < enemy.max_health:
				enemy.health += enemy.health_regen
				if enemy.health >= enemy.max_health:
					enemy.health = enemy.max_health