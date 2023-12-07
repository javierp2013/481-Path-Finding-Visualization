# This is the game objects file

import os
import warnings
import pygame
import math
import time
import pygame.font
from videogame import rgbcolors
from queue import PriorityQueue
from enum import Enum

# Following basic format for boilerplate code in CPSC 386
# TODO: Maybe move these functions into the VideoGame class?
# Create the board and populate arrays with designated Node objects
# Strategy for creating grid/board referenced here:
# http://programarcadegames.com/index.php?lang=en&chapter=array_backed_grids 
MARGIN =20


class Algorithm(Enum):
    MANHATTAN = 0
    EUCLIDEAN = 1
    CHEBYSHEV = 2


def increment_enum(value):
    members = list(Algorithm)
    index = members.index(value)
    next_index = (index + 1) % len(members)  # Wrap around if it reaches the end
    return members[next_index]


def create_board(rows, width):
        board = []
        #determine the nearest whole number for space between nodes
        space = math.floor((width-(MARGIN*2))/ rows)
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
    space = math.floor((width-(MARGIN*2))/ rows)
    
    Offset = MARGIN-1
    for row in range(rows+1):
        #draw a horizontal line with thickness of space
        pygame.draw.line(window, rgbcolors.blueviolet, (Offset, Offset+(row * space)), (width-Offset-2, Offset+(row * space)))
        for col in range(rows+1):
            #draw a vertical line with thickness of space
            pygame.draw.line(window, rgbcolors.blueviolet, (Offset+(col * space), Offset), (Offset+(col * space), width-Offset-2))

# Draw each node to screen!
def draw(window, board, rows, width):
    window.fill(rgbcolors.black)
    for row in board:
        for node in row:
            node.draw(window)
    draw_board(rows, width, window)
    pygame.display.update()

#simple mouse position retrieval courtesy of pygame docs.
def getMouse(mousePos, rows, width):
    yPos, xPos = mousePos
    space = math.floor((width-(MARGIN*2)) / rows)
    print(space)
    if MARGIN is 0:
        return math.floor(yPos / space), math.floor(xPos / space)
    else: 
        return math.floor(yPos / space)-1, math.floor(xPos / space)-1
    
