import json

from Globals import *
from BaseClasses.Character import Relationship
from NPCs.Classes.Races.Wolf import Wolf


class Environment:
	def __init__(self, map_directory: str):
		self.directory = map_directory
		temp = open(map_directory, "r")
		self.MAP = json.load(temp)
		self.environment = self.MAP["data"]

	def load_common_npcs(self):
		for npc in self.MAP["common_NPCs"]:
			if npc["id"] not in Wolf.NPC_ids:
				if npc["race"] == "Wolf":
					Wolf(npc["name"], npc["id"], npc["spawn_location"], npc["location"], npc["health"], npc["level"], Relationship(npc["relationship"]))

	def show_map(self):
		for y in range(34):
			MAP.addstr(y, 0, self.environment[y])

	def change_map(self, map_directory):
		for npc_data in self.MAP["common_NPCs"]:
			for npc in Wolf.all_NPCs:
				if npc_data["id"] == npc.id:
					Wolf.NPC_ids.remove(npc_data["id"])
					Wolf.all_NPCs.remove(npc)
		self.directory = map_directory
		temp = open(map_directory, "r")
		self.MAP = json.load(temp)
		self.environment = self.MAP["data"]
		self.load_common_npcs()

	def go_to_map(self, direction):
		if direction == "west" and self.MAP["adjacent_maps"]["west"] is not None:
			self.change_map("Maps/" + self.MAP["adjacent_maps"][direction] + ".json")
		elif direction == "east" and self.MAP["adjacent_maps"]["east"] is not None:
			self.change_map("Maps/" + self.MAP["adjacent_maps"][direction] + ".json")
		elif direction == "north" and self.MAP["adjacent_maps"]["north"] is not None:
			self.change_map("Maps/" + self.MAP["adjacent_maps"][direction] + ".json")
		elif direction == "south" and self.MAP["adjacent_maps"]["south"] is not None:
			self.change_map("Maps/" + self.MAP["adjacent_maps"][direction] + ".json")


map1 = Environment(current_map)
