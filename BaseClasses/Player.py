import curses

from BaseClasses.Character import *
from Functions import Func
from Globals import *
import Quest


class Player(Character):
	def __init__(self, name: str, character: chr, race: Race, spawn_point):
		super().__init__(name, character, race)
		self.spawn_location = spawn_point[:]
		self.quests = []
		self.equipped = {"helmet": None, "chest": None, "gloves": None, "belt": None, "pants": None, "shoes": None, "weapon": Items.IronDagger}
		self.add_inventory_item(Items.IronDagger, 1)
		self.inventory_win = curses.newwin(50, 65, 2, 110)
		self.quest_log_win = curses.newwin(50, 65, 2, 110)
		self.player_status = curses.newwin(10, 20, 38, 3)

	def begin_play(self):
		pass

	def tick(self, input_key, environment):
		global player_turn

		if self.exp_is_enough():
			self.level_up()

		# opens the player inventory
		if input_key is ord("i"):
			conversation.border()
			conversation.addstr(1, 1, "1 - equip")
			conversation.addstr(2, 1, "2 - unequip")
			conversation.refresh()
			self.open_inventory()
			conversation.clear()
			conversation.refresh()

		if input_key is ord("l"):
			self.open_quest_log()

		if input_key is ord("r"):
			if self.is_dead():
				self.respawn(30, 50)
				spawn_character(MAP, self, self.location[0], self.location[1])

		if not self.is_dead():
			self.move(input_key, dims)

			# checks to see if the player moves unto an enemy
			# if so it starts combat
			# if not the player regenerates health and updates its status
			result = Func.enemy_at_location(Character.all_enemies, self.location, enemy_status)
			if result["result"] is True:
				enemy = result["enemy"]
				Func.start_combat(self, enemy, input_key)
				self.update_quests(enemy)
			else:
				self.regenerate_health()
				self.update_player_status()

			# checks to see if the player moves onto an NPC
			# if so it starts interacting with it
			result = Func.npc_at_location(self.location, Character.all_NPCs)
			if result["result"] is True:
				NPC = result["npc"]
				if NPC.is_enemy():
					NPC.allow_movement = False
					Func.start_combat(self, NPC, input_key)
					self.update_quests(NPC)
				else:
					self.update_quests(NPC)
					self.update_player_status()
					NPC.interact(self, Character.all_enemies, Character.all_NPCs, trade_win)
					Func.update_journal()
					NPC.talking = False
					conversation.clear()
					conversation.refresh()
					self.update_quests(NPC)

			# updates the quests that the player has then ends the player's turn
					Func.update_player_location(self, MAP, environment)

		player_turn = False

		Func.player_dead(self, MAP, journal)

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
		self.quests.append(quest)

	def update_quests(self, npc):
		# TODO make function for updating each type of quest
		for quest in self.quests:
			quest.update_quest(self, npc)

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

	def open_inventory(self):
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

	def save_character(self):
		character = super().save_character()
		character["inventory"] = [[], []]
		items = []
		for item in self.inventory[0]:
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


def create_player(name: str, character: chr, race: Race, spawn_point):
	temp_player = Player(name, character, race, spawn_point)
	temp_player.location = temp_player.spawn_location
	return temp_player


def load_player(player, save):
	"""loads all player stats from the save file"""
	player.name = save["player"]["name"]
	DebugLog.write("player" + " ")
	player.location = save["player"]["location"]
	player.prevlocation = player.location[:]
	player.health = save["player"]["health"]
	player.character = save["player"]["character"]
	player.max_health = save["player"]["max_health"]
	player.race = Race(save["player"]["race"])
	DebugLog.write("Race: " + str(player.race)[5:] + "\r\n")
	player.level = save["player"]["level"]
	player.total_exp = save["player"]["total_exp"]
	player.exp_for_next_level = save["player"]["exp_for_next_level"]
	player.exp_to_next_level = save["player"]["exp_to_next_level"]
	player.coins = save["player"]["coins"]
	player.quests = Quest.load_quests(save["player"]["quests"])
	DebugLog.write("player loaded" + "\n\n")


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


def save_player(player, save):
	"""converts the player object into a dictionary
	and then saves it in the save file
	"""
	save["player"] = player.save_character()
	DebugLog.write("player saved" + "\n")
