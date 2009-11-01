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

import zipfile, os, urllib2, urllib, traceback, logging
from BeautifulSoup import BeautifulSoup

import SubtitleDatabase

class Podnapisi(SubtitleDatabase.SubtitleDB):
	url = "http://www.podnapisi.net/"
	site_name = "Podnapisi"

	def __init__(self):
		super(Podnapisi, self).__init__({"sl" : "1", "en": "2", "no" : "3", "ko" :"4", "de" : "5", "is" : "6", "cs" : "7", "fr" : "8", "it" : "9", "bs" : "10", "ja" : "11", "ar" : "12", "ro" : "13", "es-ar" : "14", "hu" : "15", "el" : "16", "zh" : "17", "lt" : "19", "et" : "20", "lv" : "21", "he" : "22", "nl" : "23", "da" : "24", "se" : "25", "pl" : "26", "ru" : "27", "es" : "28", "sq" : "29", "tr" : "30", "fi" : "31", "pt": "32", "bg" : "33", "mk" : "35", "sk" : "37", "hr" : "38", "zh" : "40", "hi": "42", "th" : "44", "uk": "46", "sr": "47", "pt-br" : "48", "ga": "49", "be": "50", "vi": "51", "fa": "52", "ca": "53", "id": "54"})
		
		#Note: Podnapisi uses two reference for latin serbian and cyrillic serbian (36 and 47). We'll add the 36 manually as cyrillic seems to be more used
		self.revertlangs["36"] = "sr";

		self.host = "http://www.sub-titles.net/"
		self.search = "ppodnapisi/search?"
			
	def process(self, filepath, langs):
		''' main method to call on the plugin, pass the filename and the wished 
		languages and it will query the subtitles source '''
		fname = self.getFileName(filepath)
		try:
			subs = []
			if langs:
				for lang in langs:
					#query one language at a time
					subs_lang = self.query(fname, [lang])
					if not subs_lang:
						# Try to remove the [VTV] or [EZTV] at the end of the file
						teamless_filename = fname[0 : fname.rfind(".[")]
						subs_lang = self.query(teamless_filename, langs)
					subs += subs_lang
			else:
				subs_lang = self.query(fname, None)
				if not subs_lang:
					# Try to remove the [VTV] or [EZTV] at the end of the file
					teamless_filename = fname[0 : fname.rfind(".[")]
					subs_lang = self.query(teamless_filename, None)
				subs += subs_lang
			return subs
		except Exception, e:
			logging.error("Error raised by plugin %s: %s" %(self.__class__.__name__, e))
			traceback.print_exc()
			return []
	
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
		for subs in soup("tr", {"class":"a"}) + soup("tr", {"class": "b"}):
			releases = subs.find("span", {"class" : "opis"}).find("span")["title"].lower().split(" ")
			if token.lower() in releases:
				logging.debug(subs)
				links = subs.findAll("a")
				lng = subs.find("a").find("img")["src"].rsplit("/", 1)[1][:-4]
				if langs and not self.getLG(lng) in langs:
					continue # The lang of this sub is not wanted => Skip
				
				dltag = subs.findAll("a")[2]["href"]
				dllink = self.host + dltag
				result = {}
				for rel in releases :
					if rel == token.lower():
						result["release"] = rel
				result["link"] = dllink
				result["lang"] = self.getLG(lng)
				sublinks.append(result)

		logging.debug(sublinks)
		return sublinks
