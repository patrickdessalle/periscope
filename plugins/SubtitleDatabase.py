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

import os, shutil, urllib2, sys, logging, traceback

class SubtitleDB(object):
	''' Base (kind of abstract) class that represent a SubtitleDB, usually a website. Should be rewritten using abc module in Python 2.6/3K'''
	def __init__(self, langs):
		self.langs = langs
		self.revertlangs = dict(map(lambda item: (item[1],item[0]), self.langs.items()))

	def searchInThread(self, queue, filename, langs):
		''' search subtitles with the given filename for the given languages'''
		subs = self.process(filename, langs)
		map(lambda item: item.setdefault("plugin", self), subs)
		map(lambda item: item.setdefault("filename", filename), subs)
		logging.info("%s writing %s items to queue" % (self.__class__.__name__, len(subs)))
		queue.put(subs, True) # Each plugin must write as the caller periscopy.py waits for an result on the queue
	
	def process(self, filename, langs):
		''' main method to call on the plugin, pass the filename and the wished 
		languages and it will query the subtitles source '''
		if os.path.isfile(filename):
			filename = os.path.basename(filename).rsplit(".", 1)[0]
		try:
			return self.query(filename, langs)
		except Exception, e:
			logging.error("Error raised by plugin %s: %s" %(self.__class__.__name__, e))
			traceback.print_exc()
			return []

	def downloadFile(self, url, filename):
		''' Downloads the given url to the given filename '''
		logging.info("Downloading %s" %url)
		f = urllib2.urlopen(url)
		dump = open(filename, "wb")
		dump.write(f.read())
		dump.close()
		f.close()
		logging.debug("Download finished to file %s"%filename)
		
	def getLG(self, language):
		''' Returns the short (two-character) representation of the long language name'''
		try:
			return self.revertlangs[language]
		except KeyError, e:
			logging.warn("Ooops, you found a missing language in the config file of %s: %s. Send a bug report to have it added." %(self.__class__.__name__, language))
		
	def getLanguage(self, lg):
		''' Returns the long naming of the language on a two character code '''
		try:
			return self.langs[lg]
		except KeyError, e:
			logging.warn("Ooops, you found a missing language in the config file of %s: %s. Send a bug report to have it added." %(self.__class__.__name__, lg))
	
	def createFile(self, suburl, videofilename):
		raise TypeError("%s has not implemented method '%s'" %(self.__class__.__name__, sys._getframe().f_code.co_name))
	
	def query(self, token):
		raise TypeError("%s has not implemented method '%s'" %(self.__class__.__name__, sys._getframe().f_code.co_name))

class InvalidFileException(Exception):
	''' Exception object to be raised when the file is invalid'''
	def __init__(self, filename, reason):
		self.filename = filename
		self.reason = reason
	def __str__(self):
		return (repr(filename), repr(reason))
