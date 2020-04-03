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
                "Crypto"
            ],
            "include_files": [
                "main_screen.png",
                "mixer_screen.png",
                "piano_roll_screen.png",
                "settings_screen.png",
                "playlist_screen.png",
                "slider_puller.png",
                "slider_puller_v.png",
                "sprite.png",
                "goldmidi_x32/Scripts/bass.dll",
                "goldmidi_x32/Scripts/bass_aac.dll",
                "goldmidi_x32/Scripts/bassmidi.dll",
                "sound_fonts/default.csf",
                "midis/BackInBlack.mid"
            ]
        }
    },
    executables=[
        executables
    ]
)

# python setup.py build -> 23-01-2020