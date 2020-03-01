"""

"""

import pygame, sys, os, time, ConfigParser, datetime
from pybass import *
from pybass.pybassmidi import *
from encrypter import SoundCoder
from Tkinter import Tk
from tkFileDialog import askopenfilename

config = ConfigParser.RawConfigParser()
config.read('config.cfg')
DEBUG = False

EVENT_SCREEN_CHANGE = 0
EVENT_MOUSE_OVER_HOT_SPOT = 1
EVENT_MOUSE_OVER_OUT_HOT_SPOT = 2
EVENT_MOUSE_CLICK_TO_FOCUS_OUT = 3
EVENT_MOUSE_BUTTON_UP = 4

TYPE_TEXT_OBJ = 0
TYPE_IMAGE_OBJ = 1
TYPE_BUTTON_OBJ = 2
TYPE_SLIDER_OBJ = 3
TYPE_TEXT_FIELD_OBJ = 4

"""

"""


class App:
    def __init__(self, interface):
        pygame.init()
        pygame.display.set_caption(config.get("interface", "app-name"))
        # Windows Setup
        self.window_size = (config.getint("interface", "screen-size-x"), config.getint("interface", "screen-size-y"))
        self.screen = pygame.display.set_mode(self.window_size)
        self.clock = pygame.time.Clock()
        self.interface = interface
        self.interface_fields = self.interface.get_fields()
        self.hot_spots = self.get_hot_spots()
        self.active_hot_spot = None
        self._active_element = None
        self.interface.set_window_size(self.window_size)
        self.cursor = 'idle'
        self.event = False
        self.volume = 1

    def get_window_size(self):
        return self.window_size

    def update(self):
        self.clock.tick(40)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self._active_element:
                    self._active_element.update(EVENT_MOUSE_CLICK_TO_FOCUS_OUT)
                element = self.mouse_click_hot_spot(pygame.mouse.get_pos())
                if element:
                    self._active_element = element
                    if hasattr(self._active_element, 'function_parameters')\
                            and self._active_element.function_parameters is not None:
                        self._active_element.function(self._active_element.function_parameters)
                    else:
                        self._active_element.function()

            elif event.type == pygame.MOUSEMOTION:
                if pygame.mouse.get_focused():
                    element = self.mouse_over_hot_spot(pygame.mouse.get_pos())
                    if element:
                        pygame.event.post(
                            pygame.event.Event(
                                pygame.USEREVENT,
                                custom_type=EVENT_MOUSE_OVER_HOT_SPOT,
                                index=element
                            )
                        )
                        if self.active_hot_spot and self.active_hot_spot != element:
                            pygame.event.post(
                                pygame.event.Event(
                                    pygame.USEREVENT,
                                    custom_type=EVENT_MOUSE_OVER_OUT_HOT_SPOT,
                                    index=self.active_hot_spot
                                )
                            )
                        self.active_hot_spot = element
                    else:
                        if self.active_hot_spot:
                            pygame.event.post(
                                pygame.event.Event(
                                    pygame.USEREVENT,
                                    custom_type=EVENT_MOUSE_OVER_OUT_HOT_SPOT,
                                    index=self.active_hot_spot
                                )
                            )
                            self.active_hot_spot = None
            elif event.type == pygame.KEYDOWN:
                if pygame.key.name(event.key) == 'up':
                    self.volume += 0.3
                    if self.volume > 1: self.volume = 1
                    self.interface.change_volume(self.volume)
                elif pygame.key.name(event.key) == 'down':
                    self.volume -= 0.3
                    if self.volume < 0: self.volume = 0
                    self.interface.change_volume(self.volume)

                if self._active_element and self._active_element.get_type() == TYPE_TEXT_FIELD_OBJ:
                    self._active_element.update(event.unicode)
            elif event.type == pygame.MOUSEBUTTONUP:
                if self._active_element and self._active_element.get_type() == TYPE_SLIDER_OBJ:
                    self._active_element.update(EVENT_MOUSE_BUTTON_UP)
                    self._active_element = None

            if self._active_element and self._active_element.get_type() == TYPE_SLIDER_OBJ:
                self._active_element.update(pygame.mouse.get_pos())
                self._active_element.render()
            try:
                if event.type == pygame.USEREVENT and event.custom_type == EVENT_MOUSE_OVER_HOT_SPOT:
                    self.interface_fields[event.index].update(event.custom_type)
                if event.type == pygame.USEREVENT and event.custom_type == EVENT_MOUSE_OVER_OUT_HOT_SPOT:
                    self.interface_fields[event.index].update(event.custom_type)
                if event.type == pygame.USEREVENT and event.custom_type == EVENT_SCREEN_CHANGE:
                    self.interface_fields = self.interface.get_fields()
                    self.hot_spots = self.get_hot_spots()
                    self.active_hot_spot = None
                    pygame.event.clear(pygame.USEREVENT)
            except IndexError:
                print('Not element with Index on event. Index: ', pygame.event.get())

        self.refresh_screen()

    """ Reconoce cuando el cursor esta sobre algun punto interactivo (Hot Spot) """
    def mouse_over_hot_spot(self, (x, y)):
        index = 0

        for element in self.hot_spots:
            if element[0][0] < x < (element[0][0] + element[1][0]):
                if element[0][1] < y < (element[0][1] + element[1][1]):
                    return index
            index += 1

        return None

    def mouse_click_hot_spot(self, (x, y)):
        for field in self.interface_fields:
            (button_x, button_y), (button_width, button_height) = field.get_coordinates()

            if button_x < x < (button_x + button_width):
                if button_y < y < (button_y + button_height):
                    return field

        return False

    def get_hot_spots(self):
        over_map = []
        for field in self.interface_fields:
            over_map.append(field.get_coordinates())
        return over_map

    def refresh_screen(self):
        self.screen.fill((0, 0, 0))
        to_render = self.interface.refresh_screen()

        for element in to_render:
            self.screen.blit(element[0], element[1])
        pygame.display.update()

