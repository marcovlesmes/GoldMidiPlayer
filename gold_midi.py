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
DEBUG = True
EVENT_SCREEN_CHANGE = 0
EVENT_MOUSE_OVER_HOT_SPOT = 1
EVENT_MOUSE_OVER_OUT_HOT_SPOT = 2
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
        self.interface.set_window_size(self.window_size)
        self.cursor = 'idle'
        self.event = False

    def get_window_size(self):
        return self.window_size

    def update(self):
        self.clock.tick(40)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                element = self.mouse_click_hot_spot(pygame.mouse.get_pos())
                if element:
                    element.function()
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
            try:
                if event.type == pygame.USEREVENT and event.custom_type == EVENT_MOUSE_OVER_HOT_SPOT:
                    self.interface_fields[event.index].update(event.custom_type)
                if event.type == pygame.USEREVENT and event.custom_type == EVENT_MOUSE_OVER_OUT_HOT_SPOT:
                    self.interface_fields[event.index].update(event.custom_type)
                if event.type == pygame.USEREVENT and event.custom_type == EVENT_SCREEN_CHANGE:
                    self.interface_fields = self.interface.get_fields()
                    self.hot_spots = self.get_hot_spots()
                    self.active_hot_spot = None
                    element = None
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
        self.GOLD_MIDI_NAME_POSITION = (430, 21)
        self.GOLD_MIDI_TIME_POSITION = (430, 42)
        self.GOLD_MIDI_TIMECOUNT_POSITION = (640, 42)

        self.fields = []
        self.images = []
        self.texts = []
        self.clock = pygame.time.Clock()
        self.hstream_handle = None
        self.track = None
        self.sound_font = 'sound_fonts/default.sf2'
        self.playlist = Playlist()
        self.window_size = None
        self.active_screen = 'main'

        """
        Loading a default sound font
        """
        sound_font = BASS_MIDI_FONT(BASS_MIDI_FontInit(self.sound_font, 0), -1, 0)
        BASS_MIDI_StreamSetFonts(0, sound_font, 1)
        self.draw_main_screen()
        """
        END of loading a default sound font
        """

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
            Image('background', (0, 0)).get_image(),
        ]
        self.fields = [
            Button(
                'play',
                (542, 74),
                (67, 67),
                self.play,
                hover_image_size=(67, 67),
                source_image_offset=(311, 135),
                image_over='sprite'
            ).get_button(),
            Button(
                'stop',
                (609, 74),
                (67, 67),
                self.stop,
                hover_image_size=(67, 67),
                source_image_offset=(379, 135),
                image_over='sprite'
            ).get_button(),
            Button(
                'piano_roll',
                (1014, 4),
                (67, 67),
                self.toggle_piano_roll,
                hover_image_size=(67, 67),
                source_image_offset=(329, 0),
                image_over='sprite'
            ).get_button(),
            Button(
                'open_sound_font',
                (1080, 4),
                (67, 67),
                self.load_sound_font,
                hover_image_size=(67, 67),
                source_image_offset=(395, 0),
                image_over='sprite'
            ).get_button(),
            Button(
                'open_file',
                (341, 4),
                (67, 67),
                self.open_new_midi,
                hover_image_size=(67, 67),
                source_image_offset=(132, 0),
                image_over='sprite'
            ).get_button(),
            Button(
                'settings',
                (1212, 4),
                (67, 67),
                self.draw_settings_screen,
                hover_image_size=(67, 67),
                source_image_offset=(527, 0),
                image_over='sprite'
            ).get_button(),
            Button(
                'convert_to_csf',
                (1146, 4),
                (67, 67),
                self.convert_sf2_to_csf,
                hover_image_size=(67, 67),
                source_image_offset=(461, 0),
                image_over='sprite'
            ).get_button()
        ]

    def draw_settings_screen(self):
        if self.active_screen == 'main':
            # Do the settings screen
            self.texts = []
            self.images = [
                Image('background_settings', (0, 0)).get_image()
            ]
            self.fields = [
                Button(
                    'settings',
                    (1217, 68),
                    (63, 63),
                    self.draw_settings_screen,
                    hover_image_size=(64, 64),
                    source_image_offset=(817, 0),
                    image_over='sprite'
                ).get_button(),
                FormField(
                    'Output Port MIDI',
                    (120, 171),
                    (227, 50)
                ).get_form_field()
            ]
            self.active_screen = 'settings'
        else:
            self.draw_main_screen()
            self.active_screen = 'main'

        pygame.event.post(
            pygame.event.Event(
                pygame.USEREVENT,
                custom_type=EVENT_SCREEN_CHANGE
            )
        )

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
        new_sound_font = askopenfilename()
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

    def toggle_piano_roll(self):
        if self.window_size[1] == 143:
            self.window_size = (1280, 328)
            self.screen = pygame.display.set_mode(self.window_size)
        else:
            self.window_size = (1280, 143)
            self.screen = pygame.display.set_mode(self.window_size)

    def play_note(self):
        BASS_MIDI_StreamEvent(self.hstream_handle, 0, MIDI_EVENT_NOTE, MAKEWORD(60, 100))
        time.sleep(2)
        BASS_MIDI_StreamEvent(handle, 0, MIDI_EVENT_NOTE, 60)

    """
    Reproduce el archivo cargado, pausa el que se encuentra sonando o abre la ventana para cargarlo
    """

    def play(self):
        file = self.playlist.get_file_to_play()
        if not file:
            return self.open_new_midi()

        if BASS_ChannelIsActive(self.hstream_handle) != BASS_ACTIVE_PLAYING:
            BASS_ChannelPlay(self.hstream_handle, False)
        else:
            BASS_ChannelPause(self.hstream_handle)

    """
    Detiene la reproduccion
    """

    def stop(self):
        if self.hstream_handle:
            BASS_ChannelStop(self.hstream_handle)

    def format_time(self, seconds):
        string_time = str(datetime.timedelta(seconds=seconds))

        return Text(string_time, self.GOLD_MIDI_TIME_POSITION).get_text()

    """
    Lanza la interfaz de windows para cargar un nuevo archivo
    """

    def open_new_midi(self):
        Tk().withdraw()
        self.stop()
        new_midi = askopenfilename()

        if new_midi:
            if new_midi.find('.mid', -4) > 5:
                if self.hstream_handle:
                    BASS_ChannelStop(self.hstream_handle)

                self.hstream_handle = BASS_MIDI_StreamCreateFile(False, str(new_midi), 0, 0, 0, 44100)
                file_size = BASS_ChannelGetLength(self.hstream_handle, BASS_POS_BYTE)
                file_lenght_seconds = BASS_ChannelBytes2Seconds(self.hstream_handle, file_size)

                file_name = self.playlist.add_new_file(new_midi)
                # TODO: Modificar funcion para que no sea por index
                self.texts[0] = Text(file_name, self.GOLD_MIDI_NAME_POSITION).get_text()
                self.texts[1] = self.format_time(file_lenght_seconds)
                if self.hstream_handle:
                    self.play()
                else:
                    print('WARNING: Archivo no encontrado')

    """
    Convierte los archivos SF2 a CSF
    """

    def convert_sf2_to_csf(self):
        Tk().withdraw()
        sound_font_path = askopenfilename()

        if sound_font_path:
            if sound_font_path.find('.sf2', -4) > 5:
                result = SoundCoder().encrypt_sound_found(sound_font_path)

    def get_counter_midi(self):
        position_seconds = '0:00:00'

        if self.hstream_handle and BASS_ChannelIsActive(self.hstream_handle) == BASS_ACTIVE_PLAYING:
            file_position = BASS_ChannelGetPosition(self.hstream_handle, BASS_POS_BYTE)
            position_seconds = BASS_ChannelBytes2Seconds(self.hstream_handle, file_position)

        return str(position_seconds)

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

    def clean_name_file(self, file_name):
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
            hover_image_size=(0, 0),
            source_image_offset=(0, 0),
            image_over=None
    ):
        self._file_name = file_name
        self._src_over_image = None
        self._src_idle_image = None
        self._render_image = None

        self._position = position
        self._size = size
        self._size_image_cropped = hover_image_size
        self._source_image_offset = source_image_offset

        self._state = None
        self._state_time = 5

        self._debug = DEBUG

        self.function = function

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
                size_image_cropped=self._size_image_cropped,
                source_image_offset=self._source_image_offset
            ).get_image()

    def get_button(self):
        return self

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
        elif event_type == EVENT_MOUSE_OVER_OUT_HOT_SPOT:
            self._render_image = self._src_idle_image
            self._state = None

    """
    Get the information to render
    """
    def render(self):
        return [self._render_image, self._position]


class FormField:
    def __init__(self, label, position, size, text=''):
        self._text = text
        self.active = False
        self._debug = DEBUG
        self._position = position
        self._size = size
        self._label = label

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
        # TODO: Crear un evento que escuche el teclado BIND value. Se actualiza al guardar
        print('Aqui quedo activo y recibo comandos del teclado')

    def update(self):
        pass

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


