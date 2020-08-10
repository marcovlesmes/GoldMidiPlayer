# For MidiPlayer
import pygame
# For EventManager
import sys
# For Bass
from Tkinter import Tk
from tkFileDialog import askopenfilename

DEBUG = True
MAIN_MODULE = "Main Module"
MIXER_MODULE = "Mixer Module"
PRESET_MODULE = "Preset Module"


class MidiPlayer:
    def __init__(self):
        pygame.init()
        self._clock = pygame.time.Clock()
        self._screen = Screen(size=(800, 150))
        self._eventManager = EventManager()

    def update(self):
        self._clock.tick(40)
        self._eventManager.update()
        self._screen.render()


class EventManager:
    def __init__(self):
        self._events = pygame.event

    def update(self):
        if DEBUG:
            from os import system

        for event in self._events.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                keys_map = pygame.key.get_pressed()
                if DEBUG and keys_map[pygame.K_c]:
                    system('cls')
                if DEBUG and keys_map[pygame.K_r]:
                    pygame.display.update()


class FileManager:
    def __init__(self):
        pass

    def add_file(self, midi):
        pass


class Bass:
    def __init__(self):
        self._fileManager = FileManager()

    @staticmethod
    def open_midi():
        Tk().withdraw()
        new_midi_path = askopenfilename(
            initialdir="./",
            title="Select MIDI file",
            filetypes=(("MIDI files", "*.mid *.kar"), ("all files", "*.*"))
        )
        if new_midi_path:
            pass

        print ('Open Midi')

    @staticmethod
    def slider_exec():
        print('Slider Call')

    @staticmethod
    def button_exec():
        print('Button Call')

    @staticmethod
    def knob_exec():
        print('Knob Call')

    @staticmethod
    def mute_track(kwargs):
        if kwargs["slider"].get_state() == kwargs["slider"].STATES["disabled"]:
            kwargs["slider"].disabled(False)
        else:
            kwargs["slider"].disabled(True)

    @staticmethod
    def get_array_of_items():
        return ["1 Acoustic Grand Piano", "2 Bright Acoustic Piano", "3 Electric Grand Piano", "4 Honky-tonk Piano", "5 Electric Piano 1"]


class VisualObject:
    def __init__(self, name, position, sprite=None, sprite_area=None):
        self._name = name
        self._position = position
        self._offset_position = (0, 0)
        self._sprite = sprite
        self._sprite_area = sprite_area

        if sprite is not None:
            self._surface = pygame.image.load(sprite).convert()
        else:
            self._surface = sprite

    def get_surface(self):
        return self._surface

    def get_position(self):
        return tuple(map(lambda a, b: a + b, self._position, self._offset_position))

    def set_offset_height(self, offset):
        self._offset_position = (self._offset_position[0], offset)

    def is_drawable(self):
        return True if self._surface is not None else False

    def update(self):
        pass


class Module:
    def __init__(self, name, height, background_src, priority=0):
        self._name = name
        self._height = height
        self._index_priority = priority
        self._background_src = background_src
        self._render_elements = [VisualObject(self._name, (0, 0), self._background_src)]

    def get_name(self):
        return self._name

    def get_height(self):
        return self._height

    def get_index_priority(self):
        return self._index_priority

    def get_objects_to_render(self):
        return self._render_elements

    def add_objects_to_render(self, objects):
        self._render_elements += objects


class Screen:
    CAPTION = "Gold Midi Player"
    ICON_PATH = "./icon.png"

    def __init__(self, size):
        self._screen_surface = None
        self._visible_elements = []
        self._size = size
        self._active_modules = []
        self._main_module = None
        self._playlist_module = None
        self._mixer_module = None
        self._preset_module = None
        self._font = None

        pygame.display.set_caption(self.CAPTION)
        pygame.display.set_icon(pygame.image.load(self.ICON_PATH))
        pygame.display.set_mode(self._size, pygame.NOFRAME)

        self._screen_surface = pygame.display.get_surface()
        """
        LOADING SCREEN
        """
        self.loading_screen()
        """
        SET MAIN MODULE
        """
        self._size = (800, 0)
        self.toggle_module({"module": MAIN_MODULE})

    def _set_module(self, module):
        if module == MAIN_MODULE:
            if self._main_module is None:
                self._main_module = Module(MAIN_MODULE, 344, './main_screen.png', 1)
                ElementManager.main_module_init(self._main_module, self)
            self._active_modules.append(self._main_module)
            return self._main_module
        elif module == MIXER_MODULE:
            if self._mixer_module is None:
                self.loading_screen()
                self._mixer_module = Module(MIXER_MODULE, 344, './mixer_screen.png', 3)
                ElementManager.mixer_module_init(self._mixer_module, self)
            self._active_modules.append(self._mixer_module)
            return self._mixer_module
        elif module == PRESET_MODULE:
            if self._preset_module is None:
                self._preset_module = Module(PRESET_MODULE, 150, './loading_screen.png', 4)
                ElementManager.preset_module_init(self._preset_module, self)
            self._active_modules.append(self._preset_module)
            return self._preset_module

    def _unset_module(self, module):
        self._active_modules.remove(module)

    def set_screen(self):
        self._visible_elements = []
        for module in self._active_modules:
            elements = ElementManager.set_height_offset(module, self._active_modules)
            self._visible_elements += elements

        pygame.display.set_mode(self._size)

    def render(self):
        self._screen_surface.fill((0, 0, 0))
        for element in self._visible_elements:
            if element.is_drawable():
                element.update()
                self._screen_surface.blit(element.get_surface(), element.get_position())
        pygame.display.update()

    def loading_screen(self):
        loading_screen = pygame.image.load('loading_screen.png')
        self._screen_surface.blit(loading_screen, (0, 0))
        if pygame.font.get_init():
            self._font = pygame.font.Font("./fonts/conthrax-sb.ttf", 20)
            self._screen_surface.blit(self._font.render("Loading...", True, (255, 255, 255)), (26, 120))
        pygame.display.update()

    def toggle_module(self, kwargs):
        unset = False
        for module in self._active_modules:
            if module.get_name() == kwargs["module"]:
                self._unset_module(module)
                height = module.get_height() * -1
                unset = True

        if not unset:
            module = self._set_module(kwargs["module"])
            height = module.get_height()

        self._size = (self._size[0], self._size[1] + height)
        self.set_screen()

    def toggle_modules(self, kwargs):
        modules = kwargs["modules"]
        for module in modules:
            self.toggle_module({"module": module})


