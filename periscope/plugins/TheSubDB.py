# -*- coding: utf-8 -*-

#   This file is part of periscope.
#
#    periscope is free software; you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    periscope is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with periscope; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import os
import urllib2
import urllib
import xml.dom.minidom
import logging
import traceback
import hashlib

import SubtitleDatabase

SS_LANGUAGES = {"en": "en",
                "nl": "nl",
                "pt": "pt",
                "pt-br":"pt",
                "no": "Norwegian",
                "fr" : "French",
                "es" : "Spanish",
                "is" : "Icelandic"}

class TheSubDB(SubtitleDatabase.SubtitleDB):
    url = "http://thesubdb.com/"
    site_name = "SubDB"
    user_agent = "SubDB/1.0 (periscope/0.1; http://code.google.com/p/periscope)"

    def __init__(self):
        super(TheSubDB, self).__init__(SS_LANGUAGES)
        self.host = "http://api.thesubdb.com/"
            
    def process(self, filepath, langs):
        ''' main method to call on the plugin, pass the filename and the wished 
        languages and it will query the subtitles source '''
        # Get the hash
        filehash = self.get_hash(filepath)
        logging.debug('File hash : %s' % filehash)
        # Make the search
        search_url = "%s?action=%s&hash=%s" % (self.host, "search", filehash)
        logging.debug('Query URL : %s' % search_url)
        req = urllib2.Request(search_url)
        req.add_header('User-Agent', self.user_agent)
        subs = []
        try : 
            page = urllib2.urlopen(req, timeout=5)
            content = page.readlines()
            plugin_langs = content[0].split(',')
            for lang in plugin_langs :
                if not langs or lang in langs:
                    result = {}
                    result['release'] = filepath
                    result['lang'] = lang
                    result['link'] = "%s?action=%s&hash=%s&language=%s" % (self.host, "download", filehash, lang)
                    result['page'] = result['link']
                    subs.append(result)
            return subs
        except urllib2.HTTPError, e :
            if e.code == 404 : # No result found
                return subs
        

    def get_hash(self, name):
        '''this hash function receives the name of the file and returns the hash code'''
        readsize = 64 * 1024
        with open(name, 'rb') as f:
            size = os.path.getsize(name)
            data = f.read(readsize)
            f.seek(-readsize, os.SEEK_END)
            data += f.read(readsize)
        return hashlib.md5(data).hexdigest()
            
    def createFile(self, subtitle):
        '''pass the URL of the sub and the file it matches, will unzip it
        and return the path to the created file'''
        suburl = subtitle["link"]
        videofilename = subtitle["filename"]
        srtfilename = videofilename.rsplit(".", 1)[0] + '.srt'
        self.downloadFile(suburl, srtfilename)
        return srtfilename

    def downloadFile(self, url, srtfilename):
        ''' Downloads the given url to the given filename '''
        req = urllib2.Request(url)
        req.add_header('User-Agent', self.user_agent)
        
        f = urllib2.urlopen(req)
        dump = open(srtfilename, "wb")
        dump.write(f.read())
        dump.close()
        f.close()
        logging.debug("Download finished to file %s. Size : %s"%(srtfilename,os.path.getsize(srtfilename)))
