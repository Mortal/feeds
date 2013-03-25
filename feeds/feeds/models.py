import datetime
import logging

from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    feed = models.ForeignKey('Feed')
    author = models.CharField(max_length=500, blank=True)
    title = models.CharField(max_length=500, blank=True)
    link = models.CharField(max_length=500, blank=True)
    content = models.TextField(blank=True)
    received = models.DateTimeField()
    published = models.DateTimeField()
    uid = models.CharField(max_length=500, unique=True)

class PostRead(models.Model):
    user = models.ForeignKey(User)
    post = models.ForeignKey(Post)

    class Meta:
        unique_together = (('user', 'post'),)

class Feed(models.Model):
    defunct = models.BooleanField(default=False)
    title = models.CharField(max_length=500)
    feed_url = models.CharField(max_length=500)
    home_url = models.CharField(max_length=500, blank=True)
    last_fetched = models.DateTimeField(auto_now_add=True)

    def fetch(self):
        import feedparser
        d = feedparser.parse(self.feed_url)

        self.last_fetched = datetime.datetime.now()

        if d.bozo != 0:
            logging.info("Failed fetching feed ["+self.title+"]")
            logging.info("Bozo exception was: ["+repr(d.bozo_exception)+"]")
            self.defunct = True
            self.save()
            return

        self.defunct = False
        if self.title == self.feed_url:
            self.subscription_set.filter(title__exact=self.title).update(title=d.feed.title)
        self.title = d.feed.title
        self.home_url = d.feed.link
        self.last_fetched = datetime.datetime.now()
        self.save()

        added = 0

        for e in d.entries:
            if Post.objects.filter(feed=self, uid=e.id).exists():
                continue

            try:
                published_src = e.updated_parsed[0:6]
                published = datetime.datetime(*published_src)
            except AttributeError:
                logging.info(u"Couldn't get post published time from title ["+e.title+u"], feed ["+self.title+u"]")
                logging.debug(str(e))
                published = datetime.datetime.now()

            post = Post(
                feed=self,
                author=e.author,
                title=e.title,
                link=e.link,
                content=e.description,
                published=published,
                received=datetime.datetime.now(),
                uid=e.id)

            post.save()
            added = added + 1

        logging.info(u"Parsed feed ["+self.title+u"]. "+str(len(d.entries))+u" entries of which "+str(added)+u" were added to database.")

class FeedTag(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=500)

class Subscription(models.Model):
    feed = models.ForeignKey(Feed)
    user = models.ForeignKey(User)
    tags = models.ManyToManyField(FeedTag)
    title = models.CharField(max_length=500)
