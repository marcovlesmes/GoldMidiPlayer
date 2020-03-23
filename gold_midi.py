"""

"""
import pygame, os, time, datetime
from pybass import *
from pybass.pybassmidi import *
from encrypter import SoundCoder
from Tkinter import Tk
from tkFileDialog import askopenfilename

DEBUG = True

WINDOW_INIT_X = 800
WINDOW_INIT_Y = 91
WINDOW_PIANO_ROLL_Y = 114
WINDOW_HELP_TEXT_POSITION = (14, 79)

COLOR_YELLOW = (235, 180, 0)

EVENT_ON_SCREEN_CHANGE = 0

EVENT_ON_MOUSE_CLICK_PB = 10
EVENT_ON_MOUSE_RELEASE = 11
EVENT_ON_MOUSE_IN = 12
EVENT_ON_MOUSE_OUT = 13
EVENT_ON_MOUSE_DRAG = 14

EVENT_ON_KEY_PRESS = 20

STATE_ELEMENT_IDLE = 30
STATE_ELEMENT_HOVER = 31
STATE_ELEMENT_ACTIVE = 32
STATE_ELEMENT_INACTIVE = 33

MAIN_SCREEN = 40
PIANO_ROLL_SCREEN = 41
MIXER_SCREEN = 42
SETTINGS_SCREEN = 43
"""
"""


