# For MidiPlayer
import pygame
# For EventManager
import sys
# For Bass
from Tkinter import Tk
from tkFileDialog import askopenfilename, asksaveasfile
from pybass import *
from pybass.pybassmidi import *
from pybass.pybassenc import *
import tkMessageBox
import re
import os
import time
import json
import xml.etree.ElementTree as ET
import webbrowser
from encrypter import SoundCoder

DEBUG = True
DEBUG_COLOR = (50, 180, 200, 70)
MAIN_MODULE = "Main Module"
MIXER_MODULE = "Mixer Module"
PRESET_MODULE = "Preset Module"
EVENT_COROUTINE = "Event Coroutine"


class MidiPlayer:
    def __init__(self):
        pygame.init()
        bass_init = BASS_Init(-1, 44100, 0, 0, None)
        if not bass_init:
            ErrorManager.raise_error(BASS_ErrorGetCode())
        self._clock = pygame.time.Clock()
        self._screen = Screen(size=(800, 150))
        self._eventManager = EventManager()

    def update(self):
        if pygame.display.get_active():
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
            elif event.type == pygame.USEREVENT:
                if event.custom_type == EVENT_COROUTINE:
                    if event.condition["params"]:
                        condition = event.condition["function"](event.condition["params"])
                    else:
                        condition = event.condition["function"]()
                    if condition:
                        if event.run["params"]:
                            event.run["function"](event.run["params"])
                        else:
                            event.run["function"]()
                        pygame.event.post(event)


class ErrorManager:
    ERROR = {
        8: "Error in the initialization. Code 8.",
        41: "The file's format is not recognised/supported.",
        48: "No MIDI file found to play.",
        49: "No SoundFond file found to play."
    }
    @staticmethod
    def raise_error(error_code):
        if error_code in ErrorManager.ERROR:
            tkMessageBox.showerror('Error', ErrorManager.ERROR[error_code])
        else:
            tkMessageBox.showerror("Error", 'Unknown Error. Code: ' + str(error_code))


