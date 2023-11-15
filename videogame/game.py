# This is the game objects file

import os
import warnings
import pygame
import math

from videogame import rgbcolors

# Following basic format for boilerplate code in CPSC 386
# TODO: Maybe move these functions into the VideoGame class?
# Create the board and populate arrays with designated Node objects
# Strategy for creating grid referenced here: http://programarcadegames.com/index.php?lang=en&chapter=array_backed_grids 
def create_board(rows, width):
        board = []
        #determine the nearest whole number for space between nodes
        space = math.floor(width / rows)
        #Python equivalent of foreach()
        for row in range(rows):
            board.append([])
            for col in range(rows):
                node = Node(rows, space, row, col)
                board[row].append(node)
        return board

# Use board from previous function to draw to screen using pygame
def draw_board(rows, width, window):
    #determine the nearest whole number for space between nodes
    space = math.floor(width / rows)
    for row in range(rows):
        #draw a horizontal line with thickness of space
        pygame.draw.line(window, rgbcolors.blueviolet, (0, row * space), (width, row * space))
        for col in range(rows):
            #draw a vertical line with thickness of space
            pygame.draw.line(window, rgbcolors.blueviolet, (col * space, 0), (col * space, width))

# Draw each node to screen!
def draw(window, grid, rows, width):
    window.fill(rgbcolors.ghost_white)
    for row in grid:
        for node in row:
            node.draw(window)
    draw_board(rows, width, window)
    pygame.display.update()

class VideoGame:
    """Base class for creating PyGame games."""
    def __init__(
        self, window_width=800, window_height=800, window_title="A* Pathfinding Visualization"
    ):
        """Initialize a new game with the given window size and window title."""
        # Borrowed from previous class project.
        pygame.init()
        self._window_size = (window_width, window_height)
        self._clock = pygame.time.Clock()
        self._screen = pygame.display.set_mode(self._window_size)
        self._title = window_title
        pygame.display.set_caption(self._title)
        self._game_is_over = False
        if not pygame.font:
            warnings.warn("Fonts disabled.", RuntimeWarning)
        if not pygame.mixer:
            warnings.warn("Sound disabled.", RuntimeWarning)
    
    def run(self, window, width):
        """Run the game; the main game loop."""
        row_num = 40
        board = create_board(row_num, width)
        while True:
            draw(window, board, row_num, width)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()



        

class Node:
    def __init__(self,total,width,row,column):
        
        self.x_pos = width * row
        self.y_pos = width * column
        self.width = width
        self.color = rgbcolors.wheat
        self.row_total = total
        self.row = row
        self.col = column
    
    def draw(self, window):
        pygame.draw.rect(window, self.color, (self.x_pos, self.y_pos, self.width, self.width))