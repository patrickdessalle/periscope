from setuptools import setup
import shutil

PACKAGE = 'periscope-gnome'
VERSION = '0.1.5'

shutil.copy('periscope-nautilus/periscope-nautilus.py', 'debian/python-gnome/usr/lib/nautilus/extensions-2.0/python/')
