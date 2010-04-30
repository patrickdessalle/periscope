from setuptools import setup
import version

PACKAGE = 'periscope'
VERSION = version.VERSION

#setup(name=PACKAGE, version=VERSION, packages=['plugins', 'periscope.py', '__init__.py'])

setup(name = PACKAGE, version = VERSION,
      license = "GNU LGPL",
      description = "Python module to download subtitles for a given video file",
      author = "Patrick Dessalle",
      author_email = "patrick.dessalle@gmail.com",
      url = "http://code.google.com/p/periscope/",
      packages= [ "periscope", "periscope/plugins" ],
      py_modules=["periscope"],
      scripts = [ "bin/periscope" ]
      )
