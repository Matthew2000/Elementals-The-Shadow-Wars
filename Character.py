import curses
from enum import Enum
from random import randint


class AutoNumber(Enum):
	def __new__(cls):
		value = len(cls.__members__) + 1
		obj = object.__new__(cls)
		obj._value_ = value
		return obj


class Races(AutoNumber):
	Human = ()
	Avaker = ()
	Elf = ()
	Dragon = ()
	Valkyrie = ()


class Character:
	def __init__(self, name, character):
		self.location = [1, 1]
		self.prevlocation = [1, 1]
		self.health = 100
		self.max_health = 100
		self.inventory = {"Coins": 100}
		self.name = name
		self.character = character

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
		opponent.health -= 10

	def death(self):  # kills the Character
		if self.health <= 0:
			self.prevlocation = self.location[:]
			self.location = [0, 0]

	def is_dead(self):  # returns True if the characters health is at or below 0
		if self.health <= 0:
			return True

	def add_coin(self, amount):
		self.inventory["Coins"] += amount

	def add_inventory_item(self, item, amount=0):
		var = False
		for x in self.inventory:
			if item.lower() == x.lower:
				var = True
		if not var:
			self.inventory[item] = amount

	def respawn(self, y, x):
		self.health = self.max_health
		self.location = [y, x]


class Player(Character):
	def __init__(self, name, character):
		super().__init__(name, character)

	def move(self, input_key, area):
		self.prevlocation = self.location[:]
		if input_key == curses.KEY_UP:
			self.move_up()
		elif input_key == curses.KEY_DOWN:
			self.move_down(area)
		elif input_key == curses.KEY_LEFT:
			self.move_left()
		elif input_key == curses.KEY_RIGHT:
			self.move_right(area)

	def attack(self, enemy):
		if enemy.location[0] == self.location[0] + 1 or enemy.location[0] == self.location[0] - 1 or enemy.location[0] == self.location[0]:
			if enemy.location[1] == self.location[1] + 1 or enemy.location[1] == self.location[1] - 1 or enemy.location[1] == self.location[1]:
				super().attack(enemy)


class NPC(Character):
	def __init__(self, name, character):
		super().__init__(name, character)
		self.allow_movement = True
		self.talking = False
		self.dialogue = {"intro": "Hi my name is %s." % self.name, "quest": "I have no quest for you at the moment.", "trade": "I have nothing to trade.", "talk": "I am an NPC."}

	def move(self, area):
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

	def interact(self, log):
		self.talking = True
		log.insertln()
		log.addstr(1, 1, self.dialogue["intro"])


class Enemy(NPC):
	def __init__(self, name, character):
		super().__init__(name, character)
		self.dialogue = {"intro": "I'm going to kill you"}

	def attack(self, player):
		if player.location[0] == self.location[0] + 1 or player.location[0] == self.location[0] - 1 or player.location[0] == self.location[0]:
			if player.location[1] == self.location[1] + 1 or player.location[1] == self.location[1] - 1 or player.location[1] == self.location[1]:
				super().attack(player)
