import curses
from enum import Enum
from random import randint
from Items import *


class Races(Enum):
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

	def add_inventory_item(self, item: Item, amount=1):
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

	def equip_armour(self, item: Armour):
		slot = item.armour_type.value
		self.equipped[slot] = item

	def unequip_armour(self, item: Armour):
		slot = item.armour_type.value
		self.equipped[slot] = None

	def equip_weapon(self, item: Weapon):
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
			player.add_inventory_item(WolfPelt, 1)
