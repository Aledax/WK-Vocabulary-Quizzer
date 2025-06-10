import pygame, sys, time, win32gui, win32con
from pygame.locals import *

from data.scripts.res import *
from data.scripts.pygametools import *
from data.scripts.pygameblock import *
from data.scripts.vocablayout import *
from data.scripts.vocabstyle import *

LEFT_MOUSE = 1
RIGHT_MOUSE = 2
APP_INPUT_FOCUS = 2

WINDOW_FPS = 60
WINDOW = pygame.display.set_mode(WINDOW_SIZE)

class App:
    def __init__(self):

        self.clock = pygame.time.Clock()
        self.window_surface = WINDOW
        pygame.display.set_caption(WINDOW_NAME)
        pygame.event.set_allowed([QUIT, MOUSEBUTTONDOWN, MOUSEBUTTONUP, KEYDOWN, KEYUP])

        self.previous_time = time.perf_counter()
        self.is_active = False

        self.layout = Layout()
        initiate_blocks(self.window_surface, COLOR_BG_MAIN)

        self.hwnd = pygame.display.get_wm_info()['window']

        self.loop()

    def loop(self):
        while True:
            # This is required in order for code execution to continue while dragging the window around.
            message_present, message = win32gui.PeekMessage(None, 0, 0, win32con.PM_REMOVE | win32con.PM_NOYIELD)
            if message_present:
                win32gui.TranslateMessage(message)
                win32gui.DispatchMessage(message)

            mouse_position = pygame.mouse.get_pos() if self.is_active else (-1, -1)
            mouse_clicked = False
            mouse_released = False
            key_events = []

            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == ACTIVEEVENT:
                    if event.state & APP_INPUT_FOCUS == APP_INPUT_FOCUS:
                        self.is_active = event.gain
                        if self.is_active:
                            render_all(self.window_surface, COLOR_BG_MAIN)
                elif event.type == MOUSEBUTTONDOWN:
                    if event.button == LEFT_MOUSE:
                        mouse_clicked = True
                        print("CLICKED " + str(mouse_position))
                elif event.type == MOUSEBUTTONUP:
                    if event.button == LEFT_MOUSE:
                        mouse_released = True
                elif event.type == KEYDOWN:
                    key_events.append(event)

            refresh_rects = render_upate_blocks(self.window_surface, IO_State(mouse_position, mouse_clicked, mouse_released, key_events))

            current_time = time.perf_counter()
            fps = 1.0 / (current_time - self.previous_time)
            # if fps < 60: print("LOW FPS!!! " + str(fps))
            self.previous_time = current_time

            pygame.display.update(refresh_rects)
            self.clock.tick(WINDOW_FPS)