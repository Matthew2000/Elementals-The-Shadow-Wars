import string

import Items
from Globals import *


# modified from https://gist.github.com/seanh/93666
def sanitize_filename(file_name):
    valid_chars = "-_.%s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in file_name if c in valid_chars)
    return filename


def load_inventory(inventory):
    """loads the player inventory from the save file"""
    new_inv = [[], []]
    temp_inv = inventory
    for inv_item in temp_inv[0]:
        index = temp_inv[0].index(inv_item)
        for item in Items.all_items:
            if inv_item == item.name:
                new_inv[0].append(item)
                new_inv[1].append(temp_inv[1][index])
    return new_inv


def update_journal():
    journal.border()
    journal.refresh()


def update_game(player):
    player.update_player_status()
    update_journal()


def update_player_location(player, environment):
    if player.prevlocation.__ne__(player.location):
        if map_window.inch(player.location[0], player.location[1]) == ord(
                " "):
            map_window.addch(player.location[0], player.location[1], ord(player.character))
            map_window.addch(player.prevlocation[0], player.prevlocation[1], " ")
            player.prevlocation = player.location[:]
        else:
            if map_window.inch(player.location[0], player.location[1]) == ord("v"):
                if environment.map["adjacent_maps"]["north"] is not None:
                    environment.go_to_map("north")
                    environment.show_map()
                    player.location = [32, player.location[1]]
                    player.prevlocation = player.location[:]
            if map_window.inch(player.location[0], player.location[1]) == ord("^"):
                if environment.map["adjacent_maps"]["south"] is not None:
                    environment.go_to_map("south")
                    environment.show_map()
                    player.location = [2, player.location[1]]
                    player.prevlocation = player.location[:]
            if map_window.inch(player.location[0], player.location[1]) == ord(">"):
                if environment.map["adjacent_maps"]["west"] is not None:
                    environment.go_to_map("west")
                    environment.show_map()
                    player.location = [player.location[0], 97]
                    player.prevlocation = player.location[:]
            if map_window.inch(player.location[0], player.location[1]) == ord("<"):
                if environment.map["adjacent_maps"]["east"] is not None:
                    environment.go_to_map("east")
                    environment.show_map()
                    player.location = [player.location[0], 2]
                    player.prevlocation = player.location[:]
            player.location = player.prevlocation[:]
    if map_window.inch(player.location[0], player.location[1]) == ord(" "):
        map_window.addch(player.location[0], player.location[1], ord(player.character))


def print_to_journal(message):
    journal.insertln()
    message = message.split()
    message_list = [""]
    x = 0
    for word in message:
        message_list[x] += word + " "
        if len(message_list[x]) >= 50:
            message_list.append("")
            x += 1
            journal.insertln()
    if len(message_list) > 1:
        # journal.deleteln()
        new_message = ""
        for words in message_list:
            new_message += words + "\n "
    else:
        new_message = ""
        for words in message_list:
            new_message += words
    journal.addstr(1, 1, new_message)
    journal.addstr(1, 1, "")
    update_journal()


def player_at_location(player, location):
    if player.location[0] is location[0] and player.location[1] is location[1]:
        return True
    else:
        return False


def player_dead(player):
    if player.is_dead():
        if map_window.inch(player.location[0], player.location[1]) == ord(player.character):
            player.on_death()
            map_window.addch(player.prevlocation[0], player.prevlocation[1], " ")
            print_to_journal(player.name + " is dead")


def print_combat_intro_text():
    print_to_journal('Press "1" to attack or "2" to leave')
    print_to_journal("Battle has started")
    update_journal()


def set_all_stats(npcs, enemies):
    for npc in npcs:
        npc.set_stats_by_level_and_race()
    for enemy in enemies:
        enemy.set_stats_by_level_and_race()
        enemy.increase_exp_by = int((enemy.level ** 2) / .4) + 5


def npc_at_location(location, npcs):
    for npc in npcs:
        if npc.location[0] is location[0] and npc.location[1] is location[1]:
            return {"result": True, "npc": npc}
    else:
        return {"result": False}


