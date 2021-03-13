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
        self.hasDoneSearch = 0
        self.searchList = []
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
    
    def doSearch(self, wrld):
        frontier = PriorityQueue()
        frontier.put(0, (self.x, self.y, []))
        came_from = {}
        cost_so_far = {}
        came_from[(self.x, self.y)] = None
        cost_so_far[(self.x, self.y)] = 0

        while not frontier.empty():
            current = frontier.get()
            if current[0] == 7 and current[1] == 18:
                return current[2]
            for next in self.getNeighbors(current, wrld):
                new_cost = cost_so_far[self.getPos(current)] + 1
                if self.getPos(next) not in cost_so_far or new_cost < cost_so_far[self.getPos(next)]:
                    cost_so_far[self.getPos(next)] = new_cost
                    priority = new_cost + math.sqrt((7 - next[0])*(7 - next[0]) + (18 - next[1])*(18 - next[1]))
                    frontier.put(next, priority)
                    came_from[self.getPos(next)] = current

            


                

    def do(self, wrld):
        if self.hasDoneSearch == 0:
            self.searchList = self.doSearch(wrld)
            self.hasDoneSearch = 1
        self.move(self.searchList[0][0], self.searchList[0][1])
        self.searchList.pop(0)
        time.sleep(2)
        # Your code here
        pass
