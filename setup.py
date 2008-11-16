from setuptools import setup

PACKAGE = 'periscope'
VERSION = '0.1.3'

#setup(name=PACKAGE, version=VERSION, packages=['plugins', 'periscope.py', '__init__.py'])

setup(name = PACKAGE, version = VERSION,
      license = "GNU GPL",
      description = "Python module to download subtitles for a given video file",
      author = "Patrick Dessalle",
      author_email = "patrick.dessalle@gmail.com",
      url = "http://code.google.com/p/periscope/",
      packages= [ "", "plugins" ],
      py_modules=["periscope"],
      scripts = [ "bin/periscope" ]
      )
