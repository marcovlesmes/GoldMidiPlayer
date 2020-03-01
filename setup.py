import cx_Freeze

executables = cx_Freeze.Executable('gold_midi.py', base='Win32GUI', targetName='gold_midi_player.exe')
cx_Freeze.setup(
    name="GoldMidiPlayer",
    options={
        "build_exe": {
            "packages": [
                "pygame",
                "sys",
                "os",
                "Tkinter",
                "pybass",
                "time",
                "Crypto",
                "ConfigParser"
            ],
            "include_files": [
                "config.cfg",
                "main_screen.png",
                "mixer_screen.png",
                "piano_roll_screen.png",
                "settings_screen.png",
                "mute_icon.png",
                "solo_icon.png",
                "slider_puller.png",
                "sprite.png",
                "goldmidi_x32/Scripts/bass.dll",
                "goldmidi_x32/Scripts/bass_aac.dll",
                "goldmidi_x32/Scripts/bassmidi.dll",
                "sound_fonts/default.csf"
            ]
        }
    },
    executables=[
        executables
    ]
)

# python setup.py build -> 23-01-2020