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
					[WolfPelt],
					[1]
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

	def death(self):  # kills the Character
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


class Player(Character):
	def __init__(self, name: str, character: chr, race: Races, spawn_point):
		super().__init__(name, character, race)
		self.spawn_location = spawn_point[:]
		self.quests = {}
		self.equipped = {"helmet": None, "chest": None, "gloves": None, "belt": None, "pants": None, "shoes": None, "weapon": IronDagger}
		self.add_inventory_item(IronDagger, 1)
		self.inventory_win = curses.newwin(50, 65, 2, 110)
		self.player_status = curses.newwin(10, 20, 38, 3)

	def make_player_stat_win(self):
		self.player_status = curses.newwin(10, 20, 38, 3)

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
				item_name = self.quests[quest]["objective"]["object"]
				amount = self.quests[quest]["objective"]["amount"]
				for inv_item in self.inventory[0]:
					if item_name == inv_item.name:
						if self.inventory[1][self.inventory[0].index(inv_item)] >= amount:
							self.quests[quest]["quest completed"] = True
						else:
							self.quests[quest]["quest completed"] = False

	def level_up(self):
		self.exp_for_next_level -= self.exp_to_next_level
		self.level += 1
		self.exp_to_next_level = float(int((self.level ** 2) / .04))
		self.set_stats_by_level_and_race()

	def update_inventory(self):
		self.inventory_win.clear()
		self.inventory_win.border()
		self.inventory_win.addstr(0, 1, "Inventory")

	def update_player_status(self):
		self.player_status.clear()
		self.player_status.border()
		self.player_status.addstr(0, 1, "Player Info")
		self.player_status.addstr(1, 1, "Health: " + str(self.health))
		self.player_status.addstr(2, 1, "Strength: " + str(self.strength))
		self.player_status.addstr(3, 1, "Coins: " + str(self.coins))
		self.player_status.addstr(4, 1, "Defense: " + str(self.defense))
		self.player_status.addstr(5, 1, "Race: " + str(self.race)[6:])
		self.player_status.addstr(6, 1, "Level: " + str(self.level))
		self.player_status.addstr(7, 1, "exp needed: " + str(self.exp_to_next_level - self.exp_for_next_level)[:len(
			str(self.exp_to_next_level - self.exp_for_next_level)) - 2])
		self.player_status.refresh()

	def refresh_inventory_menu(self):
		for item in self.inventory[0]:
			self.inventory_win.deleteln()
		self.inventory_win.refresh()

	def open_inventory(self, log):
		if not self.inventory[0]:
			return
		self.update_inventory()
		self.inventory_win.keypad(True)
		option = len(self.inventory[0]) - 1
		input_key = -1
		while input_key is not ord("i"):
			self.refresh_inventory_menu()
			self.inventory_win.clear()
			selection = [0] * len(self.inventory[0])
			selection[option] = curses.A_REVERSE
			equipped_items = list(self.equipped.values())
			for item in self.inventory[0]:
				self.inventory_win.insertln()
				index = self.inventory[0].index(item)
				if isinstance(item, Item):
					self.inventory_win.addstr(1, 1, item.name, selection[index])
					self.inventory_win.addstr(1, 20, "amount: " + str(self.inventory[1][index]))
				if self.inventory[0][index] in equipped_items:
					self.inventory_win.addstr(1, 35, "equipped")
			self.inventory_win.border()
			self.inventory_win.addstr(0, 1, "Inventory")
			self.inventory_win.refresh()
			input_key = self.inventory_win.getch()
			if input_key == curses.KEY_UP:
				option += 1
			elif input_key == curses.KEY_DOWN:
				option -= 1
			if option < 0:
				option = len(self.inventory[0]) - 1
			elif option >= len(self.inventory[0]):
				option = 0
			if input_key == ord("1"):
				item = self.inventory[0][option]
				if isinstance(item, Armour):
					self.equip_armour(item)
				elif isinstance(item, Weapon):
					self.equip_weapon(item)
				self.set_stats_by_level_and_race()
				self.update_player_status()
			elif input_key == ord("2"):
				item = self.inventory[0][option]
				if isinstance(item, Item):
					if isinstance(item, Armour):
						self.unequip_armour(item)
					elif isinstance(item, Weapon):
						self.unequip_weapon()
					self.set_stats_by_level_and_race()
					self.update_player_status()



