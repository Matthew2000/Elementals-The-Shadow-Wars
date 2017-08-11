import json
import os

from NPCs.Classes.Races import Wolf, Dragon, Human, Avaker, Unkown
from BaseClasses import NPC
from Globals import *
from Functions import Func
import Quest
import Items


def load_npcs(save, npcs):
	npcs.clear()
	for npc in save["all_NPCs"]:
		filename = 'NPCs/' + Func.sanitize_filename(npc["name"]) + '.json'
		file = open(filename, "r")
		npc_data = json.load(file)

		name = npc_data["name"]
		character = npc_data["character"]
		race = npc_data["race"]
		if race == "Human":
			temp_npc = Human.Human(name, character, npc_data["id"], npc_data["spawn_location"],
									npc_data["location"], npc_data["health"], npc_data["level"],
									NPC.Relationship(npc_data["relationship"]))
		elif race == "Avaker":
			temp_npc = Avaker.Avaker(name, character, npc_data["id"], npc_data["spawn_location"],
									npc_data["location"], npc_data["health"], npc_data["level"],
									NPC.Relationship(npc_data["relationship"]))
		elif race == "Dragon":
			temp_npc = Dragon.Dragon(name, character, npc_data["id"], npc_data["spawn_location"],
									npc_data["location"], npc_data["health"], npc_data["level"],
									NPC.Relationship(npc_data["relationship"]))
		elif race == "Wolf":
			temp_npc = Wolf.Wolf(name, npc_data["id"], npc_data["spawn_location"],
									npc_data["location"], npc_data["health"], npc_data["level"],
									NPC.Relationship(npc_data["relationship"]))
		else:
			temp_npc = Unkown.Unknown(name, character, npc_data["id"], npc_data["spawn_location"],
									npc_data["location"], npc_data["health"], npc_data["level"],
									NPC.Relationship(npc_data["relationship"]))

		DebugLog.write(temp_npc.name + " Race: " + str(temp_npc.race)[5:] + "\r\n")
		temp_npc.prevlocation = temp_npc.location[:]
		temp_npc.health = npc["health"]
		temp_npc.max_health = npc_data["max_health"]
		temp_npc.inventory = Func.load_inventory(npc_data["inventory"])
		temp_npc.has_quest = npc_data["has_quest"]
		temp_npc.level = npc_data["level"]
		temp_npc.total_exp = npc_data["total_exp"]
		temp_npc.exp_for_next_level = npc_data["exp_for_next_level"]
		temp_npc.exp_to_next_level = npc_data["exp_to_next_level"]
		temp_npc.strength = npc_data["strength"]
		temp_npc.respawnable = npc_data["respawnable"]
		temp_npc.endurance = npc_data["endurance"]
		temp_npc.defense = npc_data["defense"]
		temp_npc.dialogue = NPC.load_npc_dialogue(npc["name"])
		temp_npc.quests = Quest.load_quests(npc_data["quests"])
		temp_npc.allow_movement = npc["allow_movement"]
		# load equipped npc items
		if temp_npc.race is not NPC.Race.Wolf:
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
	DebugLog.write("NPCs loaded: " + str(len(npcs)) + "\n\n")


def load_npcs_for_new_game(npcs):
	for file in os.listdir("./NPCs"):
		if file.endswith(".json"):
			filename = "NPCs/" + file
			DebugLog.write(filename + "\n")
			with open(filename, 'r') as f:
				npc_data = json.load(f)
				f.close()

				name = npc_data["name"]
				character = npc_data["character"]
				race = npc_data["race"]
				if race == "Human":
					temp_npc = Human.Human(name, character, npc_data["id"], npc_data["spawn_location"],
											npc_data["location"], npc_data["health"], npc_data["level"],
											NPC.Relationship(npc_data["relationship"]))
				elif race == "Avaker":
					temp_npc = Avaker.Avaker(name, character, npc_data["id"], npc_data["spawn_location"],
											npc_data["location"], npc_data["health"], npc_data["level"],
											NPC.Relationship(npc_data["relationship"]))
				elif race == "Dragon":
					temp_npc = Dragon.Dragon(name, character, npc_data["id"], npc_data["spawn_location"],
											npc_data["location"], npc_data["health"], npc_data["level"],
											NPC.Relationship(npc_data["relationship"]))
				elif race == "Wolf":
					temp_npc = Wolf.Wolf(name, npc_data["id"], npc_data["spawn_location"],
											npc_data["location"], npc_data["health"], npc_data["level"],
											NPC.Relationship(npc_data["relationship"]))
				else:
					temp_npc = Unkown.Unknown(name, character, npc_data["id"], npc_data["spawn_location"],
											npc_data["location"], npc_data["health"], npc_data["level"],
											NPC.Relationship(npc_data["relationship"]))

				temp_npc.location = npc_data["location"]
				temp_npc.prevlocation = temp_npc.location[:]
				temp_npc.health = npc_data["health"]
				temp_npc.max_health = npc_data["max_health"]
				temp_npc.character = npc_data["character"]
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
				temp_npc.dialogue = NPC.load_npc_dialogue(name)
				temp_npc.quests = Quest.load_quests(npc_data["quests"])
				temp_npc.allow_movement = npc_data["allow_movement"]
				# load equipped npc items
				if temp_npc.race is not NPC.Race.Wolf:
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
