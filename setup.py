import cx_Freeze

executables = cx_Freeze.Executable('gold_midi.py', base='Win32GUI')
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
                "background.png",
                "background_settings.png",
                "sprite.png",
                "goldmidi_x32/Scripts/bass.dll",
                "goldmidi_x32/Scripts/bass_aac.dll",
                "goldmidi_x32/Scripts/bassmidi.dll",
                "sound_fonts/default_decoded.sf2",
                "sound_fonts/default.sfc"
            ]
        }
    },
    executables=[
        executables
    ]
)
