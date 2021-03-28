import sys
from cx_Freeze import setup, Executable
import os

os.environ['TCL_LIBRARY'] = "C:/Python38/tcl/tcl8.6"
os.environ['TK_LIBRARY'] = "C:/Python38/tcl/tk8.6"
include_files = [
    "C:/Python38/DLLs/tk86t.dll",
    "C:/Python38/DLLs/tcl86t.dll",
]

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    "include_files": include_files,
    "includes": ["configparser", "re", "tkinter"],
    "excludes": []
}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(  name = "Interrobang",
        version = "0.1",
        description = "A small text editor",
        options = {"build_exe": build_exe_options},
        executables = [Executable("interrobang.py", base=base)])