import curses

from BaseClasses.Character import *
import Quest


class Player(Character):
	def __init__(self, name: str, character: chr, race: Races, spawn_point):
		super().__init__(name, character, race)
		self.spawn_location = spawn_point[:]
		self.quests = []
		self.equipped = {"helmet": None, "chest": None, "gloves": None, "belt": None, "pants": None, "shoes": None, "weapon": Items.IronDagger}
		self.add_inventory_item(Items.IronDagger, 1)
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

	def add_quest(self, quest, log):
		self.quests.append(quest)

	def update_quests(self, enemies, npcs, journal):
		# TODO make function for updating each type of quest
		for quest in self.quests:
			quest.update_quest(self)
			"""requirement = self.quests[quest]["objective"]["requirement"]
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
							self.quests[quest]["quest completed"] = False"""

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
				if isinstance(item, Items.Item):
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
				if isinstance(item, Items.Armour):
					self.equip_armour(item)
				elif isinstance(item, Items.Weapon):
					self.equip_weapon(item)
				self.set_stats_by_level_and_race()
				self.update_player_status()
			elif input_key == ord("2"):
				item = self.inventory[0][option]
				if isinstance(item, Items.Item):
					if isinstance(item, Items.Armour):
						self.unequip_armour(item)
					elif isinstance(item, Items.Weapon):
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
		character["quests"] = []
		for quest in self.quests:
			character["quests"].append(quest.name)
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
		character["exp_for_next_level"] = self.exp_for_next_level
		character["coins"] = self.coins
		character["race"] = self.race.value
		return character


def create_player(name: str, character: chr, race: Races, spawn_point):
	temp_player = Player(name, character, race, spawn_point)
	temp_player.location = temp_player.spawn_location
	return temp_player


def load_player(player, save, log):
	"""loads all player stats from the save file"""
	player.name = save["player"]["name"]
	log.write(player.name + " ")
	player.location = save["player"]["location"]
	player.prevlocation = player.location[:]
	player.health = save["player"]["health"]
	player.character = save["player"]["character"]
	player.max_health = save["player"]["max_health"]
	player.race = Races(save["player"]["race"])
	player.level = save["player"]["level"]
	player.total_exp = save["player"]["total_exp"]
	player.exp_for_next_level = save["player"]["exp_for_next_level"]
	player.exp_to_next_level = save["player"]["exp_to_next_level"]
	player.coins = save["player"]["coins"]
	player.quests = Quest.load_quests(save["player"]["quests"], log)
	log.write("Race: " + str(player.race)[6:] + "\r\n")
	log.write("load player" + "\r\n")


def load_player_equipment(player, save):
	"""loads the player's equipped items from the save file"""
	equipped_item = save["player"]["equipped"]
	for weapon in Items.all_weapons:
		if equipped_item["weapon"] is not None:
			if equipped_item["weapon"] == weapon.name:
				player.equipped["weapon"] = weapon
		else:
			player.equipped["weapon"] = None

	for armour in Items.all_armours:
		if equipped_item["helmet"] is not None:
			if equipped_item["helmet"] == armour.name:
				player.equipped["helmet"] = armour
		if equipped_item["chest"] is not None:
			if equipped_item["chest"] == armour.name:
				player.equipped["chest"] = armour
		if equipped_item["gloves"] is not None:
			if equipped_item["gloves"] == armour.name:
				player.equipped["gloves"] = armour
		if equipped_item["belt"] is not None:
			if equipped_item["belt"] == armour.name:
				player.equipped["belt"] = armour
		if equipped_item["pants"] is not None:
			if equipped_item["pants"] == armour.name:
				player.equipped["pants"] = armour
		if equipped_item["shoes"] is not None:
			if equipped_item["shoes"] == armour.name:
				player.equipped["shoes"] = armour


def save_player(player, save, log):
	"""converts the player object into a dictionary
	and then saves it in the save file
	"""
	save["player"] = player.save_character(log)
	"""del player.inventory_win
	del player.player_status
	del player.quest_log_win
	save["player"] = player.__dict__
	save["player"]["race"] = save["player"]["race"].value
	equipped_item = save["player"]["equipped"]
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
	for item in save["player"]["inventory"][0]:
		index = save["player"]["inventory"][0].index(item)
		if isinstance(save["player"]["inventory"][0][index], Item):
			save["player"]["inventory"][0][index] = save["player"]["inventory"][0][index].name"""
	log.write("player saved" + "\r\n")
