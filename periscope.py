#!/usr/bin/python
# -*- coding: utf-8 -*-

#   This file is part of periscope.
#   Copyright (c) 2008-2011 Patrick Dessalle <patrick@dessalle.be>
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

import os
import mimetypes
from optparse import OptionParser
import logging
import periscope

log = logging.getLogger(__name__)

SUPPORTED_FORMATS = 'video/x-msvideo', 'video/quicktime', 'video/x-matroska', 'video/mp4'

def main():
    '''Download subtitles'''
    # parse command line options
    parser = OptionParser("usage: %prog [options] file1 file2", version = periscope.VERSION)
    parser.add_option("-l", "--language", action="append", dest="langs", help="wanted language (ISO 639-1 two chars) for the subtitles (fr, en, ja, ...). If none is specified will download a subtitle in any language. This option can be used multiple times like %prog -l fr -l en file1 will try to download in french and then in english if no french subtitles are found.")
    parser.add_option("-f", "--force", action="store_true", dest="force_download", help="force download of a subtitle even there is already one present")
    parser.add_option("-q", "--query", action="append", dest="queries", help="query to send to the subtitles website")
    parser.add_option("--cache-folder", action="store", type="string", dest="cache_folder", help="location of the periscope cache/config folder (default is ~/.config/periscope)")
    parser.add_option("--list-plugins", action="store_true", dest="show_plugins", help="list all plugins supported by periscope")
    parser.add_option("--list-active-plugins", action="store_true", dest="show_active_plugins", help="list all plugins used to search subtitles (a subset of all the supported plugins)")
    parser.add_option("--quiet", action="store_true", dest="quiet", help="run in quiet mode (only show warn and error messages)")
    parser.add_option("--debug", action="store_true", dest="debug", help="set the logging level to debug")
    (options, args) = parser.parse_args()
    
    if not args:
        print parser.print_help()
        exit()

    # process args
    if options.debug :
        logging.basicConfig(level=logging.DEBUG)
    elif options.quiet :
        logging.basicConfig(level=logging.WARN)
    else :
        logging.basicConfig(level=logging.INFO)
        

    if not options.cache_folder:
        try:
            import xdg.BaseDirectory as bd
            options.cache_folder = os.path.join(bd.xdg_config_home, "periscope")
        except:
            home = os.path.expanduser("~")
            if home == "~":
                log.error("Could not generate a cache folder at the home location using XDG (freedesktop). You must specify a --cache-config folder where the cache and config will be located (always use the same folder).")
                exit()
            options.cache_folder = os.path.join(home, ".config", "periscope")

    
    periscope_client = periscope.Periscope(options.cache_folder)
        
    if options.show_active_plugins:
        print "Active plugins: "
        plugins = periscope_client.listActivePlugins()
        for plugin in plugins:
            print "%s" %(plugin)
        exit()
        
    if options.show_plugins:
        print "All plugins: "
        plugins = periscope_client.listExistingPlugins()
        for plugin in plugins:
            print "%s" %(plugin)
        exit()
            
    if options.queries: args += options.queries
    videos = []
    for arg in args:
        videos += recursive_search(arg, options)

    subs = []
    for arg in videos:
        if not options.langs: #Look into the config
            log.info("No lang given, looking into config file")
            langs = periscope_client.preferedLanguages
        else:
            langs = options.langs
        sub = periscope_client.downloadSubtitle(arg, langs)
        if sub:
            subs.append(sub)
    
    log.info("*"*50)
    log.info("Downloaded %s subtitles" %len(subs))
    for s in subs:
        log.info(s['lang'] + " - " + s['subtitlepath'])
    log.info("*"*50)
    if len(subs) == 0:
        exit(1)


def recursive_search(entry, options):
    '''searches files in the dir'''
    files = []
    if os.path.isdir(entry):
        #TODO if hidden folder, don't keep going (how to handle windows/mac/linux ?)
        for e in os.listdir(entry):
            files += recursive_search(os.path.join(entry, e), options)
    elif os.path.isfile(entry):
        # Add mkv mimetype to the list
        mimetypes.add_type("video/x-matroska", ".mkv")
        mimetype = mimetypes.guess_type(entry)[0]
        if mimetype in SUPPORTED_FORMATS:
            # Add it to the list only if there is not already one (or forced)
            basepath = os.path.splitext(entry)[0]
            if options.force_download or not (os.path.exists(basepath+'.srt') or os.path.exists(basepath + '.sub')):
                files.append(os.path.normpath(entry))
            else:
                log.info("Skipping file %s as it already has a subtitle. Use the --force option to force the download" % entry)
        else :
            log.info("%s mimetype is '%s' which is not a supported video format (%s)" %(entry, mimetype, SUPPORTED_FORMATS))
    return files
    
if __name__ == "__main__":
    main()
