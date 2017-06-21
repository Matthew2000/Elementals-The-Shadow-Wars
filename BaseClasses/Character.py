from random import randint
from enum import Enum

import Items


class Races(Enum):
	Unknown = 0
	Human = 1
	Avaker = 2
	Elf = 3
	Dragon = 4
	Valkyrie = 5
	Wolf = 6


class Character:
	def __init__(self, name: str, character: chr, race: Races):
		self.location = [1, 1]
		self.prevlocation = [1, 1]
		self.health = 100
		self.max_health = 100
		self.coins = 100
		self.inventory = [
					[],
					[]
					]
		self.equipped = {"helmet": None, "chest": None, "gloves": None, "belt": None, "pants": None, "shoes": None, "weapon": None}
		self.name = name
		self.character = character
		self.race = race
		self.level = 1
		self.strength = 10
		self.defense = 0
		self.endurance = 0
		self.damage = 0
		self.total_exp = 0
		self.exp_for_next_level = 0
		self.exp_to_next_level = float(25)
		self.health_regen = 5
		self.spawn_location = [10, 10]

	def move_up(self):
		if self.location[0] > 1:
			self.location[0] -= 1

	def move_down(self, area):
		if self.location[0] < area[0] - 2:
			self.location[0] += 1

	def move_left(self):
		if self.location[1] > 1:
			self.location[1] -= 1

	def move_right(self, area):
		if self.location[1] < area[1] - 2:
			self.location[1] += 1

	def attack(self, opponent):  # what you attack must inherit from Character
		x = randint(0, 11)
		if x is 0:
			pass
		else:
			self.damage = int((randint(5, 11) + (self.strength * .2)) - ((randint(5, 11) + (self.strength * .1)) * opponent.defense / 100))
			if self.race is not Races.Wolf:
				if self.equipped["weapon"] is not None:
					self.damage = int(((randint(5, 11) + (self.strength * .2)) * self.equipped["weapon"].damage) - ((randint(5, 11) + (self.strength * .1)) * opponent.defense / 100))
			if self.damage <= 0:
				self.damage = 0
			opponent.health -= self.damage

	def on_death(self):  # kills the Character
		if self.health <= 0:
			self.prevlocation = self.location[:]
			self.location = [0, 0]

	def is_dead(self):  # returns True if the characters health is at or below 0
		if self.health <= 0:
			return True

	def add_inventory_item(self, item: Items.Item, amount=1):
		var = False
		index = 0
		for x in self.inventory[0]:
			if item == x:
				var = True
				self.inventory[1][index] += amount
			index += 1
		if not var:
			self.inventory[0].append(item)
			self.inventory[1].append(1)

	def remove_inventory_item(self, item, amount=1):
		index = self.inventory[0].index(item)
		self.inventory[0].remove(item)
		del self.inventory[1][index]

	def respawn(self, y, x):
		self.health = self.max_health
		self.location = [y, x]

	def increase_exp(self, amount):
		self.total_exp += amount
		self.exp_for_next_level += amount

	def exp_is_enough(self):
		if self.exp_for_next_level >= self.exp_to_next_level:
			return True

	def set_stats_by_level_and_race(self):
		armour_defense = self.get_defense_from_armour()
		if self.race is Races.Wolf:
			self.endurance = int(5 * (self.level - 1)) + 2
			self.defense = self.endurance
			self.strength = int(10 + (5 * (self.level-1))) + 10
			self.max_health = int((100 + (100 * (self.endurance * .3))))
			self.health = int(self.max_health)
		elif self.race is Races.Elf:
			self.endurance = int(5 * (self.level - 1)) + 5
			self.defense = self.endurance + armour_defense
			self.strength = int(10 + (5 * (self.level - 1))) + 5
			self.max_health = int((100 + (100 * (self.endurance * .3)))) + 50
			self.health = int(self.max_health)
		elif self.race is Races.Human:
			self.endurance = int(5 * (self.level - 1))
			self.defense = self.endurance + armour_defense
			self.strength = int(10 + (5 * (self.level - 1)))
			self.max_health = int((100 + (100 * (self.endurance * .3))))
			self.health = int(self.max_health)

	def equip_armour(self, item: Items.Armour):
		slot = item.armour_type.value
		self.equipped[slot] = item

	def unequip_armour(self, item: Items.Armour):
		slot = item.armour_type.value
		self.equipped[slot] = None

	def equip_weapon(self, item: Items.Weapon):
		self.equipped["weapon"] = item

	def unequip_weapon(self):
		self.equipped["weapon"] = None

	def get_defense_from_armour(self):
		temp_defense = 0
		if self.equipped != {}:
			if self.equipped["helmet"] is not None:
				temp_defense += self.equipped["helmet"].protection
			if self.equipped["chest"] is not None:
				temp_defense += self.equipped["chest"].protection
			if self.equipped["gloves"] is not None:
				temp_defense += self.equipped["gloves"].protection
			if self.equipped["belt"] is not None:
				temp_defense += self.equipped["belt"].protection
			if self.equipped["pants"] is not None:
				temp_defense += self.equipped["pants"].protection
			if self.equipped["shoes"] is not None:
				temp_defense += self.equipped["shoes"].protection
		return temp_defense

	def regenerate_health(self):
		if not self.is_dead():
			if self.health < self.max_health:
				self.health += self.health_regen
				if self.health >= self.max_health:
					self.health = self.max_health

	def save_character(self, log):
		character = {}
		character["location"] = self.location
		character["health"] = self.health
		character["name"] = self.name
		return character


