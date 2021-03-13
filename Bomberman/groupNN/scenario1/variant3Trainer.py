# This is necessary to find the main code
import sys
import numpy as np
sys.path.insert(0, '../../bomberman')
sys.path.insert(1, '..')

# Import necessary stuff
import random
import copy
import pygame
import json
import time
import math
from game import Game
from events import Event
from monsters.selfpreserving_monster import SelfPreservingMonster

# TODO This is your code!
sys.path.insert(1, '../groupNN')
from testcharacter import TestCharacter

from variant3Char import TestCharacter

# Create the game
random.seed(54345345) # TODO Change this if you want different random choices
alpha = 0.7
gama = 0.9
first = False
def updateQ(oldChar, newChar, action, reward):
    global first
    for key in oldChar.keys(): #for every state type
        maxVal = float('-inf') #get the max value you can have given your new state for this state type
        for a in range(0, len(newChar.actions)):
            newVal = qValOfAction(newChar.states, action)
            if maxVal < newVal:
                maxVal = newVal
            #if maxVal < newChar.states[key]['table'][newChar.states[key]['currentVal']][a]:
                #maxVal = newChar.states[key]['table'][newChar.states[key]['currentVal']][a]
        #update qTable for this state type
        newChar.states[key]['table'][oldChar[key]['currentVal']][action] = newChar.states[key]['table'][oldChar[key]['currentVal']][action] + alpha*(reward + gama*maxVal - newChar.states[key]['table'][oldChar[key]['currentVal']][action])
        #newChar.states[key]['table'][oldChar[key]['currentVal']][action] = newChar.states[key]['table'][oldChar[key]['currentVal']][action] + alpha*(reward + gama*maxVal - newChar.states[key]['table'][oldChar[key]['currentVal']][action])
        maxVal = float('-inf') # get the max q value you can have given the new total state
        for a in range(0, len(newChar.actions)):
            curQ = qValOfAction(newChar.states, a)
            if math.isinf(curQ):
                print("action: ", a, "states: ", newChar.states)
            if maxVal < curQ:
                maxVal = curQ
        delta1 = (reward + gama*maxVal)
        delta2 = qValOfAction(oldChar, action)
        delta = delta1 - delta2
        #update state type's weight
        newChar.states[key]["weight"] = newChar.states[key]["weight"] + alpha*delta*oldChar[key]['table'][oldChar[key]['currentVal']][action]
        if (math.isnan(newChar.states[key]["weight"]) or math.isinf(newChar.states[key]["weight"])) and not first:
            print("Delta: ", delta, " Delta1: ", delta1, " Delta2: ", delta2, " MaxVal: ", maxVal)
            first = True
        if newChar.states[key]["weight"] < 0.01:
            newChar.states[key]["weight"] = 0.01
        if newChar.states[key]["weight"] > 10000:
            newChar.states[key]["weight"] = 10000
    print(newChar.states)  
    return newChar

def qValOfAction(char, action):
    total = 0
    weightTotal = 1
    for key in char.keys():
        total = total + char[key]['table'][char[key]['currentVal']][action]*char[key]["weight"]
        weightTotal = weightTotal + char[key]["weight"]
    return total/weightTotal
        

def bestQOfAll(oldChar, allActions):
    maxVal = float('-inf')
    bestAction = -1
    for b in range(0, len(allActions)-1):
        a = allActions[b]
        newVal = qValOfAction(oldChar.states, a)
        if maxVal < newVal:
            bestAction = a
            maxVal = newVal
    return a

def chooseAction(oldChar, epsilon, wrld):
    allActions = oldChar.getAllActions(wrld)
    if random.random() < epsilon:
        return allActions[random.randint(0, len(allActions)-1)]
    return bestQOfAll(oldChar, allActions)

def doAction(char, action):
    actionName = char.actions[action]
    if action == 0: #Down
        char.move(0, 1)
    elif action == 1: #DownRight
        char.move(1, 1)
    elif action == 2: #"Right":
        char.move(1, 0)
    elif action == 3: #"UpRight":
        char.move(1,-1)
    elif action == 4: #"Up":
        char.move(0, -1)
    elif action == 5: #"UpLeft":
        char.move(-1, -1)
    elif action == 6: #"Left":
        char.move(-1, 0)
    elif action == 7:#"LeftDown":
        char.move(-1, 1)
    else:
        print("YO NO ACTION WAS SELECTED")

def takeTurn(game, char, epsilon):
    oldPath = char.doSearch(game.world, 7, 18)
    action = chooseAction(char, epsilon, game.world)
    oldCharStates = copy.deepcopy(char.states)
    doAction(char, action)
    (game.world, game.events) = game.world.next()
    game.display_gui()
    #game.draw()
    #step()
    game.world.next_decisions()
    char.getState(game.world)
    reward = -1
    path = char.doSearch(game.world, 7, 18)

    
    for e in game.world.events:
        if e.tpe == Event.BOMB_HIT_WALL:
            reward = reward + 10
            print("other")
        elif e.tpe == Event.BOMB_HIT_MONSTER:
            reward = reward + 50
            print("other")
        elif e.tpe == Event.BOMB_HIT_CHARACTER:
            reward = reward - 100
            print("other")
        elif e.tpe == Event.CHARACTER_KILLED_BY_MONSTER:
            reward = reward - 100
            print("oof death")
        elif e.tpe == Event.CHARACTER_FOUND_EXIT:
            reward = reward + 1000000
            print("pog exit was found")
    #time.sleep(0.05)
    char.states = updateQ(oldCharStates, char, action, reward).states
    


def runSimulation(epsilon, statesSave):
    
    #char.states = loadFromFile("variant3Char.json")

    g = Game.fromfile('map.txt')
    #g.add_monster(SelfPreservingMonster("selfpreserving", # name
    #                                "S",              # avatar
    #                                0, 0,             # position
    #                                1                 # detection range
    #))
    x = random.randint(0, 6)
    y = random.randint(0, 17)
    while not g.world.empty_at(x, y):
        x = random.randint(0, 6)
        y = random.randint(0, 17)
    char = TestCharacter("me", # name
                               "C",  # avatar
                               x, y  # position
    ).kindaInit()
    if statesSave != None:
        char.states = statesSave
    char.getState(g.world)
    #print(statesSave)
    g.add_character(char)
    while not g.done():
        takeTurn(g, char, epsilon)
    return char.states
    #saveToFile(char, "variant3Char.json")


def runLotsOfSimulations():
    statesSave = None;
    epsilon = 0.99
    for i in range(10000):
        statesSave = runSimulation(epsilon, statesSave)
        epsilon = 0.95*epsilon
        
    

def saveToFile(char, fileLoc):
    with open(fileLoc, 'w') as outfile:
        json.dump(char.states, outfile)

def loadFromFile(fileLoc):
    char = TestCharacter("me", # name
                               "C",  # avatar
                               0, 0  # position
                               ).kindaInit()
    with open(fileLoc) as json_file:
        char.states = json.load(json_file)
    return char


runLotsOfSimulations();