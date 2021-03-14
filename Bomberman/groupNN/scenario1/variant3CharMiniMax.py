# This is necessary to find the main code
import sys
sys.path.insert(0, '../bomberman')
# Import necessary stuff
from entity import CharacterEntity
from colorama import Fore, Back
from sensed_world import SensedWorld
from queue import PriorityQueue
import copy
import random
import math
import numpy as np

class TestCharacter(CharacterEntity):
    def kindaInit(self):
        return self
    
    def getActionVector(self, action):
        if action == 0: #Down
            return (0, 1)
        elif action == 1: #DownRight
            return (1, 1)
        elif action == 2: #"Right":
            return (1, 0)
        elif action == 3: #"UpRight":
            return (1,-1)
        elif action == 4: #"Up":
            return (0, -1)
        elif action == 5: #"UpLeft":
            return (-1, -1)
        elif action == 6: #"Left":
            return (-1, 0)
        elif action == 7:#"LeftDown":
            return (-1, 1)
        else:
            print("YO NO ACTION WAS SELECTED")
    
    def getAllActions(self, wrld, x, y):
        ret = []
        if self.y < 18:
            if not wrld.wall_at(x, y+1):
                ret.append(0)
        if self.x < 7:
            if self.y < 18 and not wrld.wall_at(x+1, y+1):
                ret.append(1)
            if not wrld.wall_at(x+1, y):
                ret.append(2)
            if self.y > 0 and not wrld.wall_at(x+1, y-1):
                ret.append(3)
        if self.y > 0:
            if not wrld.wall_at(x, y-1):
                ret.append(4)
        if self.x > 0:
            if self.y < 18 and not wrld.wall_at(x-1, y+1):
                ret.append(7)
            if not wrld.wall_at(x-1, y):
                ret.append(6)
            if self.y > 0 and not wrld.wall_at(self.x-1, self.y-1):
                ret.append(5)
        return ret
    
    def getCharInWorld(self, wrld):
        for i in range(0,8):
            for j in range(0,19):
                chars = wrld.characters_at(i, j)
                if not chars == None:
                    return chars[0]
        return None
    
    def getAllMonstersInWorld(self, wrld):
        ret = []
        for i in range(0,8):
            for j in range(0,19):
                chars = wrld.monsters_at(i, j)
                if not chars == None:
                    ret += chars
        return ret
    
    
    def generateCharMoveWorlds(self, wrld):
        ret = []
        allActions = self.getAllActions(wrld, self.x, self.y)
        for i in allActions:
            newWorld = SensedWorld.from_world(wrld)
            newChar = self.getCharInWorld(newWorld)
            actionVector = self.getActionVector(i)
            newChar.x += actionVector[0]
            newChar.y += actionVector[1]
            ret.append((newWorld, i))
        return ret
    
    def look_for_empty_cell(self, monster, wrld):
        # List of empty cells
        cells = []
        # Go through neighboring cells
        for dx in [-1, 0, 1]:
            # Avoid out-of-bounds access
            if ((monster.x + dx >= 0) and (monster.x + dx < wrld.width())):
                for dy in [-1, 0, 1]:
                    # Avoid out-of-bounds access
                    if ((monster.y + dy >= 0) and (monster.y + dy < wrld.height())):
                        # Is this cell safe?
                        if(wrld.exit_at(monster.x + dx, monster.y + dy) or
                           wrld.empty_at(monster.x + dx, monster.y + dy)):
                            # Yes
                            cells.append((dx, dy))
        # All done
        return cells

    def look_for_character(self, monster, wrld):
        for dx in range(-1, 1):
            # Avoid out-of-bounds access
            if ((monster.x + dx >= 0) and (monster.x + dx < wrld.width())):
                for dy in range(-1, 1):
                    # Avoid out-of-bounds access
                    if ((monster.y + dy >= 0) and (monster.y + dy < wrld.height())):
                        # Is a character at this position?
                        if (wrld.characters_at(monster.x + dx, monster.y + dy)):
                            return (True, dx, dy)
        # Nothing found
        return (False, 0, 0)
        
        
    def getMonsterMoves(self, monster, wrld):
        """Pick an action for the monster"""
        # If a character is in the neighborhood, go to it
        safe = self.look_for_empty_cell(monster, wrld)
        (found, dx, dy) = self.look_for_character(monster, wrld)
        if found and not self.must_change_direction(monster, wrld):
            return [(dx, dy)]
        #If I'm idle or must change direction, change direction
        if ((monster.dx == 0 and monster.dy == 0) or
            self.must_change_direction(monster, wrld)):
            # Get list of safe moves
            if not safe:
                # Accept death
                return [(0,0)]
            #else:
                # Pick a move at random
        return safe
    
    def must_change_direction(self, monster, wrld):
        # Get next desired position
        (nx, ny) = monster.nextpos()
        # If next pos is out of bounds, must change direction
        if ((nx < 0) or (nx >= wrld.width()) or
            (ny < 0) or (ny >= wrld.height())):
            return True
        # If these cells are an explosion, a wall, or a monster, go away
        return (wrld.explosion_at(monster.x, monster.y) or
                wrld.wall_at(nx, ny) or
                wrld.monsters_at(nx, ny) or
                wrld.exit_at(nx, ny))
    
    def generateMonsterMoveWorlds(self, wrld):
        ret = []
        monster = self.getAllMonstersInWorld(wrld)[0]
        monsterMoves = self.getMonsterMoves(monster, wrld)
        for i in monsterMoves:
            newWorld = SensedWorld.from_world(wrld)
            newMonster = self.getAllMonstersInWorld(newWorld)[0]
            newMonster.x += i[0]
            newMonster.y += i[1]
            ret.append(newWorld)
        return ret
    
    
    def ExpectimaxSearch(self, wrld, depth):
        maxVal = float('-inf')
        # alpha = float('-inf')
        # beta = float('inf')
        maxAction = -1
        newWorlds = self.generateCharMoveWorlds(wrld)
        for i in newWorlds:
            newVal = self.ExpValue(i[0], depth)
            if maxVal < newVal:
                maxVal = newVal
                maxAction = i[1]
        return maxAction
    
    def ExpValue(self, wrld, depth):
        monMoves = self.generateMonsterMoveWorlds(wrld)
        char = self.getCharInWorld(wrld)
        if wrld.exit_at(char.x, char.y):
            return 50
        if not wrld.monsters_at(char.x, char.y) == None:
            return -50000000
        v = 0
        totalProb = 0
        for i in monMoves:
            p = 1/len(monMoves)
            v = v + p*self.MaxValue(i, depth-1)
            totalProb += p
            # if beta < v:
            #     beta = v
            # if not totalProb == 1 and v + 50*(1/totalProb) <= alpha:
            #     return v
        return v
    
    def MaxValue(self, wrld, depth):
        char = self.getCharInWorld(wrld)
        if wrld.exit_at(char.x, char.y):
            return 50
        if not wrld.monsters_at(char.x, char.y) == None:
            return -50000000
        if depth <= 0:
            return 1000000/len(self.doSearch(wrld, 7, 18))
        maxVal = float('-inf')
        maxAction = -1
        newWorlds = self.generateCharMoveWorlds(wrld)
        for i in newWorlds:
            newVal = self.ExpValue(i[0], depth)
            if newVal > maxVal:
                maxVal = newVal
            # if maxVal < newVal:
            #     maxVal = newVal
            # if maxVal >= beta:
            #     return maxVal
            # if maxVal > alpha:
            #     alpha = maxVal
        return maxVal
        
    
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
            xDif = self.x - monPos[0]
            yDif = self.y - monPos[1]
            if xDif < 4 and xDif > -4 and yDif < 4 and yDif > -4:
                return (xDif/self.getDenom(xDif), yDif/self.getDenom(yDif))
        return None
    
    def do(self, wrld):
        action = self.ExpectimaxSearch(wrld, 2)
        actionVector = self.getActionVector(action)
        self.move(actionVector[0], actionVector[1])
        pass