def on_map(search_map, name, npc_id):
    if name in search_map.map["unique_NPCs"]:
        return True
    for npc in search_map.map["common_NPCs"]:
        if npc_id == npc["id"]:
            return True
    return False


def start_combat(player, enemy, key):
    print_combat_intro_text()
    update_enemy_status(enemy, enemy_status)
    player.update_player_status()
    while key is not ord("2"):
        update_enemy_status(enemy, enemy_status)
        player.update_player_status()
        if enemy.health <= 0:
            is_enemy_dead(enemy, player)
            player.update_all_quests(enemy, "")
            enemy.allow_movement = True
            update_enemy_status(enemy, enemy_status)
            break
        if player.health <= 0:
            if player.is_dead():
                player_dead(player)
                update_player_location(player, DebugLog)
            enemy.allow_movement = True
            update_enemy_status(enemy, enemy_status)
            break
        key = map_window.getch()
        if ord("1") <= key >= ord("2"):
            continue
        if key is ord("1"):
            player.attack(enemy)
        enemy.attack(player)
    else:
        enemy.allow_movement = True
        print_to_journal("You have left combat")


##############################################################


def is_enemy_dead(enemy, player):
    if enemy.is_dead():
        if map_window.inch(enemy.location[0], enemy.location[1]) == ord(enemy.character):
            enemy.on_death(player)
            map_window.addch(enemy.prevlocation[0], enemy.prevlocation[1], " ")
            print_to_journal(enemy.name + " is dead")
            enemy.prevlocation = enemy.location[:]
            enemy.location = [0, 0]
            print_to_journal("you gained " + str(enemy.increase_exp_by) + " exp")


def update_enemy_status(enemy, enemy_stat_win):
    enemy_stat_win.clear()
    if enemy.allow_movement is False:
        enemy_stat_win.border()
        enemy_stat_win.addstr(0, 1, enemy.name + "'s Stats")
        enemy_stat_win.addstr(1, 1, "Race: " + str(enemy.race)[5:])
        enemy_stat_win.addstr(2, 1, "Health: " + str(enemy.health))
        enemy_stat_win.addstr(3, 1, "Level: " + str(enemy.level))
        enemy_stat_win.addstr(4, 1, "Strength: " + str(enemy.strength))
        enemy_stat_win.addstr(5, 1, "Defense: " + str(enemy.defense))
    enemy_stat_win.refresh()


def update_npc_locations(npcs, environment):
    for npc in npcs:
        if on_map(environment, npc.name, npc.id):
            if npc.prevlocation.__ne__(npc.location):  # moves the Enemy
                if map_window.inch(npc.prevlocation[0], npc.prevlocation[1]) != ord(" "):
                    map_window.addch(npc.prevlocation[0], npc.prevlocation[1], " ")
                if map_window.inch(npc.location[0], npc.location[1]) == ord(
                        " "):  # stops Enemy from moving if there's a enemy there
                    map_window.addch(npc.location[0], npc.location[1], ord(npc.character))
                    map_window.addch(npc.prevlocation[0], npc.prevlocation[1], " ")
                    npc.prevlocation = npc.location[:]
                else:
                    npc.location = npc.prevlocation[:]  # keeps the Enemy at its current location
            if map_window.inch(npc.location[0], npc.location[1]) == ord(" "):
                map_window.addch(npc.location[0], npc.location[1], ord(npc.character))


def enemy_at_location(enemies, location, enemy_stat_win):
    for enemy in enemies:
        if enemy.location[0] is location[0] and enemy.location[1] is location[1]:
            update_enemy_status(enemy, enemy_stat_win)
            enemy.allow_movement = False
            return {"result": True, "enemy": enemy}
    else:
        return {"result": False}


def follow_the_player(enemies, player):
    for enemy in enemies:
        enemy.follow_player(player)


def respawn_enemies(enemies):
    for enemy in enemies:
        if enemy.is_dead():
            if enemy.respawnable:
                enemy.respawn_counter += 1
                if enemy.respawn_counter == 20:
                    enemy.respawn_counter = 0
                    enemy.respawn()
