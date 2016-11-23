#!/usr/bin/python3

'''
  ________        __                                                  .___
 /  _____/  _____/  |_  _____________   ____   ______ ______ ____   __| _/
/   \  ____/ __ \   __\ \____ \_  __ \_/ __ \ /  ___//  ___// __ \ / __ | 
\    \_\  \  ___/|  |   |  |_> >  | \/\  ___/ \___ \ \___ \\  ___// /_/ | 
 \______  /\___  >__|   |   __/|__|    \___  >____  >____  >\___  >____ | 
        \/     \/       |__|               \/     \/     \/     \/     \/ 

TODO:
-Universal move function
-Interact funct
-Get closest non-same team entity (for enemies)
-improve pathing for enemies
'''

from curses import wrapper
import curses, noise
from random import randint, random
from time import time

import global_consts
from entity import *

class GameMap(object):
    def __init__(self, size, screen):
        self.size = size
        self.tile_map = [[0]*size[1] for i in range(size[0])]
        self.collision_map = [[0]*size[1] for i in range(size[0])]
        self.entity_map = [[-1]*size[1] for i in range(size[0])]
        self.entities = []
        self.player = Player([0,0])
        self.make_color_pairs()
        self.entities.append(self.player)

        self.offset = [self.player.pos[0] - self.size[0]//2, self.player.pos[1] - self.size[1]//2]
        self.screen = screen

    def add_enemy(self, pos):
        self.entities.append(Killable(pos, "k"))

    def update_entities(self):
        for entity in self.entities[1:]:
            entity.update(self.collision_map, self.entity_map, self.entities, self.offset)

    def move_player(self, pos):

        if self.player.move(self.collision_map, self.entity_map, self.entities, self.offset, pos):
            self.update_map(self.player.pos)

            #spawn enemies along newly generated "BAR"
            if pos[0]:
                for i in range(self.size[1]):
                    spawnpos = [self.offset[0] + ((pos[0] + 1)// 2) * (self.size[0] - 1), i + self.offset[1]]

                    if random() < global_consts.ENEMY_SPAWN_RATE and self.tile_map[((pos[0] + 1)// 2) * (self.size[0] - 1)][i] in global_consts.PASSABLE_TILES:
                        self.add_enemy(spawnpos)

            elif pos[1]:
                for i in range(self.size[0]):
                    spawnpos = [i + self.offset[0], self.offset[1] + ((pos[1] + 1)// 2) * (self.size[1] - 1)]

                    if random() < global_consts.ENEMY_SPAWN_RATE and self.tile_map[i][((pos[1] + 1)// 2) * (self.size[1] - 1)] in global_consts.PASSABLE_TILES:
                        self.add_enemy(spawnpos)

        #self.update_entity_map()
        #self.update_entities()

    def update_player(self, screen):
        pass

    def make_color_pairs(self):
        for i in range(len(global_consts.TILES)):
                curses.init_pair(i+1, curses.COLOR_BLACK, global_consts.TILES[i])

    def is_on_screen(self, pos):
        return (self.offset[0] <= pos[0] < (self.offset[0] + self.size[0])) and (self.offset[1] <= pos[1] < (self.offset[1] + self.size[1]))

    def update_entity_map(self):
        #reset entity map
        self.entity_map = [[-1]*self.size[1] for i in range(self.size[0])]

        #store indexes of entities to remove (due to being offscreen)
        toremove = []

        #populate entity map with entities for drawing
        for index, entity in enumerate(self.entities):
            if self.is_on_screen(entity.pos):
                self.entity_map[entity.pos[0]-self.offset[0]][entity.pos[1]-self.offset[1]] = index - len(toremove)
            else:
                toremove.append(index)

        #destroy off screen entities baby please
        for index in sorted(toremove, reverse=True):
            del self.entities[index]

    def update_map(self, center):
        self.offset = [center[0] - self.size[0]//2, center[1] - self.size[1]//2]
        
        for i in range(self.size[1]):
            for j in range(self.size[0]):
                self.tile_map[j][i] = int(noise.snoise2((i+self.offset[1]) / 48, (j+self.offset[0]) / 48, 4) * 3 + 2)
                self.collision_map[j][i] = 0 if (self.tile_map[j][i] in global_consts.PASSABLE_TILES) else 1


    def draw(self, screen):
        for i in range(self.size[1]):
            for j in range(self.size[0]):
                if self.entity_map[j][i] >= 0:
                    screen.addch(j,i, ord(self.entities[self.entity_map[j][i]].character), curses.color_pair(self.tile_map[j][i] + 1))
                else:
                    screen.addch(j,i, ord(" "), curses.color_pair(self.tile_map[j][i] + 1))

        screen.addstr("\nPLAYER [HP%d/%d] [LVL %d] [XP REQ %d] ||| [I]nventory [O]ptions [P]layer"%(self.player.tags["HP"],
            self.player.tags["MHP"],self.player.tags["LVL"], self.player.xp_to_level()))

        for logline in global_consts.LOG[-6:]:
            screen.addstr("\n" + logline)
        #screen.addstr("\n" + "[%d]"%(self.time))

def main(stdscr):
    stdscr.clear()
    stdscr.refresh()

    curses.update_lines_cols()
    curses.curs_set(0)

    #stdscr.timeout(global_consts.MSF) 
    curses.noecho()
    
    gamemap = GameMap([curses.LINES-8,curses.COLS-1], stdscr)

    #gamemap = GameMap(global_consts.GAMESIZE, stdscr)


    while True:
        inp = [0,0]

        c = stdscr.getch()
        if c == curses.KEY_UP:
            inp = [-1, 0]
        if c == curses.KEY_DOWN:
            inp = [1, 0]
        if c == curses.KEY_LEFT:
            inp = [0, -1]
        if c == curses.KEY_RIGHT:
            inp = [0, 1]

        gamemap.move_player(inp)
        #gamemap.update_entity_map()
        gamemap.update_entities()

        gamemap.draw(stdscr)

        stdscr.refresh()

wrapper(main)