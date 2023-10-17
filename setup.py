import sys
from cx_Freeze import setup, Executable

# base="Win32GUI" should be used only for Windows GUI app
base = "Win32GUI" if sys.platform == "win32" else None

setup(
  executables=[
    Executable("run_script.py", base=base, target_name="es-fieldusage"),
  ]
)
