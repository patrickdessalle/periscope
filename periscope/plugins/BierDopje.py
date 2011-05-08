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
import os
import pickle
import traceback
from xml.dom import minidom

try:
    import xdg.BaseDirectory as bd
    is_local = True
except ImportError:
    is_local = False

import SubtitleDatabase

exceptions = {
    'the office' : 10358,
    'the office us' : 10358,
    'greys anatomy' : 3733,
    'sanctuary us' : 7904,
    'human target 2010' : 12986,
    'csi miami' : 2187,
    'castle 2009' : 12708,
    'chase 2010' : 14228,
    'the defenders 2010' : 14225,
    'hawaii five-0 2010' : 14211,
}

class BierDopje(SubtitleDatabase.SubtitleDB):
    url = "http://bierdopje.com/"
    site_name = "BierDopje"

    def __init__(self):
        super(BierDopje, self).__init__(None)
        #http://api.bierdopje.com/23459DC262C0A742/GetShowByName/30+Rock
        #http://api.bierdopje.com/23459DC262C0A742/GetAllSubsFor/94/5/1/en (30 rock, season 5, episode 1)
        
        key = '112C8204D6754A2A'
        self.api = "http://api.bierdopje.com/%s/" %key
        self.showid_cache = os.path.join(bd.xdg_config_home, "periscope", "bierdopje_showid.cache")
        if not os.path.exists(self.showid_cache):
            f = open(self.showid_cache, 'w')
            pickle.dump({}, f)
            f.close()
        f = open(self.showid_cache, 'r')
        self.showids = pickle.load(f)
        f.close()
        logging.debug("Cache of showids : %s" % self.showids)

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
        showName = guessedData['name'].lower()
        if exceptions.has_key(showName):
            show_id = exceptions.get(showName)
        elif self.showids.has_key(showName):
            show_id = self.showids.get(showName)
        else :
            getShowId_url = "%sGetShowByName/%s" %(self.api, urllib.quote(showName))
            logging.debug("Looking for show Id @ %s" % getShowId_url)
            page = urllib2.urlopen(getShowId_url)
            dom = minidom.parse(page)
            if not dom or len(dom.getElementsByTagName('showid')) == 0 :
                page.close()
                return []
            show_id = dom.getElementsByTagName('showid')[0].firstChild.data
            self.showids[showName] = show_id
            f = open(self.showid_cache, 'w')
            pickle.dump(self.showids, f)
            f.close()
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
