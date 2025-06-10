from pygame.locals import *
from random import shuffle, random

from .res import *
from .pygametools import *
from .pygameblock import *
from .vocabstyle import *
from .vocabwk import *
from .vocabstate import *

sfx_start = load_sfx('start.wav', 0.5)
sfx_finish = load_sfx('finish.wav')
sfx_correct = load_sfx('correct.wav')
sfx_incorrect = load_sfx('incorrect.wav')

modes = ['Listening', 'Writing', 'Speaking']

class Layout(Block):

    def __init__(self, **kwargs):

        self.tutorial = True
        self.mode = 0
        self.state = VocabState(STATE_IDLE, [], 0, [], 0)
        self.previous_state = None

        (self.w, self.h) = WINDOW_SIZE
        self.bd_color = COLOR_FG_SECONDARY
        self.bd_thick = BORDER_MAIN
        self.update_io = True

        Block.__init__(self, **kwargs)

        self.title_label = Block(
            parent = self,
            size = (750, 75),
            anchor = Anchor(0.5, 0.5, 0, 0),
            y = 35,
            fg_text = f"Japanese {modes[self.mode]} Practice!",
            fg_font = FONT_MEDIUM,
            fg_color = COLOR_FG_MAIN,
            update_appearance = True)
        
        self.help_label = Block(
            parent = self.title_label,
            size = (750, 25),
            anchor = Anchor(0.5, 0.5, 1, 0),
            y = 10,
            fg_text_limit = 100,
            fg_text = "Type the level you want to practice below, then hit Enter",
            fg_font = FONT_TINY,
            fg_color = COLOR_FG_MAIN,
            update_appearance = True)

        self.level_lower_enterbox = Block(
            parent = self.help_label,
            size = (100, 50),
            anchor = Anchor(0.5, 0.5, 1, 0),
            position = (-75, 25),
            bg_color = COLOR_BG_SECONDARY,
            bd_color = COLOR_FG_SECONDARY,
            bd_thick = BORDER_SECONDARY,
            fg_text = "1",
            fg_font = FONT_SMALL,
            fg_color = COLOR_FG_MAIN,
            is_button = True,
            button_type = Block.BUTTON_ENTER,
            enter_type = Block.ENTER_NUMERIC,
            fg_text_limit = 2,
            command = self.set_lower_level)
        
        self.level_hyphen = Block(
            parent = self.level_lower_enterbox,
            size = (25, 25),
            anchor = Anchor(0.5, 0.5, 0.5, 0.5),
            x = -self.level_lower_enterbox.x,
            fg_font = FONT_SMALL,
            fg_color = COLOR_FG_MAIN,
            fg_text = "-")
        
        self.level_upper_enterbox = Block(
            parent = self.help_label,
            size = (100, 50),
            anchor = Anchor(0.5, 0.5, 1, 0),
            position = (-self.level_lower_enterbox.x, 25),
            bg_color = COLOR_BG_SECONDARY,
            bd_color = COLOR_FG_SECONDARY,
            bd_thick = BORDER_SECONDARY,
            fg_text = "1",
            fg_font = FONT_SMALL,
            fg_color = COLOR_FG_MAIN,
            is_button = True,
            button_type = Block.BUTTON_ENTER,
            enter_type = Block.ENTER_NUMERIC,
            fg_text_limit = 2,
            command = self.set_upper_level)

        self.kanji_label = Block(
            parent = self.level_lower_enterbox,
            size = (650, 120),
            anchor = Anchor(0.5, 0.5, 1, 0),
            position = (-self.level_lower_enterbox.x, 30),
            bg_color = COLOR_BG_SECONDARY,
            bd_color = COLOR_FG_SECONDARY,
            bd_thick = BORDER_SECONDARY,
            fg_text = "",
            fg_font = FONT_LARGE,
            fg_color = COLOR_FG_MAIN,
            update_appearance = True)
        
        self.meaning_label = Block(
            parent = self.kanji_label,
            size = (650, 60),
            anchor = Anchor(0.5, 0.5, 1, 0),
            y = 30,
            bg_color = COLOR_BG_SECONDARY,
            bd_color = COLOR_FG_SECONDARY,
            bd_thick = BORDER_SECONDARY,
            fg_text = "",
            fg_font = FONT_SMALL,
            fg_color = COLOR_FG_MAIN,
            update_appearance = True)
        
        self.count_label = Block(
            parent = self.meaning_label,
            size = (500, 50),
            anchor = Anchor(0.5, 0.5, 1, 0),
            y = 15,
            fg_text = "",
            fg_font = FONT_TINY,
            fg_color = COLOR_FG_MAIN,
            update_appearance = True)
        
    def update_state(self, *args):
        self.previous_state = self.state
        self.state = VocabState(*args)

    def reverse_state(self):
        if not self.previous_state: return
        self.state = self.previous_state
        self.previous_state = None
        
    def switch_mode(self):
        if not self.state.state == STATE_IDLE: return
        self.mode = (self.mode + 1) % len(modes)
        self.title_label.set_all_fg_text(f"Japanese {modes[self.mode]} Practice!")
        # change_color_scheme(mode_colors[self.mode])

    def set_lower_level(self):
        self.level_lower_enterbox.set_all_fg_text(str(clamp(int(self.level_lower_enterbox.stored_enter_text), 1, 60)))
        self.level_upper_enterbox.set_all_fg_text(str(max(int(self.level_lower_enterbox.stored_enter_text), int(self.level_upper_enterbox.stored_enter_text))))

    def set_upper_level(self):
        self.level_upper_enterbox.set_all_fg_text(str(clamp(int(self.level_upper_enterbox.stored_enter_text), 1, 60)))
        self.level_lower_enterbox.set_all_fg_text(str(min(int(self.level_lower_enterbox.stored_enter_text), int(self.level_upper_enterbox.stored_enter_text))))

    # STATE-MODIFYING ACTIONS

    # To be called once per run-through
    def start_level(self):
        if self.tutorial: self.help_label.set_all_fg_text("Listen up! Hit Right to reveal, or Left to repeat")
        self.level_lower_enterbox.disable()
        self.level_upper_enterbox.disable()
        self.level_lower_enterbox.set_all_fg_text(str(clamp(int(self.level_lower_enterbox.stored_enter_text), 1, 60)))

        # Initialize vocabulary list
        vocabulary = extract('kanji' if modes[self.mode] == 'Writing' else 'vocabulary', list(range(int(self.level_lower_enterbox.stored_enter_text), int(self.level_upper_enterbox.stored_enter_text) + 1)))
        if modes[self.mode] in ['Listening', 'Speaking']: vocabulary = [v for v in vocabulary if v.audio_url]
        shuffle(vocabulary)
        sfx_start.play()

        # Initialize state
        self.update_state(STATE_QUESTION, vocabulary, 0, [], 1)

        # Start vocabulary procedure
        self.render_vocabulary_question()
        self.render_count()

    def render_vocabulary_question(self):
        if modes[self.mode] == 'Listening':
            self.meaning_label.set_all_fg_text("?")
            self.playback_vocabulary()
        elif modes[self.mode] == 'Speaking':
            self.meaning_label.set_all_fg_text(self.state.current_vocabulary.data['Meanings'][0])
        elif modes[self.mode] == 'Writing':
            self.meaning_label.set_all_fg_text(f"{self.state.current_vocabulary.data['Meanings'][0]} - {self.state.current_vocabulary.data['Readings'][0]}")
        self.kanji_label.set_all_fg_text("?")

    def render_vocabulary_answer(self):
        if self.tutorial: self.help_label.set_all_fg_text("Did you get it? Hit Up for yes, or Down for no")
        if modes[self.mode] == 'Listening':
            self.meaning_label.set_all_fg_text(self.state.current_vocabulary.data['Meanings'][0])
        elif modes[self.mode] == 'Speaking':
            self.playback_vocabulary()
        elif modes[self.mode] == 'Writing':
            self.meaning_label.set_all_fg_text(f"{self.state.current_vocabulary.data['Meanings'][0]} - {self.state.current_vocabulary.data['Readings'][0]}")
        self.kanji_label.set_all_fg_text(self.state.current_vocabulary.data['Kanji'])

    def render_count(self):
        self.count_label.set_all_fg_text(f"{self.state.vocabulary_index - self.state.mistake_count} / {self.state.vocabulary_index} / {self.state.vocabulary_count}")

    def playback_vocabulary(self):
        if not self.state.vocabulary or not modes[self.mode] == 'Listening': return

        self.state.current_vocabulary.sound().play()

    def reveal_vocabulary(self):
        if not self.state.state == STATE_QUESTION or not self.state.vocabulary: return

        self.update_state(STATE_ANSWER, self.state.vocabulary, self.state.vocabulary_index, self.state.mistake_indices, self.state.phase)
        self.render_vocabulary_answer()

    def advance_vocabulary(self, success: bool):
        if not self.state.state == STATE_ANSWER: return

        if self.tutorial:
            self.tutorial = False
            self.help_label.set_all_fg_text("Have fun!")
        (sfx_correct if success else sfx_incorrect).play()

        new_mistake_indices = self.state.mistake_indices if success else self.state.mistake_indices + [self.state.vocabulary_index]
        new_mistake_vocabulary = self.state.mistake_vocabulary if success else self.state.mistake_vocabulary + [self.state.vocabulary[self.state.vocabulary_index]]
        if self.state.vocabulary_index == self.state.vocabulary_count - 1:
            if self.state.mistake_count == 0:
                self.update_state(STATE_IDLE, [], 0, [], 0)
                self.finish()
            else:
                self.update_state(STATE_QUESTION, new_mistake_vocabulary, 0, [], self.state.phase + 1)
                self.render_vocabulary_question()
                self.render_count()
        else:
            self.update_state(STATE_QUESTION, self.state.vocabulary, self.state.vocabulary_index + 1, new_mistake_indices, self.state.phase)
            self.render_vocabulary_question()
            self.render_count()

    def undo_advance(self):
        if self.state.state != STATE_QUESTION: return
        if self.state.vocabulary_index == 0 and self.state.phase == 1: return

        self.reverse_state()
        self.render_vocabulary_answer()
        self.render_count()

    def finish(self):
        sfx_finish.play()
        self.level_lower_enterbox.enable()
        self.level_upper_enterbox.enable()
        self.kanji_label.set_all_fg_text("")
        self.meaning_label.set_all_fg_text("")
        self.count_label.set_all_fg_text("You completed the level!")

    # OVERRIDE
    def update(self, io_state: IO_State):
        super(Layout, self).update(io_state)

        for event in io_state.key_events:
            if   event.key == K_SPACE: self.start_level()
            elif event.key == K_LEFT: self.playback_vocabulary()
            elif event.key == K_RIGHT: self.reveal_vocabulary()
            elif event.key == K_UP: self.advance_vocabulary(True)
            elif event.key == K_DOWN: self.advance_vocabulary(False)
            elif event.key == K_z: self.undo_advance()
            elif event.key == K_TAB: self.switch_mode()