class Enemy(Character):
	def __init__(self, ID, name: str, character: chr, race: Races):
		super().__init__(name, character, race)
		self.increase_exp_by = int((self.level**2)/.4) + 5
		self.ID = ID
		self.health_regen = 15
		self.respawn_counter = 0
		self.respawnable = False
		self.allow_movement = True

	def respawn(self):
		self.health = self.max_health
		self.location = self.spawn_location[:]

	def is_near_player(self, player, distance):
		x = False
		y = False
		if distance >= (player.location[0] - self.location[0]) >= (distance * -1):
			y = True
		if distance >= (player.location[1] - self.location[1]) >= (distance * -1):
			x = True
		if x and y:
			return True
		else:
			return False

	def move_to(self, y, x):
		if y == self.location[0] and x == self.location[1]:
			self.prevlocation = self.location[:]
			pass
		elif self.location[0] == y:
			self.prevlocation = self.location[:]
			if x > self.location[1]:
				self.location[1] += 1
			else:
				self.location[1] -= 1
		elif self.location[1] == x:
			self.prevlocation = self.location[:]
			if y > self.location[0]:
				self.location[0] += 1
			else:
				self.location[0] -= 1
		elif abs(x - self.location[1]) >= abs(y - self.location[0]):
			self.prevlocation = self.location[:]
			if x > self.location[1]:
				self.location[1] += 1
			else:
				self.location[1] -= 1
		elif abs(x - self.location[1]) <= abs(y - self.location[0]):
			self.prevlocation = self.location[:]
			if y > self.location[0]:
				self.location[0] += 1
			else:
				self.location[0] -= 1

	def attack(self, player):
		if player.location[0] == self.location[0] + 1 or player.location[0] == self.location[0] - 1 or player.location[0] == self.location[0]:
			if player.location[1] == self.location[1] + 1 or player.location[1] == self.location[1] - 1 or player.location[1] == self.location[1]:
				super().attack(player)

	def follow_player(self, player):
		if self.is_near_player(player, 5):
			self.move_to(player.location[0], player.location[1])

	def move(self, area, player):
		if ((player.level - self.level) >= 9) is False:
			if self.is_near_player(player, 5):
				self.follow_player(player)
			else:
				if self.allow_movement:
					self.prevlocation = self.location[:]
					direction = randint(0, 4)
					if direction is 0:
						pass
					elif direction is 1:
						self.move_up()
					elif direction is 2:
						self.move_down(area)
					elif direction is 3:
						self.move_right(area)
					else:
						self.move_left()
		else:
			if self.allow_movement:
				self.prevlocation = self.location[:]
				direction = randint(0, 4)
				if direction is 0:
					pass
				elif direction is 1:
					self.move_up()
				elif direction is 2:
					self.move_down(area)
				elif direction is 3:
					self.move_right(area)
				else:
					self.move_left()

	def on_death(self, player):
		super().on_death()
		player.increase_exp(self.increase_exp_by)
		if self.race is Races.Wolf:
			player.add_inventory_item(Items.WolfPelt, 1)


def place_enemies(enemies, map):
	for enemy in enemies:
		spawn_character(map, enemy, enemy.location[0], enemy.location[1])


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
		temp_enemy.defense = enemy["defense"]
		# load equipped enemy items
		if temp_enemy.race is not Races.Wolf:
			equipped_item = enemy["equipped"]
			for weapon in Items.all_weapons:
				if equipped_item["weapon"] is not None:
					if equipped_item["weapon"] == weapon.name:
						temp_enemy.equipped["weapon"] = weapon
			for armour in Items.all_armours:
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


def spawn_character(map, character, y, x):
	character.location[0] = y
	character.location[1] = x
	character.prevlocation[0] = y
	character.prevlocation[1] = x
	map.addch(y, x, ord(character.character))