class Bass:

    @staticmethod
    def open_midi(kwargs):
        main_module = kwargs["main_module"]
        mixer_module = kwargs["mixer_module"]()
        Tk().withdraw()
        new_midi_path = askopenfilename(
            initialdir="./",
            title="Select MIDI file",
            filetypes=(("MIDI files", "*.mid *.kar"), ("all files", "*.*"))
        )
        if new_midi_path:
            hstream = BASS_MIDI_StreamCreateFile(False, str(new_midi_path), 0, 0, 0, 44100)

            if hstream:
                current_hstream = main_module.get_hstream()
                if current_hstream:
                    BASS_ChannelStop(current_hstream)
                main_module.set_file_path(str(new_midi_path))
                main_module.set_hstream(hstream)

                midi_name = str(re.search('.*[/](.*)[.]([a-zA-Z]{3,4}$)', new_midi_path).groups()[0])
                # TODO: Set Main Module. This code has to be in another function
                # MIDI NAME
                midi_name_text = main_module.get_element_by_name("Midi Name Text")
                midi_name_text.set_color((255, 255, 255))
                midi_name_text.render(midi_name)
                # MIDI TIME
                midi_name_text = main_module.get_element_by_name("Midi Time Text")
                midi_name_text.set_color((255, 255, 255))
                midi_name_text.render('00:00:00')
                # MIDI VOLUME
                global_volume = BASS_MIDI_StreamGetEvent(hstream, -1, MIDI_EVENT_MASTERVOL)
                slider_global_volume = main_module.get_element_by_name("Global Volume Slider")
                slider_global_volume.draw(slider_global_volume.raw_to_puller_value(global_volume, 0, 16383))
                # MIDI TEMPO TODO: Fix the value in the function slider_tempo.raw_to_puller_value(tempo_in_bpm)
                slider_tempo = main_module.get_element_by_name("Global Tempo Slider")
                tempo_in_microseconds = BASS_MIDI_StreamGetEvent(hstream, -1, MIDI_EVENT_TEMPO)
                tempo_in_bpm = 60000000 / tempo_in_microseconds
                print(tempo_in_bpm)
                slider_tempo.draw(slider_tempo.raw_to_puller_value(tempo_in_bpm))
                # UPDATE MAIN MODULE
                main_module.get_element_by_name("Save File Button").disabled(False)

                if main_module.get_soundFont():
                    main_module.get_element_by_name("Play Button").disabled(False)
                    main_module.get_element_by_name("Convert MP3 Button").disabled(False)
                # TODO: Set Mixer Module. When the mixer don't exist what have to do it?

                if mixer_module:
                    for i in range(0, 16):
                        # CHANNELS VOLUME
                        volume = BASS_MIDI_StreamGetEvent(hstream, i, MIDI_EVENT_VOLUME)
                        channel_volume_slider = mixer_module.get_element_by_name("Volume Track " + str(i + 1) + " Slider")
                        channel_volume_slider.draw(channel_volume_slider.raw_to_puller_value(volume))
                        # CHANNELS REVERB
                        reverb = BASS_MIDI_StreamGetEvent(hstream, i, MIDI_EVENT_REVERB)
                        channel_reverb_knob = mixer_module.get_element_by_name(
                            "Reverb Track " + str(i + 1) + " Knob")
                        channel_reverb_knob.draw(channel_reverb_knob.raw_to_knob_value(reverb))
                        # CHANNELS CHORUS
                        chorus = BASS_MIDI_StreamGetEvent(hstream, i, MIDI_EVENT_CHORUS)
                        channel_chorus_knob = mixer_module.get_element_by_name(
                            "Chorus Track " + str(i + 1) + " Knob")
                        channel_chorus_knob.draw(channel_chorus_knob.raw_to_knob_value(chorus))
                        # CHANNELS PAN
                        pan = BASS_MIDI_StreamGetEvent(hstream, i, MIDI_EVENT_PAN)
                        channel_pan_knob = mixer_module.get_element_by_name(
                            "Pan Track " + str(i + 1) + " Knob")
                        channel_pan_knob.draw(channel_pan_knob.raw_to_knob_value(pan))
                # TODO: Set Playlist Module

                return True
            else:
                ErrorManager.raise_error(BASS_ErrorGetCode())

    @staticmethod
    def open_soundFont(kwards):
        module = kwards["module"]
        Tk().withdraw()
        new_sound_font = askopenfilename(
            initialdir="./",
            title="Select SoundFont file",
            filetypes=(("SoundFond files", "*.csf *.sf2"), ("all files", "*.*"))
        )
        is_sound_font_coded = False

        if new_sound_font:
            """ Check if the file is suported and config the loading """
            if new_sound_font.find('.csf', -4) > 5:
                is_sound_font_coded = True

                new_sound_font = SoundCoder().decrypt_sound_found_in_memory(new_sound_font)

            sound_font = BASS_MIDI_FontInit(str(new_sound_font), 0)

            if sound_font:
                init_font = BASS_MIDI_FONT(sound_font, -1, 0)
                set_soundFont = BASS_MIDI_StreamSetFonts(0, init_font, 1)
                if set_soundFont:
                    module.set_soundFont(init_font)
                    if module.get_hstream():
                        module.get_element_by_name("Play Button").disabled(False)
                        module.get_element_by_name("Convert MP3 Button").disabled(False)
                    return True
                else:
                    ErrorManager.raise_error(BASS_ErrorGetCode())
            else:
                ErrorManager.raise_error(BASS_ErrorGetCode())
            """
            if is_sound_font_coded and os.path.exists(new_sound_font):
                os.remove(new_sound_font)
            """

    @staticmethod
    def save_file(kwards):
        main_module = kwards["main_module"]
        mixer_module = kwards["mixer_module"]()

        # TODO: Ask for where to save new file
        Tk().withdraw()
        new_midi_path = asksaveasfile(
            initialdir="./",
            title="Save New Midi As",
            filetypes=[("MIDI File", "*.mid")]
        )

        if new_midi_path:
            # Read binary file and get string
            file_path = main_module.get_file_path()
            with open(file_path, 'rb') as original_file:
                str_original_file = original_file.read().encode('hex')
            str_tracks = str_original_file.split('4d54726b')
            # TODO: Read player and get values for new MIDI
            print (str_tracks)

            new_file_values = {}

            for index in range(0, 16):
                options = {
                    "volume": BASS_MIDI_StreamGetEvent(main_module.get_hstream(), index, MIDI_EVENT_VOLUME),
                    "reverb": BASS_MIDI_StreamGetEvent(main_module.get_hstream(), index, MIDI_EVENT_REVERB),
                    "pan": BASS_MIDI_StreamGetEvent(main_module.get_hstream(), index, MIDI_EVENT_PAN),
                    "chorus": BASS_MIDI_StreamGetEvent(main_module.get_hstream(), index, MIDI_EVENT_CHORUS)
                }
                new_file_values.update([("channel_" + str(index), options)])
            options = {
                    "volume": BASS_MIDI_StreamGetEvent(main_module.get_hstream(), 0, MIDI_EVENT_MASTERVOL),
                    "pitch": BASS_MIDI_StreamGetEvent(main_module.get_hstream(), 0, MIDI_EVENT_TRANSPOSE),
                    "tempo": BASS_MIDI_StreamGetEvent(main_module.get_hstream(), 0, MIDI_EVENT_TEMPO),
                }
            new_file_values.update([("global", options)])

            print (new_file_values)
            # TODO: Write values of actual MIDI

            print("Saved file as: ", new_midi_path)

        return True

    @staticmethod
    def play_midi(kwards):
        module = kwards["module"]
        hstream = module.get_hstream()
        sound_font = module.get_soundFont()

        if hstream is None:
            ErrorManager.raise_error(48)
        elif sound_font is None:
            ErrorManager.raise_error(49)
        else:
            channel_state = BASS_ChannelIsActive(hstream)
            if channel_state == BASS_ACTIVE_PLAYING or channel_state == BASS_ACTIVE_PAUSED:
                return False
            else:
                play = BASS_ChannelPlay(hstream, False)
                Bass.set_midi_time_coroutine(module)

                if not play:
                    ErrorManager.raise_error(BASS_ErrorGetCode())

            return True

    @staticmethod
    def pause_midi(kwargs):
        module=kwargs["module"]
        hstream = module.get_hstream()

        if hstream:
            channel_state = BASS_ChannelIsActive(hstream)
            if channel_state == BASS_ACTIVE_PLAYING:
                pause = BASS_ChannelPause(hstream)
            elif channel_state == BASS_ACTIVE_PAUSED:
                pause = BASS_ChannelPlay(hstream, False)
                Bass.set_midi_time_coroutine(module)
            else:
                pause = False

            if pause:
                return True

    @staticmethod
    def stop_midi(kwargs):
        module = kwargs["module"]
        hstream = module.get_hstream()

        if hstream:
            stop_channel = BASS_ChannelStop(hstream)
            reset_position = BASS_ChannelSetPosition(hstream, 0, BASS_POS_BYTE)
            if stop_channel and reset_position:
                module.get_element_by_name("Play Button").set_idle_state()
                module.get_element_by_name("Pause Button").set_idle_state()
                midi_play_time_text = module.get_element_by_name("Midi Time Text")
                midi_play_time_text.render('00:00:00')
                return True
            else:
                ErrorManager.raise_error(BASS_ErrorGetCode())

    @staticmethod
    def convert_to_csf():
        Tk().withdraw()
        sound_font_path = askopenfilename(
            initialdir="./",
            title="Select SF2 file",
            filetypes=(("SF2 files", "*.sf2"), ("all files", "*.*"))
        )

        if sound_font_path:
            if sound_font_path.find('.sf2', -4) > 5:
                result = SoundCoder().encrypt_sound_found(sound_font_path)
                if result:
                    tkMessageBox.showinfo('File Converted', 'File converted')
                    return True

    @staticmethod
    def open_goldmidi_web():
        webbrowser.open('https://www.goldmidisf2.com/', 2, True)

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
        main_module = kwargs["main_module"]()
        channel = kwargs["channel"]
        hstream = main_module.get_hstream()
        if hstream:
            if kwargs["slider"].get_state() == kwargs["slider"].STATES["disabled"]:
                BASS_MIDI_StreamEvent(hstream, channel, MIDI_EVENT_VOLUME, 127)
                kwargs["slider"].disabled(False)
            else:
                BASS_MIDI_StreamEvent(hstream, channel, MIDI_EVENT_VOLUME, 0)
                # TODO: Can apply an filter to VOLUME Events with BASS_MIDI_StreamSetFilter
                kwargs["slider"].disabled(True)
            return True
        else:
            return False

    @staticmethod
    def solo_track(kwargs):
        main_module = kwargs["main_module"]()
        mixer_module = kwargs["mixer_module"]()
        channel = kwargs["channel"]
        hstream = main_module.get_hstream()
        manager_solo_status = mixer_module.get_manager_solo()

        if hstream:
            if manager_solo_status["is_active"](channel):
                manager_solo_status["update_status_channel"](channel, False)
                # Solo is OFF
                # If other channel is not in solo this channel and all other channels has to be in regular volume.
                # If are one or more channels in solo this channel has to be mute.
                if manager_solo_status["other_active"](channel):
                    BASS_MIDI_StreamEvent(hstream, channel, MIDI_EVENT_VOLUME, 0)
                else:
                    for index_channel in range(0, mixer_module.get_channels_count()):
                        if not manager_solo_status["is_active"](index_channel):
                            BASS_MIDI_StreamEvent(hstream, index_channel, MIDI_EVENT_VOLUME, mixer_module.get_volume(channel))
            else:
                manager_solo_status["update_status_channel"](channel, True)
                # Solo is ON.
                # If ALL other channel are OFF all channels has to be muted
                if hstream:
                    BASS_MIDI_StreamEvent(hstream, channel, MIDI_EVENT_VOLUME, mixer_module.get_volume(channel))
                    for index_channel in range(0, mixer_module.get_channels_count()):
                        if not channel == index_channel and not manager_solo_status["is_active"](index_channel):
                            BASS_MIDI_StreamEvent(hstream, index_channel, MIDI_EVENT_VOLUME, 0)
            return True
        else:
            return False

    @staticmethod
    def reverb_track(kwargs):
        pass

    @staticmethod
    def get_general_midi_presets():
        tree = ET.parse('general_midi.xml')
        root = tree.getroot()
        presets = []
        for child in root:
            presets.append(child[0].text + ' ' + child[1].text)
        return presets

    @staticmethod
    def set_preset_channel(kwargs):
        main_module = kwargs["main_module"]()
        preset_index = kwargs["index_item"]
        hstream = main_module.get_hstream()

        BASS_MIDI_StreamEvent(hstream, 0, MIDI_EVENT_PROGRAM, preset_index)
        return True

    @staticmethod
    def set_midi_time_coroutine(module):
        pygame.event.post(
            pygame.event.Event(
                pygame.USEREVENT,
                {
                    "custom_type": EVENT_COROUTINE,
                    "condition": {
                        "function": Bass.is_playing,
                        "params": {"module": module}
                    },
                    "run": {
                        "function": Bass.refresh_play_time_text,
                        "params": {"module": module}
                    }
                }
            )
        )

    @staticmethod
    def is_playing(kwargs):
        module = kwargs["module"]
        hstream = module.get_hstream()
        return BASS_ChannelIsActive(hstream) == BASS_ACTIVE_PLAYING

    @staticmethod
    def refresh_play_time_text(kwargs):
        module = kwargs["module"]
        midi_play_time_text = module.get_element_by_name("Midi Time Text")
        hstream = module.get_hstream()
        hstream_position = BASS_ChannelGetPosition(hstream, BASS_POS_BYTE)
        time_in_seconds = BASS_ChannelBytes2Seconds(hstream, hstream_position)
        format_time = time.strftime('%H:%M:%S', time.gmtime(time_in_seconds))
        midi_play_time_text.render(format_time)


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

    def get_name(self):
        return self._name

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

    def get_element_by_name(self, name):
        for element in self.get_objects_to_render():
            if element.get_name() == name:
                return element
        return None

    def get_height(self):
        return self._height

    def get_index_priority(self):
        return self._index_priority

    def get_objects_to_render(self):
        return self._render_elements

    def add_objects_to_render(self, objects):
        self._render_elements += objects