class App:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Gold Midi Player")
        # Windows Setup
        self._window_size = (WINDOW_INIT_X, WINDOW_INIT_Y)
        self._screen = pygame.display.set_mode(self._window_size)
        self._clock = pygame.time.Clock()
        self._events_buffer = []
        self._targets_area = []
        self._render_screen = []
        self._interface = None
        self.start(MidiPlayer())

    def start(self, interface):
        """
        The objects have to register the target_area.
        :return:
        """
        self._interface = interface
        self._interface.toggle_screen(MAIN_SCREEN)

    def event_manager(self):
        """
        Check all the targets area registered and register the events
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
                    active_element = self.get_active_element()
                    if active_element:
                        self._events_buffer.append([EVENT_ON_MOUSE_RELEASE, active_element])
                elif event.type == pygame.MOUSEMOTION:
                    if pygame.mouse.get_focused():
                        on_element = self.get_interaction()
                        if on_element and on_element.is_drag_enabled():
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
                    pygame.event.clear()

    def event_exec(self):
        """
        Execute all the events on the buffer
        :return:
        """
        for event in self._events_buffer:
            event_type, event_data = event[0], event[1]
            if event_type == EVENT_ON_SCREEN_CHANGE:
                self.update_screen()
            elif event_type == EVENT_ON_MOUSE_OUT:
                event_data.update(EVENT_ON_MOUSE_OUT)
            elif event_type == EVENT_ON_MOUSE_IN:
                event_data.update(EVENT_ON_MOUSE_IN)
            elif event_type == EVENT_ON_MOUSE_CLICK_PB:
                event_data.update(EVENT_ON_MOUSE_CLICK_PB)
            elif event_type == EVENT_ON_MOUSE_RELEASE:
                event_data.update(EVENT_ON_MOUSE_RELEASE)
            elif event_type == EVENT_ON_MOUSE_DRAG:
                event_data.update(EVENT_ON_MOUSE_DRAG)
            print(event)

        self._events_buffer = []

    def update_screen(self):
        self._render_screen = self._interface.render()
        self.get_targets_areas()

    def update(self):
        """
        Have to call the event_manager
        Refresh the screen
        :return:
        """
        self._clock.tick(40)
        self.event_manager()
        self.event_exec()
        self.refresh_screen()

    def send_key_pressed(self):
        """

        :return:
        """
        print(pygame.key.name)

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


class MidiPlayer:
    def __init__(self):
        BASS_Init(-1, 44100, 0, 0, 0)
        self.GOLD_MIDI_NAME_POSITION = (270, 11)
        self.GOLD_MIDI_TIME_POSITION = (270, 25)
        self.GOLD_MIDI_TIMECOUNT_POSITION = (405, 25)
        self.GOLD_MIDI_STOP = -1
        self.GOLD_MIDI_PAUSED = 0
        self.GOLD_MIDI_PLAYING = 1

        self.hstream_handle = None
        self.mixer_channels = []
        self._global_volume = 1.0
        self._file_position = '0:00:00'
        self._file_state = self.GOLD_MIDI_STOP
        self.sound_font = 'default.csf'
        self.playlist = Playlist()
        self.window_size = None
        self._screen_elements = []
        self._active_screens = []
        self.start()

    def start(self):
        sound_font = BASS_MIDI_FONT(BASS_MIDI_FontInit(self.sound_font, 0), -1, 0)
        BASS_MIDI_StreamSetFonts(0, sound_font, 1)
        return self

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
        self._screen_elements = []
        if SETTINGS_SCREEN in self._active_screens:
            self._screen_elements = self.draw_settings_screen()
        else:
            if MAIN_SCREEN in self._active_screens:
                self._screen_elements = self.draw_main_screen()
            if PIANO_ROLL_SCREEN in self._active_screens:
                self._screen_elements.append(self.draw_piano_roll((0, WINDOW_INIT_Y)))
            if MIXER_SCREEN in self._active_screens:
                self._screen_elements.append(self.draw_mixer_screen((0, WINDOW_INIT_Y + WINDOW_PIANO_ROLL_Y)))
            elif MIXER_SCREEN in self._active_screens:
                self._screen_elements.append(self.draw_mixer_screen((0, WINDOW_INIT_Y)))
        return self._screen_elements

    def set_window_size(self, size):
        self.window_size = size

    def draw_main_screen(self):
        return [
            Image(name='main_screen', position=(0, 0), size=(WINDOW_INIT_X, WINDOW_INIT_Y)),
            Text(content='MIDI Name', position=self.GOLD_MIDI_NAME_POSITION),
            Text(content='MIDI Time', position=self.GOLD_MIDI_TIME_POSITION),
            Text(
                content='MIDI Current Time',
                position=self.GOLD_MIDI_TIMECOUNT_POSITION,
                update_function=self.get_counter_midi
            ),
            HorizontalSlider(
                name='slider_puller',
                position=(588, 80),
                size=(151, 5),
                puller_size=(10, 10),
                action=self.change_volume,
                get_data_function=self.get_volume
            ),
            Button(
                name='open_file',
                position=(213, 3),
                size=(37, 37),
                action=self.open_new_midi,
                idle_hover_active_state_image=['sprite'],
                idle_hover_active_sprite_offset_position=[(0, 0), (81, 0)],
                help_text='Open new MIDI file'
            ),
            Button(
                name='mixer',
                position=(591, 3),
                size=(37, 37),
                action=self.toggle_screen,
                params_action=MIXER_SCREEN,
                idle_hover_active_state_image=['sprite'],
                idle_hover_active_sprite_offset_position=[(0, 0), (161, 0)],
                help_text='Show/Hide Mixer'
            ),
            Button(
                name='piano_roll',
                position=(634, 3),
                size=(37, 37),
                action=self.toggle_screen,
                params_action=PIANO_ROLL_SCREEN,
                idle_hover_active_state_image=['sprite'],
                idle_hover_active_sprite_offset_position=[(0, 0), (203, 0)],
                help_text='Show/Hide Piano roll'
            ),
            Button(
                name='open_sound_font',
                position=(674, 3),
                size=(37, 37),
                action=self.load_sound_font,
                idle_hover_active_state_image=['sprite'],
                idle_hover_active_sprite_offset_position=[(0, 0), (243, 0)],
                help_text='Open new SoundFont file'
            ),
            Button(
                name='convert_to_csf',
                position=(716, 3),
                size=(37, 37),
                action=self.convert_sf2_to_csf,
                idle_hover_active_state_image=['sprite'],
                idle_hover_active_sprite_offset_position=[(0, 0), (285, 0)],
                help_text='Convert SF2 to CSF format'
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
            Button(
                name='rewind',
                position=(294, 47),
                size=(37, 37),
                action=self.rewind,
                idle_hover_active_state_image=['sprite'],
                idle_hover_active_sprite_offset_position=[(0, 0), (148, 84)],
                help_text='Rewind'
            ),
            Button(
                name='playing',
                position=(337, 47),
                size=(37, 37),
                action=self.playing,
                idle_hover_active_state_image=['sprite'],
                idle_hover_active_sprite_offset_position=[(0, 0), (191, 84), (192, 40)],
                help_text='Play'
            ),
            Button(
                name='stop',
                position=(380, 47),
                size=(37, 37),
                action=self.stop,
                idle_hover_active_state_image=['sprite'],
                idle_hover_active_sprite_offset_position=[(0, 0), (233, 84)],
                help_text='Stop'
            ),
            Button(
                name='forward',
                position=(421, 47),
                size=(37, 37),
                action=self.forward,
                idle_hover_active_state_image=['sprite'],
                idle_hover_active_sprite_offset_position=[(0, 0), (274, 84)],
                help_text='Forward'
            )
        ]

    def draw_settings_screen(self):
        return [
            Image('settings_screen', (0, 0)),
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
            FormField(
                'Output Port MIDI',
                (53, 95),
                (278, 20)
            ).get_form_field()
        ]

    def draw_mixer_screen(self, position=(0, 0)):
        i = 0
        solo_buttons_coords = [
            (position[0] + 25, position[1] + 123),
            (position[0] + 75, position[1] + 123),
            (position[0] + 125, position[1] + 123),
            (position[0] + 175, position[1] + 123),
            (position[0] + 225, position[1] + 123),
            (position[0] + 275, position[1] + 123),
            (position[0] + 325, position[1] + 123),
            (position[0] + 375, position[1] + 123),
            (position[0] + 425, position[1] + 123),
            (position[0] + 475, position[1] + 123),
            (position[0] + 525, position[1] + 123),
            (position[0] + 575, position[1] + 123),
            (position[0] + 625, position[1] + 123),
            (position[0] + 675, position[1] + 123),
            (position[0] + 725, position[1] + 123),
            (position[0] + 775, position[1] + 123)
        ]
        mute_buttons_coords = [
            (position[0] + 6, position[1] + 123),
            (position[0] + 56, position[1] + 123),
            (position[0] + 106, position[1] + 123),
            (position[0] + 156, position[1] + 123),
            (position[0] + 206, position[1] + 123),
            (position[0] + 256, position[1] + 123),
            (position[0] + 306, position[1] + 123),
            (position[0] + 356, position[1] + 123),
            (position[0] + 406, position[1] + 123),
            (position[0] + 456, position[1] + 123),
            (position[0] + 506, position[1] + 123),
            (position[0] + 556, position[1] + 123),
            (position[0] + 606, position[1] + 123),
            (position[0] + 656, position[1] + 123),
            (position[0] + 706, position[1] + 123),
            (position[0] + 756, position[1] + 123)
        ]
        sliders_coords = [
            (position[0] + 31, position[1] + 28),
            (position[0] + 81, position[1] + 28),
            (position[0] + 131, position[1] + 28),
            (position[0] + 181, position[1] + 28),
            (position[0] + 231, position[1] + 28),
            (position[0] + 281, position[1] + 28),
            (position[0] + 331, position[1] + 28),
            (position[0] + 381, position[1] + 28),
            (position[0] + 431, position[1] + 28),
            (position[0] + 481, position[1] + 28),
            (position[0] + 531, position[1] + 28),
            (position[0] + 581, position[1] + 28),
            (position[0] + 631, position[1] + 28),
            (position[0] + 681, position[1] + 28),
            (position[0] + 731, position[1] + 28),
            (position[0] + 781, position[1] + 28)
        ]
        rev_buttons_coords = [
            (position[0] + 8, position[1] + 37),
            (position[0] + 58, position[1] + 37),
            (position[0] + 108, position[1] + 37),
            (position[0] + 158, position[1] + 37),
            (position[0] + 208, position[1] + 37),
            (position[0] + 258, position[1] + 37),
            (position[0] + 308, position[1] + 37),
            (position[0] + 358, position[1] + 37),
            (position[0] + 408, position[1] + 37),
            (position[0] + 458, position[1] + 37),
            (position[0] + 508, position[1] + 37),
            (position[0] + 558, position[1] + 37),
            (position[0] + 608, position[1] + 37),
            (position[0] + 658, position[1] + 37),
            (position[0] + 708, position[1] + 37),
            (position[0] + 758, position[1] + 37)
        ]
        chorus_buttons_coords = [
            (position[0] + 8, position[1] + 67),
            (position[0] + 58, position[1] + 67),
            (position[0] + 108, position[1] + 67),
            (position[0] + 158, position[1] + 67),
            (position[0] + 208, position[1] + 67),
            (position[0] + 258, position[1] + 67),
            (position[0] + 308, position[1] + 67),
            (position[0] + 358, position[1] + 67),
            (position[0] + 408, position[1] + 67),
            (position[0] + 458, position[1] + 67),
            (position[0] + 508, position[1] + 67),
            (position[0] + 558, position[1] + 67),
            (position[0] + 608, position[1] + 67),
            (position[0] + 658, position[1] + 67),
            (position[0] + 708, position[1] + 67),
            (position[0] + 758, position[1] + 67)
        ]
        pan_buttons_coords = [
            (position[0] + 8, position[1] + 97),
            (position[0] + 58, position[1] + 97),
            (position[0] + 108, position[1] + 97),
            (position[0] + 158, position[1] + 97),
            (position[0] + 208, position[1] + 97),
            (position[0] + 258, position[1] + 97),
            (position[0] + 308, position[1] + 97),
            (position[0] + 358, position[1] + 97),
            (position[0] + 408, position[1] + 97),
            (position[0] + 458, position[1] + 97),
            (position[0] + 508, position[1] + 97),
            (position[0] + 558, position[1] + 97),
            (position[0] + 608, position[1] + 97),
            (position[0] + 658, position[1] + 97),
            (position[0] + 708, position[1] + 97),
            (position[0] + 758, position[1] + 97)
        ]
        elements = [Image('mixer_screen', position).get_image()]
        while i < len(self.mixer_channels):
            elements.append(
                Button(
                    'solo_icon',
                    solo_buttons_coords[i],
                    (19, 15),
                    self.solo_track,
                    params=i,
                    hover_image_size=(19, 15),
                    source_image_offset=(358, 40),
                    image_over='sprite'
                ).get_button()
            )
            elements.append(
                Button(
                    'mute_icon',
                    mute_buttons_coords[i],
                    (19, 15),
                    self.mute_track,
                    params=i,
                    hover_image_size=(19, 15),
                    source_image_offset=(358, 55),
                    image_over='sprite'
                ).get_button()
            )
            elements.append(
                VerticalSlider(
                    sliders_coords[i],
                    (20, 87),
                    (16, 27),
                    function=self.set_channel_volume,
                    params=i,
                    get_data_function=self.get_channel_volume
                ).get_slider()
            )
            elements.append(
                RollButton(
                    pan_buttons_coords[i],
                    (21, 18),
                    self.set_channel_pan,
                    i,
                    init_sprite_position=172
                ).get_roll_button()
            )
            elements.append(
                RollButton(
                    rev_buttons_coords[i],
                    (21, 18),
                    self.set_channel_rev,
                    i,
                    init_sprite_position=109
                ).get_roll_button()
            )
            elements.append(
                RollButton(
                    chorus_buttons_coords[i],
                    (21, 18),
                    self.set_channel_chorus,
                    i,
                    init_sprite_position=109
                ).get_roll_button()
            )
            i += 1
        return elements

    def draw_piano_roll(self, position=(0, 0)):
        return [Image('piano_roll_screen', position).get_image()]

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

                if self.hstream_handle is not None:
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
                """
                MIXER IMPLEMENTATION END
                """
                file_size = BASS_ChannelGetLength(self.hstream_handle, BASS_POS_BYTE)
                file_lenght_seconds = BASS_ChannelBytes2Seconds(self.hstream_handle, file_size)
                file_name = self.playlist.add_new_file(new_midi)

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

    def set_channel_volume(self, channel, value):
        # volume level (0-127)
        BASS_MIDI_StreamEvent(self.hstream_handle, self.mixer_channels[channel]['index'], MIDI_EVENT_VOLUME, int(value))

    def set_channel_pan(self, channel, value):
        # TODO: Buscar en self.mixer la info del canal, actualizar el valor y escribir funcion para cambiar el paneo
        # pan position (0-128, 0=left, 64=middle, 127=right
        BASS_MIDI_StreamEvent(self.hstream_handle, self.mixer_channels[channel]['index'], MIDI_EVENT_PAN, int(value))
        print(channel, value)

    def set_channel_rev(self, channel, value):
        BASS_MIDI_StreamEvent(self.hstream_handle, self.mixer_channels[channel]['index'], MIDI_EVENT_REVERB, int(value))
        print(channel, value)

    def set_channel_chorus(self, channel, value):
        BASS_MIDI_StreamEvent(self.hstream_handle, self.mixer_channels[channel]['index'], MIDI_EVENT_CHORUS, int(value))
        print(channel, value)

    def get_channel_volume(self, channel):
        print('Channel X: 1')
        return 1


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


class ObjectWithStates:
    def __init__(
            self,
            name,
            position,
            size,
            init_state,
            get_data_function=None,
            params_function=None,
            target=False,
            help_text=None
    ):
        self._name = name
        self._position = position
        self._size = size
        self._state = init_state
        self._surface = None
        self._get_data_function = get_data_function
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
        else:
            self.is_dynamic_animation()

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

    def set_state(self, state):
        self._state = state

    def set_position(self, position):
        self._position = position

    def set_draggable(self, option):
        self._drag_enabled = option

    def is_drag_enabled(self):
        return self._drag_enabled

    def has_target(self):
        if self._target:
            return True
        return False

    def on_mouse_click(self):
        print('Click Button')

    def on_mouse_release(self):
        print('Released Object')

    def on_mouse_in(self):
        print('Over Button')

    def on_mouse_out(self):
        print('Out Button')

    def on_mouse_drag(self):
        print('Dragging')

    def is_dynamic_animation(self):
        if self._get_data_function is not None:
            self._get_data_function()

    def render(self):
        return [self._surface, self._position]


class Text(ObjectWithStates):
    def __init__(self, content, position, font=None, font_size=16, update_function=None):
        ObjectWithStates.__init__(
            self,
            name=content,
            position=position,
            size=(0, 0),
            init_state=STATE_ELEMENT_IDLE,
            get_data_function=update_function,
        )

        self.font_family = font
        self.size_font = font_size
        self._surface = None
        self.is_dynamic = False
        self.start()

    def start(self):
        if not pygame.font.get_init():
            pygame.font.init()
        text = pygame.font.Font(self.font_family, self.size_font)
        surface = text.render(self.get_name(), True, (255, 255, 255))
        self._surface = surface
        return self


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
            get_data_function=action,
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
        print('state_images_count: ', state_images_count, "offset_image_count: ", offset_image_count)
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

    def on_mouse_in(self):
        self._surface = self._hover_image_surface.get_surface()
        self.set_state(STATE_ELEMENT_HOVER)

    def on_mouse_out(self):
        self._surface = self._idle_image_surface.get_surface()
        self.set_state(STATE_ELEMENT_IDLE)

    def on_mouse_click(self):
        if self._params_function:
            self._get_data_function(self._params_function)
        else:
            self._get_data_function()
        if self.get_state() == STATE_ELEMENT_ACTIVE:
            if self._hover_image_surface:
                self.set_state(STATE_ELEMENT_HOVER)
                self._surface = self._hover_image_surface.get_surface()
            else:
                self.set_state(STATE_ELEMENT_IDLE)
                self._surface = self._idle_image_surface.get_surface()
        else:
            if self._active_image_surface:
                self.set_state(STATE_ELEMENT_ACTIVE)
                self._surface = self._active_image_surface.get_surface()
            else:
                self.set_state(STATE_ELEMENT_IDLE)
                self._surface = self._idle_image_surface.get_surface()


class HorizontalSlider(ObjectWithStates):
    def __init__(self,
                 name,
                 position,
                 size,
                 puller_size,
                 action,
                 get_data_function=None,
                 width_level_marker=5,
                 init_puller_position=1,
                 min_value=0,
                 max_value=1
                 ):
        ObjectWithStates.__init__(
            self,
            name=name,
            position=position,
            size=size,
            init_state=STATE_ELEMENT_INACTIVE,
            target=True
        )
        self._action = action
        self._get_data_function = get_data_function
        self._puller_size = puller_size
        self._level_size_width = width_level_marker
        self._puller_position = init_puller_position
        self._min_value = min_value
        self._max_value = max_value
        self.start()

    def start(self):
        self._surface = pygame.Surface(self.get_total_size(), pygame.SRCALPHA)
        position_level, size_level = self.get_level_bar_area()
        self.set_position((self.get_position()[0], self.get_position()[1] - position_level[1]))
        self.draw_slider(self.get_puller_absolute_position_from_volume())
        return self

    def get_total_size(self):
        y = self._puller_size[1] if self._puller_size[1] > self._size[1] else self._size[1]
        return self._size[0], y

    def get_level_bar_area(self):
        x, y = self._surface.get_size()
        level_position_y = (y / 2) - (self._level_size_width / 2)
        return [(0, level_position_y), (x, self._level_size_width)]

    def get_puller_absolute_position_from_volume(self):
        x = self.linear(
            self._get_data_function(),
            self._min_value,
            self._max_value,
            self.get_position()[0],
            (self.get_position()[0] + self.get_total_size()[0])
        )
        return x

    def get_puller_size(self):
        return self._puller_size

    def check_borders(self, position):
        x_min = self.get_position()[0]
        x_max = (self.get_total_size()[0] + x_min) - self.get_puller_size()[0]
        new_position = position
        if position < x_min:
            new_position = x_min
        elif position > x_max:
            new_position = x_max
        return new_position - x_min

    def draw_slider(self, puller_raw_position):
        position_level, size_level = self.get_level_bar_area()
        level_bar = pygame.Surface(size_level, pygame.SRCALPHA)
        level_bar.fill((235, 180, 0))
        puller = pygame.image.load(self.get_name() + '.png')
        puller_position = (self.check_borders(puller_raw_position), 0)
        self._surface.blits(((level_bar, position_level), (puller, puller_position)))

    def on_mouse_click(self):
        self.set_draggable(True)
        self.set_state(STATE_ELEMENT_ACTIVE)
        x, y = pygame.mouse.get_pos()
        self.draw_slider(x)
        volume = self.linear(x, self.get_position()[0], self.get_total_size()[0], self._min_value, self._max_value)
        self._action(volume)

    def on_mouse_drag(self):
        x, y = pygame.mouse.get_pos()
        volume = self.linear(x, self.get_position()[0], self.get_total_size()[0], self._min_value, 10)
        self.draw_slider(x)
        self._action(volume)

    def on_mouse_release(self):
        self.set_draggable(False)
        self.set_state(STATE_ELEMENT_IDLE)

    def linear(self, value, min_in, max_in, min_out, max_out):
        return (
                       ((float(value) - float(min_in)) * (float(max_out) - float(min_out))
                        ) / (float(max_in) - float(min_in))) + float(min_out)

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
            value = self._get_data_function(self.function_parameters)
            if value:
                self._puller_position = (self._puller_position[0], self.get_puller_position(value))
                self._size_level_marker = (self._size_level_marker[0], self._size_bar[1])

        self.blits_slider()

    def get_slider(self):
        return self

    def get_type(self):
        return self._type

    def get_puller_position(self, value):
        if hasattr(value, 'value'):
            value = value.value
        print(int(self._size_bar[1] * value) - self._size_bar[1], value)
        return int(self._size_bar[1] * value) - self._size_bar[1]

    def get_coordinates(self):
        return [self._position, self._size_bar]

    def blits_slider(self):
        self._shader = pygame.Surface(self._size_bar, pygame.SRCALPHA)
        level_marker = pygame.Surface(self._size_level_marker, pygame.HWSURFACE)
        level_marker.fill((235, 180, 0))
        self._shader.blits(((level_marker, (8, self._puller_position[1])), (self._puller, self._puller_position)))

    def drag_puller(self, channel):
        self._draggable = True

    def scale_value_in_range(self, old_range, new_range, value):
        return ((value - old_range[0]) * (new_range[1] + new_range[0]) / (old_range[1] + old_range[0])) + new_range[0]

    def update(self, event_type):
        if event_type == EVENT_MOUSE_BUTTON_UP:
            self._draggable = False
            axis_level_size = self._size_bar[1] - (self._size_puller[1] / 2)
            new_level = float(axis_level_size - self._puller_position[1])
            value = self.scale_value_in_range((0, axis_level_size), (0, 127), new_level)
            self._action(self.function_parameters, value)
        else:
            if self._draggable:
                mouse_coordenates = pygame.mouse.get_pos()
                y_mouse = mouse_coordenates[1]
                x_position, y_position = self._position
                new_position = y_mouse - y_position
                if new_position < 0:
                    new_position = 0
                elif new_position + (self._size_puller[1] / 2) > self._size_bar[1]:
                    new_position = self._size_bar[1] - (self._size_puller[1] / 2)
                self._puller_position = (self._puller_position[0], new_position)
                self._size_level_marker = (self._size_level_marker[0], self._size_bar[1])
                self._shader = None
                self.blits_slider()

    def render(self):
        return [self._shader, self._position]


class RollButton:
    def __init__(self, position, size, function, params, init_sprite_position, image='sprite'):
        self._position = position
        self._size = size
        self._action = function
        self._action_params = params
        self._rolleable = False
        self._init_mouse_position = None
        self._value = None
        self._sprite = pygame.image.load(image + '.png')
        self._sprite_position = init_sprite_position
        self._shader = pygame.Surface(self._size, pygame.SRCALPHA)

        self.blit_roll_button(self._sprite_position)

    def get_roll_button(self):
        return self

    def get_type(self):
        return self._type

    def get_coordinates(self):
        return [self._position, self._size]

    def function(self):
        self._rolleable = True
        self._init_mouse_position = pygame.mouse.get_pos()

    def scale_value_in_range(self, old_range, new_range, value):
        return ((value - old_range[0]) * (new_range[1] + new_range[0]) / (old_range[1] + old_range[0])) + new_range[0]

    def blit_roll_button(self, position):
        self._shader.blit(self._sprite, (0, 0), pygame.Rect((position, 124), (21, 18)))
        if DEBUG:
            self._shader.fill((255, 255, 0, 125))

    def update(self, event_type):
        if event_type == EVENT_MOUSE_BUTTON_UP:
            self._rolleable = False
            self._init_mouse_position = None
            value = self.scale_value_in_range((109, -235), (0, 127), self._sprite_position) * -1
            self._action(self._action_params, value)
            self._value = None
        else:
            if self._rolleable:
                current_position = pygame.mouse.get_pos()
                self._value = current_position[0] - self._init_mouse_position[0]
                if self._value > 0:
                    self._sprite_position += self._size[0]
                    if self._sprite_position > 235:
                        self._sprite_position = 235
                else:
                    self._sprite_position -= self._size[0]
                    if self._sprite_position < 109:
                        self._sprite_position = 109
                self.blit_roll_button(self._sprite_position)

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


