import unittest
import logging

logging.basicConfig(level=logging.DEBUG)

'''class OpenSubtitlesTestCase(unittest.TestCase):
	def runTest(self):
		import OpenSubtitles
		subdb = OpenSubtitles.OpenSubtitles()
		# movie hash if for night watch : http://trac.opensubtitles.org/projects/opensubtitles/wiki/XMLRPC
		results = subdb.query('Night.Watch.2004.CD1.DVDRiP.XViD-FiCO.avi', moviehash="09a2c497663259cb", bytesize="733589504")
		
		assert len(results) > 0, 'No result found for the example moviehash'

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
class SubSceneTestCase(unittest.TestCase):
	def runTest(self):
		import SubScene
		subdb = SubScene.SubScene()
		results = subdb.query("Dexter.S04E01.HDTV.XviD-NoTV")
		print results
		assert len(results) > 0, "No result could be found for Dexter.S04E01.HDTV.XviD-NoTV and no languages"

'''
class PodnapisiTestCase(unittest.TestCase):
	def runTest(self):
		import Podnapisi
		subdb = Podnapisi.Podnapisi()
		results = subdb.process("The.Office.US.S06E01.HDTV.XviD-2HD", None)
		print results
		assert len(results) > 5, "Not enough result could be found for The.Office.US.S06E01.HDTV.XviD-2HD and no languages (expected 6)"
		
	

class PodnapisiTestCaseTwoSerbian(unittest.TestCase):
	def runTest(self):
		import Podnapisi
		subdb = Podnapisi.Podnapisi()
		results = subdb.process("Twilight[2008]DvDrip-aXXo", None)
		print results
		assert len(results) > 0, "Not enough result could be found"
'''		
		
if __name__ == "__main__":
	unittest.main()
