#! /usr/bin/env python3
# This program is the entry point for our pygame A* visualizer

import sys
import videogame.game
import pygame

if __name__ == "__main__":
    window_width = 800
    window_surface = pygame.display.set_mode((window_width, window_width))
    CURR_GAME = videogame.game.VideoGame()
    CURR_GAME.run(window_surface, window_width)
    sys.exit(0)