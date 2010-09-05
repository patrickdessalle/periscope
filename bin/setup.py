from setuptools import setup
import shutil
import os
import version

PACKAGE = 'periscope-gnome'
VERSION = version.VERSION

try:
	os.makedirs("./debian/periscope-gnome/usr/lib/nautilus/extensions-2.0/python")
except:
	pass
shutil.copy('periscope-nautilus/periscope-nautilus.py', 'debian/periscope-gnome/usr/lib/nautilus/extensions-2.0/python')
