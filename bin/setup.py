from setuptools import setup
import shutil
import os
import version

PACKAGE = 'periscope-gnome'
VERSION = version.VERSION

setup(name = PACKAGE, version = VERSION,
      platforms=['all'],
      license = "GNU LGPL",
      description = "Use periscope in Nautilus to download subtitles",
      author = "Patrick Dessalle",
      author_email = "patrick.dessalle@gmail.com",
      url = "http://code.google.com/p/periscope/",
      packages= [ "periscope-nautilus" ],
      py_modules=["periscope"],
      scripts = [ "periscope-nautilus.py" ]
      )
