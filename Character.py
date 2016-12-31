import curses
from enum import Enum
from random import randint
from Items import *


class AutoNumber(Enum):
	def __new__(cls):
		value = len(cls.__members__) + 1
		obj = object.__new__(cls)
		obj._value_ = value
		return obj


class Races(AutoNumber):
	Human = ()     # 1
	Avaker = ()    # 2
	Elf = ()       # 3
	Dragon = ()    # 4
	Valkyrie = ()  # 5
	Wolf = ()      # 6


class Character:
	def __init__(self, name: str, character: chr, race: Races):
		self.location = [1, 1]
		self.prevlocation = [1, 1]
		self.health = 100
		self.max_health = 100
		self.inventory = {"Coins": 100}
		self.equipped = {"helmet": None, "chest": None, "gloves": None, "belt": None, "pants": None, "shoes": None, "weapon": None}
		self.name = name
		self.character = character
		self.race = race
		self.level = 1
		self.strength = 10
		self.defence = 0
		self.endurance = 0
		self.damage = 0
		self.total_exp = 0
		self.exp_for_next_level = 0
		self.exp_to_next_level = float(25)
		self.health_regen = 5

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
			self.damage = int((randint(5, 11) + (self.strength * .2)) - ((randint(5, 11) + (self.strength * .1)) * opponent.defence / 100))
			if self.race is not Races.Wolf:
				if self.equipped["weapon"] is not None:
					self.damage = int(((randint(5, 11) + (self.strength * .2)) * self.equipped["weapon"].damage) - ((randint(5, 11) + (self.strength * .1)) * opponent.defence / 100))
			if self.damage <= 0:
				self.damage = 0
			opponent.health -= self.damage

	def death(self):  # kills the Character
		if self.health <= 0:
			self.prevlocation = self.location[:]
			self.location = [0, 0]

	def is_dead(self):  # returns True if the characters health is at or below 0
		if self.health <= 0:
			return True

	def add_inventory_item(self, item, amount=0):
		var = False
		for x in self.inventory:
			if item.lower() == x.lower():
				var = True
				self.inventory[item] += amount
		if not var:
			self.inventory[item] = amount

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
		armour_defence = self.get_defence_from_armour()
		if self.race is Races.Wolf:
			self.endurance = int(5 * (self.level - 1)) + 2
			self.defence = self.endurance
			self.strength = int(10 + (5 * (self.level-1))) + 10
			self.max_health = int((100 + (100 * (self.endurance * .3))))
			self.health = int(self.max_health)
		elif self.race is Races.Elf:
			self.endurance = int(5 * (self.level - 1)) + 5
			self.defence = self.endurance + armour_defence
			self.strength = int(10 + (5 * (self.level - 1))) + 5
			self.max_health = int((100 + (100 * (self.endurance * .3)))) + 50
			self.health = int(self.max_health)
		elif self.race is Races.Human:
			self.endurance = int(5 * (self.level - 1))
			self.defence = self.endurance + armour_defence
			self.strength = int(10 + (5 * (self.level - 1)))
			self.max_health = int((100 + (100 * (self.endurance * .3))))
			self.health = int(self.max_health)

	def equip_armour(self, item: Armour):
		slot = item.armour_type.value
		self.equipped[slot] = item

	def equip_weapon(self, item: Weapon):
		self.equipped["weapon"] = item

	def get_defence_from_armour(self):
		temp_defence = 0
		if self.equipped != {}:
			if self.equipped["helmet"] is not None:
				temp_defence += self.equipped["helmet"].protection
			if self.equipped["chest"] is not None:
				temp_defence += self.equipped["chest"].protection
			if self.equipped["gloves"] is not None:
				temp_defence += self.equipped["gloves"].protection
			if self.equipped["belt"] is not None:
				temp_defence += self.equipped["belt"].protection
			if self.equipped["pants"] is not None:
				temp_defence += self.equipped["pants"].protection
			if self.equipped["shoes"] is not None:
				temp_defence += self.equipped["shoes"].protection
		return temp_defence


