from BaseClasses.NPC import *
from Globals import *


class Wolf(NPC):
	def __init__(self, id, spawn_location, location, health, level):
		self.id = id
		super().__init__("Wolf", "W", Race.Wolf, id)
		self.relationship = Relationship.Enemy
		self.spawn_location = spawn_location
		self.location = location
		self.health = health
		self.level = level
		self.allow_movement = True

	def begin_play(self):
		super().begin_play()

	def tick(self, input_key, player):
		super().tick(input_key, player)
