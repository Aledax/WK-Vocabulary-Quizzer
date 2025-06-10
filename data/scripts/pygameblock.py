import pygame, time
from pygame.locals import *
from dataclasses import dataclass, field
from typing import List

from data.scripts.res import *
from data.scripts.linalg import *
from data.scripts.pygametools import *

TRANSPARENT = pygame.Color("#00000000")
BLACK = pygame.Color("#000000FF")
WHITE = pygame.Color("#FFFFFFFF")
DISABLED_DEFAULT_WHITENESS = 50

STATE_IDLE = 0
STATE_HOVER = 1
STATE_HOLD = 2

BLOCKS = []                  # An automatically-populated list of all Blocks.
UPDATE_IO_BLOCKS = []        # An automatically-populated list of all Blocks whose update_io is True.
UPDATE_APPEARANCE_BLOCKS = [] # An automatically-populated list of all Blocks whose update_appearance is True.

# A way to package all of the current frame's input data.
@dataclass
class IO_State:
    mouse_position: tuple = (0, 0)
    mouse_clicked: bool = False
    mouse_released: bool = False
    key_events: List[str] = field(default_factory=list)

# Call this before starting the main loop of an application.
def initiate_blocks(main_window: pygame.Surface, background_default: pygame.Color):
    for block in BLOCKS:
        if block.bg_color == TRANSPARENT: block.bg_color = background_default
        block.render(main_window)
    UPDATE_APPEARANCE_BLOCKS.sort(key=lambda block: block.z_order)

# Call this every frame of the application loop. Use the returned value and pass it to the Pygame window's update() function.
def render_upate_blocks(main_window: pygame.Surface, io_state: IO_State):
    refresh_rects = []
    for block in [block for block in UPDATE_APPEARANCE_BLOCKS if block.render_next_frame]:
        block.render_next_frame = False
        refresh_rects.append(block.global_rect)
        block.render(main_window)
    for block in UPDATE_IO_BLOCKS: block.update(io_state)
    return refresh_rects

# Call this whenever the window comes back into focus (as the canvas tends to wipe itself when this happens)
def render_all(main_window: pygame.Surface, background_default: pygame.Color):
    main_window.fill(background_default)
    for block in BLOCKS: block.render(main_window)
    pygame.display.update()

# This function is a convenient way to allow an attribute to be applied
# to a class instance, providing options such as replacability, strong typing, and default values.
# - obj:            The object the attribute is to be applied to
# - kwargs:         The dictionary of provided arguments, whose keys may contain the key specified here
# - key:            The name of the attribute
# - attribute_type: The type the provided argument has to take (otherwise, the default is applied)
# - default:        The default value that the attribute takes in the event of an absence or error
# - can_replace:    Whether or not the provided argument can replace the obj's attribute of the same name, if it exists
def get_kwarg(obj, kwargs, key, attribute_type, default, can_replace = False):
    
    # If the object already has the attribute, the default variable takes its value.
    if hasattr(obj, key): default = getattr(obj, key)

    # If the object already has the attribute and it shall not be replaced, make no change.
    if hasattr(obj, key) and not can_replace: return default

    # If the attribute in question is not provided, make no change.
    if key not in kwargs: return default

    # If the attribute in question is provided as the wrong type, make no change, and alert the user.
    if not isinstance(kwargs[key], attribute_type):
        print(f"Set Attribute Error: {key} should be a {attribute_type} but is a {type(kwargs[key])}")
        return default
    
    # All checks passed; apply the new attribute value.
    return kwargs[key]

# The Block is a kind of widget has the potential to imitate almost any standard widget.

