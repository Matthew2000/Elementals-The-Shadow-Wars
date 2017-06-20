from BaseClasses.Character import *


class NPC(Character):
	def __init__(self, name: str, character: chr, race: Races):
		super().__init__(name, character, race)
		self.allow_movement = True
		self.talking = False
		self.dialogue = {"intro": "Hi my name is %s." % self.name, "quest": [{"quest name": "name", "quest type": "unique", "description": "quest description.", "objective": {"amount": 0, "requirement": "quest requirement", "object": "object"}, "reward": {"object": "reward object", "amount": "reward amount", "exp": 0}, "quest completed": False, "quest giver": self.name}], "trade": "I have nothing to trade.", "talk": "I am an NPC."}
		self.has_quest = False
		self.quests = []
		self.spawn_location = []
		self.respawn_counter = 0
		self.respawnable = False
		self.trade_inventory = []

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

	def save_character(self, log):
		character = super().save_character(log)
		character["allow_movement"] = self.allow_movement
		return character
