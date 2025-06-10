import pygame, math, time
from pygame.locals import *
from pygame import gfxdraw

from data.scripts.res import *
from data.scripts.linalg import *

pygame.mixer.init()

# Loading resources

def load_image(path: str):
    return pygame.image.load(resource_path("images/" + path)).convert_alpha()

def load_font(path: str, size: int):
    return pygame.font.Font(resource_path("fonts/" + path), size)

def load_sfx(path: str, volume: float = None):
    sound = pygame.mixer.Sound(resource_path("sounds/sfx/" + path))
    if volume != None: sound.set_volume(volume)
    return sound

def load_music(path: str):
    pygame.mixer.music.load(resource_path("sounds/music/" + path))


# Labels

def font_surface(text: str, color: tuple, font: pygame.font.Font, antialias: bool = True):
    return font.render(text, True, color)


# Cursors

def change_cursor(cursor: pygame.cursors.Cursor):
    pygame.mouse.set_cursor(cursor)


# Empty Surface
    
def empty_surface(size: tuple):
    return pygame.Surface(size, SRCALPHA).convert_alpha()


# Debug

pygame.font.init()
debugFont = pygame.font.Font(None, 24)

def pygame_debug(surface: pygame.Surface, position: tuple, text: str, color: tuple = (255, 0, 0)):
    label = font_surface(text, color, debugFont)
    surface.blit(label, position)


# blitPlus

# How to use:
#
# Values is a 4-parameter tuple.
# Parameter 0: X value of the background surface to blit onto
# Parameter 1: Y value of the background surface to blit onto
# Parameter 2: X value of the image surface to blit from
# Parameter 3: Y value of the image surface to blit from
#
# Modes is a 4-parameter tuple. 
# Parameter 0: Mode for translating the background surface X value
# Parameter 1: Mode for translating the background surface Y value
# Parameter 2: Mode for translating the image surface X value
# Parameter 3: Mode for translating the image surface Y value
#
# Each of the modes can be 0, 1, or 2.
# Mode 0: The corresponding value is the distance in pixels from the left/top of the surface.
# Mode 1: The corresponding value is the distance in pixels from the right/bottom of the surface.
# Mode 2: The corresponding value is the percentage across the surfaces width/height span from which to blit.
#
# For example, if you wanted to blit a small box on the bottom right corner of a background with a padding of
# 10 pixels, your modes would be (1, 1, 2, 2), and your values would be (10, 10, 1, 1).
#
# If you wanted to blit an image in the center of a background, your modes would be (2, 2, 2, 2), and your
# values would be (0.5, 0.5, 0.5, 0.5).
#
# Fractional coordinates are rounded.
#
# In the rotated version, all values are still based on the unrotated image's size.

def blit_plus(image: pygame.Surface, background: pygame.Surface, modes: tuple = (0, 0, 0, 0), values: tuple = (0, 0, 0, 0)):
    
    left, top, right, bottom = blit_plus_helper(image, background, modes, values)

    background.blit(image, (round(left - right), round(top - bottom)))

def blit_plus_rotate(image: pygame.Surface, background: pygame.Surface, modes: tuple = (0, 0, 0, 0), values: tuple = (0, 0, 0, 0), rotation: float = 0):

    left, top, right, bottom = blit_plus_helper(image, background, modes, values)

    t0 = time.perf_counter()

    rotatedImage = pygame.transform.rotate(image, rotation * 180 / math.pi)

    t1 = time.perf_counter()
    print("Rotozoom took {} seconds.".format(t1 - t0))

    left -= (rotatedImage.get_width() - image.get_width()) / 2
    top -= (rotatedImage.get_height() - image.get_height()) / 2

    t2 = time.perf_counter()
    print("Getting dimensions took {} second.".format(t2 - t1))

    background.blit(rotatedImage, (round(left - right), round(top - bottom)))

    t3 = time.perf_counter()
    print("Blitting took {} seconds.".format(t3 - t2))

def blit_plus_helper(image: pygame.Surface, background: pygame.Surface, modes: tuple = (0, 0, 0, 0), values: tuple = (0, 0, 0, 0)):
    
    left, top, right, bottom = 0, 0, 0, 0

    if modes[0] == 0: left = values[0]
    elif modes[0] == 1: left = background.get_width() - values[0]
    elif modes[0] == 2: left = background.get_width() * values[0]

    if modes[1] == 0: top = values[1]
    elif modes[1] == 1: top = background.get_height() - values[1]
    elif modes[1] == 2: top = background.get_height() * values[1]

    if modes[2] == 0: right = values[2]
    elif modes[2] == 1: right = image.get_width() - values[2]
    elif modes[2] == 2: right = image.get_width() * values[2]

    if modes[3] == 0: bottom = values[3]
    elif modes[3] == 1: bottom = image.get_height() - values[3]
    elif modes[3] == 2: bottom = image.get_height() * values[3]

    return left, top, right, bottom


# Colors

def color_multiply(color: pygame.Color, factor: float):
    return pygame.Color([color[c] * factor if c < 3 else color[c] for c in range(len(color))])

def color_lighten(color: pygame.Color, factor: float):
    return pygame.Color([color[c] + (255 - color[c]) * factor if c < 3 else color[c] for c in range(len(color))])

def color_add_white(color: pygame.Color, amount: int):
    return pygame.Color([min(color[c] + amount, 255) for c in range(len(color))])

def image_blend_add(surface: pygame.Surface, color: pygame.Color):
    if not surface: return None
    new_surface = surface.copy().convert_alpha()
    new_surface.fill(color, special_flags=pygame.BLEND_RGB_ADD)
    return new_surface

def image_blend_sub(surface: pygame.Surface, color: pygame.Color):
    if not surface: return None
    new_surface = surface.copy().convert_alpha()
    new_surface.fill(color, special_flags=pygame.BLEND_RGB_SUB)
    return new_surface


# Rects

def shrink_rect(rect: pygame.Rect, amount: int):
    return pygame.Rect(rect.left + amount, rect.top + amount, rect.width - amount * 2, rect.height - amount * 2)


# Anchors

class Anchor:
    def __init__(self, apx, acx, apy, acy):
        self.apx = clamp(apx, 0, 1)
        self.acx = clamp(acx, 0, 1)
        self.apy = clamp(apy, 0, 1)
        self.acy = clamp(acy, 0, 1)

        # Anchor-parent-x: The fractional distance along the parent's width at which the child is anchored
        # Anchor-child-x: The fractional distance along the child's width at which the child is anchored
        # Anchor-parent-y: The fractional distance along the parent's height at which the child is anchored
        # Anchor-child-y: The fractional distance along the child's height at which the child is anchored

    def print(self): return f"({self.apx}, {self.acx}, {self.apy}, {self.acy})"

def delocalize_position_x(pw: float, cw: float, anchor: Anchor, px: float = 0, cx: float = 0):
    return lerpFloat(px, px + pw, anchor.apx) - cw * anchor.acx + cx

def delocalize_position_y(ph: float, ch: float, anchor: Anchor, py: float = 0, cy: float = 0):
    return lerpFloat(py, py + ph, anchor.apy) - ch * anchor.acy + cy

def delocalize_position(pw: float, ph: float, cw: float, ch: float, anchor: Anchor, px: float = 0, py: float = 0, cx: float = 0, cy: float = 0):
    return (lerpFloat(px, px + pw, anchor.apx) - cw * anchor.acx + cx,
            lerpFloat(py, py + ph, anchor.apy) - ch * anchor.acy + cy)