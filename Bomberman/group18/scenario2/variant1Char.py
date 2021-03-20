# This is necessary to find the main code
import sys
sys.path.insert(0, '../bomberman')
# Import necessary stuff
from entity import CharacterEntity
from colorama import Fore, Back
from sensed_world import SensedWorld
from queue import PriorityQueue
import math
import time

class TestCharacter(CharacterEntity):
    def kindaInit(self):
        self.state = 0 #state0 is go to lowest point, #state1 is place bomb #state2 is hide for 10 tics #state3 is go to exit
        self.bombTimer = 0;
        return self

    def getNeighbors(self, current, wrld):
        retList = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if not (current[0]+dx < 0 or current[0]+dx > 7 or current[1]+dy < 0 or current[1]+dy > 18) and not wrld.wall_at(current[0]+dx, current[1]+dy):
                    copyList = current[2].copy()
                    copyList.append((dx, dy))
                    retList.append((current[0]+dx, current[1]+dy, copyList))
        return retList
    
    def getPos(self, current):
        return (current[0], current[1])
    
    def doSearch(self, wrld, x, y):
        frontier = PriorityQueue()
        frontier.put((0, (self.x, self.y, [])))
        came_from = {}
        cost_so_far = {}
        came_from[(self.x, self.y)] = None
        cost_so_far[(self.x, self.y)] = 0

        while not frontier.empty():
            current = frontier.get()[1]
            if current[0] == x and current[1] == y:
                return current[2]
            for next in self.getNeighbors(current, wrld):
                new_cost = cost_so_far[self.getPos(current)] + 1
                if self.getPos(next) not in cost_so_far or new_cost < cost_so_far[self.getPos(next)]:
                    cost_so_far[self.getPos(next)] = new_cost
                    priority = new_cost + math.sqrt((x - next[0])*(x - next[0]) + (y - next[1])*(y - next[1]))
                    frontier.put((priority, next))
                    came_from[self.getPos(next)] = current

    

    def do(self, wrld):
        if self.state == 0:
            yVal = 18
            search = self.doSearch(wrld, 1, yVal)
            while search == None:
                yVal -= 1;
                search = self.doSearch(wrld, 1, yVal)
            self.move(search[0][0], search[0][1])
            if len(search) == 1:
                self.state = 1
        elif self.state == 1:
            self.place_bomb()
            self.state = 2
        elif self.state == 2:
            self.move(-1, -1)
            self.bombTimer += 1
            if self.bombTimer > 15:
                if not self.doSearch(wrld, 7, 18) == None:
                    self.state = 3
                    self.bombTimer = 0
                else:
                    self.state = 0
                    self.bombTimer = 0
        elif self.state == 3:
            search = self.doSearch(wrld, 7, 18)
            self.move(search[0][0], search[0][1])
                
        # Your code here
        pass
