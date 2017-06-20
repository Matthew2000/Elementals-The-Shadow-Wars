from BaseClasses.Character import *


class Player(Character):
	def __init__(self, name: str, character: chr, race: Races, spawn_point):
		super().__init__(name, character, race)
		self.spawn_location = spawn_point[:]
		self.quests = []
		self.equipped = {"helmet": None, "chest": None, "gloves": None, "belt": None, "pants": None, "shoes": None, "weapon": IronDagger}
		self.add_inventory_item(IronDagger, 1)
		self.inventory_win = curses.newwin(50, 65, 2, 110)
		self.quest_log_win = curses.newwin(50, 65, 2, 110)
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

	def update_quest_log(self):
		self.quest_log_win.clear()
		self.quest_log_win.border()
		self.quest_log_win.addstr(0, 1, "Quest Log")

	def refresh_quest_log(self):
		for item in self.quests:
			self.quest_log_win.deleteln()
		self.quest_log_win.refresh()

	def open_quest_log(self):
		self.update_quest_log()
		self.quest_log_win.keypad(True)
		option = len(self.inventory[0]) - 1
		input_key = -1
		if len(self.quests) == 0:
			self.quest_log_win.addstr(1, 1, "You have no quests right now.")
			self.quest_log_win.refresh()
		while input_key is not ord("l"):
			input_key = self.quest_log_win.getch()
			if len(self.quests) == 0:
				self.quest_log_win.addstr(1, 1, "You have no quests right now.")
				self.quest_log_win.refresh()
				continue
			self.refresh_quest_log()
			self.quest_log_win.clear()
			selection = [0] * len(self.quests)
			selection[option] = curses.A_REVERSE
			for quest in self.quests:
				self.quest_log_win.insertln()
				index = self.quests.index(quest)
				self.inventory_win.addstr(1, 1, quest.name, selection[index])
				#self.inventory_win.addstr(1, 20, "amount: " + str(self.inventory[1][index]))

	def on_death(self):
		self.respawn(self.location[0], self.location[1])

	def save_character(self, log):
		character = super().save_character(log)
		character["inventory"] = [[], []]
		items = []
		for item in self.inventory[0]:
			log.write("working\n")
			items.append(item.name)
			character["inventory"][0] = items
		for amount in self.inventory[1]:
			character["inventory"][1].append(amount)
		x = 0
		for quest in self.quests:
			character["quests"][x] = quest.name
			x += 1
		character["equipped"] = {}
		if self.equipped["helmet"] is not None:
			character["equipped"]["helmet"] = self.equipped["helmet"].name
		else:
			character["equipped"]["helmet"] = None
		if self.equipped["chest"] is not None:
			character["equipped"]["chest"] = self.equipped["chest"].name
		else:
			character["equipped"]["chest"] = None
		if self.equipped["gloves"] is not None:
			character["equipped"]["gloves"] = self.equipped["gloves"].name
		else:
			character["equipped"]["gloves"] = None
		if self.equipped["belt"] is not None:
			character["equipped"]["belt"] = self.equipped["belt"].name
		else:
			character["equipped"]["belt"] = None
		if self.equipped["pants"] is not None:
			character["equipped"]["pants"] = self.equipped["pants"].name
		else:
			character["equipped"]["pants"] = None
		if self.equipped["shoes"] is not None:
			character["equipped"]["shoes"] = self.equipped["shoes"].name
		else:
			character["equipped"]["shoes"] = None
		if self.equipped["weapon"] is not None:
			character["equipped"]["weapon"] = self.equipped["weapon"].name
		else:
			character["equipped"]["weapon"] = None
		character["character"] = self.character
		character["max_health"] = self.max_health
		character["level"] = self.level
		character["total_exp"] = self.total_exp
		character["exp_to_next_level"] = self.exp_to_next_level
		character["coins"] = self.coins
		return character