class ElementManager:
    @staticmethod
    def set_height_offset(module, active_modules):
        offset_height = 0
        index = module.get_index_priority()
        for active_module in active_modules:
            if active_module is not module and active_module.get_index_priority() < index:
                offset_height += active_module.get_height()
        print('For ', module.get_name(), ' offset_height is ', offset_height)
        elements = module.get_objects_to_render()
        for element in elements:
            element.set_offset_height(offset_height)
        return elements

    @staticmethod
    def main_module_init(module, screen):
        open_midi_hover_state_surface = ImageButtonState('hover', './sprite.png', (0, 59, 54, 58))
        open_midi_button = Button('Open Midi Button', (143, 92, 54, 58), [open_midi_hover_state_surface],
                                  Bass.button_exec)
        open_midi_button.set_hold_active(False)
        save_file_hover_state_surface = ImageButtonState('hover', './sprite.png', (58, 59, 54, 58))
        save_file_button = Button('Save File Button', (199, 92, 54, 58), [save_file_hover_state_surface],
                                  Bass.button_exec)
        save_file_button.set_hold_active(False)
        open_soundfont_hover_state_surface = ImageButtonState('hover', './sprite.png', (116, 59, 54, 58))
        open_soundfont_button = Button('Open SoundFont Button', (258, 92, 54, 58), [open_soundfont_hover_state_surface],
                                       Bass.button_exec)
        open_soundfont_button.set_hold_active(False)
        save_gm_file_hover_state_surface = ImageButtonState('hover', './sprite.png', (176, 59, 54, 58))
        save_gm_file_button = Button('Convert to CSF Button', (316, 92, 54, 58), [save_gm_file_hover_state_surface],
                                     Bass.button_exec)
        save_gm_file_button.set_hold_active(False)
        export_mp3_hover_state_surface = ImageButtonState('hover', './sprite.png', (232, 59, 54, 58))
        export_mp3_button = Button('Convert MP3 Button', (372, 92, 54, 58), [export_mp3_hover_state_surface],
                                   Bass.button_exec)
        export_mp3_button.set_hold_active(False)
        toggle_mixer_hover_state_surface = ImageButtonState('hover', './sprite.png', (289, 59, 54, 58))
        toggle_mixer_active_state_surface = ImageButtonState('active', './sprite.png', (289, 59, 54, 58))
        toggle_mixer_button = Button('Toggle Mixer Button', (430, 92, 54, 58), [toggle_mixer_hover_state_surface, toggle_mixer_active_state_surface],
                                     screen.toggle_module, module=MIXER_MODULE)
        toggle_piano_hover_state_surface = ImageButtonState('hover', './sprite.png', (350, 59, 54, 58))
        toggle_piano_active_state_surface = ImageButtonState('active', './sprite.png', (350, 59, 54, 58))
        toggle_piano_button = Button('Toggle Piano Button', (488, 92, 54, 58), [toggle_piano_hover_state_surface, toggle_piano_active_state_surface],
                                     Bass.button_exec)
        toggle_settings_hover_state_surface = ImageButtonState('hover', './sprite.png', (405, 59, 54, 58))
        toggle_settings_button = Button('Toggle Settings Button', (542, 92, 54, 58),
                                        [toggle_settings_hover_state_surface], Bass.button_exec)

        prev_midi_hover_state_surface = ImageButtonState('hover', './sprite.png', (469, 47, 50, 54))
        prev_midi_button = Button('Previous File Button', (221, 264, 50, 54), [prev_midi_hover_state_surface],
                                  Bass.button_exec)
        prev_midi_button.set_hold_active(False)
        rewind_midi_hover_state_surface = ImageButtonState('hover', './sprite.png', (523, 47, 50, 54))
        rewind_midi_button = Button('Rewind Button', (276, 264, 50, 54), [rewind_midi_hover_state_surface],
                                    Bass.button_exec)
        forward_midi_hover_state_surface = ImageButtonState('hover', './sprite.png', (576, 47, 50, 54))
        forward_midi_button = Button('Forward Button', (329, 264, 50, 54), [forward_midi_hover_state_surface],
                                     Bass.button_exec)
        next_midi_hover_state_surface = ImageButtonState('hover', './sprite.png', (630, 47, 50, 54))
        next_midi_button = Button('Next File Button', (384, 264, 50, 54), [next_midi_hover_state_surface],
                                  Bass.button_exec)
        next_midi_button.set_hold_active(False)
        stop_midi_hover_state_surface = ImageButtonState('hover', './sprite.png', (684, 47, 50, 54))
        stop_midi_button = Button('Stop Button', (438, 264, 50, 54), [stop_midi_hover_state_surface], Bass.button_exec)
        stop_midi_button.set_hold_active(False)
        play_midi_hover_state_surface = ImageButtonState('hover', './sprite.png', (738, 47, 50, 54))
        play_midi_active_state_surface = ImageButtonState('active', './sprite.png', (738, 102, 50, 54))
        play_midi_button = Button('Play Button', (493, 264, 50, 54),
                                  [play_midi_hover_state_surface, play_midi_active_state_surface], Bass.button_exec)
        pause_midi_hover_state_surface = ImageButtonState('hover', './sprite.png', (790, 47, 50, 54))
        pause_midi_active_state_surface = ImageButtonState('active', './sprite.png', (790, 102, 50, 54))
        pause_midi_button = Button('Pause Button', (547, 264, 50, 54),
                                   [pause_midi_hover_state_surface, pause_midi_active_state_surface], Bass.button_exec)

        puller = Puller('./sprite.png', (913, 63, 29, 16))
        sliders_font = pygame.font.Font("./fonts/conthrax-sb.ttf", 16)
        global_volume_text = Text('Global Volume Text', (87, 114), sliders_font, '100')
        global_volume_slider = Slider('Global Volume Slider', (87, 151), 148, puller, global_volume_text, 0, 100,
                                      Bass.slider_exec)
        global_pitch_text = Text('Global Pitch Text', (632, 114), sliders_font, '0')
        global_pitch_slider = Slider('Global Pitch Slider', (638, 151), 148, puller, global_pitch_text, -100, 100,
                                     Bass.slider_exec)
        global_pitch_slider.draw(74)
        global_tempo_text = Text('Global Tempo Text', (705, 114), sliders_font, '0')
        global_tempo_slider = Slider('Global Tempo Slider', (712, 151), 148, puller, global_tempo_text, -100, 100,
                                     Bass.slider_exec)
        global_tempo_slider.draw(74)

        midi_name_text = Text('Midi Name Text', (158, 165), sliders_font, 'Midi Name', (36, 71, 84))
        midi_time_text = Text('Midi Time Text', (158, 225), sliders_font, '00:00:00', (36, 71, 84))
        midi_key_text = Text('Midi Key Text', (302, 225), sliders_font, 'Key', (36, 71, 84))

        module.add_objects_to_render([
            open_midi_button,
            save_file_button,
            open_soundfont_button,
            save_gm_file_button,
            export_mp3_button,
            toggle_mixer_button,
            toggle_piano_button,
            toggle_settings_button,
            prev_midi_button,
            rewind_midi_button,
            forward_midi_button,
            next_midi_button,
            stop_midi_button,
            play_midi_button,
            pause_midi_button,
            global_volume_text,
            global_volume_slider,
            global_pitch_text,
            global_pitch_slider,
            global_tempo_text,
            global_tempo_slider,
            midi_name_text,
            midi_time_text,
            midi_key_text
        ])

    @staticmethod
    def mixer_module_init(module, screen):
        solo_track_hover_image = ImageButtonState('hover', './sprite.png', (308, 119, 27, 10))
        solo_track_active_image = ImageButtonState('active', './sprite.png', (278, 119, 27, 10))
        solo_track_1_button = Button('Solo Track 1 Button', (14, 7, 27, 10), [solo_track_hover_image, solo_track_active_image], Bass.button_exec)
        solo_track_2_button = Button('Solo Track 2 Button', (64, 7, 27, 10), [solo_track_hover_image, solo_track_active_image], Bass.button_exec)
        solo_track_3_button = Button('Solo Track 3 Button', (114, 7, 27, 10), [solo_track_hover_image, solo_track_active_image], Bass.button_exec)
        solo_track_4_button = Button('Solo Track 4 Button', (164, 7, 27, 10), [solo_track_hover_image, solo_track_active_image], Bass.button_exec)
        solo_track_5_button = Button('Solo Track 5 Button', (214, 7, 27, 10), [solo_track_hover_image, solo_track_active_image], Bass.button_exec)
        solo_track_6_button = Button('Solo Track 6 Button', (264, 7, 27, 10), [solo_track_hover_image, solo_track_active_image], Bass.button_exec)
        solo_track_7_button = Button('Solo Track 7 Button', (314, 7, 27, 10), [solo_track_hover_image, solo_track_active_image], Bass.button_exec)
        solo_track_8_button = Button('Solo Track 8 Button', (364, 7, 27, 10), [solo_track_hover_image, solo_track_active_image], Bass.button_exec)
        solo_track_9_button = Button('Solo Track 9 Button', (414, 7, 27, 10), [solo_track_hover_image, solo_track_active_image], Bass.button_exec)
        solo_track_10_button = Button('Solo Track 10 Button', (464, 7, 27, 10), [solo_track_hover_image, solo_track_active_image], Bass.button_exec)
        solo_track_11_button = Button('Solo Track 11 Button', (514, 7, 27, 10), [solo_track_hover_image, solo_track_active_image], Bass.button_exec)
        solo_track_12_button = Button('Solo Track 12 Button', (564, 7, 27, 10), [solo_track_hover_image, solo_track_active_image], Bass.button_exec)
        solo_track_13_button = Button('Solo Track 13 Button', (614, 7, 27, 10), [solo_track_hover_image, solo_track_active_image], Bass.button_exec)
        solo_track_14_button = Button('Solo Track 14 Button', (664, 7, 27, 10), [solo_track_hover_image, solo_track_active_image], Bass.button_exec)
        solo_track_15_button = Button('Solo Track 15 Button', (714, 7, 27, 10), [solo_track_hover_image, solo_track_active_image], Bass.button_exec)
        solo_track_16_button = Button('Solo Track 16 Button', (764, 7, 27, 10), [solo_track_hover_image, solo_track_active_image], Bass.button_exec)

        knob_sprite = ImageButtonState('active', './sprite.png', (0, 117, 259, 26))
        reverb_track_1_knob = Knob('Reverb Track 1 Knob', (13, 51, 26, 26), knob_sprite, None, Bass.knob_exec)
        reverb_track_2_knob = Knob('Reverb Track 2 Knob', (63, 51, 26, 26), knob_sprite, None, Bass.knob_exec)
        reverb_track_3_knob = Knob('Reverb Track 3 Knob', (113, 51, 26, 26), knob_sprite, None, Bass.knob_exec)
        reverb_track_4_knob = Knob('Reverb Track 4 Knob', (163, 51, 26, 26), knob_sprite, None, Bass.knob_exec)
        reverb_track_5_knob = Knob('Reverb Track 5 Knob', (213, 51, 26, 26), knob_sprite, None, Bass.knob_exec)
        reverb_track_6_knob = Knob('Reverb Track 6 Knob', (263, 51, 26, 26), knob_sprite, None, Bass.knob_exec)
        reverb_track_7_knob = Knob('Reverb Track 7 Knob', (313, 51, 26, 26), knob_sprite, None, Bass.knob_exec)
        reverb_track_8_knob = Knob('Reverb Track 8 Knob', (363, 51, 26, 26), knob_sprite, None, Bass.knob_exec)
        reverb_track_9_knob = Knob('Reverb Track 9 Knob', (413, 51, 26, 26), knob_sprite, None, Bass.knob_exec)
        reverb_track_10_knob = Knob('Reverb Track 10 Knob', (463, 51, 26, 26), knob_sprite, None, Bass.knob_exec)
        reverb_track_11_knob = Knob('Reverb Track 11 Knob', (513, 51, 26, 26), knob_sprite, None, Bass.knob_exec)
        reverb_track_12_knob = Knob('Reverb Track 12 Knob', (563, 51, 26, 26), knob_sprite, None, Bass.knob_exec)
        reverb_track_13_knob = Knob('Reverb Track 13 Knob', (613, 51, 26, 26), knob_sprite, None, Bass.knob_exec)
        reverb_track_14_knob = Knob('Reverb Track 14 Knob', (663, 51, 26, 26), knob_sprite, None, Bass.knob_exec)
        reverb_track_15_knob = Knob('Reverb Track 15 Knob', (713, 51, 26, 26), knob_sprite, None, Bass.knob_exec)
        reverb_track_16_knob = Knob('Reverb Track 16 Knob', (763, 51, 26, 26), knob_sprite, None, Bass.knob_exec)
        chorus_track_1_knob = Knob('Chorus Track 1 Knob', (13, 96, 26, 26), knob_sprite, None, Bass.knob_exec)
        chorus_track_2_knob = Knob('Chorus Track 2 Knob', (63, 96, 26, 26), knob_sprite, None, Bass.knob_exec)
        chorus_track_3_knob = Knob('Chorus Track 3 Knob', (113, 96, 26, 26), knob_sprite, None, Bass.knob_exec)
        chorus_track_4_knob = Knob('Chorus Track 4 Knob', (163, 96, 26, 26), knob_sprite, None, Bass.knob_exec)
        chorus_track_5_knob = Knob('Chorus Track 5 Knob', (213, 96, 26, 26), knob_sprite, None, Bass.knob_exec)
        chorus_track_6_knob = Knob('Chorus Track 6 Knob', (263, 96, 26, 26), knob_sprite, None, Bass.knob_exec)
        chorus_track_7_knob = Knob('Chorus Track 7 Knob', (313, 96, 26, 26), knob_sprite, None, Bass.knob_exec)
        chorus_track_8_knob = Knob('Chorus Track 8 Knob', (363, 96, 26, 26), knob_sprite, None, Bass.knob_exec)
        chorus_track_9_knob = Knob('Chorus Track 9 Knob', (413, 96, 26, 26), knob_sprite, None, Bass.knob_exec)
        chorus_track_10_knob = Knob('Chorus Track 10 Knob', (463, 96, 26, 26), knob_sprite, None, Bass.knob_exec)
        chorus_track_11_knob = Knob('Chorus Track 11 Knob', (513, 96, 26, 26), knob_sprite, None, Bass.knob_exec)
        chorus_track_12_knob = Knob('Chorus Track 12 Knob', (563, 96, 26, 26), knob_sprite, None, Bass.knob_exec)
        chorus_track_13_knob = Knob('Chorus Track 13 Knob', (613, 96, 26, 26), knob_sprite, None, Bass.knob_exec)
        chorus_track_14_knob = Knob('Chorus Track 14 Knob', (663, 96, 26, 26), knob_sprite, None, Bass.knob_exec)
        chorus_track_15_knob = Knob('Chorus Track 15 Knob', (713, 96, 26, 26), knob_sprite, None, Bass.knob_exec)
        chorus_track_16_knob = Knob('Chorus Track 16 Knob', (763, 96, 26, 26), knob_sprite, None, Bass.knob_exec)
        pan_track_1_knob = Knob('Pan Track 1 Knob', (13, 141, 26, 26), knob_sprite, None, Bass.knob_exec)
        pan_track_2_knob = Knob('Pan Track 2 Knob', (63, 141, 26, 26), knob_sprite, None, Bass.knob_exec)
        pan_track_3_knob = Knob('Pan Track 3 Knob', (113, 141, 26, 26), knob_sprite, None, Bass.knob_exec)
        pan_track_4_knob = Knob('Pan Track 4 Knob', (163, 141, 26, 26), knob_sprite, None, Bass.knob_exec)
        pan_track_5_knob = Knob('Pan Track 5 Knob', (213, 141, 26, 26), knob_sprite, None, Bass.knob_exec)
        pan_track_6_knob = Knob('Pan Track 6 Knob', (263, 141, 26, 26), knob_sprite, None, Bass.knob_exec)
        pan_track_7_knob = Knob('Pan Track 7 Knob', (313, 141, 26, 26), knob_sprite, None, Bass.knob_exec)
        pan_track_8_knob = Knob('Pan Track 8 Knob', (363, 141, 26, 26), knob_sprite, None, Bass.knob_exec)
        pan_track_9_knob = Knob('Pan Track 9 Knob', (413, 141, 26, 26), knob_sprite, None, Bass.knob_exec)
        pan_track_10_knob = Knob('Pan Track 10 Knob', (463, 141, 26, 26), knob_sprite, None, Bass.knob_exec)
        pan_track_11_knob = Knob('Pan Track 11 Knob', (513, 141, 26, 26), knob_sprite, None, Bass.knob_exec)
        pan_track_12_knob = Knob('Pan Track 12 Knob', (563, 141, 26, 26), knob_sprite, None, Bass.knob_exec)
        pan_track_13_knob = Knob('Pan Track 13 Knob', (613, 141, 26, 26), knob_sprite, None, Bass.knob_exec)
        pan_track_14_knob = Knob('Pan Track 14 Knob', (663, 141, 26, 26), knob_sprite, None, Bass.knob_exec)
        pan_track_15_knob = Knob('Pan Track 15 Knob', (713, 141, 26, 26), knob_sprite, None, Bass.knob_exec)
        pan_track_16_knob = Knob('Pan Track 16 Knob', (763, 141, 26, 26), knob_sprite, None, Bass.knob_exec)
        pan_track_1_knob.draw(4)
        pan_track_2_knob.draw(4)
        pan_track_3_knob.draw(4)
        pan_track_4_knob.draw(4)
        pan_track_5_knob.draw(4)
        pan_track_6_knob.draw(4)
        pan_track_7_knob.draw(4)
        pan_track_8_knob.draw(4)
        pan_track_9_knob.draw(4)
        pan_track_10_knob.draw(4)
        pan_track_11_knob.draw(4)
        pan_track_12_knob.draw(4)
        pan_track_13_knob.draw(4)
        pan_track_14_knob.draw(4)
        pan_track_15_knob.draw(4)
        pan_track_16_knob.draw(4)

        mixer_font = pygame.font.Font("./fonts/conthrax-sb.ttf", 12)
        mixer_slider_puller = Puller('./sprite.png', (913, 63, 29, 16))
        volume_track_1_text = Text('Volume Track 1 Text', (13, 174), mixer_font, '100')
        volume_track_2_text = Text('Volume Track 2 Text', (63, 174), mixer_font, '100')
        volume_track_3_text = Text('Volume Track 3 Text', (113, 174), mixer_font, '100')
        volume_track_4_text = Text('Volume Track 4 Text', (163, 174), mixer_font, '100')
        volume_track_5_text = Text('Volume Track 5 Text', (213, 174), mixer_font, '100')
        volume_track_6_text = Text('Volume Track 6 Text', (263, 174), mixer_font, '100')
        volume_track_7_text = Text('Volume Track 7 Text', (313, 174), mixer_font, '100')
        volume_track_8_text = Text('Volume Track 8 Text', (363, 174), mixer_font, '100')
        volume_track_9_text = Text('Volume Track 9 Text', (413, 174), mixer_font, '100')
        volume_track_10_text = Text('Volume Track 10 Text', (463, 174), mixer_font, '100')
        volume_track_11_text = Text('Volume Track 11 Text', (513, 174), mixer_font, '100')
        volume_track_12_text = Text('Volume Track 12 Text', (563, 174), mixer_font, '100')
        volume_track_13_text = Text('Volume Track 13 Text', (613, 174), mixer_font, '100')
        volume_track_14_text = Text('Volume Track 14 Text', (663, 174), mixer_font, '100')
        volume_track_15_text = Text('Volume Track 15 Text', (713, 174), mixer_font, '100')
        volume_track_16_text = Text('Volume Track 16 Text', (763, 174), mixer_font, '100')
        volume_track_1_slider = Slider('Volume Track 1 Slider', (11, 202), 100, mixer_slider_puller, volume_track_1_text, 0, 100, Bass.slider_exec)
        volume_track_2_slider = Slider('Volume Track 2 Slider', (62, 202), 100, mixer_slider_puller, volume_track_2_text, 0, 100, Bass.slider_exec)
        volume_track_3_slider = Slider('Volume Track 3 Slider', (111, 202), 100, mixer_slider_puller, volume_track_3_text, 0, 100, Bass.slider_exec)
        volume_track_4_slider = Slider('Volume Track 4 Slider', (162, 202), 100, mixer_slider_puller, volume_track_4_text, 0, 100, Bass.slider_exec)
        volume_track_5_slider = Slider('Volume Track 5 Slider', (211, 202), 100, mixer_slider_puller, volume_track_5_text, 0, 100, Bass.slider_exec)
        volume_track_6_slider = Slider('Volume Track 6 Slider', (262, 202), 100, mixer_slider_puller, volume_track_6_text, 0, 100, Bass.slider_exec)
        volume_track_7_slider = Slider('Volume Track 7 Slider', (311, 202), 100, mixer_slider_puller, volume_track_7_text, 0, 100, Bass.slider_exec)
        volume_track_8_slider = Slider('Volume Track 8 Slider', (362, 202), 100, mixer_slider_puller, volume_track_8_text, 0, 100, Bass.slider_exec)
        volume_track_9_slider = Slider('Volume Track 9 Slider', (411, 202), 100, mixer_slider_puller, volume_track_9_text, 0, 100, Bass.slider_exec)
        volume_track_10_slider = Slider('Volume Track 10 Slider', (462, 202), 100, mixer_slider_puller, volume_track_10_text, 0, 100, Bass.slider_exec)
        volume_track_11_slider = Slider('Volume Track 11 Slider', (511, 202), 100, mixer_slider_puller, volume_track_11_text, 0, 100, Bass.slider_exec)
        volume_track_12_slider = Slider('Volume Track 12 Slider', (562, 202), 100, mixer_slider_puller, volume_track_12_text, 0, 100, Bass.slider_exec)
        volume_track_13_slider = Slider('Volume Track 13 Slider', (611, 202), 100, mixer_slider_puller, volume_track_13_text, 0, 100, Bass.slider_exec)
        volume_track_14_slider = Slider('Volume Track 14 Slider', (662, 202), 100, mixer_slider_puller, volume_track_14_text, 0, 100, Bass.slider_exec)
        volume_track_15_slider = Slider('Volume Track 15 Slider', (711, 202), 100, mixer_slider_puller, volume_track_15_text, 0, 100, Bass.slider_exec)
        volume_track_16_slider = Slider('Volume Track 16 Slider', (762, 202), 100, mixer_slider_puller, volume_track_16_text, 0, 100, Bass.slider_exec)

        mute_track_hover_image = ImageButtonState('hover', './sprite.png', (308, 134, 27, 10))
        mute_track_active_image = ImageButtonState('active', './sprite.png', (278, 134, 27, 10))
        mute_tack_1_button = Button('Mute Track 1 Button', (14, 22, 27, 10),
                                    [mute_track_hover_image, mute_track_active_image], Bass.mute_track, slider=volume_track_1_slider)
        mute_tack_2_button = Button('Mute Track 2 Button', (64, 22, 27, 10),
                                    [mute_track_hover_image, mute_track_active_image], Bass.mute_track,
                                    slider=volume_track_2_slider)
        mute_tack_3_button = Button('Mute Track 3 Button', (114, 22, 27, 10),
                                    [mute_track_hover_image, mute_track_active_image], Bass.mute_track,
                                    slider=volume_track_3_slider)
        mute_tack_4_button = Button('Mute Track 4 Button', (164, 22, 27, 10),
                                    [mute_track_hover_image, mute_track_active_image], Bass.mute_track,
                                    slider=volume_track_4_slider)
        mute_tack_5_button = Button('Mute Track 5 Button', (214, 22, 27, 10),
                                    [mute_track_hover_image, mute_track_active_image], Bass.mute_track,
                                    slider=volume_track_5_slider)
        mute_tack_6_button = Button('Mute Track 6 Button', (264, 22, 27, 10),
                                    [mute_track_hover_image, mute_track_active_image], Bass.mute_track,
                                    slider=volume_track_6_slider)
        mute_tack_7_button = Button('Mute Track 7 Button', (314, 22, 27, 10),
                                    [mute_track_hover_image, mute_track_active_image], Bass.mute_track,
                                    slider=volume_track_7_slider)
        mute_tack_8_button = Button('Mute Track 8 Button', (364, 22, 27, 10),
                                    [mute_track_hover_image, mute_track_active_image], Bass.mute_track,
                                    slider=volume_track_8_slider)
        mute_tack_9_button = Button('Mute Track 9 Button', (414, 22, 27, 10),
                                    [mute_track_hover_image, mute_track_active_image], Bass.mute_track,
                                    slider=volume_track_9_slider)
        mute_tack_10_button = Button('Mute Track 10 Button', (464, 22, 27, 10),
                                    [mute_track_hover_image, mute_track_active_image], Bass.mute_track,
                                    slider=volume_track_10_slider)
        mute_tack_11_button = Button('Mute Track 11 Button', (514, 22, 27, 10),
                                    [mute_track_hover_image, mute_track_active_image], Bass.mute_track,
                                    slider=volume_track_11_slider)
        mute_tack_12_button = Button('Mute Track 12 Button', (564, 22, 27, 10),
                                    [mute_track_hover_image, mute_track_active_image], Bass.mute_track,
                                    slider=volume_track_12_slider)
        mute_tack_13_button = Button('Mute Track 13 Button', (614, 22, 27, 10),
                                    [mute_track_hover_image, mute_track_active_image], Bass.mute_track,
                                    slider=volume_track_13_slider)
        mute_tack_14_button = Button('Mute Track 14 Button', (664, 22, 27, 10),
                                    [mute_track_hover_image, mute_track_active_image], Bass.mute_track,
                                    slider=volume_track_14_slider)
        mute_tack_15_button = Button('Mute Track 15 Button', (714, 22, 27, 10),
                                    [mute_track_hover_image, mute_track_active_image], Bass.mute_track,
                                    slider=volume_track_15_slider)
        mute_tack_16_button = Button('Mute Track 16 Button', (764, 22, 27, 10),
                                    [mute_track_hover_image, mute_track_active_image], Bass.mute_track,
                                    slider=volume_track_16_slider)

        change_preset_1_button = Button('Change Preset 1 Button', (7, 315, 36, 12), [], screen.toggle_module, module=PRESET_MODULE)

        module.add_objects_to_render([
            solo_track_1_button,
            solo_track_2_button,
            solo_track_3_button,
            solo_track_4_button,
            solo_track_5_button,
            solo_track_6_button,
            solo_track_7_button,
            solo_track_8_button,
            solo_track_9_button,
            solo_track_10_button,
            solo_track_11_button,
            solo_track_12_button,
            solo_track_13_button,
            solo_track_14_button,
            solo_track_15_button,
            solo_track_16_button,
            mute_tack_1_button,
            mute_tack_2_button,
            mute_tack_3_button,
            mute_tack_4_button,
            mute_tack_5_button,
            mute_tack_6_button,
            mute_tack_7_button,
            mute_tack_8_button,
            mute_tack_9_button,
            mute_tack_10_button,
            mute_tack_11_button,
            mute_tack_12_button,
            mute_tack_13_button,
            mute_tack_14_button,
            mute_tack_15_button,
            mute_tack_16_button,
            reverb_track_1_knob,
            reverb_track_2_knob,
            reverb_track_3_knob,
            reverb_track_4_knob,
            reverb_track_5_knob,
            reverb_track_6_knob,
            reverb_track_7_knob,
            reverb_track_8_knob,
            reverb_track_9_knob,
            reverb_track_10_knob,
            reverb_track_11_knob,
            reverb_track_12_knob,
            reverb_track_13_knob,
            reverb_track_14_knob,
            reverb_track_15_knob,
            reverb_track_16_knob,
            chorus_track_1_knob,
            chorus_track_2_knob,
            chorus_track_3_knob,
            chorus_track_4_knob,
            chorus_track_5_knob,
            chorus_track_6_knob,
            chorus_track_7_knob,
            chorus_track_8_knob,
            chorus_track_9_knob,
            chorus_track_10_knob,
            chorus_track_11_knob,
            chorus_track_12_knob,
            chorus_track_13_knob,
            chorus_track_14_knob,
            chorus_track_15_knob,
            chorus_track_16_knob,
            pan_track_1_knob,
            pan_track_2_knob,
            pan_track_3_knob,
            pan_track_4_knob,
            pan_track_5_knob,
            pan_track_6_knob,
            pan_track_7_knob,
            pan_track_8_knob,
            pan_track_9_knob,
            pan_track_10_knob,
            pan_track_11_knob,
            pan_track_12_knob,
            pan_track_13_knob,
            pan_track_14_knob,
            pan_track_15_knob,
            pan_track_16_knob,
            volume_track_1_text,
            volume_track_2_text,
            volume_track_3_text,
            volume_track_4_text,
            volume_track_5_text,
            volume_track_6_text,
            volume_track_7_text,
            volume_track_8_text,
            volume_track_9_text,
            volume_track_10_text,
            volume_track_11_text,
            volume_track_12_text,
            volume_track_13_text,
            volume_track_14_text,
            volume_track_15_text,
            volume_track_16_text,
            volume_track_1_slider,
            volume_track_2_slider,
            volume_track_3_slider,
            volume_track_4_slider,
            volume_track_5_slider,
            volume_track_6_slider,
            volume_track_7_slider,
            volume_track_8_slider,
            volume_track_9_slider,
            volume_track_10_slider,
            volume_track_11_slider,
            volume_track_12_slider,
            volume_track_13_slider,
            volume_track_14_slider,
            volume_track_15_slider,
            volume_track_16_slider,
            change_preset_1_button
        ])

    @staticmethod
    def preset_module_init(module, screen):
        pass


