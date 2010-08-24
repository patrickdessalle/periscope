import TheSubDB
import logging

logging.basicConfig(level=logging.DEBUG)

p = TheSubDB.TheSubDB()
filename = "/burn/Better.Off.Ted.S02E07.HDTV.XviD-2HD.[VTV].avi"
subs = p.process(filename, ["en", "pt"])

print subs

if subs:
    p.createFile(subs[0]["link"], "/tmp/test.avi")
