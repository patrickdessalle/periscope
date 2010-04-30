import OpenSubtitles

p = OpenSubtitles.OpenSubtitles()
filename = "/media/disk/Videos/Series/How I Met Your Mother/S4/How.I.Met.Your.Mother.S04E06.HDTV.XviD-LOL.[VTV].avi"
subs = p.process(filename, ["en"])

print subs

#p.createFile(subs[0]["link"], "/media/disk/Videos/Series/How I Met Your Mother/S4/How.I.Met.Your.Mother.S04E06.HDTV.XviD-LOL.[VTV].avi")
