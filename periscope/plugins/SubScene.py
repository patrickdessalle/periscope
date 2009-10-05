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

import zipfile, os, urllib2, urllib, logging, traceback
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
				"gr" : "Greek",
				"fa" : "Farsi/Persian"}

class SubScene(SubtitleDatabase.SubtitleDB):
	url = "http://www.subscene.com/"
	site_name = "SubScene"

	def __init__(self):
		super(SubScene, self).__init__(SS_LANGUAGES)
		#http://subscene.com/s.aspx?q=Dexter.S04E01.HDTV.XviD-NoTV
		self.host = "http://www.subscene.com/s.aspx?q="
			
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
			link = "http://subscene.com//s-dlpath-%s/%s/zip.zip" %(sub_id, sub_id2)
			if release == token:
				result = {}
				result["release"] = release
				result["lg"] = lang
				result["link"] = link
				sublinks.append(result)
		return sublinks
