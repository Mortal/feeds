class FeedMeta:
    def __init__(self):
        self.valid = False
        self.url = None
        self.error = None

def valid_feed_url(url):
    result = FeedMeta()
    result.valid = True
    result.url = url

    import feedparser
    d = feedparser.parse(url)

    if d.bozo == 0:
        return result

    if 'links' in d.feed:
        for l in d.feed.links:
            if 'rel' not in l:
                continue
            if 'href' not in l:
                continue
            if l.rel != 'alternate':
                continue
            if l.type == 'application/atom+xml' or l.type == 'application/rss+xml':
                result.url = l.href
                return result

    result.valid = False
    result.error = "Bozo exception: "+repr(d.bozo_exception)

    return result
