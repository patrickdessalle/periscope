## dvrasp 15.4.09 v.001
## Sources :
##  - http://code.google.com/p/arturo/source/browse/trunk/plugins/net/tvsubtitles.py
##  - http://www.gtk-apps.org/CONTENT/content-files/90184-download_tvsubtitles.net.py

import logging

import zipfile, os, urllib2
import os, re, BeautifulSoup, urllib

showNum = {
"24":38,
"30 rock":46,
"90210":244,
"afterlife":200,
"alias":5,
"aliens in america":119,
"ally mcbeal":158,
"american dad":138,
"andromeda":60,
"andy barker: p.i.":49,
"angel":98,
"army wives":242,
"arrested development":161,
"ashes to ashes":151,
"avatar: the last airbender":125,
"back to you":183,
"band of brothers":143,
"battlestar galactica":42,
"big day":237,
"big love":88,
"big shots":137,
"bionic woman":113,
"black adder":176,
"black books":175,
"blade":177,
"blood ties":140,
"bonekickers":227,
"bones":59,
"boston legal":77,
"breaking bad":133,
"brotherhood":210,
"brothers &amp; sisters":66,
"buffy the vampire slayer":99,
"burn notice":50,
"californication":103,
"carnivale":170,
"carpoolers":146,
"cashmere mafia":129,
"charmed":87,
"chuck":111,
"city of vice":257,
"cold case":95,
"criminal minds":106,
"csi":27,
"csi miami":51,
"csi ny":52,
"curb your enthusiasm":69,
"damages":124,
"dark angel":131,
"day break":6,
"dead like me":13,
"deadwood":48,
"desperate housewives":29,
"dexter":55,
"dirt":145,
"dirty sexy money":118,
"do not disturb":252,
"doctor who":141,
"dollhouse" : 448,
"drive":97,
"eli stone":149,
"entourage":25,
"er (e.r.)":39,
"eureka":43,
"everybody hates chris":81,
"everybody loves raymond":86,
"exes &amp; ohs":199,
"extras":142,
"fallen":101,
"family guy":62,
"farscape":92,
"fawlty towers":178,
"fear itself":201,
"felicity":217,
"firefly":84,
"flash gordon":134,
"flashpoint":221,
"friday night lights":57,
"friends":65,
"fringe":204,
"futurama":126,
"generation kill":223,
"ghost whisperer":14,
"gilmore girls":28,
"gossip girl":114,
"greek":102,
"grey's anatomy":7,
"hank":538,
"heroes":8,
"hidden palms":44,
"hotel babylon":164,
"house m.d.":9,
"how i met your mother":110,
"hustle":160,
"in justice":144,
"in plain sight":198,
"in treatment":139,
"into the west":256,
"invasion":184,
"it's always sunny in philadelphia":243,
"jeeves and wooster":180,
"jekyll":61,
"jericho":37,
"joey":83,
"john adams":155,
"john from cincinnati":79,
"journeyman":108,
"k-ville":107,
"keeping up appearances":167,
"knight rider":163,
"kyle xy":10,
"lab rats":233,
"las vegas":75,
"life":109,
"life is wild":120,
"life on mars (uk)":90,
"lipstick jungle":150,
"lost":3,
"lost in austen":254,
"lucky louie":238,
"mad men":136,
"meadowlands":45,
"medium":12,
"melrose place":189,
"men in trees":127,
"miami vice":208,
"monk":85,
"moonlight":117,
"my name is earl":15,
"ncis":30,
"new amsterdam":153,
"nip/tuck":23,
"northern exposure":241,
"numb3rs":11,
"october road":132,
"one tree hill":16,
"over there":93,
"oz":36,
"painkiller jane":35,
"pepper dennis":82,
"police squad":190,
"popetown":179,
"pretender":245,
"primeval":130,
"prison break":2,
"private practice":115,
"privileged":248,
"project runway":226,
"psych":17,
"pushing daisies":116,
"queer as folk":229,
"reaper":112,
"regenesis":152,
"rescue me":91,
"robin hood":121,
"rome":63,
"roswell":159,
"samantha who?":123,
"samurai girl":255,
"saving grace":104,
"scrubs":26,
"secret diary of a call girl":196,
"seinfeld":89,
"sex and the city":68,
"shameless":193,
"shark":24,
"sharpe":186,
"six feet under":94,
"skins":147,
"smallville":1,
"sophie":203,
"south park":71,
"spooks":148,
"standoff":70,
"stargate atlantis":54,
"stargate sg-1":53,
"studio 60 on the sunset strip":33,
"supernatural":19,
"swingtown":202,
"taken":67,
"tell me you love me":182,
"terminator: the sarah connor chronicles":128,
"the 4400":20,
"the andromeda strain":181,
"the big bang theory":154,
"the black donnellys":216,
"the cleaner":225,
"the closer":78,
"the dead zone":31,
"the dresden files":64,
"the fixer":213,
"the inbetweeners":197,
"the it crowd":185,
"the l word":74,
"the middleman":222,
"the net":174,
"the no. 1 ladies' detective agency":162,
"the o.c. (the oc)":21,
"the office":58,
"the outer limits":211,
"the riches":156,
"the secret life of the american teenager":218,
"the shield":40,
"the simple life":234,
"the simpsons":32,
"the sopranos":18,
"the tudors":76,
"the unit":47,
"the war at home":80,
"the west wing":168,
"the wire":72,
"the x-files":100,
"threshold":96,
"til death":171,
"tin man":122,
"top gear":232,
"torchwood":135,
"traveler":41,
"tripping the rift":188,
"tru calling":4,
"true blood":205,
"twin peaks":169,
"two and a half men":56,
"ugly betty":34,
"ultimate force":194,
"unhitched":157,
"veronica mars":22,
"weeds":73,
"will & grace":172,
"without a trace":105,
"women's murder club":166,
"wonderfalls":165
 }


