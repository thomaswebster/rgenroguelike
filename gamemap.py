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


class Entity(object):
    def __init__(self, pos, character):
        self.pos = pos
        self.character = character
        self.attributes = {"H":1, "ATK":0, "NAME":"nullentity"}

    def update(self):
        pass

class Player(Entity):
    def __init__(self, pos):
        Entity.__init__(self, pos, "@")
        self.attributes = {"H":100, "MH":100, "LVL": 1, "XP":0, "ATK": 3, "NAME":"player"}

    def add_xp(self, num):
        self.attributes["XP"] += num

        if self.xp_to_level() <= 0:
            while self.xp_to_level() <= 0:
                self.level_up()
            return True
        return False
        #boolean return so we can log level ups!

    def level_up(self):
        self.attributes["XP"] -= 10 + int((self.attributes["LVL"]**1.5)*0.5)
        self.attributes["LVL"] += 1
        self.attributes["ATK"] += 1
        self.attributes["MH"] += 10
        self.attributes["H"] = self.attributes["MH"]

    def xp_to_level(self):
        return 10 + int((self.attributes["LVL"]**1.5)*0.5) - self.attributes["XP"]

class Enemy(Entity):
    def __init__(self, pos, character):
        Entity.__init__(self, pos, character)

    def update(self):
        pass

    def interact(self):
        pass