class NPC(Character):
	def __init__(self, name: str, character: chr, race: Races):
		super().__init__(name, character, race)
		self.allow_movement = True
		self.talking = False
		self.dialogue = {"intro": "Hi my name is %s." % self.name, "quest": [{"quest name": "name", "quest type": "unique", "description": "quest description.", "objective": {"amount": 0, "requirement": "quest requirement", "object": "object"}, "reward": {"object": "reward object", "amount": "reward amount", "exp": 0}, "quest completed": False, "quest giver": self.name}], "trade": "I have nothing to trade.", "talk": "I am an NPC."}
		self.has_quest = False
		self.respawn_counter = 0
		self.respawnable = False
		self.trade_inventory = [LeatherArmour, LeatherHelmet, LeatherShoes, LeatherPants, LeatherBelt, LeatherGloves]

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

	def talk(self, journal, conversation):
		# TODO make more complex conversations
		journal.insertln()
		journal.addstr(1, 1, self.dialogue["talk"])
		self.conversation_start(conversation)

	def choose_quest(self, key, quests, enemies, npcs, player, journal, conversation, log):
		# TODO check to see if the quest is already completed when choosing quests
		# TODO make a new type of quest to talk to another npc
		player.update_quests(enemies, npcs, journal)
		log.write(str(int(chr(int(key) - 1))) + "\r\n")
		quest_list = quests
		if int(chr(key)) - 1 >= len(quest_list):
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
					if quest["reward"]["object"] == "Coins":
						player.coins += quest["reward"]["amount"]
					else:
						player.add_inventory_item(quest["reward"]["object"], quest["reward"]["amount"])
					player.increase_exp(quest["reward"]["exp"])
					if quest["objective"]["requirement"] == "collect":
						item = quest["objective"]["object"]
						amount = quest["objective"]["amount"]
						for inv_item in player.inventory[0]:
							if inv_item.name == item:
								index = player.inventory[0].index(inv_item)
						player.inventory[1][index] -= amount
						log.write("working\n")
					del player.quests[quest["quest name"]]
					if quest["quest type"] == "unique":
						del self.dialogue["quest"][index]
					self.conversation_start(conversation)
					player.update_inventory()
			else:
				journal.insertln()
				journal.addstr(1, 1, "You have already accepted that quest.")
				journal.border()
				journal.refresh()

	def interact(self, journal, conversation, input_key, player, log, enemies, npcs, trade_window):
		if not self.dialogue["quest"]:
			self.has_quest = False
		if self.talking is False:
			journal.insertln()
			journal.addstr(1, 1, self.dialogue["intro"])
			self.conversation_start(conversation)
		self.talking = True
		if input_key is ord("1"):
			self.talk(journal, conversation)
		elif input_key is ord("2"):

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
					self.choose_quest(input_key, quest_number, enemies, npcs, player, journal, conversation, log)
					self.conversation_start(conversation)
					break
			else:
				journal.insertln()
				journal.addstr(1, 1, "I have no quest for you at the moment")
				journal.refresh()
		elif input_key is ord("3"):
			journal.insertln()
			journal.addstr(1, 1, self.dialogue["trade"])
			if self.trade_inventory is not []:
				self.trade(player, trade_window, conversation, log)
			self.conversation_start(conversation)

	def refresh_trade_menu(self, journal, inv):
		for item in inv:
			journal.deleteln()
			journal.refresh()

	# TODO improve the trade system
	def trade(self, player, journal, conversation, log):
		input_key = -1
		conversation.keypad(True)
		conversation.clear()
		conversation.border()
		conversation.addstr(1, 1, "1 - buy")
		conversation.addstr(2, 1, "2 - sell")
		conversation.addstr(3, 1, "3 - leave")
		buy = True
		while input_key != ord("3"):
			input_key = conversation.getch()
			if input_key == ord("1"):
				break
			elif input_key == ord("2"):
				buy = False
				if not player.inventory[0]:
					return
				else:
					break
		else:
			return
		input_key = -1
		conversation.clear()
		conversation.border()
		if buy:
			conversation.addstr(1, 1, "1 - buy item")
			conversation.addstr(2, 1, "2 - leave trade")
			inv = self.trade_inventory
		else:
			conversation.addstr(1, 1, "1 - sell item")
			conversation.addstr(2, 1, "2 - leave trade")
			inv = player.inventory[0]
		for item in inv:
			journal.insertln()
		option = 0
		while input_key is not ord("2"):
			self.refresh_trade_menu(journal, inv)
			journal.clear()
			selection = [0] * len(inv)
			selection[option] = curses.A_REVERSE
			for item in inv:
				journal.insertln()
				journal.addstr(1, 1, item.name, selection[inv.index(item)])
				journal.addstr(1, 20, "value: " + str(item.value))
			journal.border()
			journal.refresh()
			input_key = conversation.getch()
			if input_key == curses.KEY_UP:
				option += 1
			elif input_key == curses.KEY_DOWN:
				option -= 1
			if option < 0:
				option = len(inv) - 1
			elif option >= len(inv):
				option = 0
			if input_key == ord("1"):
				if buy:
					if player.coins >= inv[option].value:
						player.coins -= inv[option].value
						player.add_inventory_item(inv[option])
				else:
					player.coins += inv[option].value
					player.remove_inventory_item(inv[option])
					option -= 1
					if option <= 0:
						option = 0
					if len(inv) == 0:
						break
				player.update_player_status()
		else:
			for item in inv:
				journal.deleteln()
				journal.border()
				journal.refresh()

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
			player.add_inventory_item(WolfPelt, 1)