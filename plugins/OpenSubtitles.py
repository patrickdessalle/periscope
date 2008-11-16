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

import os, struct, xmlrpclib, commands, gzip

import SubtitleDatabase

class OpenSubtitles(SubtitleDatabase.SubtitleDB):

	def __init__(self):
		super(OpenSubtitles, self).__init__({"en": "eng", "fr" : "fre", "hu": "hun", "cs": "cze", "pl" : "pol", "sk" : "slo", "pt" : "por", "pt-br" : "pob", "es" : "spa", "el" : "ell"})
		self.server_url = 'http://www.opensubtitles.org/xml-rpc'
		self.revertlangs = dict(map(lambda item: (item[1],item[0]), self.langs.items()))

	def process(self, filepath, langs):
		''' main method to call on the plugin, pass the filename and the wished 
		languages and it will query OpenSubtitles.org '''
		if os.path.isfile(filepath):
			filehash = self.hashFile(filepath)
			size = os.path.getsize(filepath)
			filename = os.path.basename(filepath).rsplit(".", 1)[0]
			return self.query(moviehash=filehash, langs=langs, bytesize=size, filename=filename)
		else:
			return self.query(token=filename, langs=langs, filename=filename)
		
	def createFile(self, suburl, videofilename):
		'''pass the URL of the sub and the file it matches, will unzip it
		and return the path to the created file'''
		srtbasefilename = videofilename.rsplit(".", 1)[0]
		self.downloadFile(suburl, srtbasefilename + ".srt.gz")
		f = gzip.open(srtbasefilename+".srt.gz")
		dump = open(srtbasefilename+".srt", "wb")
		dump.write(f.read())
		dump.close()
		f.close()
		os.remove(srtbasefilename+".srt.gz")
		return srtbasefilename+".srt"
		

	def hashFile(self, name):
		'''
		Calculates the Hash à-la Media Player Classic as it is the hash used by OpenSubtitles.
		By the way, this is not a very robust hash code.
		''' 
		longlongformat = 'LL'  # signed long, unsigned long 
		bytesize = struct.calcsize(longlongformat) 
		    
		f = open(name, "rb")
		filesize = os.path.getsize(name) 
		hash = filesize
		    
		if filesize < 2**16: 
		       raise invalidFileException(name, "SizeError < 2**16")
		 
		for x in range(65536/bytesize): 
			buffer = f.read(bytesize) 
			(l2, l1)= struct.unpack(longlongformat, buffer) 
			l_value = (long(l1) << 32) | long(l2) 
			hash += l_value 
			hash = hash & 0xFFFFFFFFFFFFFFFF #to remain as 64bit number  
			 

		f.seek(filesize-65536,0) 
		for x in range(65536/bytesize): 
			buffer = f.read(bytesize) 
			(l2, l1) = struct.unpack(longlongformat, buffer) 
			l_value = (long(l1) << 32) | long(l2) 
			hash += l_value 
			hash = hash & 0xFFFFFFFFFFFFFFFF 
		 
		f.close() 
		returnedhash =  "%016x" % hash 
		return returnedhash 

	def query(self, filename, token='', moviehash=None, imdbID=None, bytesize=None, langs=None):
		''' makes a query on opensubtitles and returns info about found subtitles'''
		server = xmlrpclib.Server(self.server_url)
		search = {}
		if moviehash: search['moviehash'] = moviehash
		if imdbID: search['imdbid'] = imdbID
		if bytesize: search['moviebytesize'] = str(bytesize)
		if langs: search['sublanguageid'] = ",".join([self.getLanguage(lang) for lang in langs])

		if search:
			results = server.SearchSubtitles(token, [search])
		else:
			results = server.SearchSubtitles(token)

		sublinks = []
		if results['data']:
			self.filename = filename
			# OpenSubtitles hash function is not robust ... We'll use the MovieReleaseName to help us select the best candidate
			for r in sorted(results['data'], self.sort_by_moviereleasename):
				# Only added if the MovieReleaseName matches the file
				print r
				result = {}
				result["link"] = r['SubDownloadLink']
				result["lang"] = self.getLG(r['SubLanguageID'])
				sublinks.append(result)
		return sublinks

	def sort_by_moviereleasename(self, x, y):
		''' sorts based on the movierelease name tag'''
		xmatch = x['MovieReleaseName'] and (x['MovieReleaseName'].find(self.filename)>-1 or self.filename.find(x['MovieReleaseName'])>-1)
		ymatch = y['MovieReleaseName'] and (y['MovieReleaseName'].find(self.filename)>-1 or self.filename.find(y['MovieReleaseName'])>-1)
		
		if xmatch and ymatch:
			return 0
		if not xmatch and not ymatch:
			return 0
		if xmatch and not ymatch:
			return -1
		if not xmatch and ymatch:
			return 1
		return 0
