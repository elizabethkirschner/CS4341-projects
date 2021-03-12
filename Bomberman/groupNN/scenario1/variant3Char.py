# This is necessary to find the main code
import sys
sys.path.insert(0, '../bomberman')
# Import necessary stuff
from entity import CharacterEntity
from colorama import Fore, Back
from sensed_world import SensedWorld
from queue import PriorityQueue

import numpy as np

class TestCharacter(CharacterEntity):
    def kindaInit(self):
        self.states = {};
        self.actions = ["Down", "DownRight", "Right", "UpRight", "Up", "UpLeft", "Left", "DownLeft"]
        self.states['dXExit'] = {"allVals": [0, 1, 2, 3, 4, 5], "currentVal": 0, "table": np.zeros((len(self.actions), 6)), "weight": 0}
        self.states["dYExit"] = {"allVals": [0, 1, 2, 3, 4, 5], "currentVal": 0, "table": np.zeros((len(self.actions), 6)), "weight": 0}
        self.states["dXMonsterDef"] = {"allVals": [0, 1, 2, 3, 4, 5], "currentVal": 0, "table": np.zeros((len(self.actions), 6)), "weight": 0}
        self.states["dYMonsterDef"] = {"allVals": [0, 1, 2, 3, 4, 5], "currentVal": 0, "table": np.zeros((len(self.actions), 6)), "weight": 0}
        self.states["wallDown"] = {"allVals": [0, 1, 2, 3, 4, 5], "currentVal": 0, "table": np.zeros((len(self.actions), 6)), "weight": 0}
        self.states["wallDownRight"] = {"allVals": [0, 1, 2, 3, 4, 5], "currentVal": 0, "table": np.zeros((len(self.actions), 6)), "weight": 0}
        self.states["wallRight"] = {"allVals": [0, 1, 2, 3, 4, 5], "currentVal": 0, "table": np.zeros((len(self.actions), 6)), "weight": 0}
        self.states["wallUpRight"] = {"allVals": [0, 1, 2, 3, 4, 5], "currentVal": 0, "table": np.zeros((len(self.actions), 6)), "weight": 0}
        self.states["wallUp"] = {"allVals": [0, 1, 2, 3, 4, 5], "currentVal": 0, "table": np.zeros((len(self.actions), 6)), "weight": 0}
        self.states["wallUpLeft"] = {"allVals": [0, 1, 2, 3, 4, 5], "currentVal": 0, "table": np.zeros((len(self.actions), 6)), "weight": 0}
        self.states["wallLeft"] = {"allVals": [0, 1, 2, 3, 4, 5], "currentVal": 0, "table": np.zeros((len(self.actions), 6)), "weight": 0}
        self.states["wallDownLeft"] = {"allVals": [0, 1, 2, 3, 4, 5], "currentVal": 0, "table": np.zeros((len(self.actions), 6)), "weight": 0}
        self.states["exitMoveX"] = {"allVals": [0, 1, 2, 3, 4, 5], "currentVal": 0, "table": np.zeros((len(self.actions), 6)), "weight": 0}
        self.states["exitMoveY"] = {"allVals": [0, 1, 2, 3, 4, 5], "currentVal": 0, "table": np.zeros((len(self.actions), 6)), "weight": 0}
        self.states["monMoveX"] = {"allVals": [0, 1, 2, 3, 4, 5], "currentVal": 0, "table": np.zeros((len(self.actions), 6)), "weight": 0}
        self.states["monMoveY"] = {"allVals": [0, 1, 2, 3, 4, 5], "currentVal": 0, "table": np.zeros((len(self.actions), 6)), "weight": 0}

        return self
    
    def orGreater5(self, val):
        if val > 5:
            return 5
        return val
    
    def moveVal(self, val):
        val = val + 2;
        if val > 5:
            return 5
        if val < 0:
            return 0
        return val
    
    def getState(self, wrld):
        print(self.states)
        self.states['dXExit'].currentVal = self.moveVal(7-self.x)
        self.states.dYExit.currentVal = self.moveVal(18-self.y)
        monsterPos = self.getMonsterPos(wrld)
        self.states.dXMonsterDef.currentVal = self.moveVal(monsterPos[0])
        self.states.dYMonsterDef.currentVal = self.moveVal(monsterPos[1])
        self.states.wallDown.currentVal = self.orGreater5(self.howFarWall(wrld, self.x, self.y, 0, 1))
        self.states.wallDownRight.currentVal = self.orGreater5(self.howFarWall(wrld, self.x, self.y, 1, 1))
        self.states.wallRight.currentVal = self.orGreater5(self.howFarWall(wrld, self.x, self.y, 1, 0))
        self.states.wallUpRight.currentVal = self.orGreater5(self.howFarWall(wrld, self.x, self.y, 1, -1))
        self.states.wallUp.currentVal = self.orGreater5(self.howFarWall(wrld, self.x, self.y, 0, -1))
        self.states.wallUpLeft.currentVal = self.orGreater5(self.howFarWall(wrld, self.x, self.y, -1, -1))
        self.states.wallLeft.currentVal = self.orGreater5(self.howFarWall(wrld, self.x, self.y, -1, 0))
        self.states.wallDownLeft.currentVal = self.orGreater5(self.howFarWall(wrld, self.x, self.y, -1, 1))
        exitSearch = self.doSearch(wrld, 7, 18)
        monsterSearch = self.doSearch(wrld, monsterPos[0], monsterPos[1])
        self.states.exitMoveX.currentVal = self.moveVal(exitSearch[0][0])
        self.states.exitMoveY.currentVal = self.moveVal(exitSearch[0][1])
        self.states.monMoveX.currentVal = self.moveVal(monsterSearch[0][0])
        self.states.monMoveY.currentVal = self.moveVal(monsterSearch[0][1])
        
    
    def howFarWall(self, wrld, x, y, dx, dy):
        if x<0 or x>7 or y<0 or y>18 or wrld.wall_at(x, y):
            return 0
        
        return 1 + howFarWall(wrld, x+dx, y+dy, dx, dy)
        
    
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
        frontier.put((self.x, self.y, []))
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
                    priority = new_cost + (x - next[0] + y - next[1])
                    frontier.put(next, priority)
                    came_from[self.getPos(next)] = current

            


                
    def getMonsterPos(self, wrld):
        for i in range(0,8):
            for j in range(0,19):
                if not wrld.monsters_at(i,j) == None:
                    return (i, j)
        return None
    
    def getDenom(self, num):
        if not num == 0:
            return abs(num)
        return 1
    
    def isCloseToMonster(self, wrld):
        monPos = self.getMonsterPos(wrld)
        if not monPos == None:
            xDif = self.x - monPos[0];
            yDif = self.y - monPos[1];
            if xDif < 4 and xDif > -4 and yDif < 4 and yDif > -4:
                return (xDif/self.getDenom(xDif), yDif/self.getDenom(yDif))
        return None
    
    def do(self, wrld):
        """if self.hasDoneSearch == 0:
            self.searchList = self.doSearch(wrld)
            self.hasDoneSearch = 1
        closeMove = self.isCloseToMonster(wrld)
        if not closeMove == None:
            self.move(closeMove[0], closeMove[1])
            self.scared = True
        else:
            if self.scared:
                self.searchList = self.doSearch(wrld)
                self.scared = False
            self.move(self.searchList[0][0], self.searchList[0][1])
            self.searchList.pop(0)
        # Your code here"""
        pass
