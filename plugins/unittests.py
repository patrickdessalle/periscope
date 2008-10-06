import unittest

class OpenSubtitlesTestCase(unittest.TestCase):
	def runTest(self):
		import OpenSubtitles
		subdb = OpenSubtitles.OpenSubtitles()
		results = subdb.query(moviehash="09a2c497663259cb", lang="en")
		
		assert len(results) > 0, 'No result found for the example moviehash'
		
if __name__ == "__main__":
	unittest.main()
