from enum import Enum


class Weapons(Enum):
	Sword = 1
	Dagger = 2
	Club = 3


class Armours(Enum):
	Helmet = "helmet"
	Chest = "chest"
	Gloves = "gloves"
	Belt = "belt"
	Pants = "pants"
	Shoes = "shoes"


all_weapons = []

all_armours = []

all_items = []


class Item:
	def __init__(self, name, value, description, equipable):
		self.name = name
		self.value = value
		self.description = description
		self.equipable = equipable
		all_items.append(self)


class Weapon(Item):
	def __init__(self, name, value, description, damage, weapon_type: Weapons):
		self.damage = damage
		self.weapon_type = weapon_type
		super().__init__(name, value, description, True)
		all_weapons.append(self)


class Armour(Item):
	def __init__(self, name, value, description, protection, armour_type: Armours):
		self.protection = protection
		self.armour_type = armour_type
		super().__init__(name, value, description, True)
		all_armours.append(self)

WolfPelt = Item("Wolf Pelt", 10, "The hide of a wolf", False)

# TODO add more weapons and armours
IronSword = Weapon("Iron Sword", 50, "a sword made out of iron", 20, Weapons.Sword)
IronDagger = Weapon("Iron Dagger", 20, "a dagger made out of iron", 5, Weapons.Dagger)
IronClub = Weapon("Iron Club", 30, "a club made out of iron", 10, Weapons.Club)

LeatherHelmet = Armour("Leather Helmet", 10, "a helmet made out of leather", 10, Armours.Helmet)
LeatherArmour = Armour("Leather Armour", 10, "armour made out of leather", 15, Armours.Chest)
LeatherGloves = Armour("Leather Gloves", 10, "gloves made out of leather", 5, Armours.Gloves)
LeatherBelt = Armour("Leather Belt", 10, "a belt made out of leather", 5, Armours.Belt)
LeatherPants = Armour("Leather Pants", 10, "pants made out of leather", 15, Armours.Pants)
LeatherShoes = Armour("Leather Shoes", 10, "shoes made out of leather", 5, Armours.Shoes)
