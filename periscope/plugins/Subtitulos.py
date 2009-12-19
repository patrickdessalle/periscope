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

import zipfile, os, urllib2, urllib, logging, traceback, httplib, re
from BeautifulSoup import BeautifulSoup

import SubtitleDatabase

LANGUAGES = {u"English (US)" : "en",
			 u"English (UK)" : "en",
			 u"English" : "en",
			 u"Español (España)" : "es",
			 u"French" : "fr"}

class Subtitulos(SubtitleDatabase.SubtitleDB):
	url = "http://subtitlos.es/"
	site_name = "Subtitulos.es"

	def __init__(self):
		super(Subtitulos, self).__init__(langs=None,revertlangs=LANGUAGES)
		#http://www.subtitulos.es/dexter/4x01
		self.host = "http://www.subtitulos.es"
		self.release_pattern = re.compile(" \nVersi&oacute;n (.+), ([0-9]+).([0-9])+ MBs")
		

	def process(self, filepath, langs):
		''' main method to call on the plugin, pass the filename and the wished 
		languages and it will query the subtitles source '''
		fname = self.getFileName(filepath)
		guessedData = self.guessFileData(fname)
		print guessedData
		if guessedData['type'] == 'tvshow':
			subs = self.query(guessedData['name'], guessedData['season'], guessedData['episode'], guessedData['teams'], langs)
			return subs
		else:
			return []
	
	def query(self, name, season, episode, teams, langs=None):
		''' makes a query and returns info (link, lang) about found subtitles'''
		sublinks = []
		name = name.lower().replace(" ", "-")
		searchurl = "%s/%s/%sx%s" %(self.host, name, season, episode)
		logging.debug("dl'ing %s" %searchurl)
		try:
			page = urllib2.urlopen(searchurl)
		except urllib2.HTTPError as inst:
			logging.debug(inst)
			return sublinks
		
		soup = BeautifulSoup(page)
		for subs in soup("td", {"class":"NewsTitle"}):
			print "Got one ..."
			subteams = self.release_pattern.match("%s"%subs.contents[1]).groups()[0]
			langs = subs.findNext("td", {"class" : "language"})
			lang = self.getLG(langs.string.strip())
		
			statusTD = langs.findNext("td")
			status = statusTD.find("strong").string.strip()

			link = statusTD.findNext("td").find("a")["href"]
							
			if status == "Completado" and set(subteams.split(".")).issubset(set(teams)):				
				result = {}
				result["release"] = "%s.S%.2dE%.2d.%s" %(name.replace("-", "."), int(season), int(episode), subteams)
				result["lang"] = lang
				result["link"] = link
				result["page"] = link
				sublinks.append(result)
				
		return sublinks

	def createFile(self, suburl, videofilename):
		'''pass the URL of the sub and the file it matches, will unzip it
		and return the path to the created file'''
		srtbasefilename = videofilename.rsplit(".", 1)[0]
		srtfilename = srtbasefilename +".srt"
		self.downloadFile(suburl, srtfilename)
		return srtfilename

	def downloadFile(self, url, filename):
		''' Downloads the given url to the given filename '''
		req = urllib2.Request(url, headers={'Referer' : url, 'User-Agent' : 'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.1.3)'})
		
		f = urllib2.urlopen(req)
		dump = open(filename, "wb")
		dump.write(f.read())
		dump.close()
		f.close()
