from enum import Enum
import json
import os

import Functions.Func as Func
from BaseClasses import NPC
import Items


class QuestType(Enum):
	Collect = 1
	Assassinate = 2
	Kill = 3
	Craft = 4
	Talk = 5


class Quest:
	def __init__(self, name: str, type: QuestType, giver: str, coin_reward: int, exp_reward: float,
														object_reward: Items.Item, description: str):
		self.name = name
		self.type = type
		self.giver = giver
		self.coin_reward = coin_reward
		self.exp_reward = exp_reward
		self.object_reward = object_reward
		self.description = description
		self.completed = False

	@classmethod
	def dictionary(cls, quest: dict):
		name = quest["name"]
		type = quest["type"]
		giver = quest["giver"]
		coin_reward = quest["coin_reward"]
		exp_reward = quest["exp_reward"]
		object_reward = quest["object_reward"]
		description = quest["description"]
		new_quest = Quest(name, type, giver, coin_reward, exp_reward, object_reward, description)
		return new_quest

	def update_quest(self, player):
		pass


class CollectQuest(Quest):
	def __init__(self, name: str, giver: str,
											coin_reward: int, exp_reward: float, object_reward: Items.Item,
											description: str, item_to_collect: Items.Item, amount: int):
		super().__init__(name, QuestType.Collect, giver, coin_reward, exp_reward, object_reward, description)
		self.item_to_collect = item_to_collect
		self.amount = amount

	@classmethod
	def dictionary(cls, quest: dict):
		temp = super().dictionary(quest)
		item_to_collect = quest["item_to_collect"]
		amount = quest["amount"]
		new_quest = CollectQuest(temp.name, temp.giver, temp.coin_reward, temp.exp_reward,
													temp.object_reward, temp.description, item_to_collect, amount)
		return new_quest

	def update_quest(self, player):
		if self.item_to_collect in player.inventory[0]:
			index = player.inventory[0].index(self.item_to_collect)
			if player.inventory[1][index] == self.amount:
				self.completed = True


class AssassinateQuest(Quest):
	def __init__(self, name: str, giver: str,
	             coin_reward: int, exp_reward: float, object_reward: Items.Item,
	             description: str, target: NPC):
		super().__init__(name, QuestType.Assassinate, giver, coin_reward, exp_reward, object_reward, description)
		self.target = target

	@classmethod
	def dictionary(cls, quest: dict):
		temp = super().dictionary(quest)
		target = quest["target"]
		new_quest = AssassinateQuest(temp.name, temp.giver, temp.coin_reward, temp.exp_reward,
													temp.object_reward, temp.description, target)
		return new_quest

	def update_quest(self, player):
		if self.target.is_dead():
			self.completed = True


class KillQuest(Quest):
	def __init__(self, name: str, giver: str,
	             coin_reward: int, exp_reward: float, object_reward: Items.Item,
	             description: str, target: NPC, amount: int):
		super().__init__(name, QuestType.Kill, giver, coin_reward, exp_reward, object_reward, description)
		self.target = target
		self.amount = amount

	@classmethod
	def dictionary(cls, quest: dict):
		temp = super().dictionary(quest)
		target = quest["target"]
		amount = quest["amount"]
		new_quest = KillQuest(temp.name, temp.giver, temp.coin_reward, temp.exp_reward,
													temp.object_reward, temp.description, target, amount)
		return new_quest


class CraftQuest(Quest):
	def __init__(self, name: str, giver: str,
											coin_reward: int, exp_reward: float, object_reward: Items.Item,
											description: str, item: Items.Item, amount: int):
		super().__init__(name, QuestType.Craft, giver, coin_reward, exp_reward, object_reward, description)
		self.item = item
		self.amount = amount

	@classmethod
	def dictionary(cls, quest: dict):
		temp = super().dictionary(quest)
		item = quest["item"]
		amount = quest["amount"]
		new_quest = CraftQuest(temp.name, temp.giver, temp.coin_reward, temp.exp_reward,
													temp.object_reward, temp.description, item, amount)
		return new_quest

	def update_quest(self, player):
		if self.item in player.inventory[0]:
			index = player.inventory[0].index(self.item)
			if player.inventory[1][index] == self.amount:
				self.completed = True


class TalkQuest(Quest):
	def __init__(self, name: str, giver: str,
	             coin_reward: int, exp_reward: float, object_reward: Items.Item,
	             description: str, person: NPC):
		super().__init__(name, QuestType.Talk, giver, coin_reward, exp_reward, object_reward, description)
		self.person = person

	@classmethod
	def dictionary(cls, quest: dict):
		temp = super().dictionary(quest)
		person = quest["person"]
		new_quest = TalkQuest(temp.name, temp.giver, temp.coin_reward, temp.exp_reward,
													temp.object_reward, temp.description, person)
		return new_quest


def load_quests(npc_quests, log):
	quests = []
	for quest in npc_quests:
			filename = 'Quests/' + Func.sanitize_filename(quest) + '.json'
			if os.path.exists(filename):
				with open(filename, 'r') as a:
					quest_dictionary = json.load(a)
					a.close()
				if quest_dictionary["type"] == 1:
					quests.append(CollectQuest.dictionary(quest_dictionary))
				if quest_dictionary["type"] == 2:
					quests.append(AssassinateQuest.dictionary(quest_dictionary))
				if quest_dictionary["type"] == 3:
					quests.append(KillQuest.dictionary(quest_dictionary))
				if quest_dictionary["type"] == 4:
					quests.append(CraftQuest.dictionary(quest_dictionary))
				if quest_dictionary["type"] == 5:
					quests.append(TalkQuest.dictionary(quest_dictionary))
	return quests