class MainModule(Module):
    def __init__(self):
        Module.__init__(self, MAIN_MODULE, 344, './main_screen.png', 1)
        self._hstream = None
        self._soundFont = None
        self._file_path = None

    def get_file_path(self):
        return self._file_path

    def get_hstream(self):
        return self._hstream

    def get_soundFont(self):
        return self._soundFont

    def add_file(self, midi):
        print(str(midi))

    def set_file_path(self, path):
        self._file_path = path

    def set_hstream(self, hstream):
        self._hstream = hstream

    def set_soundFont(self, soundFont):
        self._soundFont =soundFont


class MixerModule(Module):
    def __init__(self):
        Module.__init__(self, MIXER_MODULE, 344, './mixer_screen.png', 3)
        self._channels_count = 5
        self._manager_solo = {
            "active_channels": {},
            "is_active": self._is_active,
            "other_active": self._other_active,
            "update_status_channel": self._update_status_channel
        }

    def _is_active(self, channel):
        return True if "channel_" + str(channel) in self._manager_solo["active_channels"] else False

    def get_volume(self, channel):
        # TODO: Save the values of channels volume and get the request channel
        return 100

    def _other_active(self, channel):
        return True if len(self._manager_solo["active_channels"]) >= 1 else False

    def _update_status_channel(self, channel, status):
        prefix = "channel_"
        if status:
            self._manager_solo["active_channels"][prefix + str(channel)] = True
        else:
            del self._manager_solo["active_channels"][prefix + str(channel)]

    def get_channels_count(self):
        return self._channels_count

    def get_manager_solo(self):
        return self._manager_solo


