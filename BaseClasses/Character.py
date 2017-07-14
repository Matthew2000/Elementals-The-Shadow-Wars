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
	all_NPCs = []
	all_enemies = []

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

	def begin_play(self):
		pass

	def tick(self, input_key):
		pass

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

	def save_character(self):
		character = {}
		character["location"] = self.location
		character["health"] = self.health
		character["name"] = self.name
		return character


def spawn_character(map, character, y, x):
	character.location[0] = y
	character.location[1] = x
	character.prevlocation[0] = y
	character.prevlocation[1] = x
	map.addch(y, x, ord(character.character))
