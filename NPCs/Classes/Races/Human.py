from BaseClasses.NPC import *
from Globals import *


class Human(NPC):
	def __init__(self, name, character, id, spawn_location, location, health, level, relationship):
		super().__init__(name, character, Race.Human, id)
		self.relationship = relationship
		self.spawn_location = spawn_location
		self.location = location
		self.health = health
		self.level = level
		self.allow_movement = True

	def begin_play(self):
		super().begin_play()

	def tick(self, input_key, player):
		super().tick(input_key, player)

	def on_death(self, player):
		super().on_death(player)