"""
OBJECTS
"""


class State:
    """
    Interface for states
    """
    WAIT_TIME = 250
    @staticmethod
    def on_enter_state(element):
        raise NotImplementedError

    @staticmethod
    def update(element):
        raise NotImplementedError


"""
KNOB
"""


class IdleKnob(State):
    @staticmethod
    def on_enter_state(knob):
        knob.clear_relative_track_point()

    @staticmethod
    def update(knob):
        if knob.is_mouse_over():
            knob.set_state(knob.STATES["hover"])


class HoverKnob(State):
    @staticmethod
    def on_enter_state(knob):
        pass

    @staticmethod
    def update(knob):
        if not knob.is_mouse_over():
            knob.set_state(knob.STATES["idle"])
        elif knob.is_mouse_button_down():
            knob.set_relative_track_point()
            knob.set_state(knob.STATES["active"])


class ActiveKnob(State):
    @staticmethod
    def on_enter_state(knob):
        pass

    @staticmethod
    def update(knob):
        if not knob.is_mouse_over() or not knob.is_mouse_button_down():
            knob.call_bind_function()
            print('Knob calling ', knob.get_name())
            knob.set_state(knob.STATES["idle"])
        else:
            knob.draw()


class DisabledKnob(State):
    @staticmethod
    def on_enter_state(knob):
        pass

    @staticmethod
    def update(knob):
        pass


