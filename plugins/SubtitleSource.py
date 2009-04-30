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

import zipfile, os, urllib2, urllib, xml.dom.minidom, logging

import SubtitleDatabase

class SubtitleSource(SubtitleDatabase.SubtitleDB):

	def __init__(self):
		super(SubtitleSource, self).__init__({"en": "English", "se": "Swedish", "da": "Danish", "fi":"Finnish", "no": "Norwegian", "fr" : "French", "es" : "Spanish"})

		#http://www.subtitlesource.org/api/xmlsearch/Heroes.S03E09.HDTV.XviD-LOL/all/0
		#http://www.subtitlesource.org/api/xmlsearch/heroes/swedish/0

		self.host = "http://www.subtitlesource.org/"
		self.search = "sublinks.php?"
		
	def createFile(self, suburl, videofilename):
		'''pass the URL of the sub and the file it matches, will unzip it
		and return the path to the created file'''
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
		''' makes a query on subtitlessource and returns info (link, lang) about found subtitles'''
		sublinks = []
		searchurl = "%sapi/xmlsearch/%s/all/0" %(self.host, urllib.quote(token))
		logging.debug("dl'ing %s" %searchurl)
		page = urllib2.urlopen(searchurl)
		xmltree = xml.dom.minidom.parse(page)
		subs = xmltree.getElementsByTagName("sub")

		for sub in subs:
			sublang = self.getLG(self.getValue(sub, "language"))
			if langs and not sublang in langs:
				continue # The language of this sub is not wanted => Skip
			dllink = "http://www.subtitlesource.org/download/zip/%s" %self.getValue(sub, "id")
			logging.debug("Link added: %s (%s)" %(dllink,sublang))
			result = {}
			result["link"] = dllink
			result["lang"] = sublang
			sublinks.append(result)
		return sublinks

	def getValue(self, sub, tagName):
		for node in sub.childNodes:
			if node.nodeType == node.ELEMENT_NODE and node.tagName == tagName:
				return node.childNodes[0].nodeValue
