#!/usr/bin/python3

from curses import wrapper
import curses

class Choice(object):
    def __init__(self, label, function):
        self.label = label
        self.function = function

    def update(self, character):
        if ord(character) == curses.KEY_ENTER:
            self.function()

class Menu(object):
    def __init__(self, width, title):
        self.title = title
        self.width = width
        self.choices = []
        self.selected = 0


    def addchoice(self, label):
        self.choices.append(Choice(label, lambda x: print("PRESSED!")))

    def updatemenu(self, inp):
        #run the update function with the input for the active choice
        self.choices[self.selected].update(inp)

        #empty list of strings to be drawn as the menu
        self.drawbuffer = []

        #add top border with title in it
        self.drawbuffer.append("+%s%s+"%("."*(self.width-2-len(self.title)), self.title))

        #add each choice
        for index, choice in enumerate(self.choices):
            self.drawbuffer.append("%s%s"%("> "*(index == self.selected),choice.label))

        #add bottom border
        self.drawbuffer.append("+%s+"%("."*(self.width-2)))

        self.drawbuffer.append("")

    def select(self, amt):
        self.selected = min(len(self.choices) - 1, max(0, self.selected + amt))

    def draw(self, pos):
        self.window = curses.newwin(len(self.drawbuffer), self.width, pos[1], pos[0])

        for index, line in enumerate(self.drawbuffer):
            self.window.addstr(index, 0, line)

        self.window.refresh()

def main(stdscr):
    stdscr.clear()
    stdscr.refresh()

    curses.update_lines_cols()
    curses.curs_set(0)

    mainmenu = Menu(25, "Main Menu")

    mainmenu.addchoice("Generate Map")
    mainmenu.addchoice("New Character")
    mainmenu.addchoice("Start Game")
    mainmenu.addchoice("Exit")

    while True:
        c = chr(stdscr.getch())

        if c == "w":
            mainmenu.select(-1)
        if c == "s":
            mainmenu.select(1)

        mainmenu.updatemenu(c)
        mainmenu.draw([0,0])
        stdscr.refresh()

wrapper(main)