"""

"""

class MidiPlayer:
    def __init__(self):
        BASS_Init(-1, 44100, 0, 0, 0)
        self.GOLD_MIDI_NAME_POSITION = (270, 11)
        self.GOLD_MIDI_TIME_POSITION = (270, 25)
        self.GOLD_MIDI_TIMECOUNT_POSITION = (405, 25)
        self.GOLD_MIDI_STOP = -1
        self.GOLD_MIDI_PAUSED = 0
        self.GOLD_MIDI_PLAYING = 1

        self.fields = []
        self.images = []
        self.texts = []
        self.clock = pygame.time.Clock()
        self.hstream_handle = None
        self.mixer_channels = []
        self._global_volume = 1.0
        self._file_position = '0:00:00'
        self._file_state = self.GOLD_MIDI_STOP
        self.sound_font = 'default.csf'
        self.playlist = Playlist()
        self.window_size = None
        self.active_screen = []

        """
        Loading a default sound font
        """
        sound_font = BASS_MIDI_FONT(BASS_MIDI_FontInit(self.sound_font, 0), -1, 0)
        BASS_MIDI_StreamSetFonts(0, sound_font, 1)
        """
        END of loading a default sound font
        """
        self.call_main_screen()

    def call_main_screen(self):
        screen = self.toggle_screen('main')
        if screen:
            self.draw_main_screen()

    def call_mixer_screen(self):
        screen = self.toggle_screen('mixer')
        if screen:
            self.window_size = (self.window_size[0], self.window_size[1] + 144)
            pygame.display.set_mode(self.window_size)
            position = (0, 91)
            if 'piano_roll' in self.active_screen:
                self.draw_main_screen()
                self.draw_mixer_screen(position)
                position_piano_roll_screen = (0, position[1] + 144)
                self.draw_piano_roll(position_piano_roll_screen)
            else:
                self.draw_mixer_screen(position)
        else:
            self.window_size = (self.window_size[0], self.window_size[1] - 144)
            pygame.display.set_mode(self.window_size)
            if 'piano_roll' in self.active_screen:
                self.draw_main_screen()
                position_piano_roll_screen = (0, 91)
                self.draw_piano_roll(position_piano_roll_screen)
            else:
                self.draw_main_screen()

        pygame.event.post(
            pygame.event.Event(
                pygame.USEREVENT,
                custom_type=EVENT_SCREEN_CHANGE
            )
        )

    def call_piano_roll_screen(self):
        screen = self.toggle_screen('piano_roll')
        if screen:
            self.window_size = (self.window_size[0], self.window_size[1] + 114)
            pygame.display.set_mode(self.window_size)
            if 'mixer' in self.active_screen:
                self.draw_main_screen()
                self.draw_mixer_screen((0, 91))
                self.draw_piano_roll((0, 235))
            else:
                position = (0, 91)
                self.draw_piano_roll(position)
        else:
            self.window_size = (self.window_size[0], self.window_size[1] - 114)
            pygame.display.set_mode(self.window_size)
            if 'mixer' in self.active_screen:
                self.draw_main_screen()
                self.draw_mixer_screen((0, 91))
            else:
                self.draw_main_screen()

        pygame.event.post(
            pygame.event.Event(
                pygame.USEREVENT,
                custom_type=EVENT_SCREEN_CHANGE
            )
        )

    def call_settings_screen(self):
        screen = self.toggle_screen('settings')
        if screen:
            self.window_size = (800, 350)
            pygame.display.set_mode(self.window_size)
            self.draw_settings_screen()
        else:
            if 'mixer' in self.active_screen and 'piano_roll' in self.active_screen:
                self.draw_main_screen()
                self.draw_mixer_screen((0, 91))
                self.draw_piano_roll((0, 235))
            elif 'mixer' in self.active_screen:
                self.window_size = (800, 235)
                pygame.display.set_mode(self.window_size)
                self.draw_main_screen()
                self.draw_mixer_screen((0, 91))
            elif 'piano_roll' in self.active_screen:
                self.window_size = (800, 235)
                pygame.display.set_mode(self.window_size)
                self.draw_main_screen()
                self.draw_piano_roll((0, 91))
            else:
                self.window_size = (800, 91)
                pygame.display.set_mode(self.window_size)
                self.draw_main_screen()
            self.toggle_screen('settings')

        pygame.event.post(
            pygame.event.Event(
                pygame.USEREVENT,
                custom_type=EVENT_SCREEN_CHANGE
            )
        )

    def toggle_screen(self, screen):
        if screen in self.active_screen:
            self.active_screen.remove(screen)
            return False
        else:
            self.active_screen.append(screen)
            return True

    def set_window_size(self, size):
        self.window_size = size

    def draw_main_screen(self):
        self.texts = [
            Text('MIDI Name', self.GOLD_MIDI_NAME_POSITION).get_text(),
            Text('MIDI Time', self.GOLD_MIDI_TIME_POSITION).get_text(),
            Text(
                'MIDI Current Time',
                self.GOLD_MIDI_TIMECOUNT_POSITION,
                update_function=self.get_counter_midi
            ).get_text()
        ]
        self.images = [
            Image('main_screen', (0, 0)).get_image()
        ]
        self.fields = [
            HorizontalSlider(
                (551, 52),
                (233, 27),
                (16, 27),
                function=self.change_volume,
                get_data_function=self.get_volume
            ).get_slider(),
            Button(
                'open_file',
                (213, 3),
                (37, 37),
                self.open_new_midi,
                hover_image_size=(41, 40),
                source_image_offset=(81, 0),
                image_over='sprite',
                help_text='Open new MIDI file'
            ).get_button(),
            Button(
                'mixer',
                (591, 3),
                (37, 37),
                self.call_mixer_screen,
                hover_image_size=(41, 41),
                source_image_offset=(161, 0),
                image_over='sprite',
                help_text='Show/Hide Mixer'
            ).get_button(),
            Button(
                'piano_roll',
                (634, 3),
                (37, 37),
                self.call_piano_roll_screen,
                hover_image_size=(41, 41),
                source_image_offset=(203, 0),
                image_over='sprite',
                help_text='Show/Hide Piano roll'
            ).get_button(),
            Button(
                'open_sound_font',
                (674, 3),
                (37, 37),
                self.load_sound_font,
                hover_image_size=(41, 41),
                source_image_offset=(243, 0),
                image_over='sprite',
                help_text='Open new SoundFont file'
            ).get_button(),
            Button(
                'convert_to_csf',
                (716, 3),
                (37, 37),
                self.convert_sf2_to_csf,
                hover_image_size=(41, 41),
                source_image_offset=(285, 0),
                image_over='sprite',
                help_text='Convert SF2 to CSF format'
            ).get_button(),
            Button(
                'settings',
                (757, 3),
                (37, 37),
                self.call_settings_screen,
                hover_image_size=(41, 41),
                source_image_offset=(325, 0),
                image_over='sprite',
                help_text='Toggle Settings Screen'
            ).get_button(),
            Button(
                'rewind',
                (294, 47),
                (37, 37),
                self.rewind,
                hover_image_size=(41, 41),
                source_image_offset=(148, 84),
                image_over='sprite',
                help_text='Rewind'
            ).get_button(),
            Button(
                'playing',
                (337, 47),
                (37, 37),
                self.playing,
                hover_image_size=(41, 41),
                source_image_offset=(191, 84),
                image_over='sprite',
                help_text='Play'
            ).get_button(),
            Button(
                'stop',
                (380, 47),
                (37, 37),
                self.stop,
                hover_image_size=(41, 41),
                source_image_offset=(233, 84),
                image_over='sprite',
                help_text='Stop'
            ).get_button(),
            Button(
                'forward',
                (421, 47),
                (37, 37),
                self.forward,
                hover_image_size=(41, 41),
                source_image_offset=(274, 84),
                image_over='sprite',
                help_text='Forward'
            ).get_button()
        ]

    def draw_settings_screen(self):
        self.texts = []
        self.images = [
            Image('settings_screen', (0, 0)).get_image()
        ]
        self.fields = [
            Button(
                'settings',
                (757, 3),
                (37, 37),
                self.call_settings_screen,
                hover_image_size=(41, 41),
                source_image_offset=(325, 0),
                image_over='sprite'
            ).get_button(),
            FormField(
                'Output Port MIDI',
                (120, 171),
                (227, 50)
            ).get_form_field()
        ]
        self.active_screen.append('settings')

    def draw_mixer_screen(self, position=(0, 0)):
        self.images.append(Image('mixer_screen', position).get_image())
        i = 0
        solo_buttons_coords = [
            (position[0] + 50, position[1] + 126),
            (position[0] + 95, position[1] + 126),
            (position[0] + 140, position[1] + 126),
            (position[0] + 185, position[1] + 126),
            (position[0] + 231, position[1] + 126),
            (position[0] + 275, position[1] + 126),
            (position[0] + 321, position[1] + 126),
            (position[0] + 365, position[1] + 126),
            (position[0] + 411, position[1] + 126),
            (position[0] + 455, position[1] + 126),
            (position[0] + 501, position[1] + 126),
            (position[0] + 545, position[1] + 126),
            (position[0] + 590, position[1] + 126),
            (position[0] + 635, position[1] + 126),
            (position[0] + 681, position[1] + 126),
            (position[0] + 726, position[1] + 126)
        ]
        mute_buttons_coords = [
            (position[0] + 66, position[1] + 126),
            (position[0] + 110, position[1] + 126),
            (position[0] + 155, position[1] + 126),
            (position[0] + 200, position[1] + 126),
            (position[0] + 246, position[1] + 126),
            (position[0] + 291, position[1] + 126),
            (position[0] + 335, position[1] + 126),
            (position[0] + 381, position[1] + 126),
            (position[0] + 426, position[1] + 126),
            (position[0] + 470, position[1] + 126),
            (position[0] + 516, position[1] + 126),
            (position[0] + 561, position[1] + 126),
            (position[0] + 605, position[1] + 126),
            (position[0] + 650, position[1] + 126),
            (position[0] + 695, position[1] + 126),
            (position[0] + 740, position[1] + 126)
        ]
        sliders_coords = [
            (position[0] + 52, position[1] + 14),
            (position[0] + 97, position[1] + 14),
            (position[0] + 142, position[1] + 14),
            (position[0] + 187, position[1] + 14),
            (position[0] + 232, position[1] + 14),
            (position[0] + 277, position[1] + 14),
            (position[0] + 322, position[1] + 14),
            (position[0] + 367, position[1] + 14),
            (position[0] + 412, position[1] + 14),
            (position[0] + 457, position[1] + 14),
            (position[0] + 502, position[1] + 14),
            (position[0] + 547, position[1] + 14),
            (position[0] + 592, position[1] + 14),
            (position[0] + 637, position[1] + 14),
            (position[0] + 682, position[1] + 14),
            (position[0] + 727, position[1] + 14)
        ]
        while i < len(self.mixer_channels):
            self.fields.append(
                Button(
                    'solo_icon',
                    solo_buttons_coords[i],
                    (13, 15),
                    self.solo_track,
                    params=i,
                    hover_image_size=(12, 16),
                    source_image_offset=(358, 40),
                    image_over='sprite'
                ).get_button()
            )
            self.fields.append(
                Button(
                    'mute_icon',
                    mute_buttons_coords[i],
                    (13, 15),
                    self.mute_track,
                    params=i,
                    hover_image_size=(12, 16),
                    source_image_offset=(358, 57),
                    image_over='sprite'
                ).get_button()
            )
            self.fields.append(
                VerticalSlider(
                    sliders_coords[i],
                    (20, 84),
                    (16, 27),
                    self.change_channel_volume,
                ).get_slider()
            )
            i += 1

    def draw_piano_roll(self, position=(0, 0)):
        self.images.append(Image('piano_roll_screen', position).get_image())

    def index_forms(self):
        index = 0
        for element in self.fields:
            element['index'] = index
            index += 1

    """
    Convert all the fields (fields, images, _text, forms, etc...) to be render like a plain image
    """
    def refresh_screen(self):
        buffering = []

        for image in self.images:
            buffering.append([image.shader, image.position])

        for text in self.texts:
            if text.is_dynamic:
                text.update()
            buffering.append(text.render())

        for button in self.fields:
            buffering.append(button.render())

        return buffering

    def get_fields(self):
        return self.fields

    def load_sound_font(self):
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
                sound_font = BASS_MIDI_FONT(BASS_MIDI_FontInit(str(new_sound_font), 0), -1, 0)

                if self.hstream_handle is not None and BASS_ChannelIsActive(self.hstream_handle) == BASS_ACTIVE_PLAYING:
                    BASS_MIDI_StreamSetFonts(self.hstream_handle, sound_font, 1)

                BASS_MIDI_StreamSetFonts(0, sound_font, 1)

            if is_sound_font_coded and os.path.exists(new_sound_font):
                os.remove(new_sound_font)

    def play_note(self):
        BASS_MIDI_StreamEvent(self.hstream_handle, 0, MIDI_EVENT_NOTE, MAKEWORD(60, 100))
        time.sleep(2)
        BASS_MIDI_StreamEvent(handle, 0, MIDI_EVENT_NOTE, 60)

    def rewind(self):
        if self.hstream_handle and BASS_ChannelIsActive(self.hstream_handle) == BASS_ACTIVE_PLAYING:
            file_position = BASS_ChannelGetPosition(self.hstream_handle, BASS_POS_BYTE)
            return_position = file_position - 1000000
            if return_position < 0:
                return_position = 0
            BASS_ChannelSetPosition(self.hstream_handle, return_position, BASS_POS_BYTE)

    def forward(self):
        if self.hstream_handle and BASS_ChannelIsActive(self.hstream_handle) == BASS_ACTIVE_PLAYING:
            file_position = BASS_ChannelGetPosition(self.hstream_handle, BASS_POS_BYTE)
            return_position = file_position + 1000000
            BASS_ChannelSetPosition(self.hstream_handle, return_position, BASS_POS_BYTE)

    """
    Reproduce el archivo cargado, pausa el que se encuentra sonando o abre la ventana para cargarlo
    """

    def playing(self):
        file = self.playlist.get_file_to_play()
        if not file:
            return self.open_new_midi()

        if BASS_ChannelIsActive(self.hstream_handle) != BASS_ACTIVE_PLAYING:
            BASS_ChannelPlay(self.hstream_handle, False)
            self._file_state = self.GOLD_MIDI_PLAYING
        else:
            BASS_ChannelPause(self.hstream_handle)
            self._file_state = self.GOLD_MIDI_PAUSED

    """
    Detiene la reproduccion
    """

    def stop(self):
        if self.hstream_handle:
            BASS_ChannelStop(self.hstream_handle)
            BASS_ChannelSetPosition(self.hstream_handle, 0, BASS_POS_BYTE)
            self._file_state = self.GOLD_MIDI_STOP

    def change_volume(self, level):
        if self.hstream_handle:
            BASS_ChannelSetAttribute(self.hstream_handle, BASS_ATTRIB_VOL + 0, level)
        self._global_volume = level

    def get_volume(self):
        if self.hstream_handle:
            import ctypes
            volume = ctypes.c_float()
            BASS_ChannelGetAttribute(self.hstream_handle, BASS_ATTRIB_VOL + 0, volume)
            self._global_volume = volume
        return self._global_volume

    def format_time(self, seconds):
        string_time = str(datetime.timedelta(seconds=seconds))

        return Text(string_time, self.GOLD_MIDI_TIME_POSITION).get_text()

    """
    Lanza la interfaz de windows para cargar un nuevo archivo
    """

    def open_new_midi(self):
        Tk().withdraw()
        self.stop()
        new_midi = askopenfilename(
            initialdir="./",
            title="Select MIDI file",
            filetypes=(("MIDI files", "*.mid"), ("all files", "*.*"))
        )

        if new_midi:
            if new_midi.find('.mid', -4) > 5:
                if self.hstream_handle:
                    BASS_ChannelStop(self.hstream_handle)

                self.hstream_handle = BASS_MIDI_StreamCreateFile(False, str(new_midi), 0, 0, 0, 44100)
                self.mixer_channels = []
                """
                MIXER IMPLEMENTATION START
                """
                import binascii
                file_name = new_midi
                with open(file_name, 'rb') as f:
                    number_of_tracks = None
                    index_track = 0
                    while True:
                        id = f.read(4)
                        if len(id) == 0:
                            print('End of file', id)
                            break
                        if str(binascii.hexlify(id)).upper() == '4D546864':
                            print('MThd track...')
                            chunk_size = int(binascii.hexlify(f.read(4)), 16)
                            format_file = int(binascii.hexlify(f.read(2)), 16)
                            number_of_tracks = int(binascii.hexlify(f.read(2)), 16)
                            ticks_per_beat = int(binascii.hexlify(f.read(2)), 16)
                        elif str(binascii.hexlify(id).upper() == '4D54726B'):
                            chunk_size = int(binascii.hexlify(f.read(4)), 16)
                            raw_track_events = f.read(chunk_size)
                            self.mixer_channels.append({
                                'index': index_track,
                                'track_info': chunk_size,
                                'bank': BASS_MIDI_StreamGetEvent(
                                    self.hstream_handle, index_track, MIDI_EVENT_BANK
                                ),
                                'program': BASS_MIDI_StreamGetEvent(
                                    self.hstream_handle, index_track, MIDI_EVENT_PROGRAM
                                ),
                                'volume': BASS_MIDI_StreamGetEvent(
                                    self.hstream_handle, index_track, MIDI_EVENT_VOLUME
                                ),
                                'pan': BASS_MIDI_StreamGetEvent(
                                    self.hstream_handle, index_track, MIDI_EVENT_PAN
                                ),
                                'solo': False,
                                'mute': False,
                                'reverb': BASS_MIDI_StreamGetEvent(
                                    self.hstream_handle, index_track, MIDI_EVENT_REVERB
                                ),
                                'chorus': BASS_MIDI_StreamGetEvent(
                                    self.hstream_handle, index_track, MIDI_EVENT_CHORUS
                                ),
                                'reverb_delay': BASS_MIDI_StreamGetEvent(
                                    self.hstream_handle, index_track, MIDI_EVENT_REVERB_DELAY
                                ),
                                'chorus_delay': BASS_MIDI_StreamGetEvent(
                                    self.hstream_handle, index_track, MIDI_EVENT_CHORUS_DELAY
                                )
                            })
                            index_track += 1
                            print('MTrk track...', chunk_size)
                        else:
                            print('No track', str(binascii.hexlify(id)).upper())
                            break

                if 'mixer' in self.active_screen:
                    self.call_mixer_screen()
                    self.call_mixer_screen()
                """
                MIXER IMPLEMENTATION END
                """
                file_size = BASS_ChannelGetLength(self.hstream_handle, BASS_POS_BYTE)
                file_lenght_seconds = BASS_ChannelBytes2Seconds(self.hstream_handle, file_size)

                file_name = self.playlist.add_new_file(new_midi)
                # TODO: Modificar funcion para que no sea por index
                self.texts[0] = Text(file_name, self.GOLD_MIDI_NAME_POSITION).get_text()
                self.texts[1] = self.format_time(file_lenght_seconds)
                if self.hstream_handle:
                    self.playing()
                else:
                    print('WARNING: Archivo no encontrado')

    """
    Convierte los archivos SF2 a CSF
    """

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

    def get_counter_midi(self):
        if self.hstream_handle and self._file_state == self.GOLD_MIDI_PLAYING:
            file_position = BASS_ChannelGetPosition(self.hstream_handle, BASS_POS_BYTE)
            self._file_position = BASS_ChannelBytes2Seconds(self.hstream_handle, file_position)
        elif self.hstream_handle and self._file_state == self.GOLD_MIDI_STOP:
            self._file_position = '0:00:00'
        return str(self._file_position)

    def get_help_text(self):
        obj = self.acti
        if obj and hasattr(obj, 'help_text'):
            return obj.help_text

    def solo_track(self, channel):
        if self.mixer_channels[channel]['solo']:
            self.mixer_channels[channel]['solo'] = False
        else:
            self.mixer_channels[channel]['solo'] = True

        solo_tracks = []
        for track in self.mixer_channels:
            if track['solo']:
                solo_tracks.append(track['index'])

        for track in self.mixer_channels:
            if (track['index'] in solo_tracks and not track['mute']) or not solo_tracks:
                BASS_MIDI_StreamEvent(self.hstream_handle, track['index'], MIDI_EVENT_VOLUME, track['volume'])
            else:
                BASS_MIDI_StreamEvent(self.hstream_handle, track['index'], MIDI_EVENT_VOLUME, 0)

    def mute_track(self, channel):
        if self.mixer_channels[channel]['mute']:
            self.mixer_channels[channel]['mute'] = False
            BASS_MIDI_StreamEvent(
                self.hstream_handle,
                self.mixer_channels[channel]['index'],
                MIDI_EVENT_VOLUME,
                self.mixer_channels[channel]['volume']
            )
        else:
            self.mixer_channels[channel]['mute'] = True
            BASS_MIDI_StreamEvent(self.hstream_handle, self.mixer_channels[channel]['index'], MIDI_EVENT_VOLUME, 0)

    def change_channel_volume(self, channel, volume):
        print(channel, volume)


