import json
import os
from enum import Enum

import Items
from BaseClasses import NPC
from Globals import *


class QuestType(Enum):
    Collect = 1
    Assassinate = 2
    Kill = 3
    Craft = 4
    Talk = 5


class Quest:
    all = []
    names = []

    def __init__(self, name: str, type: QuestType, giver: str, coin_reward: int, exp_reward: float,
                 object_reward: Items.Item, description: str, repeatable: bool):
        self.name = name
        self.type = type
        self.giver = giver
        self.coin_reward = coin_reward
        self.exp_reward = exp_reward
        self.object_reward = object_reward
        self.description = description
        self.completed = False
        self.repeatable = repeatable

    @classmethod
    def dictionary(cls, quest: dict):
        name = quest["name"]
        type = quest["type"]
        giver = quest["giver"]
        coin_reward = quest["coin_reward"]
        exp_reward = quest["exp_reward"]
        object_reward = quest["object_reward"]
        description = quest["description"]
        repeatable = quest["repeatable"]
        new_quest = Quest(name, type, giver, coin_reward, exp_reward, object_reward, description, repeatable)
        return new_quest

    def update_quest(self, player, npc):
        pass

    def reset(self):
        pass


class CollectQuest(Quest):
    def __init__(self, name: str, giver: str,
                 coin_reward: int, exp_reward: float, object_reward: Items.Item,
                 description: str, item_to_collect: Items.Item, amount: int, repeatable: bool):
        super().__init__(name, QuestType.Collect, giver, coin_reward, exp_reward, object_reward, description,
                         repeatable)
        self.item_to_collect = item_to_collect
        self.amount = amount
        if self.name not in Quest.names:
            Quest.names.append(self.name)
            Quest.all.append(self)

    @classmethod
    def dictionary(cls, quest: dict):
        temp = super().dictionary(quest)
        item_to_collect = quest["item_to_collect"]
        amount = quest["amount"]
        new_quest = CollectQuest(temp.name, temp.giver, temp.coin_reward, temp.exp_reward,
                                 temp.object_reward, temp.description, item_to_collect, amount, temp.repeatable)
        return new_quest

    def update_quest(self, player):
        if self.item_to_collect in player.inventory[0]:
            index = player.inventory[0].index(self.item_to_collect)
            if player.inventory[1][index] == self.amount:
                self.completed = True

    def reset(self):
        self.completed = False


class AssassinateQuest(Quest):
    def __init__(self, name: str, giver: str,
                 coin_reward: int, exp_reward: float, object_reward: Items.Item,
                 description: str, target: NPC, repeatable: bool):
        super().__init__(name, QuestType.Assassinate, giver, coin_reward, exp_reward, object_reward, description,
                         repeatable)
        self.target = target
        if self.name not in Quest.names:
            Quest.names.append(self.name)
            Quest.all.append(self)

    @classmethod
    def dictionary(cls, quest: dict):
        temp = super().dictionary(quest)
        target = quest["target"]
        new_quest = AssassinateQuest(temp.name, temp.giver, temp.coin_reward, temp.exp_reward,
                                     temp.object_reward, temp.description, target, temp.repeatable)
        return new_quest

    def update_quest(self, npc):
        if npc.name == self.target:
            if npc.is_dead():
                self.completed = True

    def reset(self):
        self.completed = False


class KillQuest(Quest):
    def __init__(self, name: str, giver: str,
                 coin_reward: int, exp_reward: float, object_reward: Items.Item,
                 description: str, target: NPC, amount: int, repeatable: bool):
        super().__init__(name, QuestType.Kill, giver, coin_reward, exp_reward, object_reward, description, repeatable)
        self.target = target
        self.amount = amount
        self.amount_killed = 0
        if self.name not in Quest.names:
            Quest.names.append(self.name)
            Quest.all.append(self)

    @classmethod
    def dictionary(cls, quest: dict):
        temp = super().dictionary(quest)
        target = quest["target"]
        amount = quest["amount"]
        new_quest = KillQuest(temp.name, temp.giver, temp.coin_reward, temp.exp_reward,
                              temp.object_reward, temp.description, target, amount, temp.repeatable)
        return new_quest

    def update_quest(self, npc):
        if npc.name == self.target:
            self.amount_killed += 1
        if self.amount_killed >= self.amount:
            if not self.completed:
                DebugLog.write("\n####################\n" + self.name + " completed\n####################\n\n")
            self.completed = True

    def reset(self):
        self.completed = False
        self.amount_killed = 0


class CraftQuest(Quest):
    def __init__(self, name: str, giver: str,
                 coin_reward: int, exp_reward: float, object_reward: Items.Item,
                 description: str, item: Items.Item, amount: int, repeatable: bool):
        super().__init__(name, QuestType.Craft, giver, coin_reward, exp_reward, object_reward, description, repeatable)
        self.item = item
        self.amount = amount
        if self.name not in Quest.names:
            Quest.names.append(self.name)
            Quest.all.append(self)

    @classmethod
    def dictionary(cls, quest: dict):
        temp = super().dictionary(quest)
        item = quest["item"]
        amount = quest["amount"]
        new_quest = CraftQuest(temp.name, temp.giver, temp.coin_reward, temp.exp_reward,
                               temp.object_reward, temp.description, item, amount, temp.repeatable)
        return new_quest

    def update_quest(self, player):
        if self.item in player.inventory[0]:
            index = player.inventory[0].index(self.item)
            if player.inventory[1][index] == self.amount:
                self.completed = True

    def reset(self):
        self.completed = False


class TalkQuest(Quest):
    def __init__(self, name: str, giver: str,
                 coin_reward: int, exp_reward: float, object_reward: Items.Item,
                 description: str, person: NPC, topic: str, repeatable: bool):
        super().__init__(name, QuestType.Talk, giver, coin_reward, exp_reward, object_reward, description, repeatable)
        self.person = person
        self.topic = topic
        if self.name not in Quest.names:
            Quest.names.append(self.name)
            Quest.all.append(self)

    @classmethod
    def dictionary(cls, quest: dict):
        temp = super().dictionary(quest)
        person = quest["person"]
        topic = quest["topic"]
        new_quest = TalkQuest(temp.name, temp.giver, temp.coin_reward, temp.exp_reward,
                              temp.object_reward, temp.description, person, topic, temp.repeatable)
        return new_quest

    def update_quest(self, npc, topic):
        if npc.name == self.person:
            if topic == self.topic:
                self.completed = True

    def reset(self):
        self.completed = False


def load_all_quests():
    DebugLog.write("Quests:\n")
    for file in os.listdir("./Quests"):
        if file.endswith(".json"):
            filename = "Quests/" + file
            DebugLog.write("    " + filename + "\n")
            with open(filename, 'r') as f:
                quest_data = json.load(f)
                f.close()
                if quest_data["type"] == 1:
                    CollectQuest.dictionary(quest_data)
                    continue
                if quest_data["type"] == 2:
                    AssassinateQuest.dictionary(quest_data)
                    continue
                if quest_data["type"] == 3:
                    KillQuest.dictionary(quest_data)
                    continue
                if quest_data["type"] == 4:
                    CraftQuest.dictionary(quest_data)
                    continue
                if quest_data["type"] == 5:
                    TalkQuest.dictionary(quest_data)
                    continue
    DebugLog.write("\n")


def load_quests(npc_quests):
    quests = []
    for quest in Quest.all:
        if quest.name in npc_quests:
            if quest not in quests:
                DebugLog.write("Quest added: " + quest.name + "\n")
                quests.append(quest)
    DebugLog.write("quests loaded\n\n")
    return quests
