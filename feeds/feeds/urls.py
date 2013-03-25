from django.conf.urls import patterns, include, url
from .views import AddView, AggregateView, FeedsView, FeedUnsubscribeView, FetchView, MarkReadView, MarkUnreadView

urlpatterns = patterns('',
    url(r'^$', AggregateView.as_view(), name='aggregate'),
    url(r'^feed/(?P<sub>\d+)/$', AggregateView.as_view(), name='single_feed'),
    url(r'^feed/tag/(?P<tag>\d+)/$', AggregateView.as_view(), name='single_tag'),
    url(r'^feed/$', FeedsView.as_view(), name='feeds'),
    url(r'^feed/add/$', AddView.as_view(), name='add'),
    url(r'^feed/(?P<pk>\d+)/unsubscribe/$', FeedUnsubscribeView.as_view(), name='feed_unsubscribe'),
    url(r'^feed/(?P<pk>\d+)/fetch/$', FetchView.as_view(), name='feed_fetch'),
    url(r'^post/(?P<pk>\d+)/read/$', MarkReadView.as_view(), name='post_read'),
    url(r'^post/(?P<pk>\d+)/unread/$', MarkUnreadView.as_view(), name='post_unread'),
)