class PresetModule(Module):
    def __init__(self):
        Module.__init__(self, PRESET_MODULE, 150, './program_screen.png', 4)

        self._presets = []


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
                self._main_module = MainModule()
                ElementManager.main_module_init(self._main_module, self)
            self._active_modules.append(self._main_module)
            return self._main_module
        elif module == MIXER_MODULE:
            if self._mixer_module is None:
                self.loading_screen()
                self._mixer_module = MixerModule()
                ElementManager.mixer_module_init(self._mixer_module, self)
            self._active_modules.append(self._mixer_module)
            return self._mixer_module
        elif module == PRESET_MODULE:
            if self._preset_module is None:
                self._preset_module = PresetModule()
                ElementManager.preset_module_init(self._preset_module, self)
            self._active_modules.append(self._preset_module)
            return self._preset_module

    def _unset_module(self, module):
        self._active_modules.remove(module)

    def get_main_module(self):
        return self._main_module

    def get_mixer_module(self):
        return self._mixer_module

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
                                  Bass.open_midi, main_module=module, mixer_module=screen.get_mixer_module)
        open_midi_button.set_hold_active(False)
        save_file_hover_state_surface = ImageButtonState('hover', './sprite.png', (58, 59, 54, 58))
        save_file_disabled_state_surface = ImageButtonState('disabled', './sprite.png', (58, 156, 54, 58))
        save_file_button = Button('Save File Button', (199, 92, 54, 58), [save_file_hover_state_surface, save_file_disabled_state_surface],
                                  Bass.save_file, main_module=module, mixer_module=screen.get_mixer_module)
        save_file_button.disabled(True)
        save_file_button.set_hold_active(False)
        open_soundfont_hover_state_surface = ImageButtonState('hover', './sprite.png', (116, 59, 54, 58))
        open_soundfont_button = Button('Open SoundFont Button', (258, 92, 54, 58), [open_soundfont_hover_state_surface],
                                       Bass.open_soundFont, module=module)
        open_soundfont_button.set_hold_active(False)
        open_web_hover_state_surface = ImageButtonState('hover', './sprite.png', (176, 59, 54, 58))
        open_web_button = Button('Open Web Button', (316, 92, 54, 58), [open_web_hover_state_surface],
                                     Bass.open_goldmidi_web)
        open_web_button.set_hold_active(False)
        export_mp3_hover_state_surface = ImageButtonState('hover', './sprite.png', (232, 59, 54, 58))
        export_mp3_disabled_state_surface = ImageButtonState('disabled', './sprite.png', (232, 156, 54, 58))
        export_mp3_button = Button('Convert MP3 Button', (372, 92, 54, 58), [export_mp3_hover_state_surface, export_mp3_disabled_state_surface],
                                   Bass.button_exec)
        export_mp3_button.disabled(True)
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
        stop_midi_button = Button('Stop Button', (438, 264, 50, 54), [stop_midi_hover_state_surface], Bass.stop_midi, module=module)
        stop_midi_button.set_hold_active(False)
        play_midi_hover_state_surface = ImageButtonState('hover', './sprite.png', (738, 47, 50, 54))
        play_midi_active_state_surface = ImageButtonState('active', './sprite.png', (738, 102, 50, 54))
        play_midi_disabled_state_surface = ImageButtonState('disabled', './sprite.png', (738, 156, 50, 54))
        play_midi_button = Button('Play Button', (493, 264, 50, 54),
                                  [play_midi_hover_state_surface, play_midi_active_state_surface, play_midi_disabled_state_surface], Bass.play_midi, module=module)
        play_midi_button.disabled(True)
        pause_midi_hover_state_surface = ImageButtonState('hover', './sprite.png', (790, 47, 50, 54))
        pause_midi_active_state_surface = ImageButtonState('active', './sprite.png', (790, 102, 50, 54))
        pause_midi_button = Button('Pause Button', (547, 264, 50, 54),
                                   [pause_midi_hover_state_surface, pause_midi_active_state_surface], Bass.pause_midi, module=module)

        puller = Puller('./sprite.png', (913, 63, 29, 16))
        sliders_font = pygame.font.Font("./fonts/conthrax-sb.ttf", 16)
        global_volume_text = Text('Global Volume Text', (87, 114), sliders_font, '100')
        global_volume_slider = Slider('Global Volume Slider', (87, 151), 148, puller, global_volume_text, 0, 127,
                                      Bass.slider_exec)
        global_pitch_text = Text('Global Pitch Text', (632, 114), sliders_font, '0')
        global_pitch_slider = Slider('Global Pitch Slider', (638, 151), 148, puller, global_pitch_text, -12, 12,
                                     Bass.slider_exec)
        global_pitch_slider.draw(74)
        global_tempo_text = Text('Global Tempo Text', (705, 114), sliders_font, '120')
        global_tempo_slider = Slider('Global Tempo Slider', (712, 151), 148, puller, global_tempo_text, 1, 382,
                                     Bass.slider_exec)
        global_tempo_slider.draw(117)

        midi_name_text = Text('Midi Name Text', (158, 165), sliders_font, 'Midi Name', (36, 71, 84))
        midi_time_text = Text('Midi Time Text', (158, 225), sliders_font, '00:00:00', (36, 71, 84))
        midi_key_text = Text('Midi Key Text', (302, 225), sliders_font, 'Key', (36, 71, 84))

        module.add_objects_to_render([
            open_midi_button,
            save_file_button,
            open_soundfont_button,
            open_web_button,
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

        button_solo_y_position = 23
        button_mixer_width = 32
        solo_track_hover_image = ImageButtonState('hover', './sprite.png', (308, 119, 32, 10))
        solo_track_active_image = ImageButtonState('active', './sprite.png', (278, 119, button_mixer_width, 10))
        solo_track_1_button = Button('Solo Track 1 Button', (10, button_solo_y_position, button_mixer_width, 10), [solo_track_hover_image, solo_track_active_image], Bass.solo_track, main_module=screen.get_main_module, mixer_module=screen.get_mixer_module, channel=0)
        solo_track_2_button = Button('Solo Track 2 Button', (60, button_solo_y_position, button_mixer_width, 10), [solo_track_hover_image, solo_track_active_image], Bass.solo_track, main_module=screen.get_main_module, mixer_module=screen.get_mixer_module, channel=1)
        solo_track_3_button = Button('Solo Track 3 Button', (110, button_solo_y_position, button_mixer_width, 10), [solo_track_hover_image, solo_track_active_image], Bass.solo_track, main_module=screen.get_main_module, mixer_module=screen.get_mixer_module, channel=2)
        solo_track_4_button = Button('Solo Track 4 Button', (160, button_solo_y_position, button_mixer_width, 10), [solo_track_hover_image, solo_track_active_image], Bass.solo_track, main_module=screen.get_main_module, mixer_module=screen.get_mixer_module, channel=3)
        solo_track_5_button = Button('Solo Track 5 Button', (210, button_solo_y_position, button_mixer_width, 10), [solo_track_hover_image, solo_track_active_image], Bass.solo_track, main_module=screen.get_main_module, mixer_module=screen.get_mixer_module, channel=4)
        solo_track_6_button = Button('Solo Track 6 Button', (260, button_solo_y_position, button_mixer_width, 10), [solo_track_hover_image, solo_track_active_image], Bass.solo_track, main_module=screen.get_main_module, mixer_module=screen.get_mixer_module, channel=5)
        solo_track_7_button = Button('Solo Track 7 Button', (310, button_solo_y_position, button_mixer_width, 10), [solo_track_hover_image, solo_track_active_image], Bass.solo_track, main_module=screen.get_main_module, mixer_module=screen.get_mixer_module, channel=6)
        solo_track_8_button = Button('Solo Track 8 Button', (360, button_solo_y_position, button_mixer_width, 10), [solo_track_hover_image, solo_track_active_image], Bass.solo_track, main_module=screen.get_main_module, mixer_module=screen.get_mixer_module, channel=7)
        solo_track_9_button = Button('Solo Track 9 Button', (410, button_solo_y_position, button_mixer_width, 10), [solo_track_hover_image, solo_track_active_image], Bass.solo_track, main_module=screen.get_main_module, mixer_module=screen.get_mixer_module, channel=8)
        solo_track_10_button = Button('Solo Track 10 Button', (460, button_solo_y_position, button_mixer_width, 10), [solo_track_hover_image, solo_track_active_image], Bass.solo_track, main_module=screen.get_main_module, mixer_module=screen.get_mixer_module, channel=9)
        solo_track_11_button = Button('Solo Track 11 Button', (510, button_solo_y_position, button_mixer_width, 10), [solo_track_hover_image, solo_track_active_image], Bass.solo_track, main_module=screen.get_main_module, mixer_module=screen.get_mixer_module, channel=10)
        solo_track_12_button = Button('Solo Track 12 Button', (560, button_solo_y_position, button_mixer_width, 10), [solo_track_hover_image, solo_track_active_image], Bass.solo_track, main_module=screen.get_main_module, mixer_module=screen.get_mixer_module, channel=11)
        solo_track_13_button = Button('Solo Track 13 Button', (610, button_solo_y_position, button_mixer_width, 10), [solo_track_hover_image, solo_track_active_image], Bass.solo_track, main_module=screen.get_main_module, mixer_module=screen.get_mixer_module, channel=12)
        solo_track_14_button = Button('Solo Track 14 Button', (660, button_solo_y_position, button_mixer_width, 10), [solo_track_hover_image, solo_track_active_image], Bass.solo_track, main_module=screen.get_main_module, mixer_module=screen.get_mixer_module, channel=13)
        solo_track_15_button = Button('Solo Track 15 Button', (710, button_solo_y_position, button_mixer_width, 10), [solo_track_hover_image, solo_track_active_image], Bass.solo_track, main_module=screen.get_main_module, mixer_module=screen.get_mixer_module, channel=14)
        solo_track_16_button = Button('Solo Track 16 Button', (760, button_solo_y_position, button_mixer_width, 10), [solo_track_hover_image, solo_track_active_image], Bass.solo_track, main_module=screen.get_main_module, mixer_module=screen.get_mixer_module, channel=15)

        knob_sprite = ImageButtonState('active', './sprite.png', (0, 117, 259, 26))
        knob_reverb_y_position = 59
        reverb_track_1_knob = Knob('Reverb Track 1 Knob', (13, knob_reverb_y_position, 26, 26), knob_sprite, None, Bass.knob_exec)
        reverb_track_2_knob = Knob('Reverb Track 2 Knob', (63, knob_reverb_y_position, 26, 26), knob_sprite, None, Bass.knob_exec)
        reverb_track_3_knob = Knob('Reverb Track 3 Knob', (113, knob_reverb_y_position, 26, 26), knob_sprite, None, Bass.knob_exec)
        reverb_track_4_knob = Knob('Reverb Track 4 Knob', (163, knob_reverb_y_position, 26, 26), knob_sprite, None, Bass.knob_exec)
        reverb_track_5_knob = Knob('Reverb Track 5 Knob', (213, knob_reverb_y_position, 26, 26), knob_sprite, None, Bass.knob_exec)
        reverb_track_6_knob = Knob('Reverb Track 6 Knob', (263, knob_reverb_y_position, 26, 26), knob_sprite, None, Bass.knob_exec)
        reverb_track_7_knob = Knob('Reverb Track 7 Knob', (313, knob_reverb_y_position, 26, 26), knob_sprite, None, Bass.knob_exec)
        reverb_track_8_knob = Knob('Reverb Track 8 Knob', (363, knob_reverb_y_position, 26, 26), knob_sprite, None, Bass.knob_exec)
        reverb_track_9_knob = Knob('Reverb Track 9 Knob', (413, knob_reverb_y_position, 26, 26), knob_sprite, None, Bass.knob_exec)
        reverb_track_10_knob = Knob('Reverb Track 10 Knob', (463, knob_reverb_y_position, 26, 26), knob_sprite, None, Bass.knob_exec)
        reverb_track_11_knob = Knob('Reverb Track 11 Knob', (513, knob_reverb_y_position, 26, 26), knob_sprite, None, Bass.knob_exec)
        reverb_track_12_knob = Knob('Reverb Track 12 Knob', (563, knob_reverb_y_position, 26, 26), knob_sprite, None, Bass.knob_exec)
        reverb_track_13_knob = Knob('Reverb Track 13 Knob', (613, knob_reverb_y_position, 26, 26), knob_sprite, None, Bass.knob_exec)
        reverb_track_14_knob = Knob('Reverb Track 14 Knob', (663, knob_reverb_y_position, 26, 26), knob_sprite, None, Bass.knob_exec)
        reverb_track_15_knob = Knob('Reverb Track 15 Knob', (713, knob_reverb_y_position, 26, 26), knob_sprite, None, Bass.knob_exec)
        reverb_track_16_knob = Knob('Reverb Track 16 Knob', (763, knob_reverb_y_position, 26, 26), knob_sprite, None, Bass.knob_exec)
        knob_chorus_y_position = 95
        chorus_track_1_knob = Knob('Chorus Track 1 Knob', (13, knob_chorus_y_position, 26, 26), knob_sprite, None, Bass.knob_exec)
        chorus_track_2_knob = Knob('Chorus Track 2 Knob', (63, knob_chorus_y_position, 26, 26), knob_sprite, None, Bass.knob_exec)
        chorus_track_3_knob = Knob('Chorus Track 3 Knob', (113, knob_chorus_y_position, 26, 26), knob_sprite, None, Bass.knob_exec)
        chorus_track_4_knob = Knob('Chorus Track 4 Knob', (163, knob_chorus_y_position, 26, 26), knob_sprite, None, Bass.knob_exec)
        chorus_track_5_knob = Knob('Chorus Track 5 Knob', (213, knob_chorus_y_position, 26, 26), knob_sprite, None, Bass.knob_exec)
        chorus_track_6_knob = Knob('Chorus Track 6 Knob', (263, knob_chorus_y_position, 26, 26), knob_sprite, None, Bass.knob_exec)
        chorus_track_7_knob = Knob('Chorus Track 7 Knob', (313, knob_chorus_y_position, 26, 26), knob_sprite, None, Bass.knob_exec)
        chorus_track_8_knob = Knob('Chorus Track 8 Knob', (363, knob_chorus_y_position, 26, 26), knob_sprite, None, Bass.knob_exec)
        chorus_track_9_knob = Knob('Chorus Track 9 Knob', (413, knob_chorus_y_position, 26, 26), knob_sprite, None, Bass.knob_exec)
        chorus_track_10_knob = Knob('Chorus Track 10 Knob', (463, knob_chorus_y_position, 26, 26), knob_sprite, None, Bass.knob_exec)
        chorus_track_11_knob = Knob('Chorus Track 11 Knob', (513, knob_chorus_y_position, 26, 26), knob_sprite, None, Bass.knob_exec)
        chorus_track_12_knob = Knob('Chorus Track 12 Knob', (563, knob_chorus_y_position, 26, 26), knob_sprite, None, Bass.knob_exec)
        chorus_track_13_knob = Knob('Chorus Track 13 Knob', (613, knob_chorus_y_position, 26, 26), knob_sprite, None, Bass.knob_exec)
        chorus_track_14_knob = Knob('Chorus Track 14 Knob', (663, knob_chorus_y_position, 26, 26), knob_sprite, None, Bass.knob_exec)
        chorus_track_15_knob = Knob('Chorus Track 15 Knob', (713, knob_chorus_y_position, 26, 26), knob_sprite, None, Bass.knob_exec)
        chorus_track_16_knob = Knob('Chorus Track 16 Knob', (763, knob_chorus_y_position, 26, 26), knob_sprite, None, Bass.knob_exec)
        knob_pan__position = 133
        pan_track_1_knob = Knob('Pan Track 1 Knob', (13, knob_pan__position, 26, 26), knob_sprite, None, Bass.knob_exec)
        pan_track_2_knob = Knob('Pan Track 2 Knob', (63, knob_pan__position, 26, 26), knob_sprite, None, Bass.knob_exec)
        pan_track_3_knob = Knob('Pan Track 3 Knob', (113, knob_pan__position, 26, 26), knob_sprite, None, Bass.knob_exec)
        pan_track_4_knob = Knob('Pan Track 4 Knob', (163, knob_pan__position, 26, 26), knob_sprite, None, Bass.knob_exec)
        pan_track_5_knob = Knob('Pan Track 5 Knob', (213, knob_pan__position, 26, 26), knob_sprite, None, Bass.knob_exec)
        pan_track_6_knob = Knob('Pan Track 6 Knob', (263, knob_pan__position, 26, 26), knob_sprite, None, Bass.knob_exec)
        pan_track_7_knob = Knob('Pan Track 7 Knob', (313, knob_pan__position, 26, 26), knob_sprite, None, Bass.knob_exec)
        pan_track_8_knob = Knob('Pan Track 8 Knob', (363, knob_pan__position, 26, 26), knob_sprite, None, Bass.knob_exec)
        pan_track_9_knob = Knob('Pan Track 9 Knob', (413, knob_pan__position, 26, 26), knob_sprite, None, Bass.knob_exec)
        pan_track_10_knob = Knob('Pan Track 10 Knob', (463, knob_pan__position, 26, 26), knob_sprite, None, Bass.knob_exec)
        pan_track_11_knob = Knob('Pan Track 11 Knob', (513, knob_pan__position, 26, 26), knob_sprite, None, Bass.knob_exec)
        pan_track_12_knob = Knob('Pan Track 12 Knob', (563, knob_pan__position, 26, 26), knob_sprite, None, Bass.knob_exec)
        pan_track_13_knob = Knob('Pan Track 13 Knob', (613, knob_pan__position, 26, 26), knob_sprite, None, Bass.knob_exec)
        pan_track_14_knob = Knob('Pan Track 14 Knob', (663, knob_pan__position, 26, 26), knob_sprite, None, Bass.knob_exec)
        pan_track_15_knob = Knob('Pan Track 15 Knob', (713, knob_pan__position, 26, 26), knob_sprite, None, Bass.knob_exec)
        pan_track_16_knob = Knob('Pan Track 16 Knob', (763, knob_pan__position, 26, 26), knob_sprite, None, Bass.knob_exec)
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
        mixer_font_small = pygame.font.Font("./fonts/conthrax-sb.ttf", 7)
        mixer_slider_puller = Puller('./sprite.png', (913, 63, 29, 16))
        slider_text_volume_y_position = 167
        volume_track_1_text = Text('Volume Track 1 Text', (13, slider_text_volume_y_position), mixer_font, '100')
        volume_track_2_text = Text('Volume Track 2 Text', (63, slider_text_volume_y_position), mixer_font, '100')
        volume_track_3_text = Text('Volume Track 3 Text', (113, slider_text_volume_y_position), mixer_font, '100')
        volume_track_4_text = Text('Volume Track 4 Text', (163, slider_text_volume_y_position), mixer_font, '100')
        volume_track_5_text = Text('Volume Track 5 Text', (213, slider_text_volume_y_position), mixer_font, '100')
        volume_track_6_text = Text('Volume Track 6 Text', (263, slider_text_volume_y_position), mixer_font, '100')
        volume_track_7_text = Text('Volume Track 7 Text', (313, slider_text_volume_y_position), mixer_font, '100')
        volume_track_8_text = Text('Volume Track 8 Text', (363, slider_text_volume_y_position), mixer_font, '100')
        volume_track_9_text = Text('Volume Track 9 Text', (413, slider_text_volume_y_position), mixer_font, '100')
        volume_track_10_text = Text('Volume Track 10 Text', (463, slider_text_volume_y_position), mixer_font, '100')
        volume_track_11_text = Text('Volume Track 11 Text', (513, slider_text_volume_y_position), mixer_font, '100')
        volume_track_12_text = Text('Volume Track 12 Text', (563, slider_text_volume_y_position), mixer_font, '100')
        volume_track_13_text = Text('Volume Track 13 Text', (613, slider_text_volume_y_position), mixer_font, '100')
        volume_track_14_text = Text('Volume Track 14 Text', (663, slider_text_volume_y_position), mixer_font, '100')
        volume_track_15_text = Text('Volume Track 15 Text', (713, slider_text_volume_y_position), mixer_font, '100')
        volume_track_16_text = Text('Volume Track 16 Text', (763, slider_text_volume_y_position), mixer_font, '100')
        slider_volume_y_position = 200
        volume_track_1_slider = Slider('Volume Track 1 Slider', (11, slider_volume_y_position), 100, mixer_slider_puller, volume_track_1_text, 0, 127, Bass.slider_exec)
        volume_track_2_slider = Slider('Volume Track 2 Slider', (62, slider_volume_y_position), 100, mixer_slider_puller, volume_track_2_text, 0, 127, Bass.slider_exec)
        volume_track_3_slider = Slider('Volume Track 3 Slider', (111, slider_volume_y_position), 100, mixer_slider_puller, volume_track_3_text, 0, 127, Bass.slider_exec)
        volume_track_4_slider = Slider('Volume Track 4 Slider', (162, slider_volume_y_position), 100, mixer_slider_puller, volume_track_4_text, 0, 127, Bass.slider_exec)
        volume_track_5_slider = Slider('Volume Track 5 Slider', (211, slider_volume_y_position), 100, mixer_slider_puller, volume_track_5_text, 0, 127, Bass.slider_exec)
        volume_track_6_slider = Slider('Volume Track 6 Slider', (262, slider_volume_y_position), 100, mixer_slider_puller, volume_track_6_text, 0, 127, Bass.slider_exec)
        volume_track_7_slider = Slider('Volume Track 7 Slider', (311, slider_volume_y_position), 100, mixer_slider_puller, volume_track_7_text, 0, 127, Bass.slider_exec)
        volume_track_8_slider = Slider('Volume Track 8 Slider', (362, slider_volume_y_position), 100, mixer_slider_puller, volume_track_8_text, 0, 127, Bass.slider_exec)
        volume_track_9_slider = Slider('Volume Track 9 Slider', (411, slider_volume_y_position), 100, mixer_slider_puller, volume_track_9_text, 0, 127, Bass.slider_exec)
        volume_track_10_slider = Slider('Volume Track 10 Slider', (462, slider_volume_y_position), 100, mixer_slider_puller, volume_track_10_text, 0, 127, Bass.slider_exec)
        volume_track_11_slider = Slider('Volume Track 11 Slider', (511, slider_volume_y_position), 100, mixer_slider_puller, volume_track_11_text, 0, 127, Bass.slider_exec)
        volume_track_12_slider = Slider('Volume Track 12 Slider', (562, slider_volume_y_position), 100, mixer_slider_puller, volume_track_12_text, 0, 127, Bass.slider_exec)
        volume_track_13_slider = Slider('Volume Track 13 Slider', (611, slider_volume_y_position), 100, mixer_slider_puller, volume_track_13_text, 0, 127, Bass.slider_exec)
        volume_track_14_slider = Slider('Volume Track 14 Slider', (662, slider_volume_y_position), 100, mixer_slider_puller, volume_track_14_text, 0, 127, Bass.slider_exec)
        volume_track_15_slider = Slider('Volume Track 15 Slider', (711, slider_volume_y_position), 100, mixer_slider_puller, volume_track_15_text, 0, 127, Bass.slider_exec)
        volume_track_16_slider = Slider('Volume Track 16 Slider', (762, slider_volume_y_position), 100, mixer_slider_puller, volume_track_16_text, 0, 127, Bass.slider_exec)

        mute_track_hover_image = ImageButtonState('hover', './sprite.png', (309, 130, 32, 10))
        mute_track_active_image = ImageButtonState('active', './sprite.png', (278, 130, 32, 10))
        button_mute_y_position = 37
        mute_tack_1_button = Button('Mute Track 1 Button', (10, button_mute_y_position, button_mixer_width, 10),
                                    [mute_track_hover_image, mute_track_active_image], Bass.mute_track, slider=volume_track_1_slider, main_module=screen.get_main_module, channel=0)
        mute_tack_2_button = Button('Mute Track 2 Button', (60, button_mute_y_position, button_mixer_width, 10),
                                    [mute_track_hover_image, mute_track_active_image], Bass.mute_track,
                                    slider=volume_track_2_slider, main_module=screen.get_main_module, channel=1)
        mute_tack_3_button = Button('Mute Track 3 Button', (110, button_mute_y_position, button_mixer_width, 10),
                                    [mute_track_hover_image, mute_track_active_image], Bass.mute_track,
                                    slider=volume_track_3_slider, main_module=screen.get_main_module, channel=2)
        mute_tack_4_button = Button('Mute Track 4 Button', (160, button_mute_y_position, button_mixer_width, 10),
                                    [mute_track_hover_image, mute_track_active_image], Bass.mute_track,
                                    slider=volume_track_4_slider, main_module=screen.get_main_module, channel=3)
        mute_tack_5_button = Button('Mute Track 5 Button', (210, button_mute_y_position, button_mixer_width, 10),
                                    [mute_track_hover_image, mute_track_active_image], Bass.mute_track,
                                    slider=volume_track_5_slider, main_module=screen.get_main_module, channel=4)
        mute_tack_6_button = Button('Mute Track 6 Button', (260, button_mute_y_position, button_mixer_width, 10),
                                    [mute_track_hover_image, mute_track_active_image], Bass.mute_track,
                                    slider=volume_track_6_slider, main_module=screen.get_main_module, channel=5)
        mute_tack_7_button = Button('Mute Track 7 Button', (310, button_mute_y_position, button_mixer_width, 10),
                                    [mute_track_hover_image, mute_track_active_image], Bass.mute_track,
                                    slider=volume_track_7_slider, main_module=screen.get_main_module, channel=6)
        mute_tack_8_button = Button('Mute Track 8 Button', (360, button_mute_y_position, button_mixer_width, 10),
                                    [mute_track_hover_image, mute_track_active_image], Bass.mute_track,
                                    slider=volume_track_8_slider, main_module=screen.get_main_module, channel=7)
        mute_tack_9_button = Button('Mute Track 9 Button', (410, button_mute_y_position, button_mixer_width, 10),
                                    [mute_track_hover_image, mute_track_active_image], Bass.mute_track,
                                    slider=volume_track_9_slider, main_module=screen.get_main_module, channel=8)
        mute_tack_10_button = Button('Mute Track 10 Button', (460, button_mute_y_position, button_mixer_width, 10),
                                    [mute_track_hover_image, mute_track_active_image], Bass.mute_track,
                                    slider=volume_track_10_slider, main_module=screen.get_main_module, channel=9)
        mute_tack_11_button = Button('Mute Track 11 Button', (510, button_mute_y_position, button_mixer_width, 10),
                                    [mute_track_hover_image, mute_track_active_image], Bass.mute_track,
                                    slider=volume_track_11_slider, main_module=screen.get_main_module, channel=10)
        mute_tack_12_button = Button('Mute Track 12 Button', (560, button_mute_y_position, button_mixer_width, 10),
                                    [mute_track_hover_image, mute_track_active_image], Bass.mute_track,
                                    slider=volume_track_12_slider, main_module=screen.get_main_module, channel=11)
        mute_tack_13_button = Button('Mute Track 13 Button', (610, button_mute_y_position, button_mixer_width, 10),
                                    [mute_track_hover_image, mute_track_active_image], Bass.mute_track,
                                    slider=volume_track_13_slider, main_module=screen.get_main_module, channel=12)
        mute_tack_14_button = Button('Mute Track 14 Button', (660, button_mute_y_position, button_mixer_width, 10),
                                    [mute_track_hover_image, mute_track_active_image], Bass.mute_track,
                                    slider=volume_track_14_slider, main_module=screen.get_main_module, channel=13)
        mute_tack_15_button = Button('Mute Track 15 Button', (710, button_mute_y_position, button_mixer_width, 10),
                                    [mute_track_hover_image, mute_track_active_image], Bass.mute_track,
                                    slider=volume_track_15_slider, main_module=screen.get_main_module, channel=14)
        mute_tack_16_button = Button('Mute Track 16 Button', (760, button_mute_y_position, button_mixer_width, 10),
                                    [mute_track_hover_image, mute_track_active_image], Bass.mute_track,
                                    slider=volume_track_16_slider, main_module=screen.get_main_module, channel=15)

        change_preset_1_button = Button('Change Preset 1 Button', (7, 319, 36, 12), [], screen.toggle_module, module=PRESET_MODULE)
        change_preset_1_text = Text("Change Preset 1 Text", (10, 318), mixer_font_small, "Piano A")

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
            change_preset_1_button,
            change_preset_1_text
        ])

    @staticmethod
    def preset_module_init(module, screen):
        print('Adding elements for preset module')
        list_font = pygame.font.Font("./fonts/conthrax-sb.ttf", 10)
        presets_list = ListSelection('Presets List', (16, 35, 790, 100), list_font, 3, 4, 5, Bass.get_general_midi_presets, Bass.set_preset_channel, main_module=screen.get_main_module)

        module.add_objects_to_render([
            presets_list
        ])


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
LIST SELECTION
"""

class IdleList(State):

    @staticmethod
    def on_enter_state(selection_list):
        selection_list.draw()

    @staticmethod
    def update(selection_list):
        if selection_list.is_mouse_over() and selection_list.is_mouse_button_down():
            selection_list.click_update()
            pygame.time.wait(State.WAIT_TIME)


class ActiveList(State):

    @staticmethod
    def on_enter_state(element):
        pass

    @staticmethod
    def update(element):
        pass


class ListSelection:
    STATES = {
        "idle": IdleList,
        "active": ActiveList
    }

    def __init__(self, name, area, font, text_vertical_space, columns, padding, get_items_function, function_to_bind, **kwargs):
        self._name = name
        self._area = area
        self._offset_position = (0, 0)
        self._font = font
        self._columns = columns
        self._padding = padding
        self._text_vertical_space = text_vertical_space
        self._items_list = []
        self._index_first_item_page = 0
        self._get_items_function = get_items_function
        self._bounded_function = function_to_bind
        self._kwargs_function = kwargs
        self._state = None
        self._surface = None

        self.set_state(ListSelection.STATES["idle"])

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

    def set_items_function(self, function):
        self._get_items_function = function

    def click_update(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        position_x, position_y = self.get_position()
        width, height = self.get_size()
        if mouse_x - position_x > width -17:
            if mouse_y - position_y < 11:
                if self._index_first_item_page > 0:
                    self._index_first_item_page -= 25
            else:
                if self._index_first_item_page < 100:
                    self._index_first_item_page += 25
            self.draw()
        else:
            rel_pos_x = mouse_x - position_x
            rel_pos_y = mouse_y - position_y

            font_height = self._font.get_height()
            items_per_column = height / font_height
            row = int(rel_pos_y / font_height)
            col = int(rel_pos_x / 180)

            index_item = self._index_first_item_page + (col * items_per_column) + row
            self._kwargs_function["index_item"] = index_item
            self.call_bind_function()

    def draw(self):
        self._items_list = self._get_items_function()[self._index_first_item_page:]
        width, height = self.get_size()
        self._surface = pygame.Surface((width, height), pygame.SRCALPHA)

        font_height = self._font.get_height()
        text_pos_x, text_pos_y = (0, 0)
        display_items = self._index_first_item_page
        xpace = width / self._columns
        for item in self._items_list:
            if text_pos_x + xpace < width:
                text_pos_y += self._text_vertical_space
                preset = Text('Preset', (text_pos_x, text_pos_y), self._font, item[:26])
                self._surface.blit(preset.get_surface(), preset.get_position())
                display_items = display_items + 1
                text_pos_y += font_height + self._text_vertical_space
                if text_pos_y + font_height > height:
                    text_pos_x += xpace
                    text_pos_y = 0
            else:
                break

        print(display_items)


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
        knob.draw(value_display=True)
        pass

    @staticmethod
    def update(knob):
        if not knob.is_mouse_over():
            knob.draw(value_display=False)
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
        if not knob.is_mouse_over():
            if knob.is_mouse_button_down():
                pass
            else:
                knob.call_bind_function()
                print('Knob calling ', knob.get_name())
                knob.set_state(knob.STATES["idle"])
                knob.draw(value_display=False)
                knob.set_state(knob.STATES["idle"])
        else:
            if knob.is_mouse_button_down():
                knob.draw()
            else:
                knob.draw(value_display=False)
                knob.set_state(knob.STATES["idle"])


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
            self._surface.fill(DEBUG_COLOR)
        self._state = None
        self._relative_track_point = None
        self._bounded_function = function_to_bind
        self._kwargs_function = kwargs
        # TODO: Help Text
        self.set_state(self.STATES["idle"])
        self._value = 0
        self._text_display = None
        self.draw()

    def _linear(self, value, min_in, max_in, min_out, max_out):
        a = (float(max_out) - float(min_out)) / (float(max_in) - float(min_in))
        b = float(max_out) - float(a) * float(max_in)
        new_value = float(a) * float(value) + float(b)
        return float(new_value)

    def _add_padding(self, area, padding, widthHeightSolo=False):
        new_area = []
        count = 0
        for item in area:
            if widthHeightSolo and count < 2:
                count += 1
                continue
            new_area.append(item)

        if len(new_area) == 4:
            new_area[0] += padding
            new_area[1] += padding
            new_area[2] -= padding
            new_area[3] -= padding
        elif len(new_area) == 2:
            new_area[0] -= padding
            new_area[1] -= padding

        return tuple(new_area)

    def _limit(self, value, min, max):
        if min > value:
            value = min
        elif max < value:
            value = max

        return value

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

    def draw(self, value=None, value_display=None):
        if value is None:
            if self._relative_track_point is not None:
                raw_value = pygame.mouse.get_pos()[0] - self._relative_track_point
                convert_value = self._linear(raw_value, -14, 14, 0, 9)
                self._value = self._limit(convert_value, 0, 9)
        else:
            self._value = value
        width, height = self.get_size()
        position_x = width * int(self._value)

        if value_display is not None:
            if value_display is True:
                self._surface = pygame.Surface((50, 50), pygame.SRCALPHA)
                font_display = pygame.font.Font("./fonts/conthrax-sb.ttf", 12)
                self._text_display = Text("knob value", (0, 0), font_display, '-', (245, 245, 245))
            else:
                self._text_display = None
                self._surface = pygame.Surface(self.get_size(), pygame.SRCALPHA)
#                self._surface.fill((0, 0, 0, 0))

        self._surface.blit(self._knob_sprite.get_surface(), (0, 0), (position_x, 0, width, height))

        if self._text_display:
            display_size = self._add_padding(self._area, 5, widthHeightSolo=True)
            display = pygame.Surface((25, 15), pygame.SRCALPHA)
            display.fill(color=(10, 10, 10, 200))
            self._surface.blit(display, (20, 0))
            self._text_display.render(str(int(self._linear(self._value, 0, 9, 0, 127))))
            self._surface.blit(self._text_display.get_surface(), (22, 0))

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

    def raw_to_knob_value(self, value):
        return self._linear(value, 0, 127, 0, 9)


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
        function = button.call_bind_function()
        print("Return from function: ", function)
        if not function:
            button.set_state(button.STATES["idle"])

    @staticmethod
    def update(button):
        if not button.is_hold_active():
            button.set_state(button.STATES["idle"])
        elif button.is_mouse_over() and button.is_mouse_button_down():
            function = button.call_bind_function()
            if function:
                button.set_state(button.STATES["idle"])
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
            successful = self._bounded_function()
        else:
            successful = self._bounded_function(self._kwargs_function)

        return successful

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

    def set_idle_state(self):
        self._state = self.STATES["idle"]
        self._state.on_enter_state(self)

    def set_hold_active(self, active=True):
        self._hold_active = active

    def set_offset_height(self, offset):
        self._offset_position = (self._offset_position[0], offset)

    def set_surface_to_state(self, state):
        if state is None:
            self._surface = pygame.Surface((self._area[2], self._area[3]), pygame.SRCALPHA)
            if DEBUG:
                self._surface.fill(DEBUG_COLOR)
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
        if puller_half_height > position:
            position = puller_half_height
        elif height - puller_half_height < position:
            position = height - puller_half_height
        return position - puller_half_height

    def _has_text(self):
        return True if self._text is not None else False

    def get_name(self):
        return self._name

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
            self._surface.fill(DEBUG_COLOR)

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

    def raw_to_puller_value(self, value, min=None, max=None):
        min = min if min is not None else self._range[0]
        max = max if max is not None else self._range[1]
        return self._linear(value, min, max, self.get_level_bar_height(), 0)


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

    def get_name(self):
        return self._name

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
