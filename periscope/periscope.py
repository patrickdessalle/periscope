#!/usr/bin/python
# -*- coding: utf-8 -*-

#   This file is part of periscope.
#   Copyright (c) 2008-2011 Patrick Dessalle <patrick@dessalle.be>
#
#    periscope is free software; you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    periscope is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with periscope; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import getopt
import sys
import os
import threading
import logging
from Queue import Queue

import traceback
import ConfigParser

log = logging.getLogger(__name__)

try:
    import xdg.BaseDirectory as bd
    is_local = True
except ImportError:
    is_local = False

import plugins
import version
import locale

SUPPORTED_FORMATS = 'video/x-msvideo', 'video/quicktime', 'video/x-matroska', 'video/mp4'
VERSION = version.VERSION

class Periscope:
    ''' Main Periscope class'''
    
    def __init__(self, cache_folder=None):
        self.config = ConfigParser.SafeConfigParser({"lang": "", "plugins" : "" })        
        self.config_file = os.path.join(cache_folder, "config")
        self.cache_path = cache_folder
        if not os.path.exists(self.config_file):
            folder = os.path.dirname(self.config_file)
            if not os.path.exists(folder):
                log.info("Creating folder %s" %folder)
                os.mkdir(folder)
                log.info("Creating config file")
                configfile = open(self.config_file, "w")
                self.config.write(configfile)
                configfile.close()
        else:
            #Load it
            self.config.read(self.config_file)

        self.pluginNames = self.get_preferedPlugins()
        self._preferedLanguages = None

    def get_preferedLanguages(self):
        ''' Get the prefered language from the config file '''
        configLang = self.config.get("DEFAULT", "lang")
        log.info("lang read from config: " + configLang)
        if configLang == "":
            try :
                return [locale.getdefaultlocale()[0][:2]]
            except :
                return ["en"]
        else:
            return map(lambda x : x.strip(), configLang.split(","))

    def set_preferedLanguages(self, langs):
        ''' Update the config file to set the prefered language '''
        self.config.set("DEFAULT", "lang", ",".join(langs))
        configfile = open(self.config_file, "w")
        self.config.write(configfile)
        configfile.close()

    def get_preferedPlugins(self):
        ''' Get the prefered plugins from the config file '''
        configPlugins = self.config.get("DEFAULT", "plugins")
        if not configPlugins or configPlugins.strip() == "":
            return self.listExistingPlugins()
        else :
            log.info("plugins read from config : " + configPlugins)
            return map(lambda x : x.strip(), configPlugins.split(","))
            
    def set_preferedPlugins(self, newPlugins):
        ''' Update the config file to set the prefered plugins) '''
        self.config.set("DEFAULT", "plugins", ",".join(newPlugins))
        configfile = open(self.config_file, "w")
        self.config.write(configfile)
        configfile.close()
        

    # Getter/setter for the property preferedLanguages
    preferedLanguages = property(get_preferedLanguages, set_preferedLanguages)
    preferedPlugins = property(get_preferedPlugins, set_preferedPlugins)
    
    def deactivatePlugin(self, pluginName):
        ''' Remove a plugin from the list '''
        self.pluginNames -= pluginName
        self.set_preferedPlugins(self.pluginNames)
        
    def activatePlugin(self, pluginName):
        ''' Activate a plugin '''
        if pluginName not in self.listExistingPlugins():
            raise ImportError("No plugin with the name %s exists" %pluginName)
        self.pluginNames += pluginName
        self.set_preferedPlugins(self.pluginNames)
        
    def listActivePlugins(self):
        ''' Return all active plugins '''
        return self.pluginNames
        
    def listExistingPlugins(self):
        ''' List all possible plugins from the plugin folder '''
        return map(lambda x : x.__name__, plugins.SubtitleDatabase.SubtitleDB.__subclasses__())
    
    def listSubtitles(self, filename, langs=None):
        '''Searches subtitles within the active plugins and returns all found matching subtitles ordered by language then by plugin.'''
        #if not os.path.isfile(filename):
            #raise InvalidFileException(filename, "does not exist")
    
        log.info("Searching subtitles for %s with langs %s" %(filename, langs))
        subtitles = []
        q = Queue()
        for name in self.pluginNames:
            try :
                plugin = getattr(plugins, name)(self.config, self.cache_path)
                log.info("Searching on %s " %plugin.__class__.__name__)
                thread = threading.Thread(target=plugin.searchInThread, args=(q, filename, langs))
                thread.start()
            except ImportError :
                log.error("Plugin %s is not a valid plugin name. Skipping it.")        

        # Get data from the queue and wait till we have a result
        for name in self.pluginNames:
            subs = q.get(True)
            if subs and len(subs) > 0:
                if not langs:
                    subtitles += subs
                else:
                    for sub in subs:
                        if sub["lang"] in langs:
                            subtitles += [sub] # Add an array with just that sub
            
        if len(subtitles) == 0:
            return []
        return subtitles
    
    
    def selectBestSubtitle(self, subtitles, langs=None):
        '''Searches subtitles from plugins and returns the best subtitles from all candidates'''
        if not subtitles:
            return None

        if not langs: # No preferred language => return the first
                return subtitles[0]
        
        subtitles = self.__orderSubtitles__(subtitles)
        for l in langs:
            if subtitles.has_key(l) and len(subtitles[l]):
                return subtitles[l][0]

        return None #Could not find subtitles

    def downloadSubtitle(self, filename, langs=None):
        ''' Takes a filename and a language and creates ONE subtitle through plugins'''
        subtitles = self.listSubtitles(filename, langs)
        if subtitles:
            log.debug("All subtitles: ")
            log.debug(subtitles)    
            return self.attemptDownloadSubtitle(subtitles, langs)
        else:
            return None
        
        
    def attemptDownloadSubtitle(self, subtitles, langs):
        subtitle = self.selectBestSubtitle(subtitles, langs)
        if subtitle:
            log.info("Trying to download subtitle: %s" %subtitle['link'])
            #Download the subtitle
            try:
                subpath = subtitle["plugin"].createFile(subtitle)        
                if subpath:    
                    subtitle["subtitlepath"] = subpath
                    return subtitle
                else:
                    # throw exception to remove it
                    raise Exception("Not downloaded")
            except Exception as inst:
                # Could not download that subtitle, remove it
                log.warn("Subtitle %s could not be downloaded, trying the next on the list" %subtitle['link'])
                etype = sys.exc_info()[0]
                evalue = sys.exc_info()[1]
                etb = traceback.extract_tb(sys.exc_info()[2])
                log.error("Type[%s], Message [%s], Traceback[%s]" % (etype,evalue,etb))
                subtitles.remove(subtitle)
                return self.attemptDownloadSubtitle(subtitles, langs)
        else :
            log.error("No subtitles could be chosen.")
            return None        

    def guessFileData(self, filename):
        subdb = plugins.SubtitleDatabase.SubtitleDB(None)
        return subdb.guessFileData(filename)        
        
    def __orderSubtitles__(self, subs):
        '''reorders the subtitles according to the languages then the website'''
        try:
            from collections import defaultdict
            subtitles = defaultdict(list) #Order matters (order of plugin and result from plugins)
            for s in subs:
                subtitles[s["lang"]].append(s)
            return subtitles
        except ImportError, e: #Don't use Python 2.5
            subtitles = {}
            for s in subs:
                # return subtitles[s["lang"]], if it does not exist, set it to [] and return it, then append the subtitle
                subtitles.setdefault(s["lang"], []).append(s)
            return subtitles
