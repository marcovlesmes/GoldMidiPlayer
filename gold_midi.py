"""

"""
import pygame, os, time, datetime, re
from pybass import *
from pybass.pybassmidi import *
from pybass.pybassenc import *
from encrypter import SoundCoder
from Tkinter import Tk
from tkFileDialog import askopenfilename

DEBUG = True

WINDOW_INIT_X = 800
WINDOW_INIT_Y = 344
WINDOW_PIANO_ROLL_Y = 114
WINDOW_MIXER_Y = 344
WINDOW_SETTINGS_Y = 350
WINDOW_PLAYLIST_Y = 216
WINDOW_MAIN_HELP_TEXT_POSITION = (24, 324)
WINDOW_SETTINGS_HELP_TEXT_POSITION = (533, 8)

GOLD_MIDI_TEXT_NAME_POSITION = (158, 173)
GOLD_MIDI_TEXT_TIME_POSITION = (158, 240)
GOLD_MIDI_TEXT_CURRENT_TIME_POSITION = (155, 215)
GOLD_MIDI_TEXT_CURRENT_GLOBAL_VOLUME = (87, 114)
GOLD_MIDI_TEXT_CURRENT_PITCH = (640, 114)
GOLD_MIDI_TEXT_CURRENT_TEMPO = (705, 114)

COLOR_YELLOW = (235, 180, 0)

EVENT_ON_SCREEN_CHANGE = 0

EVENT_ON_MOUSE_CLICK_PB = 10
EVENT_ON_MOUSE_RELEASE = 11
EVENT_ON_MOUSE_IN = 12
EVENT_ON_MOUSE_OUT = 13
EVENT_ON_MOUSE_DRAG = 14
EVENT_ON_MOUSE_CLICK_RELEASE = 15

EVENT_ON_KEY_PRESS = 20

EVENT_ON_DYNAMIC_TEXT = 30
EVENT_OFF_DYNAMIC_TEXT = 31
EVENT_REFRESH_TEXT = 32
EVENT_HELP_TEXT_ON = 33
EVENT_HELP_TEXT_OFF = 34
EVENT_REFRESH_ELEMENT = 35

STATE_ELEMENT_IDLE = 40
STATE_ELEMENT_HOVER = 41
STATE_ELEMENT_ACTIVE = 42
STATE_ELEMENT_INACTIVE = 43
STATE_GOLD_MIDI_STOP = 44
STATE_GOLD_MIDI_PAUSED = 45
STATE_GOLD_MIDI_PLAYING = 46

MAIN_SCREEN = 50
PIANO_ROLL_SCREEN = 51
MIXER_SCREEN = 52
SETTINGS_SCREEN = 53
PLAYLIST_SCREEN = 54
PROGRAM_SCREEN = 55

MIX_ATTR_INDEX = 'index'
MIX_ATTR_BANK = 'bank'
MIX_ATTR_PROGRAM = 'program'
MIX_ATTR_VOLUME = 'volume'
MIX_ATTR_PAN = 'pan'
MIX_ATTR_SOLO = 'solo'
MIX_ATTR_MUTE = 'mute'
MIX_ATTR_REVERB = 'reverb'
MIX_ATTR_CHORUS = 'chorus'
MIX_ATTR_REVERB_DELAY = 'reverb_delay'
MIX_ATTR_CHORUS_DELAY = 'chorus_delay'


