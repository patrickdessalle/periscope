import unittest
import logging

logging.basicConfig(level=logging.DEBUG)

class OpenSubtitlesTestCase(unittest.TestCase):
	def runTest(self):
		import OpenSubtitles
		subdb = OpenSubtitles.OpenSubtitles()
		# movie hash if for night watch : http://trac.opensubtitles.org/projects/opensubtitles/wiki/XMLRPC
		results = subdb.query('Night.Watch.2004.CD1.DVDRiP.XViD-FiCO.avi', moviehash="09a2c497663259cb", bytesize="733589504")
		
		assert len(results) > 0, 'No result found for the example moviehash'
'''
class SubtitleSourceTestCase(unittest.TestCase):
	def runTest(self):
		import SubtitleSource
		subdb = SubtitleSource.SubtitleSource()
		results = subdb.query("Heroes.S03E09.HDTV.XviD-LOL")
		assert len(results) > 0, "No result could be found for Heroes 3X9 and no languages"

class SubtitleSourceTestCase2(unittest.TestCase):
	def runTest(self):
		import SubtitleSource
		subdb = SubtitleSource.SubtitleSource()
		results = subdb.query("Transformers.Revenge.of.the.Fallen.TS.XviD-DEViSE", ["en"])
		assert len(results) > 0, "No result could be found for Transformer 2 in English"

class SubtitleSourceTestCase3(unittest.TestCase):
	def runTest(self):
		import SubtitleSource
		subdb = SubtitleSource.SubtitleSource()
		results = subdb.query("Transformers.Revenge.of.the.Fallen.TS.XviD-DEViSE", ["en", "fi"])
		assert len(results) > 0, "No result could be found for Transformer 2 in English or Finnish"

class SubtitleSourceTestCase3(unittest.TestCase):
	def runTest(self):
		import Podnapisi
		subdb = Podnapisi.Podnapisi()
		results = subdb.query("My.Name.is.Earl.S04E24.HDTV.XviD-LOL", ["en"])
		assert len(results) > 0, "No result could be found for My.Name.is.Earl.S04E24.HDTV.XviD-LOL in any languages"
'''
if __name__ == "__main__":
	unittest.main()
