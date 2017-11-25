import json

from BaseClasses.CharacterClass import Relationship
from Globals import *
from NPCs.Classes.Races.Wolf import Wolf


class Environment:
    def __init__(self, map_directory: str):
        self.directory = map_directory
        temp = open(map_directory, "r")
        self.map = json.load(temp)
        self.environment = self.map["data"]

    def load_common_npcs(self):
        for npc in self.map["common_NPCs"]:
            if npc["id"] not in Wolf.NPC_ids:
                if npc["race"] == "Wolf":
                    Wolf(npc["name"], npc["id"], npc["spawn_location"], npc["location"], npc["health"], npc["level"],
                         Relationship(npc["relationship"]))

    def show_map(self):
        for y in range(34):
            map_window.addstr(y, 0, self.environment[y])

    def change_map(self, map_directory):
        for npc_data in self.map["common_NPCs"]:
            for npc in Wolf.all_NPCs:
                if npc_data["id"] == npc.id:
                    Wolf.NPC_ids.remove(npc_data["id"])
                    Wolf.all_NPCs.remove(npc)
        self.directory = map_directory
        temp = open(map_directory, "r")
        self.map = json.load(temp)
        self.environment = self.map["data"]
        self.load_common_npcs()

    def go_to_map(self, direction):
        if direction == "west" and self.map["adjacent_maps"]["west"] is not None:
            self.change_map("Maps/" + self.map["adjacent_maps"][direction] + ".json")
        elif direction == "east" and self.map["adjacent_maps"]["east"] is not None:
            self.change_map("Maps/" + self.map["adjacent_maps"][direction] + ".json")
        elif direction == "north" and self.map["adjacent_maps"]["north"] is not None:
            self.change_map("Maps/" + self.map["adjacent_maps"][direction] + ".json")
        elif direction == "south" and self.map["adjacent_maps"]["south"] is not None:
            self.change_map("Maps/" + self.map["adjacent_maps"][direction] + ".json")


map1 = Environment(current_map_path)
