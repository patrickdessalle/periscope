from setuptools import setup

PACKAGE = 'periscope'

setup(name = PACKAGE,
      version = 'dev',
      license = "GNU LGPL",
      description = "Python module to download subtitles for a given video file",
      author = "Patrick Dessalle",
      author_email = "patrick.dessalle@gmail.com",
      url = "http://code.google.com/p/periscope/",
      packages= [ "periscope", "periscope/plugins" ],
      py_modules=["periscope"],
      scripts = [ "bin/periscope" ],
      install_requires = ["BeautifulSoup >= 3.2.0"]
      )
