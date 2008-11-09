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

import plugins

class Periscope:
	''' Main Periscope class'''
	
	def __init__(self):
		self.pluginNames = self.listExistingPlugins()
	
	def deactivatePlugin(self, pluginName):
		self.pluginNames - pluginName
		
	def activatePlugin(self, pluginName):
		if pluginName not in self.listExistingPlugins():
			raise ImportError("No plugin with the name %s exists" %pluginName)
		self.pluginNames + pluginName
		
	def listActivePlugins(self):
		return self.pluginNames
		
	def listExistingPlugins(self):
		return [e for e in dir(plugins) if not e.startswith("__") and e != "SubtitleDatabase"]
	
	def listSubtitles(self, filename, langs=None):
		'''Searches subtitles within the plugins and returns all found matching subtitles ordered by language then by plugin.'''
		#if not os.path.isfile(filename):
			#raise InvalidFileException(filename, "does not exist")
	
		print "Searching subtitles for %s" %filename
		subtitles = []
		for name in self.pluginNames:
			print "Searching On %s " %name,
			plugin = getattr(plugins, name)()
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
		