"""
Es la clase que lleva el recuento de todos los archivos MIDI abiertos en la sesion
"""


class Playlist:
    def __init__(self):
        self.files_path = []
        self.files_name = []
        self.active_file = 0

    def get_file_to_play(self):
        if not len(self.files_name) > 0:
            return None
        return [self.files_name[self.active_file], self.files_path[self.active_file]]

    def add_new_file(self, file_path):
        self.files_path.append(file_path)
        self.files_name.append(self.clean_name_file(file_path))
        self.active_file = self.files_path.index(file_path)
        return self.files_name[-1]

    @staticmethod
    def clean_name_file(file_name):
        name = file_name.split('/')[-1]
        return name.split('.')[0]

    def change_file_to_play(self, index):
        pass


class Text:
    def __init__(self, content, position, font=None, size=16, update_function=None):
        self.position = position
        self.font_family = font
        self.size_font = size
        self.render_text = None
        self.is_dynamic = False
        self.update_function = update_function

        if not pygame.font.get_init():
            pygame.font.init()
        text = pygame.font.Font(self.font_family, self.size_font)
        surface = text.render(content, True, (255, 255, 255))
        self.render_text = surface

        if self.update_function is not None:
            self.is_dynamic = True

    def get_text(self):
        return self

    def get_type(self):
        return TYPE_TEXT_OBJ

    def update(self):
        if self.is_dynamic:
            text = pygame.font.Font(self.font_family, self.size_font)
            surface = text.render(self.update_function(), True, (255, 255, 255))
            self.render_text = surface

    def render(self):
        return [self.render_text, self.position]


