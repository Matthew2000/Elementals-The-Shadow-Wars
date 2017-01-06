import os.path
from Character import *
import curses
import json


def create_npc(name, character, race: Races, nps, log):  # this function must be assigned to an object
	var = False
	for x in nps:
		if name == x.name:  # name must be the same as the object name
			var = True
			log.write(x.name + " is already there" + "\r\n")
	if not var:
		nps.append(NPC(name, character, race))
	return nps[len(nps) - 1]


def save_npcs(save, npcs, log):
	all_NPCs = npcs[:]
	npcs.clear()
	for npc in all_NPCs:
		temp_npc = npc.__dict__
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
				x += 1
		npcs.append(temp_npc)
	save["all_NPCs"].clear()
	save["all_NPCs"] = npcs[:]
	log.write("save NPCs" + "\r\n")


def load_npcs(save, npcs, log):
	npcs.clear()
	for npc in save["all_NPCs"]:
		log.write(npc["name"] + " ")
		temp_npc = create_npc(npc["name"], npc["character"], Races(npc["race"]), npcs, log)
		temp_npc.location = npc["location"]
		temp_npc.prevlocation = npc["prevlocation"]
		temp_npc.health = npc["health"]
		temp_npc.max_health = npc["max_health"]
		temp_npc.character = npc["character"]
		temp_npc.inventory = npc["inventory"]
		temp_npc.has_quest = npc["has_quest"]
		temp_npc.level = npc["level"]
		temp_npc.total_exp = npc["total_exp"]
		temp_npc.exp_for_next_level = npc["exp_for_next_level"]
		temp_npc.exp_to_next_level = npc["exp_to_next_level"]
		temp_npc.strength = npc["strength"]
		temp_npc.respawnable = npc["respawnable"]
		temp_npc.spawn_location = npc["spawn_location"]
		temp_npc.endurance = npc["endurance"]
		temp_npc.defence = npc["defence"]
		# load equipped npc items
		if temp_npc.race is not Races.Wolf:
			equipped_item = npc["equipped"]
			for weapon in all_weapons:
				if equipped_item["weapon"] is not None:
					if equipped_item["weapon"] == weapon.name:
						temp_npc.equipped["weapon"] = weapon
			for armour in all_armours:
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
		temp_npc.trade_inventory.clear()
		for trade_item in npc["trade_inventory"]:
			for item in all_items:
				if trade_item == item.name:
					temp_npc.trade_inventory.append(item)
		log.write("Race: " + str(temp_npc.race)[6:] + "\r\n")
	log.write("load NPCs" + "\r\n")


def update_npc_locations(npcs, map):
	for npc in npcs:
		if npc.prevlocation.__ne__(npc.location):  # moves the NPC
			if map.inch(npc.location[0], npc.location[1]) == ord(
					" "):  # stops NPC from moving if there's a character there
				map.addch(npc.location[0], npc.location[1], ord(npc.character))
				map.addch(npc.prevlocation[0], npc.prevlocation[1], " ")
			else:
				npc.location = npc.prevlocation[:]  # keeps the NPC at its current location


def spawn_character(map, character, y, x):
	character.location[0] = y
	character.location[1] = x
	character.prevlocation[0] = y
	character.prevlocation[1] = x
	map.addch(y, x, ord(character.character))


def place_npcs(npcs, map):
	for npc in npcs:
		spawn_character(map, npc, npc.location[0], npc.location[1])


def npc_at_location(y, x, npcs):
	for npc in npcs:
		if npc.location[0] is y and npc.location[1] is x:
			return {"result": True, "npc": npc}
	else:
		return {"result": False}


def load_npc_dialogue(npcs, log):
	for npc in npcs:
		if os.path.exists('Dialogue/' + npc.name + '.json'):
			with open('Dialogue/' + npc.name + '.json', 'r') as a:
				npc.dialogue = json.load(a)
				a.close()
	log.write("load npc dialogue" + "\r\n")


def save_npc_dialogue(npcs, log):
	for npc in npcs:
		with open('Dialogue/' + npc.name + '.json', 'w') as a:
			json.dump(npc.dialogue, a, sort_keys=True, indent=4)
			a.close()
	log.write("dialogue save" + "\r\n")