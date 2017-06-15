import json


class Environment:

	all_maps = []

	def __init__(self, map_directory: str, west_map="", east_map="", north_map="", south_map=""):
		self.directory = map_directory
		temp = open(map_directory, "r")
		MAP = json.load(temp)
		self.environment = MAP["data"]
		self.west_map = west_map
		self.east_map = east_map
		self.north_map = north_map
		self.south_map = south_map
		self.all_maps.append(self)

	def show_map(self, map):
		for y in range(34):
			map.addstr(y, 0, self.environment[y])

	def go_to_map(self, direction, log):
		if direction == "west" and self. west_map != "":
			return Environment(self.west_map, east_map=self.directory)
		elif direction == "east" and self. east_map != "":
			log.write("test")
			return Environment(self.east_map, west_map=self.directory)
		elif direction == "north" and self. north_map != "":
			return Environment(self.north_map, south_map=self.directory)
		elif direction == "south" and self.south_map != "":
			return Environment(self.south_map, north_map=self.directory)
		else:
			return self


map1 = Environment("Maps/map1.json", "Maps/map2.json", "Maps/map3.json", "Maps/map4.json", "Maps/map5.json")
map2 = Environment("Maps/map2.json", east_map="Maps/map1.json")

current_map = map1
