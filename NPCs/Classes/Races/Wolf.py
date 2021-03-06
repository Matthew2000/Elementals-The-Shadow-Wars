from BaseClasses.NpcClass import *


class Wolf(NPC):
    def __init__(self, name, npc_id, spawn_location, location, health, level, relationship):
        super().__init__(name, "W", Race.Wolf, npc_id)
        self.relationship = relationship
        self.spawn_location = spawn_location
        self.prevlocation = spawn_location
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
        player.add_inventory_item(Items.WolfPelt)