class Player(Character):
	def __init__(self, name: str, character: chr, race: Races):
		super().__init__(name, character, race)
		self.quests = {}
		self.equipped = {"helmet": None, "chest": None, "gloves": None, "belt": None, "pants": None, "shoes": None, "weapon": IronDagger}

	def move(self, input_key, area):
		self.prevlocation = self.location[:]
		if input_key == curses.KEY_UP or input_key == ord("w"):
			self.move_up()
		elif input_key == curses.KEY_DOWN or input_key == ord("s"):
			self.move_down(area)
		elif input_key == curses.KEY_LEFT or input_key == ord("a"):
			self.move_left()
		elif input_key == curses.KEY_RIGHT or input_key == ord("d"):
			self.move_right(area)

	def attack(self, enemy):
		if enemy.location[0] == self.location[0] + 1 or enemy.location[0] == self.location[0] - 1 or enemy.location[0] == self.location[0]:
			if enemy.location[1] == self.location[1] + 1 or enemy.location[1] == self.location[1] - 1 or enemy.location[1] == self.location[1]:
				super().attack(enemy)

	def add_quest(self, quest):
		self.quests[quest["quest name"]] = quest

	def update_quests(self, enemies, npcs, journal):
		# TODO make function for updating each type of quest
		for quest in self.quests:
			requirement = self.quests[quest]["objective"]["requirement"]
			if requirement == "kill":
				for enemy in enemies:
					if enemy.name == self.quests[quest]["objective"]["object"]:
						if enemy.is_dead():
							if not self.quests[quest]["quest completed"]:
								journal.insertln()
								journal.addstr(1, 1, "You have completed the quest go to %s to claim your reward" % self.quests[quest]["quest giver"])
							self.quests[quest]["quest completed"] = True
						else:
							self.quests[quest]["quest completed"] = False
			if requirement.lower() == "collect":
				item = self.quests[quest]["objective"]["object"]
				amount = self.quests[quest]["objective"]["amount"]
				if item in self.inventory:
						if self.inventory[item] >= amount:
							self.quests[quest]["quest completed"] = True
						else:
							self.quests[quest]["quest completed"] = False

	def level_up(self):
		self.exp_for_next_level -= self.exp_to_next_level
		self.level += 1
		self.exp_to_next_level = float(int((self.level ** 2) / .04))
		self.set_stats_by_level_and_race()


