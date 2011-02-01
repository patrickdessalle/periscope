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

import urllib
import urllib2
import logging
from xml.dom import minidom
from BeautifulSoup import BeautifulSoup

try:
    import xdg.BaseDirectory as bd
    is_local = True
except ImportError:
    is_local = False

import SubtitleDatabase

class BierDopje(SubtitleDatabase.SubtitleDB):
    url = "http://bierdopje.com/"
    site_name = "BierDopje"

    def __init__(self):
        super(BierDopje, self).__init__(None)
        #http://api.bierdopje.com/23459DC262C0A742/GetShowByName/30+Rock
        #http://api.bierdopje.com/23459DC262C0A742/GetAllSubsFor/94/5/1/en (30 rock, season 5, episode 1)
        
        key = '23459DC262C0A742'
        self.api = "http://api.bierdopje.com/%s/" %key

    def process(self, filepath, langs):
        ''' main method to call on the plugin, pass the filename and the wished 
        languages and it will query the subtitles source '''
        fname = self.getFileName(filepath)
        try:
            subs = self.query(fname, langs)
            if not subs and fname.rfind(".[") > 0:
                # Try to remove the [VTV] or [EZTV] at the end of the file
                teamless_filename = fname[0 : fname.rfind(".[")]
                subs = self.query(teamless_filename, langs)
                return subs
            else:
                return subs
        except Exception, e:
            logging.error("Error raised by plugin %s: %s" %(self.__class__.__name__, e))
            traceback.print_exc()
            return []
            
    def createFile(self, subtitle):
        '''get the URL of the sub, download it and return the path to the created file'''
        sublink = subtitle["link"]
        subpath = subtitle["filename"].rsplit(".", 1)[0] + '.srt'
        self.downloadFile(sublink, subpath)
        return subpath
    
    def query(self, token, langs=None):
        ''' makes a query and returns info (link, lang) about found subtitles'''
        guessedData = self.guessFileData(token)
        if "tvshow" != guessedData['type'] :
            return []
        elif langs and not set(langs).intersection((['en', 'nl'])): # lang is given but does not include nl or en
            return []
            
        if not langs :
            availableLangs = ['nl', 'en']
        else :
            availableLangs = list(set(langs).intersection((['en', 'nl'])))
        logging.debug("possible langs : %s " % availableLangs)

        sublinks = []
        
        # Query the show to get the show id
        showName = guessedData['name']
        if showName.lower() == "the office" or showName.lower() == "the office us":
            show_id = 10358
        elif showName.lower() == "greys anatomy":
            show_id = 3733
        elif showName.lower() =="sanctuary us":
            show_id = 7904
        elif showName.lower() == "human target 2010":
            show_id=12986
        elif showName.lower() == 'csi miami':
           show_id=2187
        elif showName.lower() == "castle 2009":
           show_id=12708
        elif showName.lower() == "chase 2010":
           show_id=14228
        elif showName.lower() == "the defenders 2010":
           show_id=14225
        else :
            getShowId_url = "%sGetShowByName/%s" %(self.api, urllib.quote(showName))
            logging.debug("Looking for show Id @ %s" % getShowId_url)
            page = urllib2.urlopen(getShowId_url)
            dom = minidom.parse(page)
            if not dom or len(dom.getElementsByTagName('showid')) == 0 :
                page.close()
                return []
            show_id = dom.getElementsByTagName('showid')[0].firstChild.data
            logging.debug("Found id : %s" %show_id)
            page.close()
        
        # Query the episode to get the subs
        for lang in availableLangs :
            getAllSubs_url = "%sGetAllSubsFor/%s/%s/%s/%s" %(self.api, show_id, guessedData['season'], guessedData['episode'], lang)
            logging.debug("Looking for subs @ %s" %getAllSubs_url)
            page = urllib2.urlopen(getAllSubs_url)
            dom = minidom.parse(page)
            page.close()
            for sub in dom.getElementsByTagName('result'):
                release = sub.getElementsByTagName('filename')[0].firstChild.data
                if release.endswith(".srt"):
                    release = release[:-4]
                dllink = sub.getElementsByTagName('downloadlink')[0].firstChild.data
                logging.debug("Release found : %s" % release.lower())
                logging.debug("Searching for : %s" % token.lower())
                if release.lower() == token.lower():
                    result = {}
                    result["release"] = release
                    result["link"] = dllink
                    result["page"] = dllink
                    result["lang"] = lang
                    sublinks.append(result)
            
        return sublinks
