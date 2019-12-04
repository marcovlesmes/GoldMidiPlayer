import cx_Freeze

executables = [cx_Freeze.Executable("gold_midi.py", base="Win32GUI")]

cx_Freeze.setup(
    name="GoldMidiPlayer",
    options={"build_exe": {"packages": ["pygame", "sys", "os", "Tkinter", "pybass", "time", "Crypto"],
                           "include_files": [
                                "background.png",
                                "goldmidi_x32/Scripts/bass.dll",
                                "goldmidi_x32/Scripts/bass_aac.dll",
                                "goldmidi_x32/Scripts/bassmidi.dll",
                                "default.sf2",
                                "default.sfc"
                           ]}},
    executables=executables
)

