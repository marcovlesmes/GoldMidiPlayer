"""
La clase App es el control principal del programa, la primera capa, en donde vive la clase Midi_Player
La clase App renderiza todos los elementos que vengan de la clase MidiPlayer en su funcion refresh_screen()
get_window_size() Retorna el valor configurado del tamano de la pantalla
update() Es el corazon del programa, ejecuta lo necesario para correr el software
mouse_states() Revisa los estados (hover, clicked) del mouse
refresh_screen() Refresca la pantalla

"""

import pygame, sys, os, time, ConfigParser, datetime
from pybass import *
from pybass.pybassmidi import *
from encrypter import SoundCoder
from Tkinter import Tk
from tkFileDialog import askopenfilename

config = ConfigParser.RawConfigParser()
config.read('config.cfg')


class App:
    def __init__(self, interface):
        pygame.init()
        pygame.display.set_caption(config.get("interface", "app-name"))
        # Windows Setup
        self.window_size = (config.getint("interface", "screen-size-x"), config.getint("interface", "screen-size-y"))
        self.screen = pygame.display.set_mode(self.window_size)
        self.clock = pygame.time.Clock()
        self.interface = interface
        self.interface_hot_spots = []
        self.interface.set_window_size(self.window_size)
        self.mouse_state = 'idle'

    def get_window_size(self):
        return self.window_size

    def update(self):
        self.clock.tick(40)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
        self.mouse_states()

        self.refresh_screen()

    def mouse_states(self):
        if len(self.interface_hot_spots) > 0:
            x, y = pygame.mouse.get_pos()
            if self.mouse_state == 'idle':
                for hot_spot in self.interface_hot_spots:
                    if hot_spot[0] < x < (hot_spot[0] + hot_spot[2]):
                        if hot_spot[1] < y < (hot_spot[1] + hot_spot[3]):
                            self.mouse_state = hot_spot[6]
                            hot_spot[5]()

                self.interface_hot_spots = []
            elif self.mouse_state == 'text':
                for hot_spot in self.interface_hot_spots:
                    if hot_spot[0] > x < hot_spot[2] or hot_spot[1] < y > hot_spot[3]:
                        self.mouse_state = 'idle'
                        hot_spot[4]()


        if pygame.mouse.get_pressed()[0]:
            x, y = pygame.mouse.get_pos()
            self.interface.left_click_pressed(x, y)
        elif pygame.mouse.get_pressed()[2]:
            print(pygame.event.get())

    def refresh_screen(self):
        self.screen.fill((0, 0, 0))
        to_render = self.interface.refresh_screen()
        self.interface_hot_spots = self.interface.get_hot_spots()

        for element in to_render:
            self.screen.blit(element[0], element[1])
        pygame.display.update()

"""
La clase MidiPlayer contiene los demas elementos de su utilidad como la clase Playlist
La clase MidiPlayer inicializa toda la biblioteca de BASS
Crea los elementos a dibujar en pantalla haciento instancias y guardandolos dentro de la lista de objetos a renderizar
pasada a su clase padre App en la funcion refresh_screen()
set_window_size() Configura el tamano de la pantalla
draw_main_screen() Dibuja los elementos de la pantalla principal
draw_settings_screen() Dibuja los elementos de la pantalla de configuracion
refresh_screen() Organiza y agrega al buffer todos los elementos a renderizar
gui_dynamic_texts() Adiciona todos los textos dinamicos
load_sound_font() Carga un SoundFont del disco local
toggle_piano_roll() Habilita/Deshabilita el piano roll
"""

