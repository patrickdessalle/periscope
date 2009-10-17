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

import zipfile, os, urllib2, urllib, logging, traceback, httplib
from BeautifulSoup import BeautifulSoup

import SubtitleDatabase

SS_LANGUAGES = {"en": "English",
				"se": "Swedish",
				"da": "Danish",
				"fi":"Finnish",
				"no": "Norwegian",
				"fr" : "French",
				"es" : "Spanish",
				"is" : "Icelandic",
				"cs" : "Czech",
				"bg" : "Bulgarian",
				"de" : "German",
				"ar" : "Arabic",
				"el" : "Greek",
				"fa" : "Farsi/Persian",
				"nl" : "Dutch",
				"he" : "Hebrew",
				"id" : "Indonesian",
				"vi" : "Vietnamese",
				"pt" : "Portuguese",
				"ro" : "Romanian",
				"tr" : "Turkish",
				"pt-br" : "Brazillian Portuguese",
				"ru" : "Russian"}

class SubScene(SubtitleDatabase.SubtitleDB):
	url = "http://subscene.com/"
	site_name = "SubScene"

	def __init__(self):
		super(SubScene, self).__init__(SS_LANGUAGES)
		#http://subscene.com/s.aspx?q=Dexter.S04E01.HDTV.XviD-NoTV
		self.host = "http://subscene.com/s.aspx?q="
		
	def downloadFile(self, url, filename):
		''' Downloads the given url to the given filename '''
		#req = urllib2.Request(url, headers={'User-Agent' : 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.1', 'Referer' : 'http://subscene.com', 'Accept' : '*/*', 'Connection': 'Keep-Alive', 'Accept-Encoding' : '*'})
		req = urllib2.Request(url, headers={'Referer' : url, 'User-Agent' : 'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.1.3)'})
		
		f = urllib2.urlopen(req)
		dump = open(filename, "wb")
		try:
			f.read(1000000)
		except httplib.IncompleteRead, e:
			dump.write(e.partial)
		dump.close()
		f.close()
		
		#SubtitleDatabase.SubtitleDB.downloadFile(self, req, filename)
			
	def process(self, filename, langs):
		''' main method to call on the plugin, pass the filename and the wished 
		languages and it will query the subtitles source '''
		if os.path.isfile(filename):
			filename = os.path.basename(filename).rsplit(".", 1)[0]
		try:
			subs = self.query(filename, langs)
			return subs
		except Exception, e:
			logging.error("Error raised by plugin %s: %s" %(self.__class__.__name__, e))
			traceback.print_exc()
			return []
	
	def query(self, token, langs=None):
		''' makes a query on subscene and returns info (link, lang) about found subtitles'''
		sublinks = []
		
		searchurl = "%s%s" %(self.host, urllib.quote(token))
		logging.debug("dl'ing %s" %searchurl)
		page = urllib2.urlopen(searchurl)
		
		soup = BeautifulSoup(page)
		for subs in soup("a", {"class":"a1"}):
			lang_span = subs.find("span")
			lang = self.getLG(lang_span.contents[0].strip())
			release_span = lang_span.findNext("span")
			release = release_span.contents[0].strip().split(" (")[0]
			sub_id = subs["id"][1:]
			sub_id2 = subs["href"].split("'")[-2]
			sub_format = subs["href"].split("'")[1]
			#http://subscene.com//s-dlpath-260016/78348/rar.zipx
			link = "http://subscene.com//s-dlpath-%s/%s/%s.zipx" %(sub_id, sub_id2, sub_format)
			if release.startswith(token):
				result = {}
				result["release"] = release
				result["lang"] = lang
				result["link"] = link
				result["page"] = "http://subscene.com" + soup.find("a", {"id" : "sm"+sub_id})["href"]
				sublinks.append(result)
		return sublinks
