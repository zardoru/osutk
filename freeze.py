# https://cx-freeze.readthedocs.io/en/latest/distutils.html
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": ["os", "tkinter"]}

setup(
    name="osutk",
    version="0.1",
    description="osutk tools in python for osu!",
    options={
        "build_exe": build_exe_options
    },
    executables=[
        Executable("tools/check_duplicate_hitsounds.py"),
        Executable("tools/copy_hitsounds.py"),
        Executable("tools/make_hitsound_diff.py")
    ],
    author="Agka"
)