class MidiPlayer:
    def __init__(self):
        BASS_Init(-1, 44100, 0, 0, 0)

        self.buttons = []
        self.hot_spots = []
        self.gui = []
        self.dynamic_texts = []
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
        self.gui = [
            Image('background', (0, 0)).create_image(),
            Text('MIDI Name', (0, 0)).create_text(),
            Text('MIDI Time',  (0, 20)).create_text()
        ]
        self.buttons = [
            Button(
                'play',
                (700, 8),
                (65, 60),
                self.play, size_over_image=(64, 64),
                source_image_offset=(190, 0)
            ),
            Button(
                'piano_roll',
                (966, 68),
                (63, 62),
                self.toggle_piano_roll,
                size_over_image=(64, 64),
                source_image_offset=(570, 0)
            ),
            Button(
                'open_sound_font',
                (1028, 68),
                (63, 62),
                self.load_sound_font,
                size_over_image=(64, 64),
                source_image_offset=(635, 0)
            ),
            Button(
                'open_file',
                (323, 68),
                (65, 62),
                self.open_new_midi,
                size_over_image=(64, 64),
                source_image_offset=(379, 0)
            ),
            Button(
                'settings',
                (1217, 68),
                (63, 63),
                self.draw_settings_screen,
                size_over_image=(64, 64),
                source_image_offset=(817, 0)
            )
        ]

    def draw_settings_screen(self):
        if self.active_screen == 'main':
            # Do the settings screen
            self.gui = [
                Image('background_settings', (0, 0)).create_image()
            ]
            self.buttons = [
                Button(
                    'settings',
                    (1217, 68),
                    (63, 63),
                    self.draw_settings_screen,
                    size_over_image=(64, 64),
                    source_image_offset=(817, 0)
                ),
                Button(
                    'Output Port MIDI',
                    (120, 171),
                    (227, 50),
                    self.active_fieldtext_output_port_midi
                )
            ]
            self.hot_spots = [
                [20, 20, 100, 100, self.draw_idle_cursor, self.draw_over_field_cursor, 'text']
            ]
            self.active_screen = 'settings'
        else:
            self.draw_main_screen()
            self.active_screen = 'main'

    def active_fieldtext_output_port_midi(self):
        # surface = pygame.Surface(pygame.Rect(0, 0, 35, 35))

        print('activating_field')

    def refresh_screen(self):
        self.dynamic_texts = []
        buffering = []

        if self.hstream_handle and BASS_ChannelIsActive(self.hstream_handle) == BASS_ACTIVE_PLAYING:
            self.gui_dynamic_texts()

        for image in self.gui:
            buffering.append([image.shader, image.position])

        for dynamic_text in self.dynamic_texts:
            buffering.append([dynamic_text.shader, dynamic_text.position])

        for button in self.buttons:
            if hasattr(button, 'state') and button.state == 'active':
                if button.state_time > 0:
                    buffering.append([button.source_image_over_state.shader, button.position])
                    button.state_time -= 1
                else:
                    button.state = 'inactive'
                    button.state_time = 5
            else:
                buffering.append([button.shader, button.position])

        return buffering

    def get_hot_spots(self):
        return self.hot_spots

    def draw_idle_cursor(self):
        pygame.mouse.set_cursor((16, 19), (0, 0), (
        128, 0, 192, 0, 160, 0, 144, 0, 136, 0, 132, 0, 130, 0, 129, 0, 128, 128, 128, 64, 128, 32, 128, 16, 129, 240,
        137, 0, 148, 128, 164, 128, 194, 64, 2, 64, 1, 128), (
                                128, 0, 192, 0, 224, 0, 240, 0, 248, 0, 252, 0, 254, 0, 255, 0, 255, 128, 255, 192, 255,
                                224, 255, 240, 255, 240, 255, 0, 247, 128, 231, 128, 195, 192, 3, 192, 1, 128))

    def draw_over_field_cursor(self):
        pygame.mouse.set_cursor((8, 8), (4, 4), (24, 24, 24, 231, 231, 24, 24, 24), (0, 0, 0, 0, 0, 0, 0, 0))

    def gui_dynamic_texts(self):
        if self.hstream_handle:
            if BASS_ChannelIsActive(self.hstream_handle) == BASS_ACTIVE_PLAYING:
                file_position = BASS_ChannelGetPosition(self.hstream_handle, BASS_POS_BYTE)
                position_seconds = BASS_ChannelBytes2Seconds(self.hstream_handle, file_position)
                self.dynamic_texts.append(Text(str(position_seconds), (0, 40)).create_text())


    def load_sound_font(self):
        Tk().withdraw()
        new_sound_font = askopenfilename()
        is_sound_font_coded = False
        if new_sound_font:
            if new_sound_font.find('.sfc', -4) > 5:
                is_sound_font_coded = True
                new_sound_font = SoundCoder().decrypt_sound_found_in_memory(new_sound_font)

            if new_sound_font.find('.sf2', -4) > 5:
                sound_font = BASS_MIDI_FONT(BASS_MIDI_FontInit(str(new_sound_font), 0), -1, 0)

                if self.hstream_handle is not None and BASS_ChannelIsActive(self.hstream_handle) == BASS_ACTIVE_PLAYING:
                    BASS_MIDI_StreamSetFonts(self.hstream_handle, sound_font, 1)
                BASS_MIDI_StreamSetFonts(0, sound_font, 1)

            if is_sound_font_coded and os.path.exists(new_sound_font):
                os.remove(new_sound_font)

    def toggle_piano_roll(self):
        if self.window_size[1] == 266:
            self.window_size = (1280, 443)
            self.screen = pygame.display.set_mode(self.window_size)
        else:
            self.window_size = (1280, 266)
            self.screen = pygame.display.set_mode(self.window_size)

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
        pass

    def format_time(self, seconds):
        string_time = str(datetime.timedelta(seconds=seconds))

        return Text(string_time, (0, 20)).create_text()

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

                self.gui[1] = self.playlist.add_new_file(new_midi)
                self.gui[2] = self.format_time(file_lenght_seconds)
                if self.hstream_handle:
                    self.play()
                else:
                    print('WARNING: Archivo no encontrado')

    """
    Verifica de tener un evento en el mouse sobre que posicion se registro el evento
    """

    def left_click_pressed(self, x, y):
        for button in self.buttons:
            left, top = button.position
            width, height = button.size

            if left < x < (width + left) and top < y < (height + top):
                button.state = 'active'
                time.sleep(0.2)
                pygame.event.clear()
                button.function()

