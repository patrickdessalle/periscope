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

import os, shutil, urllib2, sys

class SubtitleDB(object):
	''' Base (kind of abstract) class that represent a SubtitleDB, usually a website. Should be rewritten using abc module in Python 2.6/3K'''
	def __init__(self, langs):
		self.langs = langs
		self.revertlangs = dict(map(lambda item: (item[1],item[0]), self.langs.items()))
		
	def downloadFile(self, url, filename):
		''' Quick download (to be replace by curl or something else) '''
		f = urllib2.urlopen(url)
		dump = open(filename, "wb")
		dump.write(f.read())
		dump.close()
		f.close()
		
	def getLG(self, language):
		''' Returns the short (two-character) representation of the long language name'''
		try:
			return self.revertlangs(language)
		except KeyError, e:
			print "Ooops, you found a missing language in the config file of %s: %s. Send a bug report to have it added." %(self.__class__.__name__, language)
		
	def getLanguage(self, lg):
		''' Returns the long naming of the language on a two character code '''
		try:
			return self.langs[lg]
		except KeyError, e:
			print "Ooops, you found a missing language in the config file of %s: %s. Send a bug report to have it added." %(self.__class__.__name__, lg)
		
	def process(self, filename, langs):
		raise TypeError("%s has not implemented method '%s'" %(self.__class__.__name__, sys._getframe().f_code.co_name))
	
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
