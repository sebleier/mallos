import httplib2
from lxml.html import fromstring
from multiprocessing import Process, Queue
from Queue import Empty
from urlparse import urlparse


class Response(object):
    def __init__(self, url, status_code=-1, content=None, links=[], depth=0, group=None):
        self.url = url
        self.status_code = status_code
        self.content = content
        self.links = links
        self.depth = depth
        self.group = group


class Link(object):
    def __init__(self, url, depth=0, group=None):
        self.url = url
        self.depth = depth
        self.group = group


class Mallos(object):
    """
    Mallos is a multiprocess spider.  It splits the work of io bound tasks and
    CPU bound task into different processes.  IO processes fetch urls and place
    them into a queue for processing.  The processing in done by the parent
    process.
    """

    def __init__(self, urls=[], spiders=5, depth=3, auto_start=True):
        self.processes = []
        self.seen_urls = set()
        self.max_depth = depth
        self.spiders = spiders

        # Set up queues
        self.urls = Queue()
        self.process_queue = Queue()

        # Initialize
        self.add(urls)
        if auto_start:
            self.crawl()

    def crawl(self):
        for i in range(self.spiders):
            process = Process(target=self.worker)
            process.start()
            self.processes.append(process)

    def get_url(self):
        while True:
            yield self.urls.get()

    def worker(self):
        try:
            http = httplib2.Http(timeout = 60)
            for url in self.get_url():
                response, content = http.request(url.url)
                response = Response(url.url, response.status,
                    content=content,
                    depth=url.depth,
                    group=url.group
                )
                self.process_queue.put(response)
        except KeyboardInterrupt:
            pass

    def add(self, urls, depth=0, group=None):
        if not isinstance(urls, list):
            urls = [urls]
        for url in urls:
            url_group = None
            if isinstance(url, tuple):
                url_group, url = url
            if url not in self.seen_urls:
                self.seen_urls.add(url)
                self.urls.put(Link(url, depth=depth, group=url_group or group))

    def get_response(self):
        response = self.process_queue.get_nowait()
        url_parts = urlparse(response.url)
        if response.depth < self.max_depth:
            base_url = "%s://%s" % (url_parts.scheme, url_parts.netloc)
            urls = self.extract_urls(base_url, response.content)
            self.add(urls, depth=response.depth + 1, group=response.group)
        return response

    def __iter__(self):
        try:
            while True:
                try:
                    yield self.get_response()
                except Empty:
                    if self.urls.qsize == 0:
                        self.terminate()
                        return
        except KeyboardInterrupt:
            self.terminate()
            return

    def extract_urls(self, base_url, content):
        """
        Extracts all URLs from an html page. Absolute URLs will be returned
        """
        try:
            html = fromstring(content)
        except Exception:
            return
        html.make_links_absolute(base_url, resolve_base_href=True)
        urls = []
        for url in html.cssselect('a'):
            if url.attrib.has_key('href') and url.attrib['href'].startswith(base_url):
                urls.append(url.attrib['href'])
        return urls

    def terminate(self):
        for p in self.processes:
            p.terminate()
            p.join()
