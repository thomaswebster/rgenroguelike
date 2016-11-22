import curses

LOG = []

TILES = {0:curses.COLOR_GREEN, 1:curses.COLOR_YELLOW, 2:curses.COLOR_CYAN, 3:curses.COLOR_BLUE}
PASSABLE_TILES = [0 , 1]
ENEMY_SPAWN_RATE = 0.01
XP_RATE = 1


def dist(self, pos1, pos2):
    return [pos1[0]-pos2[0],pos1[1]-pos2[1]]