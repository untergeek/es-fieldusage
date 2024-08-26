#!/usr/bin/env python3
"""Post Docker 'build' phase script"""
import shutil
from platform import machine, system, python_version

MAJOR, MINOR = tuple(python_version().split('.')[:-1])
SYSTEM = system().lower()
BUILD = f'build/exe.{system().lower()}-{machine()}-{MAJOR}.{MINOR}'
TARGET = 'executable_build'

# Rename the path of BUILD to be generic enough for Dockerfile to get
# In other words, rename it to 'curator_build'
shutil.move(BUILD, TARGET)