"""
Button Class
"""


class Button:
    def __init__(
            self,
            file_name,
            position,
            size,
            function,
            params=None,
            hover_image_size=(0, 0),
            source_image_offset=(0, 0),
            image_over=None,
            help_text=None
    ):
        self.GOLD_MIDI_HELP_TEXT_POSITION = (14, 79)

        self._file_name = file_name
        self._src_over_image = None
        self._src_idle_image = None
        self._render_image = None

        self._position = position
        self._size = size
        self._size_hover_image = hover_image_size
        self._source_image_offset = source_image_offset
        self._help_text = help_text

        self._state = None
        self._state_time = 5

        self._debug = DEBUG

        self.function = function
        self.function_parameters = params

        if os.path.exists(os.path.join(self._file_name + '.png')):
            image = pygame.image.load(os.path.join(self._file_name + '.png'))
        else:
            image = pygame.Surface(self._size, pygame.SRCALPHA)
            if self._debug:
                image.fill((255, 255, 0, 60))

        self._src_idle_image = image
        self._render_image = self._src_idle_image

        if image_over:
            self._src_over_image = Image(
                image_over,
                (0, 0),
                size_image_cropped=self._size_hover_image,
                source_image_offset=self._source_image_offset
            ).get_image()

    def get_button(self):
        return self

    def get_type(self):
        return TYPE_BUTTON_OBJ

    def get_coordinates(self):
        return [self._position, self._size]

    def is_active(self):
        if self._state:
            self._state = False
            return True

        return False

    """
    Update information to render
    """
    def update(self, event_type):
        if event_type == EVENT_MOUSE_OVER_HOT_SPOT:
            self._render_image = self._src_over_image.render()
            self._state = 'active'
            if self._help_text:
                full_image_size = (
                    self._position[0] + self._size_hover_image[0],
                    143
                )
                help_text = Text(self._help_text, self.GOLD_MIDI_HELP_TEXT_POSITION).get_text().render()
                image = pygame.Surface(full_image_size, pygame.SRCALPHA)
                image.blit(help_text[0], help_text[1])
                image.blit(self._render_image, self._position)

                self._render_image = image
        elif event_type == EVENT_MOUSE_OVER_OUT_HOT_SPOT:
            self._render_image = self._src_idle_image
            self._state = None

    """
    Get the information to render
    """
    def render(self):
        if self._help_text and self._state == 'active':
            return [self._render_image, (0, 0)]

        return [self._render_image, self._position]