"""
Es la clase que lleva el recuento de todos los archivos abiertos en la sesion
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
        return Text(self.files_name[-1], (0, 0)).create_text()

    def clean_name_file(self, file_name):
        name = file_name.split('/')[-1]
        return name.split('.')[0]

    def change_file_to_play(self, index):
        pass


class Text:
    def __init__(self, content, position, font=None, size=16):
        self.content = content
        self.position = position
        self.font_family = font
        self.size_font = size
        self.shader = None

    def create_text(self):
        if not pygame.font.get_init():
            pygame.font.init()
        text = pygame.font.Font(self.font_family, self.size_font)
        print(self.content)
        surface = text.render(self.content, True, (255, 255, 255))
        self.shader = surface

        return self


class Button:
    def __init__(
            self,
            name,
            position,
            size,
            function,
            size_over_image=(0, 0),
            source_image_offset=(0, 0),
            state='inactive',
            image_over='sprite'
    ):

        self.name = name
        self.position = position
        self.size = size
        self.function = function
        self.state = state
        self.source_image_over_state = image_over
        self.size_image_cropped = size_over_image
        self.source_image_offset = source_image_offset
        self.state_time = 5
        self.shader = None
        self.debug = False

        self.create_button()
        self.set_over_image()

    """
        
    """

    def create_button(self):
        if os.path.exists(os.path.join(self.name + '.png')):
            image = pygame.image.load(os.path.join(self.name + '.png'))
        else:
            image = pygame.Surface(self.size, pygame.SRCALPHA)
            if self.debug:
                image.fill((255, 255, 0, 60))
        self.shader = image
        return self

    def set_over_image(self):
        self.source_image_over_state = Image(
            self.source_image_over_state,
            (0, 0),
            size_image_cropped=self.size_image_cropped,
            source_image_offset=self.source_image_offset
        ).create_image()


class Image:
    def __init__(self, name, position, size_image_cropped=None, source_image_offset=None):
        self.name = name
        self.position = position
        # To crop images
        self.frame_size = size_image_cropped
        self.source_image_offset = source_image_offset
        self.shader = None

    """
        Registra la creacion de cada imagen
    """

    def create_image(self):
        self.shader = pygame.image.load(os.path.join(self.name + '.png'))

        if self.frame_size:
            cropped_image = pygame.Surface(self.frame_size)
            cropped_image.blit(
                self.shader,
                self.position,
                (self.source_image_offset[0], self.source_image_offset[1], self.frame_size[0], self.frame_size[0])
            )
            self.shader = cropped_image
        return self


# def open_sound_found(file_name):
#     if file_name.split('.')[1] == 'sfc':
#         print('Crypto Sound Font')
#         file = open(file_name, 'r')
#         for line in file.readlines():
#             print(line)
#         # decoded_file = base64.b64decode(file.read())
#         # file.close()
#         # temp_name = 'temp/' + str(random.random()).split('.')[1] + '.sf2'
#         # file = open(temp_name, 'w')
#         # file.write(decoded_file)
#         # file.close()
#         # temp_name = 'all voices.sf2'
#         # print(temp_name)
#         # print(BASS_MIDI_FontInit(temp_name, 0))
#         # sf = BASS_MIDI_FONT(BASS_MIDI_FontInit(temp_name, 0), -1, 0)
#         # print(BASS_MIDI_StreamSetFonts(0, sf, 1))
#         # sys.exit()
#         # os.remove(temp_name)
#     else:
#         print('Normal Sound Font')


# def create_crypto_sound(file_name):
#     name = file_name.split('.')[0]
#
#     file = open(file_name, 'r')
#     # newFile = open(name + '.sfc', 'w')
#     for line in file:
#         print(line)
#         # newFile.write('|' + base64.b64encode(line))
#     file.close()
#     # newFile.close()
#     print(name + '.sfc se ha creado correctamente.')

# open_sound_found(sound_font)
# create_crypto_sound(sound_font)

# sys.exit()


# """
# filePlayerHandle = BASS_StreamCreateFile(False, mp3_file, 0, 0, 0)
# BASS_ChannelPlay(filePlayerHandle, False)
# """
#
# while BASS_ChannelIsActive(filePlayerHandle):
#     print(BASS_MIDI_StreamGetEvent(filePlayerHandle, 0, MIDI_EVENT_NOTE))
#
# print ('Saliendo...')

app = App(MidiPlayer())

while 1:
    app.update()


