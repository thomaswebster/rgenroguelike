#global imports


#local imports
import global_consts

#base entity class for anything that could be on the map that isnt a land tile
class Entity(object):
    def __init__(self, pos, character):
        self.pos = pos
        self.character = character

    def interact(self, ent):
        return "%s interacted with %s"%(self.attributes["NAME"], ent.attributes["NAME"])


class Killable(Entity):
    def __init__(self, pos, character):
        Entity.__init__(self, pos, character)
        self.stats = {"STR":5, "END":5, "SPD":5}    #increase on level up (choice for player)
        self.profs = {"SWM":10, "SWD":5}            #increase on usage -> perks? [placeholder]
        self.tags = {"NAME":"killable", "LVL":1,"HP":10, "MHP":10, "TEAM":"nature"}
        self.xp = {"XP":0, "DXP":5}

    def is_dead(self):
        #check for deadness
        if self.tags["HP"] <= 0:
            return True
        return False


    def damage(self, num):
        self.tags["HP"] -= num

        return is_dead()

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

        #increase level by 1...
        self.tags["LVL"] += 1

        #log dat shit
        global_consts.LOG.append("%s levelled up to level %d"%(self.tags["NAME"], self.tags["LVL"]))

        #default leveling up (for NPCs) increases each stat by 1 and adds lvl HP
        for stat in self.stats:
            self.stats[stat] += 1
        self.tags["HP"] += self.tags["LVL"]

        #heal on level up
        self.attributes["H"] = self.attributes["MH"]

    def update(self, entlist):
        #behavior of killables (find closest ent not on team then go kill...)
        pass

    def move(self, colmap, entmap, entlist, amt):
        #find tile we want to move to
        totile = [self.pos[0] + amt[0], self.pos[1] + amt[1]]

        if colmap[totile[0]][totile[1]] == 0:
        #first check if terrain is passable
            if entmap[totile[0]][totile[1]] == -1:
                #then check no entities either
                self.pos = totile
            else:
                #interact with whatever we bumped into!
                self.interact(entlist[entmap[totile[0]][totile[1]]])
    
    def interact(self, ent, entlist):
        if isinstance(ent, Killable) and ent.attributes["TEAM"] != self.attributes["TEAM"]:
            dam = randint(0, self.attributes["STR"])
            
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

    def move(self, colmap, entmap, entlist, amt):
        #find tile we want to move to
        totile = [self.pos[0] + amt[0], self.pos[1] + amt[1]]

        if colmap[totile[0]][totile[1]] == 0:
        #first check if terrain is passable
            if entmap[totile[0]][totile[1]] == -1:
                #then check no entities either
                self.pos = totile

                #return true when the player has moved for map redrawing and spawning
                return True
            else:
                #interact with whatever we bumped into!
                self.interact(entlist[entmap[totile[0]][totile[1]]], entlist)

        return False