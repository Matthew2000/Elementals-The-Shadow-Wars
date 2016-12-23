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
	Human = ()     # 1
	Avaker = ()    # 2
	Elf = ()       # 3
	Dragon = ()    # 4
	Valkyrie = ()  # 5


class Character:
	def __init__(self, name: str, character: chr, race: Races):
		self.location = [1, 1]
		self.prevlocation = [1, 1]
		self.health = 100
		self.max_health = 100
		self.inventory = {"Coins": 100}
		self.name = name
		self.character = character
		self.race = race

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
	def __init__(self, name: str, character: chr, race: Races):
		super().__init__(name, character, race)
		self.quests = {}

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


class NPC(Character):
	def __init__(self, name: str, character: chr, race: Races):
		super().__init__(name, character, race)
		self.allow_movement = True
		self.talking = False
		self.dialogue = {"intro": "Hi my name is %s." % self.name, "quest": [{"quest name": "name", "description": "quest description.", "objective": {"requirement": "quest requirement", "object": "object"}, "reward": {"object": "reward object", "amount": "reward amount"}, "quest completed": False, "quest giver": self.name}], "trade": "I have nothing to trade.", "talk": "I am an NPC."}
		self.has_quest = False

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

	def interact(self, journal, conversation, input_key, player, log):
		if self.talking is False:
			journal.insertln()
			journal.addstr(1, 1, self.dialogue["intro"])
			self.conversation_start(conversation)
		self.talking = True
		if input_key is ord("1"):
			journal.insertln()
			journal.addstr(1, 1, self.dialogue["talk"])
			self.conversation_start(conversation)
		elif input_key is ord("2"):

			def choose_quest(key, quests):
				log.write(str(int(chr(int(key)-1))) + "\r\n")
				quest_list = quests
				quest = quest_list[int(chr(int(key)-1))]
				if str(int(chr(key))-1) >= str(len(quest_list)):
					pass
				else:
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
					elif player.quests[quest["quest name"]]["quest completed"]:
						journal.insertln()
						journal.addstr(1, 1, "You have completed my quest, here is your reward.")
						journal.border()
						journal.refresh()
						self.show_options(conversation, log, "1 - Accept")
						key = conversation.getch()
						if key is ord("1"):
							if quest["reward"]["object"] not in player.inventory:
								player.add_inventory_item(quest["reward"]["object"], 0)
							player.inventory[quest["reward"]["object"]] += quest["reward"]["amount"]
							del player.quests[quest["quest name"]]
							self.conversation_start(conversation)

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


class Enemy(NPC):
	def __init__(self, name: str, character: chr, race: Races):
		super().__init__(name, character, race)
		self.dialogue = {"intro": "I'm going to kill you"}

	def attack(self, player):
		if player.location[0] == self.location[0] + 1 or player.location[0] == self.location[0] - 1 or player.location[0] == self.location[0]:
			if player.location[1] == self.location[1] + 1 or player.location[1] == self.location[1] - 1 or player.location[1] == self.location[1]:
				super().attack(player)
