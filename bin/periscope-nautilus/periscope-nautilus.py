# -*- coding: utf-8 -*-

#   This file is part of periscope.
#   Copyright (c) 2008-2011 Patrick Dessalle <patrick@dessalle.be>
#   Ported to GTK3/PyGI with multiprocessing by Shock <shock@corezero.net>
#
#    periscope is free software; you can redistribute it and/or
#    modify it under the terms of the GNU General Public
#    License as published by the Free Software Foundation; either
#    version 2 of the License, or (at your option) any later version.
#
#    periscope is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with periscope; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from gi.repository import Gtk, Gio, GObject, Nautilus
from multiprocessing import Process, Queue
from Queue import Empty
from time import sleep
# import urllib2
import os
import gettext
# import logging
import xdg.BaseDirectory as bd # required
try:
    from gi.repository import Notify
except ImportError:
    pass

import periscope

# i18n stuff
gettext.install('periscope-nautilus')

class DownloadSubtitles(GObject.GObject, Nautilus.MenuProvider):
    ''' This class is to be used in Nautilus with the python-nautilus extension. 
    It provides a context menu on video file to download subtitles.'''
    def __init__(self):
        if Notify:
            Notify.init("periscope subtitles downloader")
        self.cache_folder = os.path.join(bd.xdg_config_home, "periscope")

    def get_file_items(self, window, files):
        # Keep only the files we want (right type and file)
        files = [ f for f in files if self.is_valid(f)]
        if len(files) == 0:
            return

        item = Nautilus.MenuItem(name='Nautilus::download_subtitles',
                                 label=_('Find subtitles for this video'),
                                 tip=_('Download subtitles for this video'),
                                 icon=Gtk.STOCK_FIND_AND_REPLACE)
        item.connect('activate', self.menu_activate_cb, files)
        return item,

    def menu_activate_cb(self, menu, files):
        #List the valid files
        videos = [f for f in files if not f.is_gone() and self.is_valid(f)]
        # Get the file paths from gvfs so we support non local file systems, yay!
        g = Gio.Vfs.get_default()
        videos = map(lambda f: g.get_file_for_uri(f.get_uri()).get_path(), videos)

        # Download the subtitles in a new process and get the results in this process via a Queue
        queue = Queue()
        invoker = PeriscopeInvoker(videos, self.cache_folder, queue)
        invoker.start()
        result = []
        while not result:
            try:
                result = queue.get_nowait()
            except Empty:
                pass
            finally:
                Gtk.main_iteration_do(False) # a blocking version with timeout would have been nice
                sleep(0.01)
        [found, notfound] = result
        self.notify(found, notfound)
        invoker.join()

    def is_valid(self, f):
        return f.get_mime_type() in periscope.SUPPORTED_FORMATS and (f.get_uri_scheme() == 'file' or f.get_uri_scheme() == 'smb')

    def notify(self, found, notfound):
        ''' Use Notify to warn the user that subtitles have been downloaded'''
        if Notify:
            title = "periscope found %s out of %s subtitles" %(len(found), len(found) + len(notfound))
            if len(notfound) > 0:
                msg = _("Could not find: \n")
                filenames = [os.path.basename(f["filename"]) for f in notfound]
                msg += "\n".join(filenames)
                msg += "\n"

            if len(found) > 0:
                msg = _("Found: \n")
                filenames = [os.path.basename(f["filename"]) + " ("+f['lang']+")" for f in found]
                msg += "\n".join(filenames)

            n = Notify.Notification.new(title, msg, Gtk.STOCK_FIND_AND_REPLACE)
            n.set_timeout(Notify.EXPIRES_DEFAULT)
            n.show()
        else:
            pass

class PeriscopeInvoker(Process):
    ''' Thread that will call persicope in the background'''
    def __init__(self, filenames, cache_folder, queue):
        self.filenames = filenames
        self.found = []
        self.notfound = []
        self.cache_folder = cache_folder
        self.queue = queue
        Process.__init__(self)

    def run(self):
        subdl = periscope.Periscope(self.cache_folder)
        print "prefered languages: %s" %subdl.preferedLanguages
        for filename in self.filenames:
            subtitle = subdl.downloadSubtitle(filename, subdl.preferedLanguages)
            if subtitle:
                del subtitle["plugin"] # multiprocessing Queue won't be able to pickle this and will bark
                self.found.append(subtitle)
            else:
                self.notfound.append({"filename": filename })
        self.queue.put([self.found, self.notfound])
        self.queue.close() # we won't have anything more to transmit to the parent process