class Knob:
    STATES = {
        "idle": IdleKnob,
        "hover": HoverKnob,
        "active": ActiveKnob,
        "disabled": DisabledKnob
    }

    def __init__(self, name, area, knob_sprite, text, function_to_bind, **kwargs):
        self._name = name
        self._area = area
        self._offset_position = (0, 0)
        self._knob_sprite = knob_sprite
        self._surface = pygame.Surface(self.get_size(), pygame.SRCALPHA)
        if DEBUG:
            self._surface.fill((200, 180, 0, 35))
        self._state = None
        self._relative_track_point = None
        self._bounded_function = function_to_bind
        self._kwargs_function = kwargs
        # TODO: Help Text
        self.set_state(self.STATES["idle"])
        self._value = 0
        self.draw()

    def _linear(self, value, min_in, max_in, min_out, max_out):
        a = (float(max_out) - float(min_out)) / (float(max_in) - float(min_in))
        b = float(max_out) - float(a) * float(max_in)
        new_value = float(a) * float(value) + float(b)
        return float(new_value)

    def call_bind_function(self):
        if not self._kwargs_function:
            self._bounded_function()
        else:
            self._bounded_function(self._kwargs_function)

    def get_name(self):
        return self._name

    def get_position(self):
        return self._area[0] + self._offset_position[0], self._area[1] + self._offset_position[1]

    def get_surface(self):
        return self._surface

    def get_size(self):
        return self._area[2], self._area[3]

    def set_state(self, state):
        self._state = state
        self._state.on_enter_state(self)

    def set_offset_height(self, offset):
        self._offset_position = (self._offset_position[0], offset)

    def set_relative_track_point(self):
        self._relative_track_point = pygame.mouse.get_pos()[0]

    def clear_relative_track_point(self):
        self._relative_track_point = None

    def disabled(self, disabled):
        if disabled:
            self.set_state(self.STATES["disabled"])
        else:
            self.set_state(self.STATES["idle"])

    def draw(self, value=None):

        if value is None:
            if self._relative_track_point is not None:
                raw_value = pygame.mouse.get_pos()[0] - self._relative_track_point
                self._value = self._linear(raw_value, -18, 18, 0, 9)
        width, height = self.get_size()
        position_x = width * int(self._value)
        self._surface.blit(self._knob_sprite.get_surface(), (0, 0), (position_x, 0, width, height))

    def is_drawable(self):
        return True

    def is_mouse_over(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        width, height = self.get_size()
        position_x, position_y = self.get_position()
        offset_x = 0
        if position_x - offset_x < mouse_x < position_x + width + offset_x and position_y < mouse_y < position_y + height:
            touching = True
        else:
            touching = False
        return touching

    def is_mouse_button_down(self, button=0):
        return pygame.mouse.get_pressed()[button]

    def update(self):
        self._state.update(self)


"""
BUTTON
"""


class IdleButton(State):
    @staticmethod
    def on_enter_state(button):
        if button.has_state_image("idle"):
            button.set_surface_to_state("idle")
        else:
            button.set_surface_to_state(None)

    @staticmethod
    def update(button):
        if button.is_mouse_over():
            button.set_state(button.STATES["hover"])


class HoverButton(State):
    @staticmethod
    def on_enter_state(button):
        if button.has_state_image("hover"):
            button.set_surface_to_state("hover")
        else:
            button.set_surface_to_state(None)

    @staticmethod
    def update(button):
        if not button.is_mouse_over():
            button.set_state(button.STATES["idle"])
        elif button.is_mouse_button_down():
            button.set_state(button.STATES["active"])
            pygame.time.wait(State.WAIT_TIME)


class ActiveButton(State):
    @staticmethod
    def on_enter_state(button):
        if button.has_state_image("active"):
            button.set_surface_to_state("active")
        else:
            button.set_surface_to_state(None)
        button.call_bind_function()

    @staticmethod
    def update(button):
        if not button.is_hold_active():
            button.set_state(button.STATES["idle"])
        elif button.is_mouse_over() and button.is_mouse_button_down():
            button.set_state(button.STATES["idle"])
            button.call_bind_function()
            pygame.time.wait(State.WAIT_TIME)


class DisabledButton(State):
    @staticmethod
    def on_enter_state(button):
        if button.has_state_image("disabled"):
            button.set_surface_to_state("disabled")
        else:
            button.set_surface_to_state(None)

    @staticmethod
    def update(button):
        pass


class ImageButtonState:
    def __init__(self, state, image_src, area):
        self._name = state
        self._surface = pygame.Surface((area[2], area[3]), pygame.SRCALPHA)
        self._surface.blit(pygame.image.load(image_src), (0, 0), area)
        self._surface.convert()
        self._return()

    def _return(self):
        return self

    def get_name(self):
        return self._name

    def get_surface(self):
        return self._surface


class Button:
    STATES = {
        "idle": IdleButton,
        "hover": HoverButton,
        "active": ActiveButton,
        "disabled": DisabledButton
    }

    def __init__(self, name, area, images_states, function_to_bind, **kwargs):
        self._name = name
        self._surface = None
        self._area = area
        self._offset_position = (0, 0)
        self._images_states = images_states
        self._bounded_function = function_to_bind
        self._kwargs_function = kwargs
        self._hold_active = True
        self._state = None

        self.set_state(self.STATES["idle"])

    def call_bind_function(self):
        if not self._kwargs_function:
            self._bounded_function()
        else:
            self._bounded_function(self._kwargs_function)

    def get_name(self):
        return self._name

    def get_surface(self):
        return self._surface

    def get_position(self):
        return self._area[0] + self._offset_position[0], self._area[1] + self._offset_position[1]

    def get_size(self):
        return self._area[2], self._area[3]

    def set_state(self, state):
        self._state = state
        self._state.on_enter_state(self)

    def set_hold_active(self, active=True):
        self._hold_active = active

    def set_offset_height(self, offset):
        self._offset_position = (self._offset_position[0], offset)

    def set_surface_to_state(self, state):
        if state is None:
            self._surface = pygame.Surface((self._area[2], self._area[3]), pygame.SRCALPHA)
            if DEBUG:
                self._surface.fill((200, 180, 0, 50))
            return
        for image in self._images_states:
            if image.get_name() == state:
                self._surface = image.get_surface()
                break

    def disabled(self, disabled):
        if disabled:
            self.set_state(self.STATES["disabled"])
        else:
            self.set_state(self.STATES["idle"])

    def is_drawable(self):
        return True

    def is_hold_active(self):
        return self._hold_active

    def is_mouse_over(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        width, height = self.get_size()
        position_x, position_y = self.get_position()
        if position_x < mouse_x < position_x + width and position_y < mouse_y < position_y + height:
            touching = True
        else:
            touching = False
        return touching

    def is_mouse_button_down(self, button=0):
        return pygame.mouse.get_pressed()[button]

    def has_state_image(self, state):
        for image in self._images_states:
            if image.get_name() == state:
                return True
        return False

    def update(self):
        self._state.update(self)


"""
SLIDER
"""


class IdleSlider(State):
    @staticmethod
    def on_enter_state(slider):
        slider.draw(slider.get_puller_position())

    @staticmethod
    def update(slider):
        if slider.is_mouse_over():
            slider.set_state(slider.STATES["hover"])


class HoverSlider(State):
    @staticmethod
    def on_enter_state(slider):
        pass

    @staticmethod
    def update(slider):
        if not slider.is_mouse_over():
            slider.set_state(slider.STATES["idle"])
        elif slider.is_mouse_button_down():
            slider.set_state(slider.STATES["active"])


class ActiveSlider(State):
    @staticmethod
    def on_enter_state(slider):
        pass

    @staticmethod
    def update(slider):
        if not slider.is_mouse_button_down() or not slider.is_mouse_over():
            slider.call_binded_function()
            slider.set_state(slider.STATES["idle"])

        slider.draw()


class DisabledSlider(State):
    @staticmethod
    def on_enter_state(slider):
        slider.draw(slider.get_level_bar_height())

    @staticmethod
    def update(slider):
        pass


class Puller:
    def __init__(self, src_image, area):
        self._area = area
        self._surface = pygame.Surface((self._area[2], self._area[3]), pygame.SRCALPHA)
        self._surface.blit(pygame.image.load(src_image), (0, 0), area)
        self._surface.convert()
        self._return()

    def _return(self):
        return self

    def get_size(self):
        return self._area[2], self._area[3]

    def get_surface(self):
        return self._surface


class Slider:
    STATES = {
        "idle": IdleSlider,
        "hover": HoverSlider,
        "active": ActiveSlider,
        "disabled": DisabledSlider
    }

    def __init__(self, name, position, height, puller, text, min, max, function_to_bind, **kwargs):
        self._name = name
        self._offset_position = (0, 0)
        self._puller = puller
        self._puller_position = 0
        self._text = text
        self._bounded_function = function_to_bind
        self._kwargs_function = kwargs
        self._state = None
        self._surface = None
        self._range = min, max

        puller_width, puller_height = self._puller.get_size()
        self._area = (position[0], position[1] - (puller_height / 2), puller_width, puller_height + height)

        self.draw(self._puller_position)

        self.set_state(self.STATES["idle"])

    def _linear(self, value, min_in, max_in, min_out, max_out):
        a = (float(max_out) - float(min_out)) / (float(max_in) - float(min_in))
        b = float(max_out) - float(a) * float(max_in)
        new_value = float(a) * float(value) + float(b)
        return float(new_value)

    def _check_boarder(self, position):
        puller_half_height = self._puller.get_size()[1] / 2
        height = self.get_size()[1]
        if 0 + puller_half_height > position:
            position = 0 + puller_half_height
        elif height - puller_half_height < position:
            position = height - puller_half_height
        return position - puller_half_height

    def _has_text(self):
        return True if self._text is not None else False

    def call_binded_function(self):
        if not self._kwargs_function:
            self._bounded_function()
        else:
            self._bounded_function(self._kwargs_function)

    def draw(self, puller_position=None):
        width, height = self.get_size()
        position_x, position_y = self.get_position()
        self._surface = pygame.Surface((width, height), pygame.SRCALPHA)
        if DEBUG:
            self._surface.fill((200, 180, 0, 35))

        puller_half_height = self._puller.get_size()[1] / 2
        if puller_position is None:
            puller_position = self._check_boarder(pygame.mouse.get_pos()[1] - position_y)
        level_bar_height = self.get_level_bar_height()
        puller_position_inverted = int(self._linear(puller_position, 0, level_bar_height, level_bar_height, 0))

        width_level_bar = 2
        level_bar_surface = pygame.Surface((width_level_bar, puller_position_inverted))
        level_bar_surface.fill((235, 180, 0))

        level_bar = (level_bar_surface, ((self._area[2] / 2) - (width_level_bar / 2), puller_position + puller_half_height))
        puller = (self._puller.get_surface(), (0, puller_position))
        self._surface.blits((level_bar, puller))
        self._puller_position = puller_position
        if self._has_text():
            self._text.render(str(int(self._linear(puller_position_inverted, 0, level_bar_height, self._range[0], self._range[1]))))

    def get_surface(self):
        return self._surface

    def get_position(self):
        return self._area[0] + self._offset_position[0], self._area[1] + self._offset_position[1]

    def get_puller_position(self):
        return self._puller_position

    def get_size(self):
        return self._area[2], self._area[3]

    def get_level_bar_height(self):
        return self.get_size()[1] - self._puller.get_size()[1]

    def get_state(self):
        return self._state

    def set_offset_height(self, offset):
        self._offset_position = (self._offset_position[0], offset)

    def set_puller_position(self, position):
        self._puller_position = position

    def set_state(self, state):
        self._state = state
        self._state.on_enter_state(self)

    def disabled(self, disabled):
        if disabled:
            pre_mute_puller_position = self.get_puller_position()
            self.set_state(self.STATES["disabled"])
            self.set_puller_position(pre_mute_puller_position)
        else:
            self.set_state(self.STATES["idle"])

    def is_drawable(self):
        return True

    def is_mouse_over(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        width, height = self.get_size()
        position_x, position_y = self.get_position()
        if position_x < mouse_x < position_x + width and position_y < mouse_y < position_y + height:
            touching = True
        else:
            touching = False
        return touching

    def is_mouse_button_down(self, button=0):
        return pygame.mouse.get_pressed()[button]

    def update(self):
        self._state.update(self)


"""
TEXT
"""


class Text:
    def __init__(self, name, position, font, content, color=(255, 255, 255)):
        self._name = name
        self._position = position
        self._offset_position = (0, 0)
        self._font = font
        self._surface = None
        self._color = color
        self.render(content)

    def get_surface(self):
        return self._surface

    def get_position(self):
        return tuple(map(lambda a, b: a + b, self._position, self._offset_position))

    def set_offset_height(self, offset):
        self._offset_position = (self._offset_position[0], offset)

    def set_color(self, color):
        self._color = color

    def is_drawable(self):
        return True

    def render(self, text):
        self._surface = self._font.render(text, True, self._color)

    def update(self):
        pass


app = MidiPlayer()

while True:
    app.update()
