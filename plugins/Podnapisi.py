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

import zipfile, os, urllib2, urllib, logging
from BeautifulSoup import BeautifulSoup

import SubtitleDatabase

class Podnapisi(SubtitleDatabase.SubtitleDB):

	def __init__(self):
		super(Podnapisi, self).__init__({"sk" : "1", "en": "2", "no" : "3", "ko" :"4", "de" : "5", "cs" : "7", "fr" : "8", "it" : "9", "bs" : "10", "ja" : "11", "ar" : "12", "ro" : "13", "es-ar" : "14", "hu" : "15", "el" : "16", "zh" : "17", "he" : "22", "nl" : "23", "da" : "24", "se" : "25", "pl" : "26", "ru" : "27", "es" : "28", "tr" : "30", "fi" : "31", "pt": "32", "bg" : "33", "mk" : "35", "sh" : "36", "hr" : "38", "th" : "44", "pt-br" : "48"})

		self.host = "http://www.podnapisi.net/"
		self.search = "ppodnapisi/search?"
		
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
		''' makes a query on podnapisi and returns info (link, lang) about found subtitles'''
		sublinks = []
		params = {"sR" : token}
		if langs and len(langs) == 1:
			params["sJ"] = self.getLanguage(langs[0])
		else:
			params["sJ"] = 0

		searchurl = self.host + self.search + urllib.urlencode(params)
		logging.debug("dl'ing %s" %searchurl)
		page = urllib2.urlopen(searchurl)
		soup = BeautifulSoup(page)
		for subs in soup("tr", {"class":"bg1"}) + soup("tr", {"class": "bg2"}):
			dltag = subs.find("a")
			href_start = str(dltag).find("href")+6
			dllink = "http://www.podnapisi.net" + str(dltag)[href_start:str(dltag).find(">", href_start)-1]

			lng_img = subs.find("a", {"rel": "nofollow"}).find("img")["src"]
			lng = lng_img.rsplit("/", 1)[1][:-4]

			title = subs.find("span").find("span")
			if title:			
				release_name = title["onmouseover"].split("'")[1]
				if release_name == token:
					if langs and not self.getLG(lng) in langs:
						continue # The lang of this sub is not wanted => Skip
					result = {}
					result["link"] = dllink
					result["lang"] = self.getLG(lng)
					sublinks.append(result)
		return sublinks
