#!/usr/bin/python
# -*- coding: utf-8 -*-

#   This file is part of periscope.
#
#    periscope is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    periscope is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with emesene; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import getopt
import sys
import os
import traceback
import ConfigParser

import xdg.BaseDirectory as bd

import plugins

class Periscope:
	''' Main Periscope class'''
	
	def __init__(self):
		self.config = ConfigParser.SafeConfigParser({"lang": "en"})
		self.config_file = os.path.join(bd.xdg_config_home, "periscope", "config")
		if not os.path.exists(self.config_file):
			folder = os.path.dirname(self.config_file)
			if not os.path.exists(folder):
				print "Creating folder %s" %folder
				os.mkdir(folder)
			print "Creating config file"
			configfile = open(self.config_file, "w")
			self.config.write(configfile)
			configfile.close()

		self.pluginNames = self.listExistingPlugins()
		self._preferedLanguages = None

	def get_preferedLanguages(self):
		lang = self.config.get("DEFAULT", "lang")
		print "lang read from config: " + lang
		if lang == "":
			return None
		else:
			return lang.split(",")

	def set_preferedLanguages(self, langs):
		self.config.set("DEFAULT", "lang", ",".join(langs))
		configfile = open(self.config_file, "w")
		self.config.write(configfile)
		configfile.close()

	preferedLanguages = property(get_preferedLanguages, set_preferedLanguages)

	
	def deactivatePlugin(self, pluginName):
		self.pluginNames - pluginName
		
	def activatePlugin(self, pluginName):
		if pluginName not in self.listExistingPlugins():
			raise ImportError("No plugin with the name %s exists" %pluginName)
		self.pluginNames + pluginName
		
	def listActivePlugins(self):
		return self.pluginNames
		
	def listExistingPlugins(self):
		return plugins.SubtitleDatabase.SubtitleDB.__subclasses__()
	
	def listSubtitles(self, filename, langs=None):
		'''Searches subtitles within the plugins and returns all found matching subtitles ordered by language then by plugin.'''
		#if not os.path.isfile(filename):
			#raise InvalidFileException(filename, "does not exist")
	
		print "Searching subtitles for %s with langs %s" %(filename, langs)
		subtitles = []
		for name in self.pluginNames:
			plugin = name()
			print "Searching On %s " %plugin.__class__.__name__,
			try:
				subs = plugin.process(filename, langs)
				map(lambda item: item.setdefault("plugin", plugin), subs)
				map(lambda item: item.setdefault("filename", filename), subs)
				subtitles += subs
			except Exception, e:
				print "Error raised by plugin %s: %s" %(name, e)
				traceback.print_exc()
			print "Total: %s subtitles so far" %len(subtitles)
			
		if len(subtitles) == 0:
			return None
		return subtitles
	
	
	def selectBestSubtitle(self, subtitles, langs=None):
		'''Searches subtitles from plugins and select the best subtitles '''
		if not subtitles:
			return None

		if not langs: # No preferred language => return the first
				return subtitles[0]
		
		subtitles = self.regroupSubtitles(subtitles)
		for l in langs:
			if subtitles.has_key(l) and len(subtitles[l]):
				return subtitles[l][0]

		return None #Could not find subtitles

	def downloadSubtitle(self, filename, langs=None):
		''' Takes a filename and a language and creates ONE subtitle through plugins'''
		subtitles = self.listSubtitles(filename, langs)
		subtitle = self.selectBestSubtitle(subtitles, langs)
		if subtitle:
			#Download the subtitle
			subpath = subtitle["plugin"].createFile(subtitle["link"], filename)
			subtitle["subtitlepath"] = subpath
			return subtitle
		
		
	def regroupSubtitles(self, subs):
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

class Subtitle:
	''' Attributes and method characterizing a subtitle'''
	def __init__(self, filename, lang=None, link=None, downloadmethod=None):
		self.filename = filename
		self.lang = lang
		self.link = link
		self.downloadmethod = downloadmethod
		
	def download(self):
		self.downloadmethod(self.link, self.filename)
		


