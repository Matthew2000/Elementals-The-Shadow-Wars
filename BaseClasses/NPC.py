import curses
import json
import os

from BaseClasses.Character import *
from Functions import Func
import Quest


class Relationship(Enum):
	Friend = 0
	Neutral = 1
	Enemy = 2


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
		self.relationship = Relationship.Neutral

	@classmethod
	def dictionary(cls, npc_data: dict, log):
		name = npc_data["name"]
		character = npc_data["character"]
		race = npc_data["race"]
		temp_npc = NPC(name, character, Races(race))

		filename = 'NPCs/' + Func.sanitize_filename(name) + '.json'
		file = open(filename, "r")
		npc_data = json.load(file)
		temp_npc.location = npc_data["location"]
		temp_npc.prevlocation = temp_npc.location[:]
		temp_npc.health = npc_data["health"]
		temp_npc.max_health = npc_data["max_health"]
		temp_npc.character = npc_data["character"]
		log.write("working\n")
		temp_npc.inventory = Func.load_inventory(npc_data["inventory"])
		temp_npc.has_quest = npc_data["has_quest"]
		temp_npc.level = npc_data["level"]
		temp_npc.total_exp = npc_data["total_exp"]
		temp_npc.exp_for_next_level = npc_data["exp_for_next_level"]
		temp_npc.exp_to_next_level = npc_data["exp_to_next_level"]
		temp_npc.strength = npc_data["strength"]
		temp_npc.respawnable = npc_data["respawnable"]
		temp_npc.spawn_location = npc_data["spawn_location"]
		temp_npc.endurance = npc_data["endurance"]
		temp_npc.defense = npc_data["defense"]
		temp_npc.dialogue = npc_data["dialogue"]
		temp_npc.quests = Quest.load_quests(npc_data["quests"], log)
		temp_npc.relationship = Relationship(npc_data["relationship"])
		# load equipped npc items
		if temp_npc.race is not Races.Wolf:
			equipped_item = npc_data["equipped"]
			for weapon in Items.all_weapons:
				if equipped_item["weapon"] is not None:
					if equipped_item["weapon"] == weapon.name:
						temp_npc.equipped["weapon"] = weapon
			for armour in Items.all_armours:
				if equipped_item["helmet"] is not None:
					if equipped_item["helmet"] == armour.name:
						temp_npc.equipped["helmet"] = armour
				if equipped_item["chest"] is not None:
					if equipped_item["chest"] == armour.name:
						temp_npc.equipped["chest"] = armour
				if equipped_item["gloves"] is not None:
					if equipped_item["gloves"] == armour.name:
						temp_npc.equipped["gloves"] = armour
				if equipped_item["belt"] is not None:
					if equipped_item["belt"] == armour.name:
						temp_npc.equipped["belt"] = armour
				if equipped_item["pants"] is not None:
					if equipped_item["pants"] == armour.name:
						temp_npc.equipped["pants"] = armour
				if equipped_item["shoes"] is not None:
					if equipped_item["shoes"] == armour.name:
						temp_npc.equipped["shoes"] = armour
		# load items to trade
		for trade_item in npc_data["trade_inventory"]:
			for item in Items.all_items:
				if trade_item == item.name:
					temp_npc.trade_inventory.append(item)
		return temp_npc

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
		character["relationship"] = self.relationship.value
		return character


def create_npc(name, character, race: Races, npcs, log):  # this function must be assigned to an object
	var = False
	for x in npcs:
		if name == x.name:  # name must be the same as the object name
			var = True
			log.write(x.name + " is already there" + "\r\n")
	if not var:
		npcs.append(NPC(name, character, race))
	return npcs[len(npcs) - 1]


def save_npcs(save, npcs, log):
	all_NPCs = npcs[:]
	npcs.clear()
	for npc in all_NPCs:
		temp_npc = npc.save_character(log)
		"""temp_npc = npc.__dict__
		temp_npc["race"] = temp_npc["race"].value
		equipped_item = temp_npc["equipped"]
		if equipped_item["helmet"] is not None:
			equipped_item["helmet"] = equipped_item["helmet"].__dict__
			equipped_item["helmet"] = equipped_item["helmet"]["name"]
			log.write(str(equipped_item["helmet"]) + "\r\n")
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
		if temp_npc["trade_inventory"] is not []:
			x = 0
			for item in temp_npc["trade_inventory"]:
				item = item.__dict__
				temp_npc["trade_inventory"][x] = item["name"]
				x += 1"""
		npcs.append(temp_npc)
	save["all_NPCs"].clear()
	save["all_NPCs"] = npcs[:]
	log.write("save NPCs" + "\r\n")


def npc_at_location(location, npcs):
	for npc in npcs:
		if npc.location[0] is location[0] and npc.location[1] is location[1]:
			return {"result": True, "npc": npc}
	else:
		return {"result": False}


def load_npc_dialogue(npcs, log):  # for NEW game only
	for npc in npcs:
		filename = 'Dialogue/' + Func.sanitize_filename(npc.name) + '.json'
		if os.path.exists(filename):
			with open(filename, 'r') as a:
				npc.dialogue = json.load(a)
				a.close()
	log.write("load npc dialogue" + "\r\n")


def update_npc_locations(npcs, map):
	for npc in npcs:
		if npc.prevlocation.__ne__(npc.location):  # moves the NPC
			if map.inch(npc.location[0], npc.location[1]) == ord(
					" "):  # stops NPC from moving if there's a character there
				map.addch(npc.location[0], npc.location[1], ord(npc.character))
				map.addch(npc.prevlocation[0], npc.prevlocation[1], " ")
				npc.prevlocation = npc.location[:]
			else:
				npc.location = npc.prevlocation[:]  # keeps the NPC at its current location
		if map.inch(npc.location[0], npc.location[1]) == ord(" "):
			map.addch(npc.location[0], npc.location[1], ord(npc.character))


def place_npcs(npcs, map):
	for npc in npcs:
		spawn_character(map, npc, npc.location[0], npc.location[1])
