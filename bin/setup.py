from setuptools import setup
import shutil
import os

PACKAGE = 'periscope-gnome'
VERSION = '0.1.12'

os.makedirs('debian/python-gnome/usr/lib/nautilus/extensions-2.0/python/')
shutil.copy('periscope-nautilus/periscope-nautilus.py', 'debian/python-gnome/usr/lib/nautilus/extensions-2.0/python/')