class GameMap(object):
    TILES = {0:curses.COLOR_GREEN, 1:curses.COLOR_YELLOW, 2:curses.COLOR_CYAN, 3:curses.COLOR_BLUE}
    PASSABLE_TILES = [0 , 1]
    ENEMY_SPAWN_RATE = 0.01
    XP_RATE = 1

    ENEMIES_LIST = {
    0.025:["A", {"H":1000, "ATK":30,"LEVEL":20,"XP":1000, "NAME":"angel", "SIGHT":3}],
    0.1:["D", {"H":100, "ATK":10,"LEVEL":10,"XP":500, "NAME":"dragon", "SIGHT":4}],
    0.15:["w", {"H":25, "ATK":4,"LEVEL":7,"XP":50, "NAME":"warrior", "SIGHT":5}],
    0.25:["b", {"H":10, "ATK":3,"LEVEL":4,"XP":15, "NAME":"bandit", "SIGHT":10}],
    0.5:["g", {"H":5, "ATK":1,"LEVEL":2,"XP":5,"NAME":"goblin", "SIGHT":8}],
    1:["c", {"H":2, "ATK":1,"LEVEL":1,"XP":3,"NAME":"chicken", "SIGHT":0}]
    }

    def __init__(self, size):
        self.size = size
        self.tile_map = [[0]*size[1] for i in range(size[0])]
        self.entity_map = [[-1]*size[1] for i in range(size[0])]
        self.entities = []
        self.player = Player([0,0])
        self.make_color_pairs()
        self.entities.append(self.player)
        self.time = 0
        self.offset = [self.player.pos[0] - self.size[0]//2, self.player.pos[1] - self.size[1]//2]
        self.log = ["[0] Welcome to goblin world!","[0] wasd to move","[0] kill stuff","[0]","[0]"]

    def check_tile_collision(self, pos):
        return (self.tile_map[pos[0]][pos[1]] in GameMap.PASSABLE_TILES) and self.entity_map[pos[0]][pos[1]] == -1

    def alog(self, string):
        self.log.append("[%d] "%self.time + string)

    def fight(self, ent1, ent2):
        ent1dam = randint(0, ent1.attributes["ATK"])
        ent2dam = randint(0, ent2.attributes["ATK"])

        ent1.attributes["H"] -= ent2dam
        ent2.attributes["H"] -= ent1dam
        self.alog("%s damaged %s for %d points"%(ent1.attributes["NAME"], ent2.attributes["NAME"], ent1dam))
        self.alog("%s damaged %s for %d points"%(ent2.attributes["NAME"], ent1.attributes["NAME"], ent2dam))

        if ent2.attributes["H"] <= 0:
            self.alog("%s has killed %s!"%(ent1.attributes["NAME"], ent2.attributes["NAME"]))
            if ent1.add_xp(ent2.attributes["XP"]):
                self.alog("%s levelled up to level %d"%(ent1.attributes["NAME"], ent1.attributes["LVL"]))
            self.entities.remove(ent2)

        elif ent1.attributes["H"] <= 0:
            self.alog("%s has killed %s!"%(ent2.attributes["NAME"], ent1.attributes["NAME"]))
            self.entities.remove(ent1)

    def add_enemy(self, pos):
        choice = random()

        for chance in sorted(GameMap.ENEMIES_LIST):
            if choice < chance:
                toadd = Enemy(pos, GameMap.ENEMIES_LIST[chance][0])
                toadd.attributes = {}
                for atrb in GameMap.ENEMIES_LIST[chance][1]:    #copy attributes over from dictionary
                    toadd.attributes[atrb] = GameMap.ENEMIES_LIST[chance][1][atrb]
                break

        self.entities.append(toadd)

    def dist(self, pos1, pos2):
        return [pos1[0]-pos2[0],pos1[1]-pos2[1]]

    def update_entities(self):
        for enemy in self.entities[1:]:
            plyrdist = self.dist(enemy.pos, self.player.pos)
            if sum(map(abs, plyrdist)) <= enemy.attributes["SIGHT"]:
                if enemy.pos[0] > self.player.pos[0]:
                    enemy.pos[0] -= 1
                elif enemy.pos[0] < self.player.pos[0]:
                    enemy.pos[0] +=1
                elif enemy.pos[1] < self.player.pos[1]:
                    enemy.pos[1] +=1
                elif enemy.pos[1] > self.player.pos[1]:
                    enemy.pos[1] -=1


    def move_player(self, pos):
        self.time += 1
        if self.entity_map[self.size[0]//2 + pos[0]][self.size[1]//2 + pos[1]] + 1:
            self.fight(self.player, self.entities[self.entity_map[self.size[0]//2 + pos[0]][self.size[1]//2 + pos[1]]])
        elif self.check_tile_collision([self.size[0]//2 + pos[0], self.size[1]//2 + pos[1]]):
            self.player.pos[0] += pos[0]
            self.player.pos[1] += pos[1]

            self.offset = [self.player.pos[0] - self.size[0]//2, self.player.pos[1] - self.size[1]//2]

            self.update_map()
                
            #spawn enemies along newly generated "BAR"
            if pos[0]:
                for i in range(self.size[1]):
                    spawnpos = [self.offset[0] + ((pos[0] + 1)// 2) * (self.size[0] - 1), i + self.offset[1]]

                    if random() < GameMap.ENEMY_SPAWN_RATE and self.tile_map[((pos[0] + 1)// 2) * (self.size[0] - 1)][i] in GameMap.PASSABLE_TILES:
                        self.add_enemy(spawnpos)

            elif pos[1]:
                for i in range(self.size[0]):
                    spawnpos = [i + self.offset[0], self.offset[1] + ((pos[1] + 1)// 2) * (self.size[1] - 1)]

                    if random() < GameMap.ENEMY_SPAWN_RATE and self.tile_map[i][((pos[1] + 1)// 2) * (self.size[1] - 1)] in GameMap.PASSABLE_TILES:
                        self.add_enemy(spawnpos)

        self.update_entity_map()
        self.update_entities()

    def update_player(self, screen):
        self.screen = screen

        c = chr(screen.getch())
        if c == "w":
            self.move_player([-1, 0])
        if c == "s":
            self.move_player([1, 0])
        if c == "a":
            self.move_player([0, -1])
        if c == "d":
            self.move_player([0, 1])

    def make_color_pairs(self):
        for i in range(len(GameMap.TILES)):
                curses.init_pair(i+1, curses.COLOR_BLACK, GameMap.TILES[i])

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

    def update_map(self):
        for i in range(self.size[1]):
            for j in range(self.size[0]):
                self.tile_map[j][i] = int(noise.snoise2((i+self.offset[1]) / 48, (j+self.offset[0]) / 48, 4) * 3 + 2)

    def draw(self, screen):
        for i in range(self.size[1]):
            for j in range(self.size[0]):
                if self.entity_map[j][i] >= 0:
                    screen.addch(j,i, ord(self.entities[self.entity_map[j][i]].character), curses.color_pair(self.tile_map[j][i] + 1))
                else:
                    screen.addch(j,i, ord(" "), curses.color_pair(self.tile_map[j][i] + 1))

        screen.addstr("\nPLAYER [HP%d/%d] [LVL %d] [ATK %d] [XP REQ %d] ||| [I]nventory [O]ptions [P]layer"%(self.player.attributes["H"],
            self.player.attributes["MH"],self.player.attributes["LVL"],self.player.attributes["ATK"], self.player.xp_to_level()))

        for logline in self.log[-6:]:
            screen.addstr("\n" + logline)
        screen.addstr("\n" + "[%d]"%(self.time))

def main(stdscr):
    stdscr.clear()
    stdscr.refresh()

    curses.update_lines_cols()
    curses.curs_set(0)

    gamemap = GameMap([curses.LINES-8,curses.COLS-1])

    while True:
        gamemap.update_player(stdscr)

        gamemap.draw(stdscr)

        stdscr.refresh()

wrapper(main)