class HorizontalSlider:
    def __init__(self,
                 position,
                 bar_size,
                 puller_size,
                 function,
                 puller_image='slider_puller',
                 width_level_marker=5,
                 init_puller_position=1,
                 get_data_function=None
                 ):
        self._type = TYPE_SLIDER_OBJ
        self._position = position
        self._puller_position = (position[0], 0)
        self._puller_image_name = puller_image
        self._puller = pygame.image.load(self._puller_image_name + '.png')
        self._size_puller = puller_size
        self._size_level_marker = (self._puller_position[0], width_level_marker)
        self._size_bar = bar_size
        self._draggable = False
        self._level_marker = None
        self._shader = None
        self._action = function
        self._shader = None
        self.function = self.drag_puller
        self._get_data_function = get_data_function
        self._puller_position = (
            self.get_puller_position(init_puller_position),
            self._puller_position[1]
        )

        if self._get_data_function:
            value = self._get_data_function()
            if value:
                self._puller_position = (self.get_puller_position(value), self._puller_position[1])
                self._size_level_marker = (self.get_puller_position(value), self._size_level_marker[1])

        self.blits_slider()

    def get_slider(self):
        return self

    def get_type(self):
        return self._type

    def get_puller_position(self, value):
        if hasattr(value, 'value'):
            value = value.value
        return int(self._size_bar[0] * float(value))

    def get_coordinates(self):
        return [self._position, self._size_bar]

    def blits_slider(self):
        self._shader = pygame.Surface((self._size_bar[0] + self._size_puller[0], self._size_bar[1]), pygame.SRCALPHA)
        level_marker = pygame.Surface(self._size_level_marker, pygame.HWSURFACE)
        level_marker.fill((235, 180, 0))
        self._shader.blits(((level_marker, (0, 12)), (self._puller, self._puller_position)))

    def drag_puller(self):
        self._draggable = True

    def update(self, event_type):
        if event_type == EVENT_MOUSE_BUTTON_UP:
            self._draggable = False
            new_level = float(self._puller_position[1]) / float(self._size_bar[1] - (self._size_puller[1] / 2))
            self._action(new_level)
        else:
            if self._draggable:
                mouse_coordenates = pygame.mouse.get_pos()
                x_mouse = mouse_coordenates[0]
                x_position, y_position = self._position
                new_position = x_mouse - x_position
                if new_position < 0:
                    new_position = 0
                elif new_position > self._size_bar[0]:
                    new_position = self._size_bar[0]
                self._puller_position = (new_position, self._puller_position[1])
                self._size_level_marker = (new_position, self._size_level_marker[1])
                self._shader = None
                self.blits_slider()

    def render(self):
        return [self._shader, self._position]


