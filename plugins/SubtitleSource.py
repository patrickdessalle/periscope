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

import zipfile, os, urllib2, urllib
from BeautifulSoup import BeautifulSoup

import SubtitleDatabase

class SubtitleSource(SubtitleDatabase.SubtitleDB):

	def __init__(self):
		self.langs = {"English": "en", "Swedish": "se", "Danish": "da", "Finnish": "fi", "Norwegian": "no"}

		self.host = "http://www.subtitlesource.org/"
		self.search = "sublinks.php?"
	
	def process(self, filename, lang):
		if os.path.isfile(filename):
			filename = os.path.basename(filename).rsplit(".", 1)[0]
		return self.query(filename, lang)
		
	def createFile(self, suburl, videofilename):
		srtbasefilename = videofilename.rsplit(".", 1)[0]
		zipfilename = srtbasefilename +".zip"
		self.downloadFile(suburl, zipfilename)
		
		if zipfile.is_zipfile(zipfilename):
			zf = zipfile.ZipFile(zipfilename, "r")
			for el in zf.infolist():
				if el.orig_filename.rsplit(".", 1)[1] in ("srt", "sub"):
					outfile = open(srtbasefilename + ".srt", "wb")
					outfile.write(zf.read(el.orig_filename))
					outfile.flush()
					outfile.close()
			# Deleting the zip file
			zf.close()
			os.remove(zipfilename)
			return srtbasefilename + ".srt"
	
	def query(self, token, langs=None):
		sublinks = []
		params = {"q": token}
		searchurl = self.host + self.search + urllib.urlencode(params)
		print "dl'ing %s" %searchurl
		page = urllib2.urlopen(searchurl)
		soup = BeautifulSoup(page)
		for subs in soup('a'):
			sublang = subs("img")[0]["src"].rsplit("/", 1)[1][:-4] #Strip the .gif
			if not self.langs.has_key(sublang):
				print "Ooops, you found a missing language in the config file of SubtitleSource.py: %s. Send a bug report to have it added." %sublang
				continue
			if langs and not self.langs[sublang] in langs:
				continue # The lang of this sub is not wanted => Skip
			else:
				dllink = subs["href"]
				print "Link added: %s (%s)" %(dllink,sublang)
				result = {}
				result["link"] = dllink
				result["lang"] = self.langs[sublang]
				sublinks.append(result)
		return sublinks
