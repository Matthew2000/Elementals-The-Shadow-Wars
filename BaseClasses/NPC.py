import json
import os

from BaseClasses.Character import *
from Functions import Func
from Globals import *
from Maps import *


class NPC(Character):
    all = []

    def __init__(self, name: str, character: chr, race: Race, npc_id):
        super().__init__(name, character, race)
        self.allow_movement = False
        self.talking = False
        self.dialogue = {"intro": "Hi my name is %s." % self.name, "quest": [
            {"quest name": "name", "quest type": "unique", "description": "quest description.",
             "objective": {"amount": 0, "requirement": "quest requirement", "object": "object"},
             "reward": {"object": "reward object", "amount": "reward amount", "exp": 0}, "quest completed": False,
             "quest giver": self.name}], "trade": "I have nothing to trade.", "talk": "I am an NPC."}
        self.has_quest = False
        self.quests = []
        self.spawn_location = []
        self.respawn_counter = 0
        self.respawnable = True
        self.trade_inventory = []
        self.relationship = Relationship.Neutral
        self.increase_exp_by = int((self.level ** 2) / .4) + 5
        self.id = npc_id
        Character.all_NPCs.append(self)
        Character.NPC_ids.append(self.id)

    def begin_play(self):
        if not self.quests:
            self.has_quest = False
        else:
            self.has_quest = True

    def tick(self, input_key, player):

        if not self.is_dead():
            self.move(dims, player)
            self.regenerate_health()
            if Func.player_at_location(player, self.location):
                if self.is_enemy():
                    self.location = self.prevlocation[:]
                    self.allow_movement = False
                    Func.start_combat(player, self, input_key)

    def conversation_start(self):
        conversation.clear()
        conversation.border()
        conversation.addstr(0, 1, "Conversation")
        conversation.addstr(2, 1, "1 - Talk")
        conversation.addstr(3, 1, "2 - Quest")
        conversation.addstr(4, 1, "3 - Trade")
        conversation.addstr(5, 1, "4 - Leave")
        conversation.refresh()

    def show_options(self, *options):
        x = 2
        y = 1
        conversation.clear()
        conversation.border()
        conversation.addstr(0, 1, "Conversation")
        for option in options:
            if option == str(option):
                conversation.addstr(x, 1, str(y) + " - " + str(option))
                x += 1
                y += 1
            else:
                for option1 in option:
                    conversation.addstr(x, 1, str(y) + " - " + str(option1))
                    x += 1
                    y += 1
        conversation.refresh()

    def talk(self, player):
        topic_list = []
        for topic in self.dialogue["talk"]:
            if topic["base_topic"]:
                topic_list.append(topic["topic"])
        topic_list.append("Back")

        topics = []
        for topic in self.dialogue["talk"]:
            if topic["base_topic"]:
                topics.append(topic)
        topics.append("")

        Func.print_to_journal("Hello")

        while 1:
            self.show_options(topic_list)

            input_key = conversation.getch()
            if not chr(input_key).isnumeric():
                continue

            if int(chr(input_key)) - 1 >= len(topic_list):
                continue

            if topics[int(chr(input_key)) - 1] == "":
                break

            chosen_topic = topics[int(chr(input_key)) - 1]
            player.update_talk_quests(self, chosen_topic["topic"])

            topic_list = []
            for topic in chosen_topic["choices"]:
                topic_list.append(topic)
            topics = []
            for topic in self.dialogue["talk"]:
                if topic["topic"] in chosen_topic["responses"]:
                    topics.append(topic)
            for response in chosen_topic["responses"]:
                if response == "":
                    topics.append(response)
            Func.print_to_journal(chosen_topic["content"])

    def choose_quest(self, key, quests, enemies, npcs, player):
        player.update_all_quests(self, "")
        quest_list = quests
        if int(chr(key)) - 1 >= len(quest_list):
            pass
        else:
            quest = quest_list[int(chr(int(key) - 1))]
            npc_quest_index = self.quests.index(quest)
            if quest not in player.quests:
                journal.insertln()
                journal.addstr(1, 1, quest.description)
                journal.border()
                journal.refresh()
                list_key = int(chr(int(key) - 1))
                while 1:
                    self.show_options(conversation, "Yes", "No")
                    key = conversation.getch()
                    if key is ord("1"):
                        journal.insertln()
                        journal.addstr(1, 1, "You have accepted the quest")
                        journal.refresh()
                        player.add_quest(quest_list[list_key])
                        self.conversation_start()
                        break
                    elif key is ord("2"):
                        break
            else:
                player_quest_index = player.quests.index(quest)
                if player.quests[player_quest_index].completed:

                    journal.insertln()
                    journal.addstr(1, 1, "You have completed my quest, here is your reward.")
                    journal.border()
                    journal.refresh()
                    self.show_options("1 - Accept")
                    key = conversation.getch()
                    if key is ord("1"):
                        quest.reset()
                        player.coins += quest.coin_reward
                        if quest.object_reward is not None:
                            player.add_inventory_item(quest.object_reward)
                        player.increase_exp(quest.exp_reward)
                        if quest.type.value == 1:
                            item = quest.item_to_collect
                            amount = quest.amount
                            for inv_item in player.inventory[0]:
                                if inv_item.name == item:
                                    index = player.inventory[0].index(inv_item)
                            player.inventory[1][index] -= amount
                        del player.quests[player_quest_index]
                        if not quest.repeatable:
                            del self.quests[npc_quest_index]
                            del quest
                        self.conversation_start()
                        player.update_inventory()
                else:
                    journal.insertln()
                    journal.addstr(1, 1, "You have already accepted that quest.")
                    journal.border()
                    journal.refresh()

    def interact(self, player, enemies, npcs):
        input_key = -1
        while input_key is not ord("4"):
            if not self.quests:
                self.has_quest = False
            if self.talking is False:
                journal.insertln()
                journal.addstr(1, 1, self.dialogue["intro"][0])
                self.conversation_start()
            self.talking = True
            conversation.refresh()
            Func.update_journal()
            input_key = conversation.getch()
            if input_key is ord("1"):
                self.talk(player)
                self.conversation_start()
                input_key = -1
            elif input_key is ord("2"):

                if self.has_quest is True:
                    while 1:
                        journal.insertln()
                        journal.addstr(1, 1, "These are the quests that I have")
                        journal.border()
                        journal.refresh()
                        quest_list = []
                        for quest in self.quests:
                            quest_list.append(quest.name)

                        self.show_options(quest_list)

                        quests = []
                        for quest in self.quests:
                            quests.append(quest)
                        input_key = conversation.getch()
                        self.choose_quest(input_key, quests, enemies, npcs, player)
                        self.conversation_start()
                        break
                    input_key = -1
                else:
                    journal.insertln()
                    journal.addstr(1, 1, "I have no quest for you at the moment")
                    journal.refresh()
            elif input_key is ord("3"):
                journal.insertln()
                journal.addstr(1, 1, self.dialogue["trade"][0])
                if self.trade_inventory is not []:
                    self.trade(player)
                self.conversation_start()

    def refresh_trade_menu(self, inv):
        for item in inv:
            journal.deleteln()
            journal.refresh()

    # TODO improve the trade system
    def trade(self, player):
        input_key = -1
        conversation.keypad(True)
        conversation.clear()
        conversation.border()
        conversation.addstr(1, 1, "1 - buy")
        conversation.addstr(2, 1, "2 - sell")
        conversation.addstr(3, 1, "3 - leave")
        buy = True
        while input_key != ord("3"):
            input_key = conversation.getch()
            if input_key == ord("1"):
                break
            elif input_key == ord("2"):
                buy = False
                if not player.inventory[0]:
                    return
                else:
                    break
        else:
            return
        input_key = -1
        conversation.clear()
        conversation.border()
        if buy:
            conversation.addstr(1, 1, "1 - buy item")
            conversation.addstr(2, 1, "2 - leave trade")
            inv = self.trade_inventory
        else:
            conversation.addstr(1, 1, "1 - sell item")
            conversation.addstr(2, 1, "2 - leave trade")
            inv = player.inventory[0]
        for item in inv:
            journal.insertln()
        option = 0
        while input_key is not ord("2"):
            self.refresh_trade_menu(inv)
            journal.clear()
            selection = [0] * len(inv)
            selection[option] = curses.A_REVERSE
            for item in inv:
                journal.insertln()
                journal.addstr(1, 1, item.name, selection[inv.index(item)])
                journal.addstr(1, 20, "value: " + str(item.value))
            journal.border()
            journal.refresh()
            input_key = conversation.getch()
            if input_key == curses.KEY_UP:
                option += 1
            elif input_key == curses.KEY_DOWN:
                option -= 1
            if option < 0:
                option = len(inv) - 1
            elif option >= len(inv):
                option = 0
            if input_key == ord("1"):
                if buy:
                    if player.coins >= inv[option].value:
                        player.coins -= inv[option].value
                        player.add_inventory_item(inv[option])
                else:
                    player.coins += inv[option].value
                    player.remove_inventory_item(inv[option])
                    option -= 1
                    if option <= 0:
                        option = 0
                    if len(inv) == 0:
                        break
                player.update_player_status()
        else:
            for item in inv:
                journal.deleteln()
                journal.border()
                journal.refresh()

    def move_to(self, y, x):
        if y == self.location[0] and x == self.location[1]:
            self.prevlocation = self.location[:]
            pass
        elif self.location[0] == y:
            self.prevlocation = self.location[:]
            if x > self.location[1]:
                self.location[1] += 1
            else:
                self.location[1] -= 1
        elif self.location[1] == x:
            self.prevlocation = self.location[:]
            if y > self.location[0]:
                self.location[0] += 1
            else:
                self.location[0] -= 1
        elif abs(x - self.location[1]) >= abs(y - self.location[0]):
            self.prevlocation = self.location[:]
            if x > self.location[1]:
                self.location[1] += 1
            else:
                self.location[1] -= 1
        elif abs(x - self.location[1]) <= abs(y - self.location[0]):
            self.prevlocation = self.location[:]
            if y > self.location[0]:
                self.location[0] += 1
            else:
                self.location[0] -= 1

    def is_near_player(self, player, distance):
        x = False
        y = False
        if distance >= (player.location[0] - self.location[0]) >= (distance * -1):
            y = True
        if distance >= (player.location[1] - self.location[1]) >= (distance * -1):
            x = True
        if x and y:
            return True
        else:
            return False

    def respawn(self):
        self.health = self.max_health
        self.location = self.spawn_location[:]

    def attack(self, player):
        if player.location[0] == self.location[0] + 1 or player.location[0] == self.location[0] - 1 or \
           player.location[0] == self.location[0]:
            if player.location[1] == self.location[1] + 1 or player.location[1] == self.location[1] - 1 or \
                            player.location[1] == self.location[1]:
                super().attack(player)

    def follow_player(self, player):
        if self.is_near_player(player, 5):
            self.move_to(player.location[0], player.location[1])

    def move(self, area, player):
        if self.allow_movement:
            if self.relationship == Relationship.Enemy:
                if ((player.level - self.level) >= 9) is False:
                    if self.is_near_player(player, 5):
                        self.follow_player(player)
                    else:
                        self.prevlocation = self.location[:]
                        direction = randint(0, 4)
                        if direction is 0:
                            pass
                        elif direction is 1:
                            self.move_up()
                        elif direction is 2:
                            self.move_down(area)
                        elif direction is 3:
                            self.move_right(area)
                        else:
                            self.move_left()
                else:
                    self.prevlocation = self.location[:]
                    direction = randint(0, 4)
                    if direction is 0:
                        pass
                    elif direction is 1:
                        self.move_up()
                    elif direction is 2:
                        self.move_down(area)
                    elif direction is 3:
                        self.move_right(area)
                    else:
                        self.move_left()
            else:
                self.prevlocation = self.location[:]
                direction = randint(0, 4)
                if direction is 0:
                    pass
                elif direction is 1:
                    self.move_up()
                elif direction is 2:
                    self.move_down(area)
                elif direction is 3:
                    self.move_right(area)
                else:
                    self.move_left()

    def save_character(self):
        character = super().save_character()
        character["allow_movement"] = self.allow_movement
        character["relationship"] = self.relationship.value
        return character

    def is_enemy(self):
        if self.relationship == Relationship.Enemy:
            return True
        else:
            return False

    def is_friend(self):
        if self.relationship == Relationship.Friend:
            return True
        else:
            return False

    def on_death(self, player):
        super().on_death()
        if self.is_enemy():
            player.increase_exp(self.increase_exp_by)


def on_map(name, npc_id):
    if name in map1.MAP["unique_NPCs"]:
        return True
    for npc in map1.MAP["common_NPCs"]:
        if npc_id == npc["id"]:
            return True
    return False


def save_npcs(save, npcs):
    all_NPCs = npcs[:]
    npcs.clear()
    for npc in all_NPCs:
        if npc.race is not Race.Wolf:
            temp_npc = npc.save_character()
            npcs.append(temp_npc)
    save["all_NPCs"].clear()
    save["all_NPCs"] = npcs[:]
    DebugLog.write("NPCs saved" + "\n")


def load_npc_dialogue(name):  # for NEW game only
    filename = 'Dialogue/' + Func.sanitize_filename(name) + '.json'
    if os.path.exists(filename):
        with open(filename, 'r') as a:
            dialogue = json.load(a)
            a.close()
        DebugLog.write("dialogue loaded" + "\n")
        return dialogue
    else:
        DebugLog.write("no dialogue\n")


def place_npcs(npcs):
    for npc in npcs:
        spawn_character(map1, npc, npc.location[0], npc.location[1])


global map1