class VerticalSlider:
    def __init__(self,
                 position,
                 bar_size,
                 puller_size,
                 function,
                 params=None,
                 puller_image='slider_puller_v',
                 width_level_marker=5,
                 init_puller_position=1,
                 get_data_function=None
                 ):
        self._type = TYPE_SLIDER_OBJ
        self._position = position
        self._puller_position = (0, position[1])
        self._puller_image_name = puller_image
        self._puller = pygame.image.load(self._puller_image_name + '.png')
        self._size_puller = puller_size
        self._size_bar = bar_size
        self._size_level_marker = (width_level_marker, self._size_bar[1])
        self._draggable = False
        self._level_marker = None
        self._shader = None
        self._action = function
        self._shader = None
        self.function = self.drag_puller
        self.function_parameters = params
        self._get_data_function = get_data_function
        self._puller_position = (
            self._puller_position[0],
            self.get_puller_position(init_puller_position)
        )

        if self._get_data_function:
            value = self._get_data_function()
            if value:
                self._puller_position = (self._puller_position[0], self.get_puller_position(value))
                self._size_level_marker = (self._size_level_marker[0], self.get_puller_position(value))

        self.blits_slider()

    def get_slider(self):
        return self

    def get_type(self):
        return self._type

    def get_puller_position(self, value):
        if hasattr(value, 'value'):
            value = value.value
        return int((self._size_bar[1] - self._size_puller[0]) * float(value))

    def get_coordinates(self):
        return [self._position, self._size_bar]

    def blits_slider(self):
        self._shader = pygame.Surface(self._size_bar, pygame.SRCALPHA)
        level_marker = pygame.Surface(self._size_level_marker, pygame.HWSURFACE)
        level_marker.fill((235, 180, 0))
        self._shader.blits(((level_marker, (8, 0)), (self._puller, self._puller_position)))

    def drag_puller(self):
        self._draggable = True

    def update(self, event_type):
        if event_type == EVENT_MOUSE_BUTTON_UP:
            self._draggable = False
            new_level = float(self._puller_position[1]) / float(self._size_bar[1] - (self._size_puller[1] / 2))
            self._action(self.function_parameters, new_level)
        elif event_type == EVENT_MOUSE_OVER_OUT_HOT_SPOT:
            pass
        elif event_type == EVENT_MOUSE_CLICK_TO_FOCUS_OUT:
            pass
        else:
            if self._draggable:
                mouse_coordenates = pygame.mouse.get_pos()
                y_mouse = mouse_coordenates[1]
                x_position, y_position = self._position
                new_position = y_mouse - y_position
                if new_position < 0:
                    new_position = 0
                elif new_position + self._size_puller[1] > self._size_bar[1]:
                    new_position = self._size_bar[1] - (self._size_puller[1] / 2)
                self._puller_position = (self._puller_position[0], new_position)
                self._size_level_marker = (self._size_level_marker[0], new_position)
                self._shader = None
                self.blits_slider()

    def render(self):
        return [self._shader, self._position]


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

    def get_type(self):
        return TYPE_TEXT_FIELD_OBJ

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


class Image:
    def __init__(self, name, position, size_image_cropped=None, source_image_offset=None):
        self.name = name
        self.position = position
        # To crop images
        self.frame_size = size_image_cropped
        self.source_image_offset = source_image_offset
        self.shader = None

        self.shader = pygame.image.load(os.path.join(self.name + '.png'))

        if self.frame_size:
            cropped_image = pygame.Surface(self.frame_size)
            cropped_image.blit(
                self.shader,
                self.position,
                (self.source_image_offset[0], self.source_image_offset[1], self.frame_size[0], self.frame_size[0])
            )
            self.shader = cropped_image

    def get_image(self):
        return self

    def render(self):
        return self.shader


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


app = App(MidiPlayer())

while 1:
    app.update()


