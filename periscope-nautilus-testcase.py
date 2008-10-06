import unittest
import MenuProvider

class MenuProviderTestCase(unittest.TestCase):

	def runTest(self):
		try:
			dir(MenuProvider)
			mp = MenuProvider.DownloadSubtitles()
			mp.notify([{"filename": "a"}], [])
		except Exception, e:
			print e
			self.fail("Could not notify")
		
if __name__ == "__main__":
	unittest.main()