import SubtitleDatabase

class TvSubtitles(SubtitleDatabase.SubtitleDB):
	url = "http://www.tvsubtitles.net"
	site_name = "TvSubtitles"
	
	URL_SHOW_PATTERN = "http://www.tvsubtitles.net/tvshow-%s.html"
	URL_SEASON_PATTERN = "http://www.tvsubtitles.net/tvshow-%s-%d.html"

	def __init__(self):
		super(TvSubtitles, self).__init__({"en":'en', "fr":'fr'})## TODO ??
		self.host = TvSubtitles.url
    
	def _get_episode_urls(self, show, season, episode, langs):
		showId = showNum.get(show, None)
		if not showId:
			return []
		show_url = self.URL_SEASON_PATTERN % (showId, season)
		logging.debug("Show url: %s" % show_url)
		page = urllib.urlopen(show_url)
		content = page.read()
		content = content.replace("SCR'+'IPT", "script")
		soup = BeautifulSoup.BeautifulSoup(content)
		td_content = "%sx%s"%(season, episode)
		tds = soup.findAll(text=td_content)
		links = []
		for td in tds:
			imgs =  td.parent.parent.findAll("td")[3].findAll("img")
			for img in imgs:
				# If there is an alt, and that alt in langs or you didn't specify a langs
				if img['alt'] and ((langs and img['alt'] in langs) or (not langs)):
					url = self.host + "/" + img.parent['href']
					lang = img['alt']
					logging.debug("Found lang %s - %s" %(lang, url))
					links.append((url, lang))
					
		return links

	def query(self, show, season, episode, teams, langs):
		showId = showNum.get(show, None)
		if not showId:
			return []
		show_url = self.URL_SEASON_PATTERN % (showId, season)
		logging.debug("Show url: %s" % show_url)
		page = urllib.urlopen(show_url)
		content = page.read()
		content = content.replace("SCR'+'IPT", "script")
		soup = BeautifulSoup.BeautifulSoup(content)
		td_content = "%dx%02d"%(season, episode)
		tds = soup.findAll(text=td_content)
		links = []
		for td in tds:
			imgs =  td.parent.parent.findAll("td")[3].findAll("img")
			for img in imgs:
				# If there is an alt, and that alt in langs or you didn't specify a langs
				if img['alt'] and ((langs and img['alt'] in langs) or (not langs)):
					url = img.parent['href']
					lang = img['alt']
					logging.debug("Found lang %s - %s" %(lang, url))
					if url.startswith("subtitle"):
						url = self.host + "/" + url
						logging.debug("Parse : %s" %url)
						sub = self.parseSubtitlePage(url, lang, show, season, episode, teams)
						if sub:
							links.append(sub)
					else:
						page2 = urllib.urlopen(self.host + "/" + url)
						soup2 = BeautifulSoup.BeautifulSoup(page2)
						subs = soup2.findAll("div", {"class" : "subtitlen"})
						for sub in subs:
							url = self.host + sub.get('href', None)
							logging.debug("Parse2 : %s" %url)
							sub = self.parseSubtitlePage(url, lang, show, season, episode, teams)
							if sub:
								links.append(sub)
					
		return links
		
	def parseSubtitlePage(self, url, lang, show, season, episode, teams):
		fteams = []
		for team in teams:
			fteams += team.split("-")
		fteams = set(fteams)
		
		subid = url.rsplit("-", 1)[1].split('.', 1)[0]
		link = self.host + "/download-" + subid + ".html"
		
		page = urllib.urlopen(url)
		content = page.read()
		content = content.replace("SCR'+'IPT", "script")
		soup = BeautifulSoup.BeautifulSoup(content)
		
		subteams = set()
		releases = soup.findAll(text="release:")
		if releases:
			subteams.update([releases[0].parent.parent.parent.parent.findAll("td")[2].string.lower()])
		
		rips = soup.findAll(text="rip:")
		if rips:
			subteams.update([rips[0].parent.parent.parent.parent.findAll("td")[2].string.lower()])
		
		if subteams.issubset(fteams):
			logging.debug("It'a match ! : %s <= %s" %(subteams, fteams))
			result = {}
			result["release"] = "%s.S%.2dE%.2d.%s" %(show.replace(" ", ".").title(), int(season), int(episode), '.'.join(subteams).upper()
	)
			result["lang"] = lang
			result["link"] = link
			result["page"] = url
			return result
		else:
			logging.debug("It'not a match ! : %s > %s" %(subteams, fteams))
			return None
			
		
		

	def process(self, filename, langs):
		''' main method to call on the plugin, pass the filename and the wished 
		languages and it will query TvSubtitles.net '''
		fname = unicode(self.getFileName(filename).lower())
		guessedData = self.guessFileData(fname)
		logging.debug(fname)
		if guessedData['type'] == 'tvshow':
			subs = self.query(guessedData['name'], guessedData['season'], guessedData['episode'], guessedData['teams'], langs)
			return subs
		else:
			return []
