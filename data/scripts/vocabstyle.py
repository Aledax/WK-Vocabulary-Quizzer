import pygame

from data.scripts.res import *
from data.scripts.pygametools import *

WINDOW_NAME = "WaniKani Auditory"
WINDOW_SIZE = (800, 555)

# Fonts

FONT = "K Gothic.ttf"
FONT_LARGE = load_font(FONT, 72)
FONT_MEDIUM = load_font(FONT, 48)
FONT_SMALL = load_font(FONT, 32)
FONT_TINY = load_font(FONT, 20)

# Colors

mode_colors = [pygame.Color("#00b1cc"), pygame.Color("#8800cc"), pygame.Color("#00cc44")]
COLOR_BG_MAIN = mode_colors[0]
# COLOR_BG_SECONDARY = pygame.Color("#009bb3")
COLOR_BG_SECONDARY = None
COLOR_FG_MAIN = pygame.Color("#ffffff")
# COLOR_FG_SECONDARY = pygame.Color("#40daf2")
COLOR_FG_SECONDARY = None

def change_color_scheme(bg_main: pygame.Color):
    global COLOR_BG_MAIN, COLOR_BG_SECONDARY, COLOR_FG_SECONDARY
    COLOR_BG_MAIN = bg_main
    COLOR_BG_SECONDARY = color_multiply(COLOR_BG_MAIN, 0.9)
    COLOR_FG_SECONDARY = color_lighten(COLOR_BG_MAIN, 0.3)

change_color_scheme(COLOR_BG_MAIN)

# Borders

BORDER_MAIN = 12
BORDER_SECONDARY = 4