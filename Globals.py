import curses

DebugLog = open('RPGLog.txt', 'w')
player_turn = True
current_map_path = "Maps/map1.json"

# creates the screens and windows that are used in the game
screen = curses.initscr()
map_window = curses.newwin(35, 100, 2, 3)
trade_win = curses.newwin(50, 65, 2, 110)
enemy_status = curses.newwin(10, 20, 38, 57)
journal = curses.newwin(50, 65, 2, 110)
conversation = curses.newwin(10, 20, 38, 84)

dims = map_window.getmaxyx()
