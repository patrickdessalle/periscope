import unittest
import logging

logging.basicConfig(level=logging.DEBUG)


class RegexTestCase(unittest.TestCase):
	def runTest(self):
		import OpenSubtitles
		subdb = OpenSubtitles.OpenSubtitles()
		#filenames = ('Marley & Me.2008-L33t-DvDRiP.DivX.NoRaR', 'Dexter.S04E01.HDTV.XviD-NoTV', 'Night.Watch.2004.CD1.DVDRiP.XViD-FiCO' , 'Stargate.Universe.S01E06.HDTV.XviD-XII.avi', 'The.Office.US.S06E01.HDTV.XviD-2HD.[VTV]', 'Twilight[2008]DvDrip-aXXo', 'Heroes.S03E09.HDTV.XviD-LOL', 'Transformers.Revenge.of.the.Fallen.TS.XviD-DEViSE', 'My.Name.is.Earl.S04E24.HDTV.XviD-LOL', 'Wallace.And.Gromit.A.Matter.Of.Loaf.And.Death.HDTV.XviD-BiA', 'arw-spread.dvdrip-xvid', 'Rec.2.[Spanish].TS-Screener.XviD.[DTL]', 'X-Men Origins Wolverine [2009] dvd rip nlx', 'Saw VI (2009) TS DivXNL-Team', 'Michael Jackson This Is It 2009 CAM XVID-PrisM.NoRar.www.crazy-torrent.com', 'The.Goods.Live.Hard.Sell.Hard.2009.PROPER.DvDRiP.XviD-ExtraScene RG')
		filenames = ('The.Hurt.Locker.2008.DVDRiP.XViD.CD1.avi', 'Catwoman.CAM-NOX-CD2.avi','Marley & Me.2008-L33t-DvDRiP.DivX.NoRaR')
		for filename in filenames:
			print "%s => %s" %(filename, subdb.guessFileData(filename))
		
'''

class SubtitulosTestCase(unittest.TestCase):
	def runTest(self):
		import Subtitulos
		subdb = Subtitulos.Subtitulos()
		fname = "CSI.S10E13.HDTV.XvID-FQM.avi"
		guessedData = subdb.guessFileData(fname)
		print fname
		print guessedData
		if guessedData['type'] == 'tvshow':
			subs = subdb.query(guessedData['name'], guessedData['season'], guessedData['episode'], guessedData['teams'])
			print subs

class Addic7edTestCase(unittest.TestCase):
	def runTest(self):
		import Addic7ed
		subdb = Addic7ed.Addic7ed()
		fname = "The.Big.Bang.Theory.S03E13.HDTV.XviD-2HD"
		guessedData = subdb.guessFileData(fname)
		print fname
		print guessedData
		if guessedData['type'] == 'tvshow':
			subs = subdb.query(guessedData['name'], guessedData['season'], guessedData['episode'], guessedData['teams'])
			print subs
			
class OpenSubtitlesTestCase(unittest.TestCase):
	def runTest(self):
		import OpenSubtitles
		subdb = OpenSubtitles.OpenSubtitles()
		# movie hash if for night watch : http://trac.opensubtitles.org/projects/opensubtitles/wiki/XMLRPC
		results = subdb.query('Night.Watch.2004.CD1.DVDRiP.XViD-FiCO.avi', moviehash="09a2c497663259cb", bytesize="733589504")
		
		assert len(results) > 0, 'No result found for Night.Watch.2004.CD1.DVDRiP.XViD-FiCO.avi by movie hash'

class OpenSubtitlesTestCaseFileName(unittest.TestCase):
	def runTest(self):
		import OpenSubtitles
		subdb = OpenSubtitles.OpenSubtitles()
		# movie hash if for night watch : http://trac.opensubtitles.org/projects/opensubtitles/wiki/XMLRPC
		filenames = []
		#filename = 'Dexter.S04E01.HDTV.XviD-NoTV'
		#filename = 'The.Office.US.S06E01.HDTV.XviD-2HD.[VTV]'
		#filenames.append('Marley & Me.2008-L33t-DvDRiP.DivX.NoRaR')
		filenames.append("Twilight[2008]DvDrip-aXXo")
		
		for filename in filenames:
			results = subdb.query(filename)
		
			if results :
				print "Found %s results" %len(results)
				print "Showing first for unit test::"
				print results[0]
			assert len(results) > 0, 'No result found for %s' %filename

class SubtitleSourceTestCase(unittest.TestCase):
	def runTest(self):
		import SubtitleSource
		subdb = SubtitleSource.SubtitleSource()
		results = subdb.query("Heroes.S03E09.HDTV.XviD-LOL")
		print results
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

class SubSceneTestCase(unittest.TestCase):
	def runTest(self):
		import SubScene
		subdb = SubScene.SubScene()
		results = subdb.query("Dexter.S04E01.HDTV.XviD-NoTV")
		print results
		assert len(results) > 0, "No result could be found for Dexter.S04E01.HDTV.XviD-NoTV and no languages"


class Podnapisi2TestCase(unittest.TestCase):
	def runTest(self):
		import Podnapisi2
		subdb = Podnapisi2.Podnapisi()
		results = subdb.process("/burn/Bored.to.Death.S01E01.HDTV.XviD-NoTV.avi", None)
		print results
		assert len(results) > 5, "Not enough result could be found for The.Office.US.S06E01.HDTV.XviD-2HD and no languages (expected 6)"

class PodnapisiTestCase(unittest.TestCase):
	def runTest(self):
		import Podnapisi
		subdb = Podnapisi.Podnapisi()
		results = subdb.process("/burn/Community.S01E01.Pilot.HDTV.XviD-FQM.avi", None)
		print results
		assert len(results) > 5, "Not enough result could be found for Community.S01E01.Pilot.HDTV.XviD-FQM.avi and no languages (expected 6)"
'''		

class PodnapisiTestCaseMultiPart(unittest.TestCase):
	def runTest(self):
		import Podnapisi
		subdb = Podnapisi.Podnapisi()
		results = subdb.process("/tmp/Catwoman.CAM-NOX-CD1.avi", None)
		print results
		assert len(results) > 0
		results = subdb.process("/tmp/Catwoman.CAM-NOX-CD2.avi", None)
		print results
		assert len(results) > 0
		
		Catwoman.CAM-NOX-CD1
'''	

class PodnapisiTestCaseTwoSerbian(unittest.TestCase):
	def runTest(self):
		import Podnapisi
		subdb = Podnapisi.Podnapisi()
		results = subdb.process("Twilight[2008]DvDrip-aXXo", None)
		print results
		assert len(results) > 0, "Not enough result could be found"

class TvSubtitlesTestCase(unittest.TestCase):
	def runTest(self):
		import TvSubtitles
		subdb = TvSubtitles.TvSubtitles()
		fname = "The.Big.Bang.Theory.S03E15.The.Large.Hadron.Collision.HDTV.XviD-FQM"
		guessedData = subdb.guessFileData(fname)
		subs = subdb.query(guessedData['name'], guessedData['season'], guessedData['episode'], guessedData['teams'], ['en'])
		for s in subs:
			print "Sub : %s" %s
'''		
if __name__ == "__main__":
	unittest.main()