class App:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Gold Midi Player")
        # Windows Setup
        self._window_size = None
        self._screen = None
        self._clock = pygame.time.Clock()
        self._events_buffer = []
        self._targets_area = []
        self._render_screen = []
        self._interface = None
        self.start()

    def start(self):
        """
        The objects have to register the target_area.
        :return:
        """
        self._interface = MidiPlayer.get_instance()
        loaded_screen = self._interface.toggle_screen(MAIN_SCREEN)
        if not loaded_screen:
            raise Exception('Main Screen is not loaded')

    def event_manager(self):
        """
        Fill self._events_buffer with the events registered in Pygame
        :return:
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif len(self._targets_area) > 0:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    clicked_element = self.get_interaction()
                    if clicked_element is not None:
                        self._events_buffer.append([EVENT_ON_MOUSE_CLICK_PB, clicked_element])
                elif event.type == pygame.MOUSEBUTTONUP:
                    all_active_elements = self.get_all_active_elements()
                    for element in all_active_elements:
                        self._events_buffer.append([EVENT_ON_MOUSE_RELEASE, element])
                elif event.type == pygame.MOUSEMOTION:
                    if pygame.mouse.get_focused():
                        on_element = self.get_interaction()
                        if on_element and on_element.is_drag_enabled():
                            print("Dragging on element: ", on_element)
                            self._events_buffer.append([EVENT_ON_MOUSE_DRAG, on_element])
                        elif on_element:
                            active_element = self.get_active_element()
                            if active_element is not on_element:
                                self._events_buffer.append([EVENT_ON_MOUSE_IN, on_element])
                        else:
                            active_element = self.get_active_element()
                            if active_element and active_element.is_drag_enabled():
                                self._events_buffer.append([EVENT_ON_MOUSE_DRAG, active_element])
                            else:
                                hover_element = self.get_hovered_element()
                                if hover_element:
                                    self._events_buffer.append([EVENT_ON_MOUSE_OUT, hover_element])
                elif event.type == pygame.KEYDOWN:
                    self._events_buffer.append([EVENT_ON_KEY_PRESS, event])
            if event.type == pygame.USEREVENT and event.custom_type == EVENT_ON_SCREEN_CHANGE:
                    self._events_buffer.append([EVENT_ON_SCREEN_CHANGE, event.screen])
                    # pygame.event.clear()
            elif event.type == pygame.USEREVENT:
                if event.custom_type == EVENT_HELP_TEXT_ON or event.custom_type == EVENT_HELP_TEXT_OFF:
                    self._events_buffer.append([event.custom_type, None])
                elif event.custom_type == EVENT_REFRESH_ELEMENT:
                    self._events_buffer.append([event.custom_type, event.element, event.value])
                else:
                    self._events_buffer.append([event.custom_type, event.element])

    def event_exec(self):
        """
        Execute all the events (update elements) on the buffer
        :return:
        """
        for event in self._events_buffer:
            event_type, event_data = event[0], event[1]
            if event_type == EVENT_ON_SCREEN_CHANGE:
                self.update_screen()
            elif event_type == EVENT_HELP_TEXT_ON:
                self._interface.set_help_text_on()
            elif event_type == EVENT_HELP_TEXT_OFF:
                self._interface.set_help_text_off()
            elif event_type == EVENT_REFRESH_ELEMENT:
                event_value = event[2]
                event_data.update(event_type, event_value)
            else:
                event_data.update(event_type)
        self._events_buffer = []

    def update_screen(self):
        self._render_screen = self._interface.render()
        print("========================= UPDATE SCREEN =======================")
        for e in self._render_screen:
            print(e.get_name())
        print("===================================================================")
        self.get_targets_areas()
        self._window_size = self._interface.window_size
        self._screen = pygame.display.set_mode(self._window_size)

    def update(self):
        """
        This function is executed every time the screen is updated
        :return:
        """
        self._clock.tick(40)
        self.event_manager()
        self.event_exec()
        self.refresh_screen()

    def get_window_size(self):
        return self._window_size

    def get_targets_areas(self):
        if len(self._render_screen) > 0:
            over_map = []
            for field in self._render_screen:
                if field.has_target():
                    over_map.append(field)
            self._targets_area = over_map
        else:
            print('WARNING: There is nothing loaded in the screen. Interface must be started.')

    def get_active_element(self):
        if len(self._render_screen) > 0:
            for element in self._render_screen:
                if element.get_state() == STATE_ELEMENT_ACTIVE:
                    return element
        return False

    def get_all_active_elements(self):
        if len(self._render_screen) > 0:
            elements = []
            for element in self._render_screen:
                if element.get_state() == STATE_ELEMENT_ACTIVE:
                    elements.append(element)
        return elements

    def get_hovered_element(self):
        if len(self._render_screen) > 0:
            for element in self._render_screen:
                if element.get_state() == STATE_ELEMENT_HOVER:
                    return element
        return False

    def get_interaction(self):
        """
        Return the index of the element when the cursor are over it
        :return:
        """
        x, y = pygame.mouse.get_pos()

        for element in self._targets_area:
            element_coords = element.get_coordinates()
            if element_coords[0][0] < x < (element_coords[0][0] + element_coords[1][0]):
                if element_coords[0][1] < y < (element_coords[0][1] + element_coords[1][1]):
                    return element

        return None

    def refresh_screen(self):
        """
        Render all the list of elements
        :return:
        """
        self._screen.fill((0, 0, 0))
        for element in self._render_screen:
            self._screen.blit(element.get_surface(), element.get_position())
        pygame.display.update()
        # pygame.display.flip()


class MidiPlayer:
    _instance = None

    @staticmethod
    def get_instance():
        if MidiPlayer._instance is None:
            MidiPlayer()
        return MidiPlayer._instance

    def __init__(self):
        if MidiPlayer._instance is not None:
            raise Exception('This class is a singleton"')
        else:
            MidiPlayer._instance = self

            BASS_Init(-1, 44100, 0, 0, 0)
            self._main_screen = None
            self._playlist_screen = None
            self._mixer_screen = None
            self._program_screen = None
            self._piano_roll_screen = None
            self._settings_screen = None
            self._render_elements = []
            self._active_screens = []
            self.playlist = Playlist()
            self.window_size = (WINDOW_INIT_X, WINDOW_INIT_Y)

    def get_element_by_name(self, name):
        for element in self._render_elements:
            if element.get_name() == name:
                return element
        return None

    def get_main_screen(self):
        if self._main_screen is None:
            self._main_screen = MainScreen.get_instance()
            self._main_screen.set_get_elements_function(self.draw_main_screen)
        return self._main_screen

    def get_playlist_screen(self):
        if self._playlist_screen is None:
            self._playlist_screen = PlaylistScreen.get_instance()
            self._playlist_screen.set_get_elements_function(self.draw_playlist_screen)
        return self._playlist_screen

    def get_mixer_screen(self):
        if self._mixer_screen is None:
            self._mixer_screen = MixerScreen.get_instance()
            self._mixer_screen.set_get_elements_function(self.draw_mixer_screen)
        return self._mixer_screen

    def get_program_screen(self):
        if self._program_screen is None:
            self._program_screen = ProgramScreen.get_instance()
            self._program_screen.set_get_elements_function(self.draw_program_screen)
        return self._program_screen

    def get_piano_roll_screen(self):
        if self._piano_roll_screen is None:
            self._piano_roll_screen = PianoRollScreen.get_instance()
            self._piano_roll_screen.set_get_elements_function(self.draw_piano_roll_screen)
        return self._piano_roll_screen

    def _get_settings_screen(self):
        if self._settings_screen is None:
            self._settings_screen = SettingsScreen.get_instance()
            self._settings_screen.set_get_elements_function(self.draw_settings_screen)
        return self._settings_screen

    def get_bank_text(self, channel):
        return str(self.playlist.get_mixer_value(channel, MIX_ATTR_BANK))

    def get_program_text(self, params):
        channel, limit = params
        position = str(self.playlist.get_mixer_value(channel, MIX_ATTR_PROGRAM))
        programs = self.get_dict_programs()
        if programs.get(position):
            program = programs.get(position)[:limit]
        else:
            program = 'N/A'
        return program

    def get_float_current_global_volume(self):
        return self.playlist.get_global_volume()

    def get_str_current_global_volume(self):
        return str(self.playlist.get_global_volume() * 100).split('.')[0]

    def get_str_current_pitch(self):
        transpose = Utility.convert_to_zero_twohundred_scale(self.playlist.get_transpose())
        if transpose > 100:
            text = '+' + str(int(transpose * 0.5))
        elif transpose < 100:
            text = '-' + str(100 - transpose)
        else:
            text = '-'
        return str(text)

    def get_str_current_tempo(self):
        tempo = self.playlist.get_tempo();
        if tempo < 0.5:
            tempo_str = '-' + str(int(Utility.linear(tempo, 0, 0.5, 100, 0)))
        elif tempo > 0.5:
            tempo_str = '+' + str(int(Utility.linear(tempo, 0.5, 1, 0, 100)))
        else:
            tempo_str = '+0'
        return tempo_str

    def get_tempo(self):
        return self.playlist.get_tempo()

    def get_transpose(self):
        return self.playlist.get_transpose()

    def get_midi_name(self):
        midi = self.playlist.get_active_file()
        if midi:
            return midi.get_name()
        return 'No MIDI file'

    def get_midi_time(self):
        midi = self.playlist.get_active_file()
        if midi:
            return Utility.format_time(midi.get_length())
        return '00:00:00'

    def get_current_midi_time(self):
        midi = self.playlist.get_active_file()
        if midi:
            return Utility.format_time(midi.get_current_time())
        return '00:00:00'

    def get_element_by_state(self, state):
        if len(self._render_elements) > 0:
            for element in self._render_elements:
                if element.get_state() == state:
                    return element
        return False

    def get_hover_element_help_text(self):
        hover_element = self.get_element_by_state(STATE_ELEMENT_HOVER)
        if hover_element:
            return hover_element.get_help_text()
        else:
            return 'No action.'

    def get_window_size(self):
        return self.window_size

    def get_channel_volume(self, channel):
        return self.playlist.get_channel_volume(channel)

    def get_str_channel_volume(self, channel):
        return str(int(Utility.linear(self.playlist.get_channel_volume(channel), 0, 127, 0, 100))) + "%"

    def get_channel_rev(self, channel):
        return self.playlist.get_channel_rev(channel)

    def get_channel_chorus(self, channel):
        return self.playlist.get_channel_chorus(channel)

    def get_channel_pan(self, channel):
        return self.playlist.get_channel_pan(channel)

    def set_global_volume(self, level):
        pygame.event.post(
            pygame.event.Event(
                pygame.USEREVENT,
                {
                    "custom_type": EVENT_REFRESH_TEXT,
                    "element": self.get_element_by_name('Current Volume')
                }
            )
        )
        self.playlist.set_global_volume(level)

    def set_tempo(self, tempo):
        pygame.event.post(
            pygame.event.Event(
                pygame.USEREVENT,
                {
                    "custom_type": EVENT_REFRESH_TEXT,
                    "element": self.get_element_by_name('Current Tempo')
                }
            )
        )
        self.playlist.set_tempo(tempo)

    def set_transpose(self, key):
        pygame.event.post(
            pygame.event.Event(
                pygame.USEREVENT,
                {
                    "custom_type": EVENT_REFRESH_TEXT,
                    "element": self.get_element_by_name('Current Pitch')
                }
            )
        )
        self.playlist.set_transpose(key)

    def set_channel_volume(self, channel, value):
        # volume level (0-127)
        pygame.event.post(
            pygame.event.Event(
                pygame.USEREVENT,
                {
                    "custom_type": EVENT_REFRESH_TEXT,
                    "element": self.get_element_by_name('channel_' + str(channel) + '_text_volume')
                }
            )
        )
        self.playlist.set_channel_volume(channel, value)

    def set_channel_chorus(self, channel, value):
        self.playlist.set_channel_chorus(channel, value)

    def set_channel_pan(self, channel, value):
        # pan position (0-128, 0=left, 64=middle, 127=right
        self.playlist.set_channel_pan(channel, value)

    def set_channel_rev(self, channel, value):
        self.playlist.set_channel_rev(channel, value)

    def set_solo_track(self, channel):
        self.playlist.set_solo_track(channel)

    def set_mute_track(self, channel):
        self.playlist.set_mute_track(channel)

    def _set_window_size(self, size):
        self.window_size = size

    def set_help_text_on(self):
        help_text = self.get_element_by_name('Help Text')
        if help_text:
            help_text.draw_text(self.get_hover_element_help_text())

    def set_help_text_off(self):
        help_text = self.get_element_by_name('Help Text')
        if help_text:
            help_text.draw_text('')

    def change_program(self, channel):
        print("Change program channel ", channel)
        self.toggle_screen(MIXER_SCREEN)
        self.toggle_screen(PROGRAM_SCREEN)

    def toggle_screen(self, screen):
        pygame.event.post(
            pygame.event.Event(
                pygame.USEREVENT,
                custom_type=EVENT_ON_SCREEN_CHANGE,
                screen=screen
            )
        )
        if screen in self._active_screens:
            self._active_screens.remove(screen)
            return False
        else:
            self._active_screens.append(screen)
            return True

    def render(self):
        """
        Get all the elements to render
        :return:
        """
        print(self._active_screens)
        self._render_elements = []
        if SETTINGS_SCREEN in self._active_screens:
            # TODO: self._render_elements = self.get_settings_screen().get_screen_elements()
            settings_screen = self._get_settings_screen()
            self._render_elements = settings_screen.get_screen_elements()
            self._set_window_size((WINDOW_INIT_X, WINDOW_SETTINGS_Y))
        else:
            screen_height = 0
            if MAIN_SCREEN in self._active_screens:
                main_screen = self.get_main_screen()
                self._render_elements = main_screen.get_screen_elements()
                screen_height = main_screen.get_size_y()
            if PLAYLIST_SCREEN in self._active_screens:
                playlist_screen = self.get_playlist_screen()
                self._render_elements += playlist_screen.get_screen_elements(screen_height)
                screen_height += playlist_screen.get_size_y()
            if PROGRAM_SCREEN in self._active_screens:
                program_screen = self.get_program_screen()
                self._render_elements += program_screen.get_screen_elements(screen_height)
                screen_height += program_screen.get_size_y()
            elif MIXER_SCREEN in self._active_screens:
                mixer_screen = self.get_mixer_screen()
                mixer_screen.set_elements()
                self._render_elements += mixer_screen.get_screen_elements(screen_height, init=True)
                screen_height += mixer_screen.get_size_y()
            if PIANO_ROLL_SCREEN in self._active_screens:
                piano_roll_screen = self.get_piano_roll_screen()
                self._render_elements += piano_roll_screen.get_screen_elements(screen_height)
                screen_height += piano_roll_screen.get_size_y()
            self._set_window_size((WINDOW_INIT_X, screen_height))
        return self._render_elements

    def draw_main_screen(self):
        return [
            Image(name='main_screen', position=(0, 0), size=(WINDOW_INIT_X, WINDOW_INIT_Y)),
            Button(
                name='playlist',
                position=(151, 157),
                size=(442, 45),
                action=self.toggle_screen,
                params_action=PLAYLIST_SCREEN,
                idle_hover_active_state_image=['sprite'],
                idle_hover_active_sprite_offset_position=[(59, 0),  (501, 0)],
                help_text='Show/Hide Playlist'
            ),
            Text(
                content='MIDI Name',
                position=GOLD_MIDI_TEXT_NAME_POSITION,
                font='./fonts/conthrax-sb.ttf',
                font_size=14,
                update_function=self.get_midi_name
            ),
            Text(
                content='MIDI Time',
                position=GOLD_MIDI_TEXT_TIME_POSITION,
                font='./fonts/conthrax-sb.ttf',
                font_size=10,
                update_function=self.get_midi_time
            ),
            Text(
                content='MIDI Current Time',
                position=GOLD_MIDI_TEXT_CURRENT_TIME_POSITION,
                font='./fonts/conthrax-sb.ttf',
                font_size=21,
                update_function=self.get_current_midi_time
            ),
            Text(
                content='Current Volume',
                position=GOLD_MIDI_TEXT_CURRENT_GLOBAL_VOLUME,
                font='./fonts/conthrax-sb.ttf',
                update_function=self.get_str_current_global_volume
            ),
            Text(
                content='Current Pitch',
                position=GOLD_MIDI_TEXT_CURRENT_PITCH,
                font='./fonts/conthrax-sb.ttf',
                update_function=self.get_str_current_pitch
            ),
            Text(
                content='Current Tempo',
                position=GOLD_MIDI_TEXT_CURRENT_TEMPO,
                font='./fonts/conthrax-sb.ttf',
                update_function=self.get_str_current_tempo
            ),
            Text(
                content='Help Text',
                position=WINDOW_MAIN_HELP_TEXT_POSITION,
                update_function=self.get_hover_element_help_text
            ),
            VerticalSlider(
                puller_image_name='volume',
                position=(87, 147),
                size=(30, 159),
                puller_size=(30, 16),
                exec_function=self.set_global_volume,
                get_function=self.get_float_current_global_volume
            ),
            VerticalSlider(
                puller_image_name='tempo',
                position=(710, 147),
                size=(30, 159),
                puller_size=(30, 16),
                init_puller_position=0.5,
                exec_function=self.set_tempo,
                get_function=self.get_tempo
            ),
            VerticalSlider(
                puller_image_name='transpose',
                position=(636, 147),
                size=(30, 159),
                puller_size=(30, 16),
                init_puller_position=0.5,
                exec_function=self.set_transpose,
                get_function=self.get_transpose
            ),
            Button(
                name='open_file',
                position=(143, 92),
                size=(54, 58),
                action=self.open_new_midi,
                idle_hover_active_state_image=['sprite'],
                idle_hover_active_sprite_offset_position=[(0, 0), (0, 59)],
                help_text='Open new MIDI file'
            ),
            Button(
                name='save_file',
                position=(199, 92),
                size=(54,58),
                action=self.save_file,
                idle_hover_active_state_image=['sprite'],
                idle_hover_active_sprite_offset_position=[(0, 0), (58, 59)],
                help_text='Save file'
            ),
            Button(
                name='mixer',
                position=(430, 92),
                size=(54, 58),
                action=self.toggle_screen,
                params_action=MIXER_SCREEN,
                idle_hover_active_state_image=['sprite'],
                idle_hover_active_sprite_offset_position=[(0, 0), (289, 59)],
                help_text='Show/Hide Mixer'
            ),
            Button(
                name='piano_roll',
                position=(488, 92),
                size=(54, 58),
                action=self.toggle_screen,
                params_action=PIANO_ROLL_SCREEN,
                idle_hover_active_state_image=['sprite'],
                idle_hover_active_sprite_offset_position=[(0, 0), (350, 59)],
                help_text='Show/Hide Piano roll'
            ),
            Button(
                name='open_sound_font',
                position=(258, 92),
                size=(54, 58),
                action=self.open_sound_font,
                idle_hover_active_state_image=['sprite'],
                idle_hover_active_sprite_offset_position=[(0, 0), (116, 59)],
                help_text='Open new SoundFont file'
            ),
            Button(
                name='convert_to_csf',
                position=(316, 92),
                size=(54, 58),
                action=self.convert_sf2_to_csf,
                idle_hover_active_state_image=['sprite'],
                idle_hover_active_sprite_offset_position=[(0, 0), (175, 59)],
                help_text='Convert SF2 to CSF format'
            ),
            Button(
                name="export_file",
                position=(372, 92),
                size=(54, 58),
                action=self.export_file,
                idle_hover_active_state_image=['sprite'],
                idle_hover_active_sprite_offset_position=[(0, 0), (232, 59)],
                help_text='Export as MP3 file'
            ),
            Button(
                name='settings',
                position=(545, 92),
                size=(54, 58),
                action=self.toggle_screen,
                params_action=SETTINGS_SCREEN,
                idle_hover_active_state_image=['sprite'],
                idle_hover_active_sprite_offset_position=[(0, 0), (407, 59)],
                help_text='Toggle Settings Screen'
            ),
            Button(
                name='rewind',
                position=(273, 263),
                size=(52, 53),
                action=self.rewind,
                idle_hover_active_state_image=['sprite'],
                idle_hover_active_sprite_offset_position=[(0, 0), (520, 47)],
                help_text='Rewind'
            ),
            Button(
                name='play',
                position=(493, 263),
                size=(52, 53),
                action=self.play,
                idle_hover_active_state_image=['sprite'],
                idle_hover_active_sprite_offset_position=[(0, 0), (739, 47), (738, 102)],
                help_text='Play'
            ),
            Button(
                name='pause',
                position=(547, 263),
                size=(52, 53),
                action=self.play,
                idle_hover_active_state_image=['sprite'],
                idle_hover_active_sprite_offset_position=[(0, 0), (790, 47), (790, 102)],
                help_text='Play'
            ),
            Button(
                name='stop',
                position=(438, 263),
                size=(52, 53),
                action=self.stop,
                idle_hover_active_state_image=['sprite'],
                idle_hover_active_sprite_offset_position=[(0, 0), (684, 47)],
                help_text='Stop'
            ),
            Button(
                name='forward',
                position=(329, 263),
                size=(52, 53),
                action=self.forward,
                idle_hover_active_state_image=['sprite'],
                idle_hover_active_sprite_offset_position=[(0, 0), (576, 47)],
                help_text='Forward'
            )
        ]

    # TODO: Delete function
    def get_dict_programs(self):
        if self.playlist.get_soundfont():
            data = BASS_MIDI_FONTINFO()
            BASS_MIDI_FontGetInfo(self.playlist.get_soundfont()[-1], data)
            index_preset = 0
            index_bank = 0
            preset = ''
            programs = {}
            while preset is not None:
                preset = BASS_MIDI_FontGetPreset(self.playlist.get_soundfont()[-1], index_preset, index_bank)
                if preset:
                    programs.update({str(index_preset): preset})
                index_preset += 1
            return programs
        else:
            import xml.etree.ElementTree as et
            file = et.parse('./general_midi.xml')
            root = file.getroot()
            programs = {}
            for program in root:
                programs.update({program[0].text: program[1].text})
            return programs

        return {}

    def draw_settings_screen(self):
        return [
            Image(
                name='settings_screen',
                position=(0, 0),
                size=(WINDOW_INIT_X, WINDOW_SETTINGS_Y)
            ),
            Button(
                name='settings',
                position=(757, 3),
                size=(37, 37),
                action=self.toggle_screen,
                params_action=SETTINGS_SCREEN,
                idle_hover_active_state_image=['sprite'],
                idle_hover_active_sprite_offset_position=[(0, 0), (325, 0)],
                help_text='Toggle Settings Screen'
            ),
            Text(
                content='Help Text',
                position=WINDOW_SETTINGS_HELP_TEXT_POSITION,
                update_function=self.get_hover_element_help_text
            )

        ]

    def draw_mixer_screen(self):
        i = 0
        x_dist = self.get_window_size()[0] / 16
        bank_x_coord = 8
        program_x_coord = 12
        solo_buttons_x_coord = 14
        mute_buttons_x_coord = 14
        sliders_x_coord = 15
        rev_chorus_pan_buttons_x_coord = 13
        channels_count = self.playlist.get_mixer_channels_count()
        # TODO: Draw ON/OFF elements OR draw OFF and switch

        elements = [
            Image(
                name='mixer_screen',
                position=(0, 0),
                size=(WINDOW_INIT_X, WINDOW_MIXER_Y)
            )
        ]
        while i < channels_count:
            elements.append(
                Text(
                    content='PROGRAM',
                    position=(program_x_coord, 317),
                    update_function=self.get_program_text,
                    params_function=[i, 4]
                )
            )
            elements.append(
                Button(
                    name='solo',
                    position=(solo_buttons_x_coord, 7),
                    size=(27, 10),
                    action=self.set_solo_track,
                    params_action=i,
                    idle_hover_active_state_image=['sprite'],
                    idle_hover_active_sprite_offset_position=[(0, 0), (308, 119), (278, 119)],
                    help_text='Solo channel'
                )
            )
            elements.append(
                Button(
                    name='mute',
                    position=(mute_buttons_x_coord, 22),
                    size=(27, 10),
                    action=self.set_mute_track,
                    params_action=i,
                    idle_hover_active_state_image=['sprite'],
                    idle_hover_active_sprite_offset_position=[(0, 0), (308, 134), (278, 134)],
                    help_text='Mute channel'
                )
            )
            elements.append(
                Button(
                    name='Change program',
                    position=(program_x_coord, 317),
                    size=(34, 8),
                    action=self.change_program,
                    params_action=i,
                    idle_hover_active_state_image=['sprite'],
                    idle_hover_active_sprite_offset_position=[(0, 0)],
                    help_text='Change program'
                )
            )
            elements.append(
                VerticalSlider(
                    puller_image_name='channel_' + str(i) + '_volume',
                    position=(sliders_x_coord, 196),
                    size=(24, 115),
                    puller_size=(16, 27),
                    exec_function=self.set_channel_volume,
                    params_function=i,
                    get_function=self.get_channel_volume,
                    max_value=127
                )
            )
            elements.append(
                Text(
                    content='channel_' + str(i) + '_text_volume',
                    position=(program_x_coord, 177),
                    update_function=self.get_str_channel_volume,
                    params_function=i
                )
            )
            elements.append(
                RollButton(
                    name='reverb',
                    position=(rev_chorus_pan_buttons_x_coord, 51),
                    size=(29, 29),
                    exec_function=self.set_channel_rev,
                    get_function=self.get_channel_rev,
                    params_function=i,
                    init_sprite_position=110
                )
            )
            elements.append(
                RollButton(
                    name='chorus',
                    position=(rev_chorus_pan_buttons_x_coord, 96),
                    size=(29, 29),
                    exec_function=self.set_channel_chorus,
                    get_function=self.get_channel_chorus,
                    params_function=i,
                    init_sprite_position=110
                )
            )
            elements.append(
                RollButton(
                    name='pan',
                    position=(rev_chorus_pan_buttons_x_coord, 141),
                    size=(29, 29),
                    exec_function=self.set_channel_pan,
                    get_function=self.get_channel_pan,
                    params_function=i,
                    init_sprite_position=1
                )
            )
            i += 1
            bank_x_coord += x_dist
            program_x_coord += x_dist
            solo_buttons_x_coord += x_dist
            mute_buttons_x_coord += x_dist
            sliders_x_coord += x_dist
            rev_chorus_pan_buttons_x_coord += x_dist
        return elements

    def draw_program_screen(self):
        return [
            Text(
                content='Program Screen',
                position=(10, 10),
                update_function=self.get_program_text,
                params_function=[0, 20]
            )
        ]

    def draw_piano_roll_screen(self):
        return [
            Image(name='piano_roll_screen', position=(0, 0), size=(WINDOW_INIT_X, WINDOW_PIANO_ROLL_Y))
        ]

    def draw_playlist_screen(self):
        elements = [
            Image(
                name='playlist_screen',
                position=(0, 0),
                size=(WINDOW_INIT_X, WINDOW_PLAYLIST_Y)
            )
        ]

        playlist = self.playlist.get_playlist()
        offset = 0
        for midi in playlist:
            elements.append(
                Text(
                    content='MIDI name',
                    position=(25, 56 + offset),
                    update_function=midi.get_name
                )
            )
            elements.append(
                Text(
                    content='MIDI path',
                    position=(212, 56 + offset),
                    update_function=midi.get_short_path
                )
            )
            elements.append(
                Text(
                    content='MIDI ',
                    position=(404, 56 + offset),
                    update_function=midi.get_length
                )
            )
            offset += 18
        return elements

    def play(self):
        if self.playlist.get_player_state() != STATE_GOLD_MIDI_PLAYING:
               self.playlist.play()
               pygame.event.post(
                   pygame.event.Event(
                       pygame.USEREVENT,
                       {
                           "custom_type": EVENT_ON_DYNAMIC_TEXT,
                           "element": self.get_element_by_name('MIDI Current Time')
                       }
                   )
               )
        else:
            self.playlist.pause()
            pygame.event.post(
                pygame.event.Event(
                    pygame.USEREVENT,
                    {
                        "custom_type": EVENT_OFF_DYNAMIC_TEXT,
                        "element": self.get_element_by_name('MIDI Current Time')
                    }
                )
            )

    def stop(self):
        self.playlist.stop()
        pygame.event.post(
            pygame.event.Event(
                pygame.USEREVENT,
                {
                    "custom_type": EVENT_OFF_DYNAMIC_TEXT,
                    "element": self.get_element_by_name('MIDI Current Time')
                }
            )
        )
        pygame.event.post(
            pygame.event.Event(
                pygame.USEREVENT,
                {
                    "custom_type": EVENT_REFRESH_TEXT,
                    "element": self.get_element_by_name('MIDI Current Time')
                }
            )
        )
        pygame.event.post(
            pygame.event.Event(
                pygame.USEREVENT,
                {
                    "custom_type": EVENT_ON_MOUSE_CLICK_RELEASE,
                    "element": self.get_element_by_name('play')
                }
            )
        )

    def rewind(self):
        self.playlist.rewind()

    def forward(self):
        self.playlist.forward()

    def open_new_midi(self):
        # TODO: if file was saved ask for open it
        saved_file = self.playlist.open_new_midi()
        pygame.event.post(
            pygame.event.Event(
                pygame.USEREVENT,
                {
                    "custom_type": EVENT_REFRESH_TEXT,
                    "element": self.get_element_by_name('MIDI Name')
                }
            )
        )
        pygame.event.post(
            pygame.event.Event(
                pygame.USEREVENT,
                {
                    "custom_type": EVENT_REFRESH_TEXT,
                    "element": self.get_element_by_name('MIDI Time')
                }
            )
        )
        if saved_file:
            pygame.event.post(
                pygame.event.Event(
                    pygame.USEREVENT,
                    {
                        "custom_type": EVENT_REFRESH_ELEMENT,
                        "element": self.get_element_by_name('volume'),
                        "value": saved_file['global_volume']
                    }
                )
            )
            pygame.event.post(
                pygame.event.Event(
                    pygame.USEREVENT,
                    {
                        "custom_type": EVENT_REFRESH_TEXT,
                        "element": self.get_element_by_name('Current Volume')
                    }
                )
            )
            pygame.event.post(
                pygame.event.Event(
                    pygame.USEREVENT,
                    {
                        "custom_type": EVENT_REFRESH_ELEMENT,
                        "element": self.get_element_by_name('tempo'),
                        "value": saved_file['tempo']
                    }
                )
            )
            pygame.event.post(
                pygame.event.Event(
                    pygame.USEREVENT,
                    {
                        "custom_type": EVENT_REFRESH_TEXT,
                        "element": self.get_element_by_name('Current Tempo')
                    }
                )
            )
            pygame.event.post(
                pygame.event.Event(
                    pygame.USEREVENT,
                    {
                        "custom_type": EVENT_REFRESH_ELEMENT,
                        "element": self.get_element_by_name('transpose'),
                        "value": saved_file['transpose']
                    }
                )
            )
            pygame.event.post(
                pygame.event.Event(
                    pygame.USEREVENT,
                    {
                        "custom_type": EVENT_REFRESH_TEXT,
                        "element": self.get_element_by_name('Current Pitch')
                    }
                )
            )
            # print(saved_file)
        pygame.event.post(
            pygame.event.Event(
                pygame.USEREVENT,
                {
                    "custom_type": EVENT_ON_SCREEN_CHANGE,
                    "screen": PLAYLIST_SCREEN
                }
            )
        )

    def save_file(self):
        self.playlist.save_file()

    def open_sound_font(self):
        self.playlist.open_sound_font()
        # TODO: Delete Event
        pygame.event.post(
            pygame.event.Event(
                pygame.USEREVENT,
                {
                    "custom_type": EVENT_REFRESH_TEXT,
                    "element": self.get_element_by_name('Debug')
                }
            )
        )

    def convert_sf2_to_csf(self):
        Tk().withdraw()
        sound_font_path = askopenfilename(
            initialdir="./",
            title="Select SF2 file",
            filetypes=(("SF2 files", "*.sf2"), ("all files", "*.*"))
        )

        if sound_font_path:
            if sound_font_path.find('.sf2', -4) > 5:
                result = SoundCoder().encrypt_sound_found(sound_font_path)

    def export_file(self):
        self.playlist.export_file()


class Screen:
    def __init__(self, size_y):
        self._get_elements_function = None
        self._elements = None
        self._elements_init_pos_y = []
        self._size_y = size_y

    def _init_elements(self, origin_y):
        self._elements = self._get_elements_function()
        self._elements_init_pos_y = []
        if self._elements:
            for element in self._elements:
                self._elements_init_pos_y.append(element.get_position()[1])

            if origin_y is not 0:
                i = 0
                for element in self._elements:
                    element_x, element_y = element.get_position()
                    element.set_position((element_x, self._elements_init_pos_y[i] + origin_y))
                    i += 1
        else:
            print('Screen() > get_screen_elements(): Dont have screen elements')

    def get_screen_elements(self, origin_y=0, init=False):
        init = False
        if self._elements is None or init:
            self._init_elements(origin_y)
        print("============= Function Elements ==========")
        for e in self._elements:
            print(e.get_name())
        print("=========================================")
        return self._elements

    def get_size_y(self):
        return self._size_y

    def set_get_elements_function(self, function):
        if self._get_elements_function is None:
            self._get_elements_function = function


class MainScreen(Screen):
    _instance = None

    @staticmethod
    def get_instance():
        if MainScreen._instance is None:
            MainScreen()
        return MainScreen._instance

    def __init__(self):
        if MainScreen._instance is not None:
            raise Exception('This class is a singleton"')
        else:
            MainScreen._instance = self
            Screen.__init__(self, WINDOW_INIT_Y)


class PlaylistScreen(Screen):
    _instance = None

    @staticmethod
    def get_instance():
        if PlaylistScreen._instance is None:
            PlaylistScreen()
        return PlaylistScreen._instance

    def __init__(self):
        if PlaylistScreen._instance is not None:
            raise Exception('This class is a singleton"')
        else:
            PlaylistScreen._instance = self
        Screen.__init__(self, WINDOW_PLAYLIST_Y)


class MixerScreen(Screen):
    _instance = None

    @staticmethod
    def get_instance():
        if MixerScreen._instance is None:
            MixerScreen()
        return MixerScreen._instance

    def __init__(self):
        if MixerScreen._instance is not None:
            raise Exception('This class is a singleton"')
        else:
            MixerScreen._instance = self
        Screen.__init__(self, WINDOW_MIXER_Y)

    def set_elements(self):
        if self._elements is not None:
            # print (self._elements, "\n")
            return 0


class ProgramScreen(Screen):
    _instance = None

    @staticmethod
    def get_instance():
        if ProgramScreen._instance is None:
            ProgramScreen()
        return ProgramScreen._instance

    def __init__(self):
        if ProgramScreen._instance is not None:
            raise Exception('This class is a singleton"')
        else:
            ProgramScreen._instance = self
        Screen.__init__(self, WINDOW_MIXER_Y)


class PianoRollScreen(Screen):
    _instance = None

    @staticmethod
    def get_instance():
        if PianoRollScreen._instance is None:
            PianoRollScreen()
        return PianoRollScreen._instance

    def __init__(self):
        if PianoRollScreen._instance is not None:
            raise Exception('This class is a singleton"')
        else:
            PianoRollScreen._instance = self
        Screen.__init__(self, WINDOW_PIANO_ROLL_Y)


class SettingsScreen(Screen):
    _instance = None

    @staticmethod
    def get_instance():
        if SettingsScreen._instance is None:
            SettingsScreen()
        return SettingsScreen._instance

    def __init__(self):
        if SettingsScreen._instance is not None:
            raise Exception('This class is a singleton"')
        else:
            SettingsScreen._instance = self
        Screen.__init__(self, WINDOW_SETTINGS_Y)


class Playlist:

    def __init__(self):
        self._midi_list = []
        self._sound_font_list = []
        self._player_state = STATE_GOLD_MIDI_STOP
        self._mixer_channels = {}
        self._global_volume = 1
        self._tempo = 0.5
        self._transpose = 0.5

    def get_active_file(self):
        if not len(self._midi_list) > 0:
            return None
        for midi in self._midi_list:
            if midi.get_state() == STATE_ELEMENT_ACTIVE:
                return midi
        print('WARNING: Exist MIDI files in playlist but none are active (STATE_ELEMENT_ACTIVE.)')
        return None

    def get_player_state(self):
        return self._player_state

    def get_global_volume(self):
        return self._global_volume

    def get_tempo(self):
        return self._tempo

    def get_transpose(self):
        return self._transpose

    def get_mixer_channels(self):
        return self._mixer_channels

    def get_mixer_channels_count(self):
        return len(self._mixer_channels)

    def get_mixer_value(self, channel, param):
        if param in self._mixer_channels['channel_' + str(channel)]:
            return self._mixer_channels.get('channel_' + str(channel)).get(param)

    def get_channel_volume(self, channel):
        return self.get_mixer_value(channel, MIX_ATTR_VOLUME)

    def get_channel_rev(self, channel):
        return self.get_mixer_value(channel, MIX_ATTR_REVERB)

    def get_channel_chorus(self, channel):
        return self.get_mixer_value(channel, MIX_ATTR_CHORUS)

    def get_channel_pan(self, channel):
        return self.get_mixer_value(channel, MIX_ATTR_PAN)

    def get_playlist(self):
        return self._midi_list

    def get_soundfont(self):
        return self._sound_font_list

    def set_mixer_value(self, channel, param, value):
        if param in self._mixer_channels['channel_' + str(channel)]:
            self._mixer_channels['channel_' + str(channel)][param] = value

    def set_mixer_channels(self, midi):
        self._mixer_channels = {}
        for index in range(0, midi.get_tracks()):
            Utility.set_nested_value(
                self._mixer_channels,
                ['channel_' + str(index), MIX_ATTR_INDEX],
                index
            )
            Utility.set_nested_value(
                self._mixer_channels,
                ['channel_' + str(index), MIX_ATTR_BANK],
                BASS_MIDI_StreamGetEvent(
                    self.get_active_file().get_hstream_handle(), index, MIDI_EVENT_BANK
                )
            )
            Utility.set_nested_value(
                self._mixer_channels,
                ['channel_' + str(index), MIX_ATTR_PROGRAM],
                BASS_MIDI_StreamGetEvent(
                    self.get_active_file().get_hstream_handle(), index, MIDI_EVENT_PROGRAM
                )
            )
            Utility.set_nested_value(
                self._mixer_channels,
                ['channel_' + str(index), MIX_ATTR_VOLUME],
                BASS_MIDI_StreamGetEvent(
                    self.get_active_file().get_hstream_handle(), index, MIDI_EVENT_VOLUME
                )
            )
            Utility.set_nested_value(
                self._mixer_channels,
                ['channel_' + str(index), MIX_ATTR_PAN],
                BASS_MIDI_StreamGetEvent(
                    self.get_active_file().get_hstream_handle(), index, MIDI_EVENT_PAN
                )
            )
            Utility.set_nested_value(
                self._mixer_channels,
                ['channel_' + str(index), MIX_ATTR_SOLO],
                False
            )
            Utility.set_nested_value(
                self._mixer_channels,
                ['channel_' + str(index), MIX_ATTR_MUTE],
                False
            )
            Utility.set_nested_value(
                self._mixer_channels,
                ['channel_' + str(index), MIX_ATTR_REVERB],
                BASS_MIDI_StreamGetEvent(
                    self.get_active_file().get_hstream_handle(), index, MIDI_EVENT_REVERB
                )
            )
            Utility.set_nested_value(
                self._mixer_channels,
                ['channel_' + str(index), MIX_ATTR_CHORUS],
                BASS_MIDI_StreamGetEvent(
                    self.get_active_file().get_hstream_handle(), index, MIDI_EVENT_CHORUS
                )
            )
            Utility.set_nested_value(
                self._mixer_channels,
                ['channel_' + str(index), MIX_ATTR_REVERB_DELAY],
                BASS_MIDI_StreamGetEvent(
                    self.get_active_file().get_hstream_handle(), index, MIDI_EVENT_REVERB_DELAY
                )
            )
            Utility.set_nested_value(
                self._mixer_channels,
                ['channel_' + str(index), MIX_ATTR_CHORUS_DELAY],
                BASS_MIDI_StreamGetEvent(
                    self.get_active_file().get_hstream_handle(), index, MIDI_EVENT_CHORUS_DELAY
                )
            )

    def set_global_volume(self, level):
        self._global_volume = level
        if self.get_active_file():
            BASS_ChannelSetAttribute(self.get_active_file().get_hstream_handle(), BASS_ATTRIB_VOL + 0, level)

    def set_tempo(self, tempo):
        self._tempo = tempo
        tempo_in_mpb = Utility.convert_to_mpb(tempo)
        if self.get_active_file():
            BASS_MIDI_StreamEvent(self.get_active_file().get_hstream_handle(), 0, MIDI_EVENT_TEMPO, tempo_in_mpb)

    def set_transpose(self, transpose):
        self._transpose = transpose
        transpose_in_raw = Utility.convert_to_zero_twohundred_scale(transpose)
        if self.get_active_file():
            for index in range(0, self.get_mixer_channels_count()):
                BASS_MIDI_StreamEvent(
                    self.get_active_file().get_hstream_handle(),
                    index,
                    MIDI_EVENT_TRANSPOSE, transpose_in_raw
                )

    def set_channel_volume(self, channel, level):
        if self.get_active_file():
            BASS_MIDI_StreamEvent(
                self.get_active_file().get_hstream_handle(),
                channel, MIDI_EVENT_VOLUME, int(level)
            )
            self.set_mixer_value(channel, MIX_ATTR_VOLUME, level)

    def set_channel_chorus(self, channel, level):
        BASS_MIDI_StreamEvent(self.get_active_file().get_hstream_handle(), channel, MIDI_EVENT_CHORUS, int(level))

    def set_channel_pan(self, channel, level):
        BASS_MIDI_StreamEvent(self.get_active_file().get_hstream_handle(), channel, MIDI_EVENT_PAN, int(level))

    def set_channel_rev(self, channel, level):
        BASS_MIDI_StreamEvent(self.get_active_file().get_hstream_handle(), channel, MIDI_EVENT_REVERB, int(level))

    def set_solo_track(self, channel):
        if self.get_mixer_value(channel, 'solo'):
            self.set_mixer_value(channel, 'solo', False)
        else:
            self.set_mixer_value(channel, 'solo', True)

        for chn in self._mixer_channels:
            if self._mixer_channels[chn].get('solo') and not self._mixer_channels[chn].get('mute'):
                BASS_MIDI_StreamEvent(
                    self.get_active_file().get_hstream_handle(),
                    self._mixer_channels[chn].get('index'),
                    MIDI_EVENT_VOLUME,
                    self._mixer_channels[chn].get('volume')
                )
            else:
                BASS_MIDI_StreamEvent(
                    self.get_active_file().get_hstream_handle(),
                    self._mixer_channels[chn].get('index'),
                    MIDI_EVENT_VOLUME,
                    0
                )

    def set_mute_track(self, channel):
        if self.get_mixer_value(channel, 'mute'):
            self.set_mixer_value(channel, 'mute', False)
            BASS_MIDI_StreamEvent(
                self.get_active_file().get_hstream_handle(),
                channel,
                MIDI_EVENT_VOLUME,
                self.get_mixer_value(channel, 'volume')
            )
        else:
            self.set_mixer_value(channel, 'mute', True)
            BASS_MIDI_StreamEvent(
                self.get_active_file().get_hstream_handle(),
                channel,
                MIDI_EVENT_VOLUME,
                0
            )

    def add_midi_to_player(self, midi):
        self._midi_list.append(midi)

    def play(self):
        if not self.get_active_file():
            self.open_new_midi()
        BASS_ChannelPlay(self.get_active_file().get_hstream_handle(), False)
        self._player_state = STATE_GOLD_MIDI_PLAYING

    def pause(self):
        BASS_ChannelPause(self.get_active_file().get_hstream_handle())
        self._player_state = STATE_GOLD_MIDI_PAUSED

    def stop(self):
        if self.get_active_file() and self.get_active_file().get_hstream_handle():
            BASS_ChannelStop(self.get_active_file().get_hstream_handle())
            BASS_ChannelSetPosition(self.get_active_file().get_hstream_handle(), 0, BASS_POS_BYTE)
            self._player_state = STATE_GOLD_MIDI_STOP

    def rewind(self):
        if self.get_active_file() and \
                BASS_ChannelIsActive(self.get_active_file().get_hstream_handle()) == BASS_ACTIVE_PLAYING:
            file_position = BASS_ChannelGetPosition(self.get_active_file().get_hstream_handle(), BASS_POS_BYTE)
            return_position = file_position - 1000000
            if return_position < 0:
                return_position = 0
            BASS_ChannelSetPosition(self.get_active_file().get_hstream_handle(), return_position, BASS_POS_BYTE)

    def forward(self):
        if self.get_active_file() and \
                BASS_ChannelIsActive(self.get_active_file().get_hstream_handle()) == BASS_ACTIVE_PLAYING:
            file_position = BASS_ChannelGetPosition(self.get_active_file().get_hstream_handle(), BASS_POS_BYTE)
            return_position = file_position + 1000000
            BASS_ChannelSetPosition(self.get_active_file().get_hstream_handle(), return_position, BASS_POS_BYTE)

    def open_new_midi(self):
        Tk().withdraw()
        self.stop()
        new_midi_path = askopenfilename(
            initialdir="./",
            title="Select MIDI file",
            filetypes=(("MIDI files", "*.mid *.kar"), ("all files", "*.*"))
        )
        if self.get_active_file():
            self.get_active_file().set_state(STATE_ELEMENT_INACTIVE)

        if new_midi_path:
            new_midi = Midi(new_midi_path)
            self.add_midi_to_player(new_midi)
            self.set_mixer_channels(new_midi)
            if os.path.exists(new_midi_path + '.json'):
                import json
                with open(new_midi_path + '.json', 'r') as options:
                    dict_options = json.loads(options.read())
                self.set_global_volume(dict_options['global_volume'])
                self.set_tempo(dict_options['tempo'])
                self.set_transpose(dict_options['transpose'])
                # self.set_mixer_channels(dict_options['mixer_channels'])
                return dict_options
        return False

    def save_file(self):
        import json
        if self.get_active_file():
            info = {
                'global_volume': self.get_global_volume(),
                'tempo': self.get_tempo(),
                'transpose': self.get_transpose(),
                'channel_count': self.get_mixer_channels_count(),
                'mixer_channels': self.get_mixer_channels()
            }
            with open(self.get_active_file().get_path() + '.json', 'w') as write_file:
                write_file.write(json.dumps(info))

    def open_sound_font(self):
        Tk().withdraw()
        new_sound_font = askopenfilename(
            initialdir="./",
            title="Select SoundFont file",
            filetypes=(("SoundFond files", "*.csf *.sf2"), ("all files", "*.*"))
        )
        is_sound_font_coded = False
        file_type_supported = False

        if new_sound_font:
            """ Check if the file is suported and config the loading """
            if new_sound_font.find('.csf', -4) > 5:
                file_type_supported = True
                is_sound_font_coded = True

                new_sound_font = SoundCoder().decrypt_sound_found_in_memory(new_sound_font)

            if new_sound_font and (new_sound_font.find('.sf2', -4) > 5 or new_sound_font.find('.') == -1):
                file_type_supported = True

            """ File is suported. Loading: """
            if file_type_supported:
                self._sound_font_list.append(BASS_MIDI_FontInit(str(new_sound_font), 0))
                init_font = BASS_MIDI_FONT(self._sound_font_list[-1], -1, 0)
                if self.get_active_file() and self.get_active_file().get_hstream_handle() is not None:
                    BASS_MIDI_StreamSetFonts(self.get_active_file().get_hstream_handle(), init_font, 1)

                BASS_MIDI_StreamSetFonts(0, init_font, 1)

            if is_sound_font_coded and os.path.exists(new_sound_font):
                os.remove(new_sound_font)

    def export_file(self):
        if self.get_active_file():
            midi_hstream = self.get_active_file().get_hstream_handle()
            enc_handle = BASS_ENC_Start(midi_hstream, 'lame.exe -h -V 2 - "test.mp3"', 0x10010, None, 0)
            BASS_ChannelPlay(midi_hstream, 0)
            if enc_handle:
                last_perc = -1
                length = BASS_ChannelGetLength(midi_hstream, BASS_POS_BYTE)
                buffer_track = None
                # print(BASS_ChannelGetData(midi_hstream, buffer_track, length))
                """""
                while True:
                    if BASS_ChannelGetData(midi_hstream, buffer_track, len(buffer_track)) == -1:
                        break
                    position = BASS_ChannelGetPosition(midi_hstream, BASS_POS_BYTE)
                    perc = position / length * 100
                    if perc != last_perc:
                        # progress?.Invoke(perc)
                        last_perc = perc
                """""
            else:
                print(BASS_ErrorGetCode())

        else:
            self.open_new_midi()
            self.open_sound_font()


class Midi:
    def __init__(self, path):
        self._path = path
        self._state = STATE_ELEMENT_ACTIVE
        self._hstream_handle = None
        self._size = 0
        self._length = 0
        self._tracks = 0
        self._ticks_per_beat = 0
        self.start()

    def start(self):
        midi_path = self.get_path()
        if midi_path:
            if self.check_extension(midi_path):
                if self._hstream_handle:
                    BASS_ChannelStop(self._hstream_handle)
                self._hstream_handle = BASS_MIDI_StreamCreateFile(False, str(midi_path), 0, 0, 0, 44100)
                self.set_midi_from_file(midi_path)
                self._size = BASS_ChannelGetLength(self._hstream_handle, BASS_POS_BYTE)
                self._length = BASS_ChannelBytes2Seconds(self._hstream_handle, self._size)
            return self
        return None

    def get_hstream_handle(self):
        return self._hstream_handle

    def get_path(self):
        return self._path

    def get_short_path(self):
        return '...' + self._path[-30:]

    def get_name(self):
        name = re.search('.*[/](.*)[.]([a-zA-Z]{3,4}$)', self._path)
        return name.groups()[0]

    def get_length(self):
        return self._length

    def get_current_time(self):
        file_position = BASS_ChannelGetPosition(self.get_hstream_handle(), BASS_POS_BYTE)
        return BASS_ChannelBytes2Seconds(self.get_hstream_handle(), file_position)

    def get_file_size(self):
        return self._size

    def get_state(self):
        return self._state

    def get_tracks(self):
        return self._tracks

    def set_midi_from_file(self, midi_path):
        import binascii
        with open(midi_path, 'rb') as f:
            index_track = 0
            while True:
                content = f.read(4)
                if len(content) == 0:
                    print('End of file')
                    break
                if str(binascii.hexlify(content)).upper() == '4D546864':
                    print('MThd track...')
                    chunk_size = int(binascii.hexlify(f.read(4)), 16)
                    format_file = int(binascii.hexlify(f.read(2)), 16)
                    self._tracks = int(binascii.hexlify(f.read(2)), 16)
                    self._ticks_per_beat = int(binascii.hexlify(f.read(2)), 16)
                elif str(binascii.hexlify(content)).upper() == '4D54726B':
                    chunk_size = int(binascii.hexlify(f.read(4)), 16)
                    raw_track_events = f.read(chunk_size)
                    if index_track == 0:
                        # print(repr(raw_track_events))
                        print(raw_track_events.encode('hex'))
                    index_track += 1

    def set_state(self, state):
        self._state = state

    def check_extension(self, midi_path):
        if midi_path.find('.mid', -4) > 5:
            return True
        if midi_path.find('.kar', -4) > 5:
            return True
        return False


class ObjectWithStates:
    def __init__(
            self,
            name,
            position,
            size,
            init_state,
            exec_function=None,
            params_function=None,
            target=False,
            help_text=None
    ):
        self._name = name
        self._position = position
        self._size = size
        self._state = init_state
        self._surface = None
        self._exec_function = exec_function
        self._params_function = params_function
        self._drag_enabled = False
        self._target = target
        self._help_text = help_text

    def start(self):
        return self

    # EVENT_ON_MOUSE_IN, ON_MOUSE_OFF, ON_MOUSE_CLICK, ON_DRAG, ON_KEY_PRESS, ON_KEY_RELEASE
    def update(self, event_type):
        if event_type == EVENT_ON_MOUSE_IN:
            self.on_mouse_in()
        elif event_type == EVENT_ON_MOUSE_OUT:
            self.on_mouse_out()
        elif event_type == EVENT_ON_MOUSE_CLICK_PB:
            self.on_mouse_click()
        elif event_type == EVENT_ON_MOUSE_DRAG:
            self.on_mouse_drag()
        elif event_type == EVENT_ON_MOUSE_RELEASE:
            self.on_mouse_release()

    def get_name(self):
        return self._name

    def get_coordinates(self):
        return [self._position, self._size]

    def get_surface(self):
        return self._surface

    def get_position(self):
        return self._position

    def get_size(self):
        return self._size

    def get_state(self):
        return self._state

    def get_help_text(self):
        return self._help_text

    def set_state(self, state):
        self._state = state

    def set_position(self, position):
        self._position = position

    def set_draggable(self, option):
        self._drag_enabled = option

    def connect(self, function):
        self._exec_function = function

    def is_drag_enabled(self):
        return self._drag_enabled

    def has_target(self):
        if self._target:
            return True
        return False

    def exec_data_function(self):
        if self._params_function is None:
            return self._exec_function()
        else:
            return self._exec_function(self._params_function)

    def on_mouse_click(self):
        print('Click Button')

    def on_mouse_release(self):
        Cursor.to_idle_state()

    def on_mouse_in(self):
        Cursor.to_hover_state()
        pygame.event.post(
            pygame.event.Event(
                pygame.USEREVENT,
                custom_type=EVENT_HELP_TEXT_ON
            )
        )

    def on_mouse_out(self):
        Cursor.to_idle_state()
        pygame.event.post(
            pygame.event.Event(
                pygame.USEREVENT,
                {
                    "custom_type": EVENT_HELP_TEXT_OFF
                }
            )
        )

    def on_mouse_drag(self):
        pass

    def render(self):
        return [self._surface, self._position]


class Text(ObjectWithStates):
    def __init__(self, content, position, font=None, font_size=16, update_function=None, params_function=None):
        ObjectWithStates.__init__(
            self,
            name=content,
            position=position,
            size=(0, 0),
            init_state=STATE_ELEMENT_IDLE,
            exec_function=update_function,
            params_function=params_function
        )

        self.font_family = font
        self.size_font = font_size
        self.is_dynamic = False
        self._text = None
        self.start()

    def start(self):
        self.draw_text(self.exec_data_function())
        return self

    def draw_text(self, string):
        if not pygame.font.get_init():
            pygame.font.init()
        if not self._text:
            self._text = pygame.font.Font(self.font_family, self.size_font)
        self._surface = self._text.render(string, True, (255, 255, 255))

    def update(self, event_type):
        if event_type == EVENT_ON_DYNAMIC_TEXT:
            self.set_active_state()
        elif event_type == EVENT_OFF_DYNAMIC_TEXT:
            self.set_idle_state()
        elif event_type == EVENT_REFRESH_TEXT:
            self.update_text()
        ObjectWithStates.update(self, event_type)

    def set_active_state(self):
        self.set_state(STATE_ELEMENT_ACTIVE)
        pygame.event.post(
            pygame.event.Event(
                pygame.USEREVENT,
                {
                    "custom_type": EVENT_REFRESH_TEXT,
                    "element": self
                }
            )
        )

    def set_idle_state(self):
        self.set_state(STATE_ELEMENT_IDLE)
        pygame.event.clear(pygame.USEREVENT)

    def update_text(self):
        self.draw_text(self.exec_data_function())
        if self.get_state() == STATE_ELEMENT_ACTIVE:
            pygame.event.post(
                pygame.event.Event(
                    pygame.USEREVENT,
                    {
                        "custom_type": EVENT_REFRESH_TEXT,
                        "element": self
                    }
                )
            )


class Image(ObjectWithStates):
    def __init__(self, name, position, size, offset_position=None):
        ObjectWithStates.__init__(
            self,
            name=name,
            position=position,
            size=size,
            init_state=STATE_ELEMENT_IDLE
        )
        self._offset_position = offset_position
        self.start()

    def start(self):
        self._surface = pygame.image.load(os.path.join(self._name + '.png'))

        if self._offset_position:
            cropped_image = pygame.Surface(self._size, pygame.SRCALPHA)
            cropped_image.blit(
                self._surface,
                self._position,
                (self._offset_position[0], self._offset_position[1], self._size[0], self._size[0])
            )
            self._surface = cropped_image
        return self


class Button(ObjectWithStates):
    """
    idle_hover_active_state_image param take an list of strings with the name
    ["idle", "hover", "active"], ["idle", "hover"], ["hover"]

    idle_hover_active_sprite_offset_position param take an list of tuples with the offset coordinates
    ["idle", "hover", "active"], ["idle", "hover"], ["hover"]
    """
    def __init__(
            self,
            name,
            position,
            size,
            action,
            params_action=None,
            idle_hover_active_state_image=[],
            idle_hover_active_sprite_offset_position=[],
            help_text=None
    ):
        ObjectWithStates.__init__(
            self,
            name=name,
            position=position,
            size=size,
            init_state=STATE_ELEMENT_IDLE,
            exec_function=action,
            params_function=params_action,
            target=True,
            help_text=help_text
        )
        self._states_images = idle_hover_active_state_image
        self._sprite_offset_position_states_images = idle_hover_active_sprite_offset_position
        self._idle_image_surface = None
        self._hover_image_surface = None
        self._active_image_surface = None

        self.start()

    def start(self):
        self._surface = self.create_images_states()
        return self

    def create_images_states(self):
        state_images_count = len(self._states_images)
        offset_image_count = len(self._sprite_offset_position_states_images)
        if state_images_count > 3 or offset_image_count > 3:
            print(
                'ERROR: More than 3 states images or offset coordinates.'
                '["idle", "hover", "active"], ["idle", "hover"], ["hover"]'
            )
        elif state_images_count == 0 and offset_image_count == 0:
            print('WARNING: No images states for button: ' + self.get_name())
            return pygame.Surface(self.get_size())
        else:
            if state_images_count > 2:
                # 3 independent images for states (idle, hover, active). Create "active"
                self._active_image_surface = self.create_image_state(self._states_images[2])
                state_images_count = 2
            if state_images_count > 1:
                # 2 independent images for stages (idle, hover) . Create "hover"
                self._hover_image_surface = self.create_image_state(self._states_images[1])
                state_images_count = 1
            if state_images_count == 1:
                if offset_image_count > 2:
                    # 3 sprite images (idle, hover, active). Create "active"
                    self._active_image_surface = self.create_image_state(
                        self._states_images[0],
                        self._sprite_offset_position_states_images[2]
                    )
                    offset_image_count = 2
                if offset_image_count > 1:
                    # 2 sprite images (idle, hover). Create "hover"
                    self._hover_image_surface = self.create_image_state(
                        self._states_images[0],
                        self._sprite_offset_position_states_images[1]
                    )
                    offset_image_count = 1
                if offset_image_count == 1:
                    # 1 sprite image (idle). Create "idle"
                    self._idle_image_surface = self.create_image_state(
                        self._states_images[0],
                        self._sprite_offset_position_states_images[0]
                    )
                else:
                    # 1 independent images for stage (idle). Create "idle"
                    self._idle_image_surface = self.create_image_state(self._states_images[0])

            return self._idle_image_surface.get_surface()

    def create_image_state(self, name, offset_position=None):
        return Image(
            name=name,
            position=(0, 0),
            size=self.get_size(),
            offset_position=offset_position
        )

    def get_idle_offset_position(self):
        return self._sprite_offset_position_states_images[0]

    def get_hover_offset_position(self):
        return self._sprite_offset_position_states_images[1]

    def get_active_offset_position(self):
        return self._sprite_offset_position_states_images[3]

    def update(self, event_type):
        ObjectWithStates.update(self, event_type)
        if event_type == EVENT_ON_MOUSE_CLICK_RELEASE:
            self.on_mouse_click_release()

    def on_mouse_in(self):
        ObjectWithStates.on_mouse_in(self)
        if self.get_state() != STATE_ELEMENT_ACTIVE:
            if self._hover_image_surface:
                self._surface = self._hover_image_surface.get_surface()
            self.set_state(STATE_ELEMENT_HOVER)

    def on_mouse_out(self):
        ObjectWithStates.on_mouse_out(self)
        if self.get_state() != STATE_ELEMENT_ACTIVE:
            if self._idle_image_surface:
                self._surface = self._idle_image_surface.get_surface()
            self.set_state(STATE_ELEMENT_IDLE)

    def on_mouse_click(self):
        if self._params_function is not None:
            self._exec_function(self._params_function)
        else:
            self._exec_function()
        if self.get_state() == STATE_ELEMENT_ACTIVE:
            self.set_state(STATE_ELEMENT_HOVER)
            if self._hover_image_surface:
                self._surface = self._hover_image_surface.get_surface()
            else:
                if self._idle_image_surface:
                    self._surface = self._idle_image_surface.get_surface()
        else:
            self.set_state(STATE_ELEMENT_ACTIVE)
            if self._active_image_surface:
                self._surface = self._active_image_surface.get_surface()
            elif self._idle_image_surface:
                self._surface = self._idle_image_surface.get_surface()
            else:
                self._surface = pygame.Surface(self.get_size())

    def on_mouse_click_release(self):
        self.set_state(STATE_ELEMENT_IDLE)
        if self._idle_image_surface:
            self._surface = self._idle_image_surface.get_surface()


class Slider(ObjectWithStates):
    def __init__(
            self,
            name,
            position,
            size,
            axis_direction,
            puller_size,
            exec_function,
            get_function,
            level_marker_width,
            init_puller_position,
            min_value,
            max_value,
            params_function=None
    ):
        ObjectWithStates.__init__(
            self,
            name=name,
            position=position,
            size=size,
            init_state=STATE_ELEMENT_IDLE,
            target=True
        )
        self._exec_function = exec_function
        self._get_function = get_function
        self._puller_size = puller_size
        self._level_marker_width = level_marker_width
        self._puller_position = init_puller_position
        self._min_value = min_value
        self._max_value = max_value
        self._axis_direction = axis_direction
        self._params_function = params_function
        self.start()

    def start(self):
        if self._params_function is not None:
            self._puller_position = self._get_function(self._params_function)
        else:
            self._puller_position = self._get_function()
        self.draw_slider()
        return self

    def get_coordinates(self):
        size = list(self._size)
        size[self._axis_direction] += 5
        return [self._position, size]

    def get_total_size(self):
        size = list(self.get_size())
        opposite_axis = 0 if self._axis_direction == 1 else 1
        size[opposite_axis] = self._puller_size[opposite_axis] if self._puller_size[opposite_axis] > self._size[opposite_axis] else self._size[opposite_axis]
        return size

    def get_level_bar_area(self):
        opposite_axis = 0 if self._axis_direction == 1 else 1
        position_axis_direction = self.get_puller_position_in_pixels()
        size_axis_direction = self.get_size()[self._axis_direction] - position_axis_direction -\
                              (self.get_puller_size()[self._axis_direction] / 2)
        init_position = self.get_size()[opposite_axis] / 2 -\
            self._level_marker_width / 2
        level_position = [init_position, init_position]
        level_position[self._axis_direction] = position_axis_direction
        total_size = [self._level_marker_width, self._level_marker_width]
        total_size[self._axis_direction] = size_axis_direction
        return [tuple(level_position), tuple(total_size)]

    def get_puller_size(self):
        return self._puller_size

    def get_puller_position(self):
        return self._puller_position

    def get_puller_position_in_pixels(self):
        return Utility.linear(
            self._puller_position,
            self._min_value,
            self._max_value,
            self.get_total_size()[self._axis_direction] - (self.get_puller_size()[self._axis_direction]),
            0
        )

    def check_borders(self, position):
        new_position = position
        if position < self._min_value:
            new_position = self._min_value
        elif position > self._max_value:
            new_position = self._max_value
        return new_position

    def draw_slider(self):
        self._surface = pygame.Surface(self.get_total_size(), pygame.SRCALPHA)
        position_level, size_level = self.get_level_bar_area()
        level_bar = pygame.Surface(size_level, pygame.SRCALPHA)
        level_bar.fill(COLOR_YELLOW)
        puller = pygame.image.load('slider_puller_v.png')  # FIX
        puller_position = [0, 0]
        puller_position[self._axis_direction] = self.get_puller_position_in_pixels()
        self._surface.blits(((level_bar, position_level), (puller, puller_position)))

    def on_mouse_click(self):
        self.set_draggable(True)
        self.set_state(STATE_ELEMENT_ACTIVE)
        self.set_slider()

    def on_mouse_drag(self):
        if self.is_drag_enabled():
            self.set_slider()

    def set_slider(self):
        mouse_position = pygame.mouse.get_pos()
        value = self.check_borders(Utility.linear(
            ((self.get_total_size()[self._axis_direction] + self.get_position()[self._axis_direction]) -
             mouse_position[self._axis_direction]) + self.get_position()[self._axis_direction],
            self.get_position()[self._axis_direction] + (self.get_puller_size()[self._axis_direction] / 2),
            (self.get_size()[self._axis_direction] - (self.get_puller_size()[self._axis_direction] / 2)) +
            self.get_position()[self._axis_direction],
            self._min_value,
            self._max_value
        ))
        if self._params_function is not None:
            self._exec_function(self._params_function, value)
        else:
            self._exec_function(value)
        self._puller_position = value
        self.draw_slider()

    def on_mouse_release(self):
        ObjectWithStates.on_mouse_release(self)
        self.set_draggable(False)
        self.set_state(STATE_ELEMENT_IDLE)

    def update(self, event_type, event_value=None):
        if event_value:
            self._puller_position = event_value
            self.draw_slider()
        ObjectWithStates.update(self, event_type)


class HorizontalSlider(Slider):
    def __init__(
            self,
            puller_image_name,
            position,
            size,
            puller_size,
            exec_function,
            get_function=None,
            level_marker_width=5,
            init_puller_position=1.0,
            min_value=0,
            max_value=1
    ):
        Slider.__init__(
            self,
            name=puller_image_name,
            position=position,
            size=size,
            puller_size=puller_size,
            exec_function=exec_function,
            get_function=get_function,
            level_marker_width=level_marker_width,
            init_puller_position=init_puller_position,
            min_value=min_value,
            max_value=max_value,
            axis_direction=0
        )


class VerticalSlider(Slider):
    def __init__(
        self,
        puller_image_name,
        position,
        size,
        puller_size,
        exec_function,
        params_function=None,
        get_function=None,
        level_marker_width=3,
        init_puller_position=1.0,
        min_value=0,
        max_value=1
    ):
        Slider.__init__(
            self,
            name=puller_image_name,
            position=position,
            size=size,
            puller_size=puller_size,
            exec_function=exec_function,
            params_function=params_function,
            get_function=get_function,
            level_marker_width=level_marker_width,
            init_puller_position=init_puller_position,
            min_value=min_value,
            max_value=max_value,
            axis_direction=1
        )


class RollButton(ObjectWithStates):
    def __init__(
            self,
            name,
            position,
            size,
            exec_function,
            get_function,
            params_function,
            init_sprite_position,
            image='sprite'
    ):
        ObjectWithStates.__init__(
            self,
            name=name,
            position=position,
            size=size,
            init_state=STATE_ELEMENT_IDLE,
            exec_function=exec_function,
            params_function=params_function,
            target=True
        )
        self._get_function = get_function
        self._init_mouse_position = None
        self._sprite = pygame.image.load(image + '.png')
        self._sprite_position = init_sprite_position
        self.start()

    def start(self):
        if self._params_function is not None:
            self._get_function(self._params_function)
        else:
            self._get_function()
        self.blit_roll_button()

    def scale_value_in_range(self, old_range, new_range, value):
        return ((value - old_range[0]) * (new_range[1] + new_range[0]) / (old_range[1] + old_range[0])) + new_range[0]

    def blit_roll_button(self):
        surface = pygame.Surface(self._size, pygame.SRCALPHA)
        position = round(self._sprite_position / 27) * 27
        surface.blit(self._sprite, (0, 0), pygame.Rect((position, 115), (27, 27)))
        DEBUG = False
        if DEBUG:
            surface.fill((255, 255, 0, 125))
        self._surface = surface

    def on_mouse_click(self):
        self.set_draggable(True)
        self.set_state(STATE_ELEMENT_ACTIVE)
        self._init_mouse_position = pygame.mouse.get_pos()

    def on_mouse_release(self):
        self.set_draggable(False)
        self.set_state(STATE_ELEMENT_IDLE)
        self._init_mouse_position = None
        value = self.scale_value_in_range((1, -243), (0, 127), self._sprite_position) * -1
        self._exec_function(self._params_function, value)

    def on_mouse_drag(self):
        current_position = pygame.mouse.get_pos()
        if self._init_mouse_position:
            value = current_position[0] - self._init_mouse_position[0]
        else:
            value = 0
        if value > 0:
            self._sprite_position += self._size[0]
            if self._sprite_position > 243:
                self._sprite_position = 243
        else:
            self._sprite_position -= self._size[0]
            if self._sprite_position < 1:
                self._sprite_position = 1
        self.blit_roll_button()


class FormField:
    def __init__(self, label, position, size, text=''):
        self._raw_text = text
        self._text = Text(self._raw_text, position, update_function=self.enter_value)
        self._new_key = ''
        self.active = False
        self._debug = DEBUG
        self._position = position
        self._size = size
        self._label = label
        self._enabled = False
        self._padding = (10, 10)

        image = pygame.Surface(self._size, pygame.SRCALPHA)
        if self._debug:
            image.fill((0, 255, 255, 60))

        self._shader = image

    def get_form_field(self):
        return self

    def to_hover_state(self):
        pass

    def to_idle_state(self):
        pass

    def get_coordinates(self):
        return [self._position, self._size]

    def function(self):
        # TODO: Animation of text indicator ON, FormFieldEnabled
        if not self._enabled:
            self._enabled = True

    def enter_value(self):
        if self._enabled:
            if self._new_key == EVENT_KEY_BACKSPACE:
                self._raw_text = self._raw_text[:-1]
            else:
                self._raw_text += self._new_key
            return self._raw_text

    def update(self, event_type):
        if event_type == EVENT_MOUSE_OVER_HOT_SPOT:
            if self._raw_text == '':
                self._shader.fill((0, 150, 255, 255))
        elif event_type == EVENT_MOUSE_OVER_OUT_HOT_SPOT:
            if not self._enabled:
                if self._raw_text == '':
                    self._shader.fill((0, 255, 255, 60))
        elif event_type == EVENT_MOUSE_CLICK_TO_FOCUS_OUT:
            self._enabled = False
            if self._raw_text == '':
                self._shader.fill((0, 255, 255, 60))
        elif event_type == EVENT_KEY_BACKSPACE:
            self._new_key = EVENT_KEY_BACKSPACE
            self._text.update()
            self._shader = self._text.render()[0]
        else:
            if self._enabled:
                try:
                    self._new_key = str(event_type)
                    self._text.update()
                    self._shader = self._text.render()[0]
                    # TODO: Change position
                except UnicodeEncodeError:
                    print('Warning: [FORM FIELD :: UPDATE]  codec can\'t encode character')

    def render(self):
        return [self._shader, self._position]


class Utility:
    @staticmethod
    def linear(value, min_in, max_in, min_out, max_out):
        a = (float(max_out) - float(min_out)) / (float(max_in) - float(min_in))
        b = float(max_out) - float(a) * float(max_in)
        new_value = float(a) * float(value) + float(b)
        return float(new_value)

    @staticmethod
    def format_time(seconds):
        import time
        return time.strftime('%H:%M:%S', time.gmtime(seconds))


    @staticmethod
    def set_nested_value(dic, keys, value):
        for key in keys[:-1]:
            dic = dic.setdefault(key, {})
        dic[keys[-1]] = value

    @staticmethod
    def convert_to_mpb(tempo):
        if tempo < 0.2:
            return 78321
        return int(tempo * 2800000)

    @staticmethod
    def convert_to_zero_twohundred_scale(value):
        return int(value * 200)


class Cursor:
    def __init__(self):
        pass

    @staticmethod
    def to_hover_state():
        pygame.mouse.set_cursor((8, 8), (4, 4), (24, 24, 24, 231, 231, 24, 24, 24), (0, 0, 0, 0, 0, 0, 0, 0))

    @staticmethod
    def to_idle_state():
        pygame.mouse.set_cursor((16, 19), (0, 0), (
            128, 0, 192, 0, 160, 0, 144, 0, 136, 0, 132, 0, 130, 0, 129, 0, 128, 128, 128, 64, 128, 32, 128, 16, 129,
            240,
            137, 0, 148, 128, 164, 128, 194, 64, 2, 64, 1, 128), (
                                    128, 0, 192, 0, 224, 0, 240, 0, 248, 0, 252, 0, 254, 0, 255, 0, 255, 128, 255, 192,
                                    255,
                                    224, 255, 240, 255, 240, 255, 0, 247, 128, 231, 128, 195, 192, 3, 192, 1, 128))


app = App()

while 1:
    app.update()
