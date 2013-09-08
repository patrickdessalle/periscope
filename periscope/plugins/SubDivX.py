# -*- coding: utf-8 -*-

#   This file is part of periscope.
#   Copyright (c) 2008-2011 Matias Bordese
#
#   periscope is free software; you can redistribute it and/or modify
#   it under the terms of the GNU Lesser General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   periscope is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Lesser General Public License for more details.
#
#   You should have received a copy of the GNU Lesser General Public License
#   along with periscope; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import logging
import os
import re
import subprocess
import urllib
import urllib2

from BeautifulSoup import BeautifulSoup

import SubtitleDatabase


LANGUAGES = {"es": "Spanish"}


class SubDivX(SubtitleDatabase.SubtitleDB):
    url = "http://www.subdivx.com"
    site_name = "SubDivX"

    def __init__(self, config, cache_folder_path):
        super(SubDivX, self).__init__(LANGUAGES)
        self.api_base_url = 'http://www.subdivx.com/index.php'

    def process(self, filepath, langs):
        '''Main method to call on the plugin.

        Pass the filename and the wished languages and it will query
        the subtitles source. Only Spanish available.
        '''
        if 'es' not in langs:
            return []

        fname = unicode(self.getFileName(filepath).lower())
        guessedData = self.guessFileData(fname)
        if guessedData['type'] == 'tvshow':
            subs = self.query(guessedData['name'],
                              guessedData['season'],
                              guessedData['episode'],
                              guessedData['teams'])
            return subs
        elif guessedData['type'] == 'movie':
            subs = self.query(guessedData['name'], extra=guessedData['teams'])
            return subs
        else:
            return []

    def _get_result_title(self, result):
        '''Return the title of the result.'''
        return result.find('a', {'class': 'titulo_menu_izq'}).text

    def _get_result_link(self, result):
        '''Return the absolute link of the result. (not the downloadble file)'''
        return result.find('a', {'class': 'titulo_menu_izq'}).get('href')

    def _get_download_link(self, result_url):
        '''Return the direct link of the subtitle'''
        content = self.downloadContent(result_url, timeout=5)
        soup = BeautifulSoup(content)
        return soup.find('a', {'class': 'link1'}).get('href')

    def _get_result_rating(self, result, extra):
        if extra is None:
            extra = []
        description = result.findNext('div', {'id': 'buscador_detalle_sub'}).text
        description = description.split('<!--')[0].lower()
        rating = 0
        for keyword in extra:
            if not keyword:
                continue
            elif keyword in description:
                rating += 1
        return rating

    def query(self, name, season=None, episode=None, extra=None):
        '''Query on SubDivX and return found subtitles details.'''
        sublinks = []

        if season and episode:
            query = "%s s%02de%02d" % (name, season, episode)
        else:
            query = name

        params = {'buscar': query,
                  'accion': '5',
                  'oxdown': '1', }
        encoded_params = urllib.urlencode(params)
        query_url = '%s?%s' % (self.api_base_url, encoded_params)

        logging.debug("SubDivX query: %s", query_url)

        content = self.downloadContent(query_url, timeout=5)
        if content is not None:
            soup = BeautifulSoup(content)
            for subs in soup('div', {"id": "menu_detalle_buscador"}):
                result = {}
                result["release"] = self._get_result_title(subs)
                result["lang"] = 'es'
                result["link"] = self._get_result_link(subs)
                result["page"] = query_url
                result["rating"] = self._get_result_rating(subs, extra)
                sublinks.append(result)
        sorted_links = sorted(sublinks, key=lambda k: k['rating'], reverse=True)
        return sorted_links

    def createFile(self, subtitle):
        '''Download and extract subtitle.

        Pass the URL of the sub and the file it matches, will unzip it
        and return the path to the created file.
        '''
        download_url = self._get_download_link(subtitle["link"])
        subtitle["link"] = download_url
        request = urllib2.Request(download_url)
        request.get_method = lambda: 'HEAD'
        response = urllib2.urlopen(request)

        if response.url.endswith('.zip'):
            # process as usual
            return super(SubDivX, self).createFile(subtitle)
        elif response.url.endswith('.rar'):
            # Rar support based on unrar commandline, download it here:
            # http://www.rarlab.com/rar_add.htm
            # Install and make sure it is on your path
            logging.warning(
                'Rar is not really supported yet. Trying to call unrar')

            video_filename = os.path.basename(subtitle["filename"])
            base_filename, _ = os.path.splitext(video_filename)
            base_rar_filename, _ = os.path.splitext(subtitle["filename"])
            rar_filename = '%s%s' % (base_rar_filename, '.rar')
            self.downloadFile(download_url, rar_filename)

            try:
                args = ['unrar', 'lb', rar_filename]
                output = subprocess.Popen(
                    args, stdout=subprocess.PIPE).communicate()[0]

                for fname in output.splitlines():
                    base_name, extension = os.path.splitext(fname)
                    if extension in (".srt", ".sub", ".txt"):
                        wd = os.path.dirname(rar_filename)
                        final_name = '%s%s' % (base_filename, extension)
                        final_path = os.path.join(wd, final_name)
                        args = ['unrar', 'e', rar_filename, fname, wd]
                        output = subprocess.Popen(
                            args, stdout=subprocess.PIPE).communicate()[0]
                        tmp = os.path.join(wd, fname)
                        if os.path.exists(tmp):
                            # rename extracted subtitle file
                            os.rename(tmp, final_path)
                            return final_path
            except OSError:
                logging.exception("Execution failed: unrar not available?")
                return None
            finally:
                os.remove(rar_filename)
        else:
            logging.info(
                "Unexpected file type (not zip) for %s" % rar_filename)
            return None
