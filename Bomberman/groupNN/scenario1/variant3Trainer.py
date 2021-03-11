# This is necessary to find the main code
import sys
import numpy as np
sys.path.insert(0, '../../bomberman')
sys.path.insert(1, '..')

# Import necessary stuff
import random
import pygame
from game import Game
from monsters.selfpreserving_monster import SelfPreservingMonster

# TODO This is your code!
sys.path.insert(1, '../groupNN')
from testcharacter import TestCharacter

from variant3Char import TestCharacter

# Create the game
random.seed(4444777) # TODO Change this if you want different random choices
alpha = 0.75
gama = 0.9
def updateQ(oldChar, newChar, action, reward):
    for key in oldChar.keys(): #for every state type
        maxVal = float('-inf') #get the max value you can have given your new state for this state type
        for a in range(0, len(newChar.actions)):
            if maxVal < newChar.states[key].table[newChar.states[key].currentVal][a]:
                maxVal = newChar.states[key].table[newChar.states[key].currentVal][a]
        #update qTable for this state type
        newChar.states[key].table[oldChar[key].currentVal][action] = newChar.states[key].table[oldChar[key].currentVal][action] + alpha(reward + gama*maxVal - newChar.states[key].table[oldChar[key].currentVal][action])
        maxVal = float('-inf') # get the max q value you can have given the new total state
        for a in range(0, len(newChar.actions)):
            curQ = qValOfAction(newChar.states, a)
            if maxVal < curQ:
                maxVal = curQ
        delta = (reward + gama*maxVal) - qValOfAction(oldChar, action)
        #update state type's weight
        newChar.states[key].weight = newChar.states[key].weight + alpha*delta*oldChar[key].table[oldChar[key].currentVal][action] 
    return newChar

def qValOfAction(char, action):
    total = 0
    for key in oldChar.keys():
        total = total + char[key].table[char[key].currentVal][action]*char[key].weight
    return total
        

def bestQOfAll(oldChar):
    maxVal = float('-inf')
    bestAction = -1
    for a in range(0, len(oldChar.actions)):
        newVal = qValOfAction(oldChar.states, a)
        if maxVal < newVal:
            bestAction = a
            maxVal = newVal
    return a

def chooseAction(oldChar, epsilon):
    if random.random() < epsilon:
        return random.randint(0, len(oldChar.actions))
    return bestQOfAll(oldChar)

def doAction(char, action):
    actionName = char.actions[action]
    if actionName == "Down":
        char.move(0, 1)
    elif actionName == "DownRight":
        char.move(1, 1)
    elif actionName == "Right":
        char.move(1, 0)
    elif actionName == "UpRight":
        char.move(1,-1)
    elif actionName == "Up":
        char.move(0, -1)
    elif actionName == "UpLeft":
        char.move(-1, -1)
    elif actionName == "Left":
        char.move(-1, 0)
    elif actionName == "LeftDown":
        char.move(-1, 1)

def takeTurn(game, char, epsilon):
    action = chooseAction(char, epsilon)
    oldCharStates = copy.deepcopy(char.states)
    doAction(char, action)
    (game.world, game.events) = game.world.next()
    #game.display_gui()
    game.draw()
    #step()
    game.world.next_decisions()
    char.getState(game.world)
    reward = -1
    for e in game.world.events:
        if e.tpe == Event.BOMB_HIT_WALL:
            reward = reward + 10
        elif e.tpe == Event.BOMB_HIT_MONSTER:
            reward = reward + 50
        elif e.tpe == Event.BOMB_HIT_CHARACTER:
            reward = reward - 100
        elif e.tpe == Event.CHARACTER_KILLED_BY_MONSTER:
            reward = reward - 100
        elif e.tpe == Event.CHARACTER_FOUND_EXIT:
            reward = reward + 1000
    updateQ(oldCharStates, char, action, reward)

def runSimulation():
    char = TestCharacter("me", # name
                               "C",  # avatar
                               0, 0  # position
    ).kindaInit()
    #char.states = loadFromFile("variant3Char.json")

    g = Game.fromfile('map.txt')
    g.add_monster(SelfPreservingMonster("selfpreserving", # name
                                    "S",              # avatar
                                    3, 9,             # position
                                    1                 # detection range
    ))
    char.getState(g.world)
    g.add_character(char)
    epsilon = 0.8
    while not g.done():
        takeTurn(g, char, epsilon)
        epsilon = 0.9*epsilon
    saveToFile(char, "variant3Char.json")
    

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


runSimulation();