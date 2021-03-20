# This is necessary to find the main code
import sys
#from ../estCharacter import
sys.path.insert(0, '../../bomberman')
sys.path.insert(1, '..')

# Import necessary stuff
from game import Game

# TODO This is your code!
sys.path.insert(1, '../group18')

# Uncomment this if you want the empty test character
from variant1Char import TestCharacter

# Uncomment this if you want the interactive character
from interactivecharacter import InteractiveCharacter

# Create the game
g = Game.fromfile('map.txt')

# TODO Add your character

# Uncomment this if you want the test character

g.add_character(TestCharacter("me", # name
                               "C",  # avatar
                               0, 0  # position
 ).kindaInit())

# Uncomment this if you want the interactive character
#g.add_character(InteractiveCharacter("me", # name
#                                     "C",  # avatar
#                                     0, 0  # position
#))

# Run!

# Use this if you want to press ENTER to continue at each step
# g.go(0)

# Use this if you want to proceed automatically
g.go(1)