class Block:

    BUTTON_STANDARD = 0 # Considered pressed when the mouse is currently clicking it.
    BUTTON_TOGGLE = 1   # Considered pressed from when the mouse clicks it until when the mouse clicks it again.
    BUTTON_ENTER = 2    # Considered pressed from when the mouse clicks it until when the mouse clicks anywhere else.
    BUTTON_DRAG = 3     # Considered pressed from when the mouse clicks it until when the mouse releases.

    ENTER_ANY = 0
    ENTER_ALPHA = 1
    ENTER_NUMERIC = 2
    ENTER_ALPHANUMERIC = 3
    ENTER_FLOAT = 4
    ENTER_NNFLOAT = 5
    ENTER_NOCSV = 6

    def __init__(self, **kwargs):

        # ========== VARIABLE USER-SET ATTRIBUTES ==========

        # The render flag. It must be set to True manually, VIA THE REQUEST_RENDER FUNCTION, for every frame you wish for it
        # to be visually updated, except for cases involving changes to self.mouse_state and self.button_held.
        self.render_next_frame = False

        # Background attributes.
        self.bg_color = get_kwarg(self, kwargs, "bg_color", pygame.Color, TRANSPARENT)
        self.bg_color_hover = get_kwarg(self, kwargs, "bg_color_hover", pygame.Color, color_lighten(self.bg_color, 0.15))
        self.bg_color_hold = get_kwarg(self, kwargs, "bg_color_hold", pygame.Color, color_multiply(self.bg_color, 0.8))
        self.bg_color_disabled = get_kwarg(self, kwargs, "bg_color_disabled", pygame.Color, color_add_white(self.bg_color, DISABLED_DEFAULT_WHITENESS))

        # Border attributes.
        self.bd_thick = get_kwarg(self, kwargs, "bd_thick", int, 0)
        self.bd_color = get_kwarg(self, kwargs, "bd_color", pygame.Color, BLACK)

        self.bd_thick_hover = get_kwarg(self, kwargs, "bd_thick_hover", int, self.bd_thick)
        self.bd_thick_hold = get_kwarg(self, kwargs, "bd_thick_hold", int, self.bd_thick)
        self.bd_thick_disabled = get_kwarg(self, kwargs, "bd_thick_disabled", int, self.bd_thick)

        self.bd_color_hover = get_kwarg(self, kwargs, "bd_color_hover", pygame.Color, color_lighten(self.bd_color, 0.15))
        self.bd_color_hold = get_kwarg(self, kwargs, "bd_color_hold", pygame.Color, color_multiply(self.bd_color, 0.8))
        self.bd_color_disabled = get_kwarg(self, kwargs, "bd_color_disabled", pygame.Color, color_add_white(self.bd_color, DISABLED_DEFAULT_WHITENESS))

        # Image attributes.
        self.im_surface = get_kwarg(self, kwargs, "im_surface", pygame.Surface, None)
        self.im_fitted = get_kwarg(self, kwargs, "im_fitted", bool, False)
        self.im_anchor = get_kwarg(self, kwargs, "im_anchor", Anchor, Anchor(0, 0, 0, 0))
        self.im_surface_hover = get_kwarg(self, kwargs, "im_surface_hover", pygame.Surface, image_blend_add(self.im_surface, pygame.Color(25, 25, 25)))
        self.im_surface_hold = get_kwarg(self, kwargs, "im_surface_hold", pygame.Surface, image_blend_sub(self.im_surface, pygame.Color(25, 25, 25)))
        self.im_surface_disabled = get_kwarg(self, kwargs, "im_surface_disabled", pygame.Surface, image_blend_add(self.im_surface, pygame.Color(DISABLED_DEFAULT_WHITENESS, DISABLED_DEFAULT_WHITENESS, DISABLED_DEFAULT_WHITENESS)))

        # Foreground attributes.
        self.fg_text_limit = get_kwarg(self, kwargs, "fg_text_limit", int, 30)
        self.fg_font = get_kwarg(self, kwargs, "fg_font", pygame.font.Font, pygame.font.Font("freesansbold.ttf", 12))
        self.fg_color = get_kwarg(self, kwargs, "fg_color", pygame.Color, BLACK)
        self.fg_text = get_kwarg(self, kwargs, "fg_text", str, "")[:self.fg_text_limit]
        self.fg_anchor = get_kwarg(self, kwargs, "fg_anchor", Anchor, Anchor(0.5, 0.5, 0.5, 0.5))
        self.fg_offset = get_kwarg(self, kwargs, "fg_offset", tuple, (0, 0))
        self.fg_fit_width = get_kwarg(self, kwargs, "fg_fit_width", bool, False)

        self.fg_font_hover = get_kwarg(self, kwargs, "fg_font_hover", pygame.font.Font, self.fg_font)
        self.fg_font_hold = get_kwarg(self, kwargs, "fg_font_hold", pygame.font.Font, self.fg_font)
        self.fg_font_disabled = get_kwarg(self, kwargs, "fg_font_disabled", pygame.font.Font, self.fg_font)

        self.fg_color_hover = get_kwarg(self, kwargs, "fg_color_hover", pygame.Color, self.fg_color)
        self.fg_color_hold = get_kwarg(self, kwargs, "fg_color_hold", pygame.Color, color_multiply(self.fg_color, 0.8))
        self.fg_color_disabled = get_kwarg(self, kwargs, "fg_color_disabled", pygame.Color, color_add_white(self.fg_color, DISABLED_DEFAULT_WHITENESS))

        self.fg_text_hover = get_kwarg(self, kwargs, "fg_text_hover", str, self.fg_text)
        self.fg_text_hold = get_kwarg(self, kwargs, "fg_text_hold", str, self.fg_text)
        self.fg_text_disabled = get_kwarg(self, kwargs, "fg_text_disabled", str, self.fg_text)

        # Activation attributes.
        self.disabled = get_kwarg(self, kwargs, "disabled", bool, False)
        self.local_visibility = get_kwarg(self, kwargs, "local_visibility", bool, True)

        # ========== CONSTANT USER-SET ATTRIBUTES ==========

        # Position and size attributes.
        self.anchor = get_kwarg(self, kwargs, "anchor", Anchor, Anchor(0, 0, 0, 0))
        if "position" in kwargs:
            (self.x, self.y) = get_kwarg(self, kwargs, "position", tuple, (0, 0))
        else:
            self.x = get_kwarg(self, kwargs, "x", int, 0)
            self.y = get_kwarg(self, kwargs, "y", int, 0)

        if "size" in kwargs:
            (self.w, self.h) = get_kwarg(self, kwargs, "size", tuple, (0, 0))
        elif "im_surface" in kwargs:
            (self.w, self.h) = self.im_surface.get_size()
        else:
            self.w = get_kwarg(self, kwargs, "w", int, 0)
            self.h = get_kwarg(self, kwargs, "h", int, 0)
        if self.fg_fit_width: self.w = font_surface(self.fg_text, TRANSPARENT, self.fg_font).get_width()

        # The only "inheritance" that is passed down from these parental Blocks
        # are 1) their position, and 2) their visibility.
        if "parent" in kwargs:
            self.parent_x = get_kwarg(self, kwargs, "parent", Block, None)
            self.parent_y = self.parent_x
        elif "parents" in kwargs:
            (self.parent_x, self.parent_y) = get_kwarg(self, kwargs, "parents", tuple, (None, None))
        else:
            self.parent_x = get_kwarg(self, kwargs, "parent_x", Block, None)
            self.parent_y = get_kwarg(self, kwargs, "parent_y", Block, None)

        self.z_order = get_kwarg(self, kwargs, "z_order", int, 0)

        # Tooltip attributes. The Block on which a tooltip is based on should be assigned to tt_block, NOT parent.
        self.is_tooltip = get_kwarg(self, kwargs, "is_tooltip", bool, False)
        self.tt_block = get_kwarg(self, kwargs, "tt_block", Block, None)
        self.tt_anchor = get_kwarg(self, kwargs, "tt_anchor", Anchor, Anchor(0, 0, 0, 0))
        self.tt_offset = get_kwarg(self, kwargs, "tt_offset", tuple, (0, 0))

        # Button attributes.
        self.is_button = get_kwarg(self, kwargs, "is_button", bool, False)
        self.execute_on_rising = get_kwarg(self, kwargs, "execute_on_rising", bool, False)
        self.execute_repeating = get_kwarg(self, kwargs, "execute_repeating", bool, False)
        self.button_type = get_kwarg(self, kwargs, "button_type", int, Block.BUTTON_STANDARD)
        self.enter_type = get_kwarg(self, kwargs, "enter_type", int, Block.ENTER_ANY)
        self.enter_allow_empty = get_kwarg(self, kwargs, "enter_allow_empty", bool, False)

        if "command" not in kwargs:
            self.commands = get_kwarg(self, kwargs, "commands", list, [])
            self.args = get_kwarg(self, kwargs, "args", list, [() for _ in range(len(self.commands))])
        else:
            self.commands = [get_kwarg(self, kwargs, "command", object, lambda: None)]
            self.args = [get_kwarg(self, kwargs, "args", tuple, ())]

        # Update attributes.
        self.update_io = get_kwarg(self, kwargs, "update_io", bool, self.is_button)
        self.update_appearance = get_kwarg(self, kwargs, "update_appearance", bool, self.is_button)

        # =============== READ-ONLY VARIABLES ==============
            
        self.children = []
        self.last_io_state = IO_State()
        self.mouse_state = STATE_IDLE
        self.button_held = False
        self.fg_surface = None

        # =============== READ-ONLY CONSTANTS ==============

        self.global_position = self.generate_global_position
        self.global_visibility = self.generate_global_visibility
        self.stored_enter_text = self.fg_text
        
        # ================= INITIALIZATION =================
        
        BLOCKS.append(self)
        if self.update_io: UPDATE_IO_BLOCKS.append(self)
        if self.update_appearance: UPDATE_APPEARANCE_BLOCKS.append(self)

    # ============== DERIVED READ-ONLY VALUES ==============

    @property
    def global_x(self):
        return self.x if not self.parent_x else delocalize_position_x(self.parent_x.w, self.w, self.anchor, 0, self.x) + self.parent_x.global_x
    
    @property
    def global_y(self):
        return self.y if not self.parent_y else delocalize_position_y(self.parent_y.h, self.h, self.anchor, 0, self.y) + self.parent_y.global_y

    @property
    def local_position(self):
        return (self.x, self.y)

    @property
    def size(self):
        return (self.w, self.h)
    
    @property
    def global_rect(self):
        return pygame.Rect(*self.global_position, *self.size)
    
    @property
    def generate_global_position(self):
        return (self.x if not self.parent_x else delocalize_position_x(self.parent_x.w, self.w, self.anchor, 0, self.x) + self.parent_x.global_x,
                self.y if not self.parent_y else delocalize_position_y(self.parent_y.h, self.h, self.anchor, 0, self.y) + self.parent_y.global_y)
    
    @property
    def generate_global_visibility(self):
        if not self.local_visibility: return False
        if self.parent_x and not self.parent_x.global_visibility: return False
        if self.parent_y and not self.parent_y.global_visibility: return False
        return True

    # ========== MODIFICATION HELPER FUNCTIONS ==========

    def move_to(self, new_pos: tuple):
        self.x = new_pos[0]
        self.y = new_pos[1]
        self.global_position = self.generate_global_position

    def set_size(self, size: tuple):
        self.w = size[0]
        self.h = size[1]

    def add_command(self, command, args: tuple = (), execution_position: int = -1):
        if execution_position < 0:
            self.commands.append(command)
            self.args.append(args)
        else:
            self.commands.insert(execution_position, command)
            self.args.insert(execution_position, args)

    def set_all_fg_text(self, text: str, including_stored: bool = True):
        text = text[:self.fg_text_limit]
        self.fg_text = text
        self.fg_text_hover = text
        self.fg_text_hold = text
        self.fg_text_disabled = text
        if including_stored: self.stored_enter_text = text
        self.request_render()

    def regenerate_fg_surface(self):
        fg_color = self.fg_color
        fg_font = self.fg_font
        fg_text = ""

        if not self.is_button \
            or (self.is_button and not self.disabled and not self.button_type == Block.BUTTON_TOGGLE and self.mouse_state == STATE_IDLE) \
            or (self.is_button and not self.disabled and self.button_type == Block.BUTTON_TOGGLE and self.mouse_state == STATE_IDLE and not self.button_held):
            fg_color, fg_font, fg_text = self.fg_color, self.fg_font, self.fg_text
        elif self.disabled:
            fg_color, fg_font, fg_text = self.fg_color_disabled, self.fg_font_disabled, self.fg_text_disabled
        elif self.mouse_state == STATE_HOLD or self.button_held:
            fg_color, fg_font, fg_text = self.fg_color_hold, self.fg_font_hold, self.fg_text_hold
        elif self.mouse_state == STATE_HOVER:
            fg_color, fg_font, fg_text = self.fg_color_hover, self.fg_font_hover, self.fg_text_hover

        self.fg_surface = font_surface(fg_text, fg_color, fg_font)
        if self.fg_fit_width: self.w = self.fg_surface.get_width()

    def disable(self):
        self.disabled = True
        self.request_render()

    def enable(self):
        self.disabled = False
        self.request_render()

    def toggle_disabled(self):
        self.disabled = not self.disabled
        self.request_render()

    def set_disabled(self, disabled: bool = True):
        self.disabled = disabled
        self.request_render()

    # ========== FRAME-BY-FRAME UPDATE FUNCTIONS ==========

    def update(self, io_state: IO_State):

        if self.disabled: return

        self.last_io_state = io_state
        mouse_inside = self.global_rect.collidepoint(io_state.mouse_position)

        # Update the mouse_state according to the current mouse information.
        if self.mouse_state == STATE_IDLE:
            if mouse_inside:
                self.change_mouse_state(STATE_HOVER)
        elif self.mouse_state == STATE_HOVER:
            if not mouse_inside:
                self.change_mouse_state(STATE_IDLE)
            elif io_state.mouse_clicked and not io_state.mouse_released:
                self.change_mouse_state(STATE_HOLD)
        elif self.mouse_state == STATE_HOLD:
            if self.button_type == Block.BUTTON_ENTER:
                if not mouse_inside and io_state.mouse_clicked:
                    self.change_mouse_state(STATE_IDLE)
                    self.set_all_fg_text(self.stored_enter_text)
            elif self.button_type == Block.BUTTON_DRAG:
                if io_state.mouse_released:
                    if mouse_inside:
                        self.change_mouse_state(STATE_HOVER)
                    else:
                        self.change_mouse_state(STATE_IDLE)
            else:
                if not mouse_inside:
                    self.change_mouse_state(STATE_IDLE)
                elif io_state.mouse_released and not io_state.mouse_clicked:
                    self.change_mouse_state(STATE_HOVER)

        # Update the button_pressed state according to the inputs and button type.
        # Additionally, execute its command on certain conditions.
        if self.button_type == Block.BUTTON_ENTER:
            self.change_button_held(self.mouse_state == STATE_HOLD)
            if self.mouse_state == STATE_HOLD:
                for event in io_state.key_events:
                    if event.key == pygame.K_RETURN:
                        if not (not self.enter_allow_empty and self.fg_text == ""):
                            self.stored_enter_text = self.fg_text
                            self.execute()
                        else:
                            self.set_all_fg_text(self.stored_enter_text)
                        self.change_mouse_state(STATE_HOVER if mouse_inside else STATE_IDLE)
                    elif event.key == pygame.K_ESCAPE:
                        self.set_all_fg_text(self.stored_enter_text)
                        self.change_mouse_state(STATE_HOVER if mouse_inside else STATE_IDLE)
                    elif event.key == pygame.K_BACKSPACE:
                        self.set_all_fg_text(self.fg_text[:-1] if self.fg_text else "", False)
                    elif event.key == pygame.K_DELETE:
                        self.set_all_fg_text("", False)
                    else:
                        valid = True
                        unicode = event.unicode
                        if self.enter_type == Block.ENTER_ALPHA and not unicode.isalpha(): valid = False
                        elif self.enter_type == Block.ENTER_NUMERIC and not unicode.isdigit(): valid = False
                        elif self.enter_type == Block.ENTER_ALPHANUMERIC and not (unicode.isalnum() or unicode in ['-', '_']): valid = False
                        elif self.enter_type == Block.ENTER_FLOAT and ( \
                            (not unicode.isdigit() and not unicode in ['-', '.']) or \
                            (unicode == '-' and len(self.fg_text) != 0) or \
                            (unicode == '.' and len(self.fg_text) == 0) or \
                            (unicode == '.' and '.' in self.fg_text)):
                            valid = False
                        elif self.enter_type == Block.ENTER_NNFLOAT and (\
                            (not unicode.isdigit() and not unicode in ['-', '.']) or \
                            (unicode == '.' and len(self.fg_text) == 0) or \
                            (unicode == '.' and '.' in self.fg_text)):
                            valid = False
                        elif self.enter_type == Block.ENTER_NOCSV and unicode in [',', ';']: valid = False
                        if valid: self.set_all_fg_text(self.fg_text + event.unicode, False)
        elif self.button_type == Block.BUTTON_TOGGLE:
            self.change_button_held(self.mouse_state == STATE_HOLD)
            if self.is_button and \
                ((not self.execute_on_rising and self.mouse_state == STATE_HOVER and io_state.mouse_released) or \
                (self.execute_on_rising and self.mouse_state == STATE_HOLD and io_state.mouse_clicked)):
                self.execute()
        else:
            if (not self.execute_on_rising and self.mouse_state == STATE_HOVER and io_state.mouse_released) or \
                (self.execute_on_rising and self.mouse_state == STATE_HOLD and io_state.mouse_clicked):
                self.change_button_held(not self.change_button_held)
                self.execute()

        if self.execute_repeating and self.mouse_state == STATE_HOLD: self.execute()

        # If the Block is a tooltip, update its position based on the mouse's
        # current position.
        if self.is_tooltip:
            (self.x, self.y) = delocalize_position(0, 0, *self.size, self.tt_anchor, *io_state.mouse_position, *self.local_position)
    
    def change_mouse_state(self, new_state):
        if self.mouse_state == new_state: return
        self.mouse_state = new_state
        self.request_render()

    def change_button_held(self, button_held):
        if self.button_held == button_held: return
        self.button_held = button_held
        self.request_render()

    # ================ RENDER FUNCTION ===============
        
    def request_render(self, ignore_flag: bool = False):
        if not ignore_flag and not self.update_appearance:
            print("WARNING: Trying to render a Block that is not flagged as requiring it")
        self.render_next_frame = True

    def render(self, main_window: pygame.Surface):
        if not self.global_visibility: return

        surface = pygame.Surface(self.size, SRCALPHA).convert_alpha()

        # Temporary visual parameters, to be used in rendering.
        im_surface = None
        bd_thick = 0
        bd_color = BLACK
        bg_color = WHITE

        # Check whether the Block is flagged as a button, and set visual parameters appropriately.
        if not self.is_button \
            or (self.is_button and not self.disabled and not self.button_type == Block.BUTTON_TOGGLE and self.mouse_state == STATE_IDLE) \
            or (self.is_button and not self.disabled and self.button_type == Block.BUTTON_TOGGLE and self.mouse_state == STATE_IDLE and not self.button_held):
            im_surface = self.im_surface
            bd_thick, bd_color = self.bd_thick, self.bd_color
            bg_color = self.bg_color
        elif self.disabled:
            im_surface = self.im_surface_disabled
            bd_thick, bd_color = self.bd_thick_disabled, self.bd_color_disabled
            bg_color = self.bg_color_disabled
        elif self.mouse_state == STATE_HOLD or self.button_held:
            im_surface = self.im_surface_hold
            bd_thick, bd_color = self.bd_thick_hold, self.bd_color_hold
            bg_color = self.bg_color_hold
        elif self.mouse_state == STATE_HOVER:
            im_surface = self.im_surface_hover
            bd_thick, bd_color = self.bd_thick_hover, self.bd_color_hover
            bg_color = self.bg_color_hover

        # Draw the border.
        if self.bd_thick:
            pygame.draw.rect(surface, bd_color, pygame.Rect(0, 0, self.w, bd_thick))
            pygame.draw.rect(surface, bd_color, pygame.Rect(0, 0, bd_thick, self.h))
            pygame.draw.rect(surface, bd_color, pygame.Rect(0, self.h - bd_thick, self.w, bd_thick))
            pygame.draw.rect(surface, bd_color, pygame.Rect(self.w - bd_thick, 0, bd_thick, self.h))

        # Fill the inside of the border with the background and image.
        shrunken_rect = shrink_rect(pygame.Rect(0, 0, *self.size), bd_thick)
        pygame.draw.rect(surface, bg_color, shrunken_rect)
        if im_surface:
            if self.im_fitted:
                surface.blit(pygame.transform.smoothscale(im_surface, self.size), (0, 0))
            else:
                im_local_position = delocalize_position(*shrunken_rect.size, *self.im_surface.get_size(), self.im_anchor, 0, 0, bd_thick, bd_thick)
                surface.blit(im_surface, im_local_position, pygame.Rect(0, 0, *shrunken_rect.size))

        # Place the resulting Block onto the main window.
        main_window.blit(surface, self.global_position)

        # Draw the foreground text.
        if self.fg_text:
            self.regenerate_fg_surface()
            text_local_position = delocalize_position(*self.size, *self.fg_surface.get_size(), self.fg_anchor, 0, 0, *self.fg_offset)
            main_window.blit(self.fg_surface, addV(self.global_position, text_local_position))

        # Update the visibility of the tooltip.
        if self.tt_block:
            self.tt_block.visibility = (self.tt_block and self.mouse_state == STATE_HOVER or self.mouse_state == STATE_HOLD)

    # =============== EXECUTE FUNCTION ===============

    def execute(self):
        if self.disabled or not self.local_visibility: return
        print("EXECUTE", self.global_position)
        for i in range(len(self.commands)): self.commands[i](*self.args[i])