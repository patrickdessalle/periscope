import os, shutil, urllib2

class SubtitleDB:
	def __init__(self):
		pass
		
	def downloadFile(self, url, filename):
		''' Quick download (to be replace by curl or something else) '''
		f = urllib2.urlopen(url)
		dump = open(filename, "wb")
		dump.write(f.read())
		dump.close()
		f.close()
		

class InvalidFileException(Exception):
	''' Exception object to be raised when the file is invalid'''
	def __init__(self, filename, reason):
		self.filename = filename
		self.reason = reason
	def __str__(self):
		return (repr(filename), repr(reason))
