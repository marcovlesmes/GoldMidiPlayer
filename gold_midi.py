import pygame, sys, os, time, ConfigParser
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
        self.interface.set_window_size(self.window_size)

    def get_window_size(self):
        return self.window_size

    def update(self):
        self.clock.tick(40)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
        if pygame.mouse.get_pressed()[0]:
            x, y = pygame.mouse.get_pos()
            self.interface.left_click_pressed(x, y)
        elif pygame.mouse.get_pressed()[2]:
            print(pygame.event.get())
        """"""
        self.refresh_screen()

    def refresh_screen(self):
        self.screen.fill((0, 0, 0))
        to_render = self.interface.refresh_screen()
        for element in to_render:
            self.screen.blit(element[0], element[1])
        pygame.display.update()


class MidiPlayer:
    def __init__(self):
        BASS_Init(-1, 44100, 0, 0, 0)

        self.buttons = []
        self.gui = []
        self.clock = pygame.time.Clock()
        self.hstream_handle = None
        self.track = None
        self.sound_font = 'sound_fonts/default.sf2'
        self.playlist = []
        self.playlist_index = 0
        self.debug = False
        self.window_size = None

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
            Image('background', (0, 0)).create_image()
        ]
        self.buttons = [
            Button('play', (700, 8), (65, 60), self.play),
            Button('piano_roll', (966, 68), (63, 62), self.toggle_piano_roll),
            Button('open_sound_font', (1028, 68), (63, 62), self.load_sound_font),
            Button('open_file', (323, 68), (65, 62), self.open_new_midi)
        ]

    def refresh_screen(self):
        buffering = []

        for image in self.gui:
            buffering.append([image.shader, image.position])

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
        print(self.window_size)
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
        if len(self.playlist) == 0:
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

    """
    Lanza la interfaz de windows para cargar un nuevo archivo
    """

    def open_new_midi(self):
        Tk().withdraw()
        self.stop()
        new_midi = askopenfilename()

        if new_midi:
            if new_midi.find('.mid', -4) > 5:
                if self.hstream_handle: BASS_ChannelStop(self.hstream_handle)
                self.playlist.append(new_midi)
                self.playlist_index = len(self.playlist) - 1
                self.hstream_handle = BASS_MIDI_StreamCreateFile(False, str(new_midi), 0, 0, 0, 44100)
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


class Button:
    def __init__(self, name, position, size, function, state='inactive', image_over='sprite', size_over_image=(0, 0)):
        self.name = name
        self.position = position
        self.size = size
        self.function = function
        self.state = state
        self.source_image_over_state = image_over
        self.size_image_cropped = size_over_image
        self.state_time = 5
        self.shader = None
        self.debug = True

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
            source_image_offset=(573, 0)
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