#Heuristic functions
def manhattanDistance(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

def euclideanDistance(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

def chebyshevDistance(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return max(abs(x1 - x2), abs(y1 - y2))


def colorFinalPath(previous, currNode, draw):
    ##go backwards through previous list and color it to make final path.
    while currNode in previous:
        currNode = previous[currNode]
        currNode.definePath()
        draw()

#A star algorithm modified from example from lecture and wikipedia implementation in python
def astarRun(draw, board, beginning, end, distance=Algorithm.MANHATTAN):
    count = 0
    #setup frontier priorityqueue to keep open nodes
    frontier = PriorityQueue()
    frontier.put((0, count, beginning))
    #initialize the pathcost for each path to infinity so that it is overwritten with heuristic cost later.
    pathCost = {node: float("inf") for row in board for node in row}
    pathCost[beginning] = 0
    heuristic = {node: float("inf") for row in board for node in row}
    heuristic[beginning] = manhattanDistance(beginning.getPos(), end.getPos())
    previous = {}
    #keep track of items in priority queue
    frontier_hash = {beginning}
    distanceFunction = None
    #switch between heuristic types
    if distance==Algorithm.MANHATTAN:
        distanceFunction = manhattanDistance 
    elif distance==Algorithm.EUCLIDEAN:
        distanceFunction = euclideanDistance
    elif distance== Algorithm.CHEBYSHEV:
        distanceFunction = chebyshevDistance
    #redo the beginning heuristic in case the option changed
    heuristic[beginning] = distanceFunction(beginning.getPos(), end.getPos())
    #while there are still nodes in frontier, keep running
    while not frontier.empty():
        #2 gets the node since its the 3rd item in that set, preceded by heuristic and count            
        currNode = frontier.get()[2]
        #its no longer in the frontier so it needs to be removed.
        frontier_hash.remove(currNode)
        #we're done and can now draw the final path
        if currNode == end:
            colorFinalPath(previous, end, draw)
            end.defineEnd()
            return True
        #go through all adjacent nodes and determine if its a better path in terms of cost
        for adjacent in currNode.adjacents:
            #since we are moving only one node ahead, we can add 1 to pathcost.
            temp_pathCost = pathCost[currNode] + 1
            #if this currNode pathcost is smaller than the adjacents, make this the path we choose
            if temp_pathCost < pathCost[adjacent]:
                previous[adjacent] = currNode
                pathCost[adjacent] = temp_pathCost
                heuristic[adjacent] = temp_pathCost + distanceFunction(adjacent.getPos(), end.getPos())		
                #if adjacent node is not in frontier, add it with order.		
                if adjacent not in frontier_hash:
                    count += 1
                    #add 1 to count and then add count to it
                    #this prioritizes exploring nodes that were added earlier in the run
                    #it gives it a smaller heuristic score because it was added when count was lower.
                    frontier.put((heuristic[adjacent], count, adjacent))
                    frontier_hash.add(adjacent)
                    adjacent.open()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
        draw()
        #make sure not to recolor the beginning node.
        if currNode != beginning:
            currNode.close()

    return False






class VideoGame:
    """Base class for creating PyGame games."""
    def __init__(
        self, window_width=800, window_height=800, window_title="A* Pathfinding Visualization"
    ):
        """Initialize a new game with the given window size and window title."""
        # Borrowed from previous class project.
        pygame.init()
        pygame.font.init()
        self.duration_text = None
        self.font = pygame.font.SysFont('Arial', 20)
        #used to switch between heurstics 
       # self.distance_method = "manhattan"
        self.distance_method = Algorithm.MANHATTAN
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
        beginning = None
        end = None
        while True:
            draw(window, board, row_num, width)
            
            #Input
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                #Left mouse click
                if pygame.mouse.get_pressed()[0]:
                    pos = pygame.mouse.get_pos()
                    row, col = getMouse(pos, row_num, width)
                    #debugging info about node position when clicked
                    if(row==-1 or col==-1 or row>len(board)-1 or col>len(board[0])-1):
                        break
                    print(row, col)
                    node = board[row][col]
                    #if beginning is undefined, set the current clicked node as beginning
                    if not beginning:
                        beginning = node
                        beginning.defineBeginning()
                    #if end is undefined, and node is not the beginning, set the current clicked node as end
                    elif not end and node != beginning:
                        end = node
                        end.defineEnd()
                    #now that both prev are defined, make all proceeding clicks into walls.
                    elif node != end and node != beginning:
                        node.defineWall()
                        node.defineTag("wall")
                
                if event.type == pygame.KEYDOWN:
                    #Pressing the D Key switches between manhattan and euclidean 
                    if event.key == pygame.K_d:
                        self.distance_method=increment_enum(self.distance_method)
                  
                    #only run if the beginning and end are defined.
                    if event.key == pygame.K_SPACE and beginning and end:
                        start_time = time.time()
                        for row in board:
                            for node in row:
                                node.defineAdjacents(board)
                                if node != beginning and node !=end and node.tag!="wall":
                                     node.color = rgbcolors.wheat
                        pathFound=astarRun(lambda: draw(window, board, row_num, width), board, beginning, end, distance=self.distance_method)
                        ##timer to keep track of the time it takes for path to be found.
                        duration = time.time() - start_time
                        if pathFound:
                            self.duration_text = f"Pathfinding Algorithm took {duration:.2f} seconds"
                        else:
                            self.duration_text = "No valid path found!"

                #draw(window, board, row_num, width) 
                        
                
            #draws the timer onto screen    
            if self.duration_text:
                text_surface = self.font.render(self.duration_text, True, rgbcolors.red)
                window.blit(text_surface, (0,0))    
            ##draws the selected distance method to screen.
            if self.distance_method:
                algorithm_text = f"Current Algorithm: {self.distance_method.name}"
                text_surface = self.font.render(algorithm_text, True, rgbcolors.red)
                window.blit(text_surface, (width-300,0))    
                
            pygame.display.update()    

#Node class, represented by a square on the screen
class Node:
    def __init__(self,total,width,row,column):
        
        self.x_pos = width * row
        self.y_pos = width * column
        
        if MARGIN is not 0:            
            self.x_pos = width * (row+1)
            self.y_pos = width * (column+1)
        #Boilerplate attributes to keep track of location, color, and adjacents.
        self.width = width
        self.color = rgbcolors.wheat
        self.row_total = total
        self.row = row
        self.col = column
        self.adjacents = []
        self.tag="empty"

    
    def draw(self, window):
        pygame.draw.rect(window, self.color, (self.x_pos, self.y_pos, self.width, self.width))
            
    
    def defineTag(self, tag_type):
        self.tag = tag_type
    #changes color of node depending on what kind of node it is.   
    def defineBeginning(self):
        self.color = rgbcolors.azure4
    def defineEnd(self):
        self.color = rgbcolors.purple
    def defineWall(self):
        self.color = rgbcolors.dark_red
    def isWall(self):
        return self.color == rgbcolors.dark_red
    def definePath(self):
         self.color = rgbcolors.green4
    
    
        #fills out the adjacents for each node
        #adapted from grid traversal article on geeksforgeeks.
    def defineAdjacents(self, board):
        self.adjacents = []
        #checks adjacent to the north
        if self.row > 0 and not board[self.row - 1][self.col].isWall():
            self.adjacents.append(board[self.row - 1][self.col])
        #south
        if self.row < self.row_total - 1 and not board[self.row + 1][self.col].isWall():
            self.adjacents.append(board[self.row + 1][self.col])
        #left
        if self.col > 0 and not board[self.row][self.col - 1].isWall():
            self.adjacents.append(board[self.row][self.col - 1])
        #right
        if self.col < self.row_total - 1 and not board[self.row][self.col + 1].isWall():
            self.adjacents.append(board[self.row][self.col + 1])
    #simple fuctions that return position. open/close nodes as well as return bools.
    def getPos(self):
         return self.row, self.col
    def open(self):
         self.color = rgbcolors.aquamarine
    def isOpen(self):
         return self.color == rgbcolors.aquamarine
    def close(self):
         self.color = rgbcolors.black
    def isClosed(self):
        return self.color == rgbcolors.black

