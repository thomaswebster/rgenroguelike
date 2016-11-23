#global imports
from random import randint

#local imports
import global_consts

#base entity class for anything that could be on the map that isnt a land tile
class Entity(object):
    def __init__(self, pos, character):
        self.pos = pos
        self.character = character

    def interact(self, ent):
        global_consts.LOG.append("%s interacted with %s"%(self.attributes["NAME"], ent.attributes["NAME"]))

class Killable(Entity):
    def __init__(self, pos, character):
        Entity.__init__(self, pos, character)
        self.stats = {"STR":5, "END":5, "SPD":5}    #increase on level up (choice for player)
        self.profs = {"SWM":10, "SWD":5}            #increase on usage -> perks? [placeholder]
        self.tags = {"NAME":"killable", "LVL":1,"HP":10, "MHP":10, "TEAM":"nature", "SIGHT":15}
        self.xp = {"XP":0, "DXP":5}

    def is_dead(self):
        #check for deadness
        if self.tags["HP"] <= 0:
            return True
        return False

    def is_onscreen(self, offset):
        x = (offset[1] <= self.pos[1] < (offset[1] + global_consts.GAMESIZE[1]))
        y = (offset[0] <= self.pos[0] < (offset[0] + global_consts.GAMESIZE[0]))
        return x and y

    def damage(self, num):
        self.tags["HP"] -= num

        return self.is_dead()

    def xp_to_level(self):
        return 10 + int((self.tags["LVL"]**1.5)*0.5) - self.xp["XP"]


    def add_xp(self, num):
        global_consts.LOG.append("%s gained %d experience"%(self.tags["NAME"], num))
        self.xp["XP"] += num

        #while we have experience to level up, we do just that!
        if self.xp_to_level() <= 0:
            while self.xp_to_level() <= 0:
                self.level_up()
            return True
        return False

    def level_up(self):
        self.xp["XP"] -= 10 + int((self.tags["LVL"]**1.5)*0.5)

        #increase level by 1...
        self.tags["LVL"] += 1

        #log dat shit
        global_consts.LOG.append("%s levelled up to level %d"%(self.tags["NAME"], self.tags["LVL"]))

        #default leveling up (for NPCs) increases each stat by 1 and adds lvl HP
        for stat in self.stats:
            self.stats[stat] += 1
        self.tags["HP"] += self.tags["LVL"]

        #heal on level up
        self.tags["HP"] = self.tags["MHP"]


    def update(self, colmap, entmap, entlist, offset):
        #basic AI for attack-player-on-sight enemies

        amt = [0, 0]
        disttoplayer = sum(map(abs, global_consts.dist(self.pos, entlist[0].pos)))
        if disttoplayer < self.tags["SIGHT"]:
            relpos = global_consts.dist(self.pos, entlist[0].pos)

            normalise = max(map(abs, relpos + [1]))
            tomove = [-int(relpos[0]/normalise), -int(relpos[1]/normalise)]# + abs(int(relpos[0]/max(relpos)))]
            global_consts.LOG.append(str(tomove) + " " + str(max(relpos)))
            amt = tomove

        self.move(colmap, entmap, entlist, offset, amt)

    def move(self, colmap, entmap, entlist, offset, amt):
        #find tile we want to move to
        totile = [self.pos[0] + amt[0], self.pos[1] + amt[1]]

        if colmap[totile[0] - offset[0]][totile[1] - offset[1]] == 0:
        #first check if terrain is passable
            if entmap[totile[0] - offset[0]][totile[1] - offset[1]] == -1:
                #then check no entities either

                #remove from map array old position
                entmap[self.pos[0] - offset[0]][self.pos[1] - offset[1]] = -1

                #update location
                self.pos = totile

                if self.is_onscreen(offset):
                    entlist.remove(self)
                    return False
                global_consts.LOG.append(str(entlist))
                #whack in new position
                entmap[self.pos[0] - offset[0]][self.pos[1] - offset[1]] = entlist.index(self)
                
                return True
            else:
                #interact with whatever we bumped into!
                self.interact(entlist[entmap[totile[0] - offset[0]][totile[1] - offset[1]]], entlist)
        return False
    
    def interact(self, ent, entlist):
        if isinstance(ent, Killable) and ent.tags["TEAM"] != self.tags["TEAM"]:
            dam = randint(0, self.stats["STR"])
            
            global_consts.LOG.append("%s damaged %s for %d damage"%(self.tags["NAME"], ent.tags["NAME"], dam))

            if ent.damage(dam):
                #if damage kills entity
                global_consts.LOG.append("%s killed %s!"%(self.tags["NAME"], ent.tags["NAME"]))
                self.add_xp(ent.xp["DXP"])

                entlist.remove(ent)


class Player(Killable):
    def __init__(self, pos):
        Killable.__init__(self, pos, "@")
        self.tags = {"NAME":"player", "LVL":1, "HP":100, "MHP":100, "TEAM":"player"}