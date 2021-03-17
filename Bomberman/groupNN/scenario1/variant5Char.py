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
import json
import numpy as np

class TestCharacter(CharacterEntity):
    def __init__(self, name, avatar, x, y):
        CharacterEntity.__init__(self, name, avatar, x, y)
        self.state = 0 #State0 try to find exit, State1 bomb is planted run away
        self.bombTimer = 0
        self.bombX = 0
        self.bombY = 0
        self.bombActive = 0
        
    
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
        elif action == 8:#"No Move":
            return (0, 0)
        else:
            print("YO NO ACTION WAS SELECTED")
    
    def getAllActions(self, wrld, x, y):
        ret = []
        #ret.append(8)
        if y < 18:
            if not wrld.wall_at(x, y+1) and not wrld.explosion_at(x, y+1) and not self.willBeInBlast(wrld, x, y+1, 2):
                ret.append(0)
        if x < 7:
            if y < 18 and not wrld.wall_at(x+1, y+1) and not wrld.explosion_at(x+1, y+1) and not self.willBeInBlast(wrld, x+1, y+1, 2):
                ret.append(1)
            if not wrld.wall_at(x+1, y) and not wrld.explosion_at(x+1, y) and not self.willBeInBlast(wrld, x+1, y, 2):
                ret.append(2)
            if y > 0 and not wrld.wall_at(x+1, y-1) and not wrld.explosion_at(x+1, y-1) and not self.willBeInBlast(wrld, x+1, y-1, 2):
                ret.append(3)
        if y > 0:
            if not wrld.wall_at(x, y-1) and not wrld.explosion_at(x, y-1) and not self.willBeInBlast(wrld, x, y-1, 2):
                ret.append(4)
        if x > 0:
            if y < 18 and not wrld.wall_at(x-1, y+1) and not wrld.explosion_at(x-1, y+1) and not self.willBeInBlast(wrld, x-1, y+1, 2):
                ret.append(7)
            if not wrld.wall_at(x-1, y) and not wrld.explosion_at(x-1, y) and not self.willBeInBlast(wrld, x-1, y, 2):
                ret.append(6)
            if y > 0 and not wrld.wall_at(x-1, y-1) and not wrld.explosion_at(x-1, y-1) and not self.willBeInBlast(wrld, x-1, y-1, 2):
                ret.append(5)
        if not wrld.explosion_at(x, y) and not self.willBeInBlast(wrld, x, y, 2):
            ret.append(8)
        return ret
    
    def getCharInWorld(self, wrld):
        for i in range(0,8):
            for j in range(0,19):
                chars = wrld.characters_at(i, j)
                if not chars == None:
                    return chars[0]
        return None
    

        
    
    def sortMonstersByDistance(self, char, monsters, wrld):
        def sortValue(monster):
            search = self.doSearch(wrld, char, monster.x, monster.y)
            if not search == None:
                if monster.avatar == 'A':
                    return len(search)
                return len(search)
            return float('-inf')
        monsters = sorted(monsters, key = sortValue)
        return monsters
    
    def getAllMonstersInWorld(self, char, wrld):
        ret = []
        for i in range(0,8):
            for j in range(0,19):
                chars = wrld.monsters_at(i, j)
                if not chars == None:
                    ret += chars
        return self.sortMonstersByDistance(char, ret, wrld)
            
    
    def getNewWorld(self, char, wrld, action):
        newWorld = SensedWorld.from_world(wrld)
        newChar = self.getCharInWorld(newWorld)
        actionVector = self.getActionVector(action)
        newChar.x += actionVector[0]
        newChar.y += actionVector[1]
        return newWorld
            
    
    def generateCharMoveWorlds(self, char, wrld):
        ret = []
        allActions = self.getAllActions(wrld, char.x, char.y)
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
        for dx in range(-8, 8):
            # Avoid out-of-bounds access
            if ((monster.x + dx >= 0) and (monster.x + dx < wrld.width())):
                for dy in range(-19, 19):
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
        return [wrld]
        #monster = self.getAllMonstersInWorld(wrld)[0]
        #monsterMoves = self.getMonsterMoves(monster, wrld)
        #for i in monsterMoves:
        #    newWorld = SensedWorld.from_world(wrld)
        #    newMonster = self.getAllMonstersInWorld(newWorld)[0]
        #    newMonster.x += i[0]
        #    newMonster.y += i[1]
        #    ret.append(newWorld)
        #return ret
    
    def isMonsterXAway(self, char, wrld, x):
        for i in range(-x, x):
            for j in range(-x, x):
                if wrld.monsters_at(char.x+i, char.y+j):
                    search = self.doSearch(wrld, char, char.x+i, char.y+j)
                    if not search == None and len(search) <= x:
                        return True
        return False
        
    
    def ExpectimaxSearch(self, wrld, depth, state):
        maxVal = float('-inf')
        # alpha = float('-inf')
        # beta = float('inf')
        maxAction = -1
        newWorlds = self.generateCharMoveWorlds(self, wrld)
        for i in newWorlds:
            char = self.getCharInWorld(wrld)
            newVal = self.ExpValue(i[0], depth, state)
            if maxVal < newVal:
                maxVal = newVal
                maxAction = i[1]
        print(maxVal)
        return maxAction
    
    def willBeInBlast(self, wrld, x, y, timer):
        if self.bombActive == True and self.bombTimer + timer >= 9:
            if (x == self.bombX and (x-self.bombX <= 5 and x-self.bombX >= -5)) or (y == self.bombY and (y-self.bombY <= 5 and y-self.bombY >= -5)):
                return True
        return False
    
    def ExpValue(self, wrld, depth, state):
        monMoves = None
        char = self.getCharInWorld(wrld)
        if len(self.getAllMonstersInWorld(char, wrld)) == 0:
            monMoves = [wrld]
        else:
            monMoves = self.generateMonsterMoveWorlds(wrld)
        char = self.getCharInWorld(wrld)
        if wrld.exit_at(char.x, char.y):
            return 50000000000000000
        if self.isMonsterXAway(char, wrld, 3-depth):
            return -50000000000000000*depth
        #if not wrld.monsters_at(char.x, char.y) == None:
            #return -50000000000000000
        #if wrld.explosion_at(char.x, char.y):
            #return -50000000000000000
        #if self.willBeInBlast(wrld, char.x, char.y, 3-depth):
            #return -500000000000000000
        v = 0
        totalProb = 0
        for i in monMoves:
            p = 1/len(monMoves)
            v = v + p*self.MaxValue(i, depth-1, state)
            totalProb += p
            # if beta < v:
            #     beta = v
            # if not totalProb == 1 and v + 50*(1/totalProb) <= alpha:
            #     return v
        return v
    
    def MaxValue(self, wrld, depth, state):
        char = self.getCharInWorld(wrld)
        #if wrld.exit_at(char.x, char.y):
            #return 50000000000000000
        #if not wrld.monsters_at(char.x, char.y) == None:
            #return -5000000000000000
        if depth <= 0:
            if state == 0:
                search = self.doSearch(wrld, char, 7, 18)
                if search == None:
                    return 0
                return 100/len(self.doSearch(wrld, char, 7, 18))
            else:
                monPos = self.getMonsterPos(wrld, char)
                print(monPos)
                search = self.doSearch(wrld, char, monPos[0], monPos[1])
                if search == None:
                    return 10*((char.x - monPos[0])*(char.x - monPos[0]) + (char.y - monPos[1])*(char.y - monPos[1]))
                return -100/len(self.doSearch(wrld, char, monPos[0], monPos[1])) + 10*((char.x - monPos[0])*(char.x - monPos[0]) + (char.y - monPos[1])*(char.y - monPos[1]))
        maxVal = float('-inf')
        maxAction = -1
        newWorlds = self.generateCharMoveWorlds(char, wrld)
        for i in newWorlds:
            newVal = self.ExpValue(i[0], depth, state)
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
                    copyList = json.loads(json.dumps(current[2]))
                    copyList.append((dx, dy))
                    retList.append((current[0]+dx, current[1]+dy, copyList))
        return retList
    
    def getPos(self, current):
        return (current[0], current[1])
        


            
    def doSearch(self, wrld, char, x, y):
        frontier = PriorityQueue()
        frontier.put((0, (char.x, char.y, [])))
        came_from = {}
        cost_so_far = {}
        came_from[(char.x, char.y)] = None
        cost_so_far[(char.x, char.y)] = 0

        while not frontier.empty():
            current = frontier.get()[1]
            if current[0] == x and current[1] == y:
                if len(current[2]) == 0:
                    return [(0, 0)]
                return current[2]
            for next in self.getNeighbors(current, wrld):
                extracost = 1
                if wrld.wall_at(self.getPos(next)[0], self.getPos(next)[1]):
                    extracost = 100
                new_cost = cost_so_far[self.getPos(current)] + extracost
                if self.getPos(next) not in cost_so_far or new_cost < cost_so_far[self.getPos(next)]:
                    cost_so_far[self.getPos(next)] = new_cost
                    priority = new_cost + math.sqrt((x - next[0])*(x - next[0]) + (y - next[1])*(y - next[1]))
                    frontier.put((priority, next))
                    came_from[self.getPos(next)] = current
        #return [(0, 0)]


                
    def getMonsterPos(self, wrld, char):
        monsters = self.getAllMonstersInWorld(char, wrld)
        if len(monsters) == 0:
            return (0,0)
        return(monsters[0].x, monsters[0].y)
    
    def getDenom(self, num):
        if not num == 0:
            return abs(num)
        return 1
    
    
    def do(self, wrld):
        if self.state == 0: #exploring
            if self.isMonsterXAway(self, wrld, 5): #if close to monster, place bomb because scared
                self.state = 1
                self.place_bomb()
                self.bombTimer = 0
                self.bombActive = 1
                self.bombX = self.x
                self.bombY = self.y
            else: #otherwise explore
                search = self.doSearch(wrld, self, 7, 18)
                yVal = 18
                while search == None:
                    yVal -= 1;
                    search = self.doSearch(wrld, self, 1, yVal)
                self.move(search[0][0], search[0][1])
                if search == [(0,0)]:
                    self.state = 1
                    self.place_bomb()
                    self.bombTimer = 0
                    self.bombActive = 1
                    self.bombX = self.x
                    self.bombY = self.y
                        
        if self.state == 1: #if scared run away until bomb explodes
            action = self.ExpectimaxSearch(wrld, 2, self.state)
            actionVector = self.getActionVector(action)
            self.move(actionVector[0], actionVector[1])
            self.bombTimer += 1
            if self.bombTimer > 14:
                self.state = 0
                self.bombActive = 0
        pass