class NPC(Character):
	def __init__(self, name: str, character: chr, race: Races):
		super().__init__(name, character, race)
		self.allow_movement = True
		self.talking = False
		self.dialogue = {"intro": "Hi my name is %s." % self.name, "quest": [{"quest name": "name", "quest type": "unique", "description": "quest description.", "objective": {"amount": 0, "requirement": "quest requirement", "object": "object"}, "reward": {"object": "reward object", "amount": "reward amount", "exp": 0}, "quest completed": False, "quest giver": self.name}], "trade": "I have nothing to trade.", "talk": "I am an NPC."}
		self.has_quest = False
		self.spawn_location = [10, 10]
		self.respawn_counter = 0
		self.respawnable = False

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

	def conversation_start(self, conversation):
		conversation.clear()
		conversation.border()
		conversation.addstr(0, 1, "Conversation")
		conversation.addstr(2, 1, "1 - Talk")
		conversation.addstr(3, 1, "2 - Quest")
		conversation.addstr(4, 1, "3 - Trade")
		conversation.addstr(5, 1, "4 - Leave")
		conversation.refresh()

	def show_options(self, conversation, log, *options):
		x = 2
		y = 1
		conversation.clear()
		conversation.border()
		conversation.addstr(0, 1, "Conversation")
		for option in options:
			if option == str(option):
				conversation.addstr(x, 1, str(y) + " - " + str(option))
				x += 1
				y += 1
			else:
				for option1 in option:
					conversation.addstr(x, 1, str(y) + " - " + str(option1))
					x += 1
					y += 1
		conversation.refresh()

	def interact(self, journal, conversation, input_key, player, log, enemies, npcs):
		if not self.dialogue["quest"]:
			self.has_quest = False
		if self.talking is False:
			journal.insertln()
			journal.addstr(1, 1, self.dialogue["intro"])
			self.conversation_start(conversation)
		self.talking = True
		if input_key is ord("1"):
			# TODO make more complex conversations
			journal.insertln()
			journal.addstr(1, 1, self.dialogue["talk"])
			self.conversation_start(conversation)
		elif input_key is ord("2"):

			def choose_quest(key, quests):
				# TODO check to see if the quest is already completed when choosing quests
				# TODO make a new type of quest to talk to another npc
				player.update_quests(enemies, npcs, journal)
				log.write(str(int(chr(int(key)-1))) + "\r\n")
				quest_list = quests
				if int(chr(key))-1 >= len(quest_list):
					pass
				else:
					quest = quest_list[int(chr(int(key) - 1))]
					index = int(chr(int(key) - 1))
					if quest["quest name"] not in player.quests:
						journal.insertln()
						journal.addstr(1, 1, quest["description"])
						log.write("not fail" + "\r\n")
						journal.border()
						journal.refresh()
						list_key = int(chr(int(key) - 1))
						while 1:
							self.show_options(conversation, log, "Yes", "No")
							key = conversation.getch()
							if key is ord("1"):
								journal.insertln()
								journal.addstr(1, 1, "You have accepted the quest")
								journal.refresh()
								player.add_quest(quest_list[list_key])
								self.conversation_start(conversation)
								break
							elif key is ord("2"):
								break
					elif player.quests[quest["quest name"]]["quest completed"] == True:
						journal.insertln()
						journal.addstr(1, 1, "You have completed my quest, here is your reward.")
						journal.border()
						journal.refresh()
						self.show_options(conversation, log, "1 - Accept")
						key = conversation.getch()
						if key is ord("1"):
							player.add_inventory_item(quest["reward"]["object"], quest["reward"]["amount"])
							player.increase_exp(quest["reward"]["exp"])
							if quest["objective"]["requirement"] == "collect":
								item = quest["objective"]["object"]
								amount = quest["objective"]["amount"]
								player.inventory[item] -= amount
							del player.quests[quest["quest name"]]
							if quest["quest type"] == "unique":
								del self.dialogue["quest"][index]
							self.conversation_start(conversation)
					else:
						journal.insertln()
						journal.addstr(1, 1, "You have already accepted that quest.")
						journal.border()
						journal.refresh()

			if self.has_quest is True:
				while 1:
					journal.insertln()
					journal.addstr(1, 1, "These are the quests that I have")
					journal.border()
					journal.refresh()
					quest_list = []
					for quest in self.dialogue["quest"]:
						log.write(quest["quest name"] + "\r\n")
						quest_list.append(quest["quest name"])
					self.show_options(conversation, log, quest_list)

					quest_number = []
					for quest in self.dialogue["quest"]:
						quest_number.append(quest)
					input_key = conversation.getch()
					choose_quest(input_key, quest_number)
					self.conversation_start(conversation)
					break
			else:
				journal.insertln()
				journal.addstr(1, 1, "I have no quest for you at the moment")
				journal.refresh()
		elif input_key is ord("3"):
			journal.insertln()
			journal.addstr(1, 1, self.dialogue["trade"])
			self.conversation_start(conversation)

	# TODO make a trade system
	#def trade(self):

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

	def respawn(self):
		self.health = self.max_health
		self.location = self.spawn_location[:]


class Enemy(Character):
	def __init__(self, ID, name: str, character: chr, race: Races):
		super().__init__(name, character, race)
		self.increase_exp_by = int((self.level**2)/.4) + 5
		self.ID = ID
		self.health_regen = 15
		self.spawn_location = [10, 10]
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

	def death(self, player):
		super().death()
		player.increase_exp(self.increase_exp_by)
		if self.race is Races.Wolf:
			player.add_inventory_item("Wolf Pelt", 1)
