import os
from mallos import Mallos

logfile = os.path.join(os.path.dirname(__file__), 'mallos.log')

spider = Mallos('http://www2.ljworld.com', spiders=5, depth=1, logfile=logfile)
for response in spider:
    print "Queue Length: %s" % spider.urls.qsize(), response.status_code, "depth: %s" % response.depth, response.url
