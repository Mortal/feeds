# Create your views here.
from django.views.generic import ListView, FormView, TemplateView, View
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
import django.contrib.auth.views
from django import forms
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from django.db import IntegrityError

from .models import Post, Feed, PostRead
from .feedparser import valid_feed_url

class AddForm(forms.Form):
    url = forms.CharField()

    def clean_url(self):
        data = self.cleaned_data['url']
        feed_meta = valid_feed_url(data)
        if not feed_meta.valid:
            raise forms.ValidationError(feed_meta.error)
        if Feed.objects.filter(subscribers=self.user, feed_url=feed_meta.url).exists():
            raise forms.ValidationError("You are already subscribed to that feed.")
        return feed_meta.url

class AddView(FormView):
    form_class = AddForm
    success_url = reverse_lazy('aggregate')
    template_name = 'feeds/add.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(AddView, self).dispatch(*args, **kwargs)

    def get_form(self, form_class):
        form = super(FormView, self).get_form(form_class)
        form.user = self.request.user
        return form

    def form_valid(self, form):
        url = form.cleaned_data.get('url')
        try:
            feed = Feed.objects.get(feed_url=url)
        except Feed.DoesNotExist:
            feed = Feed(feed_url=url, title=url)
            feed.save()
        feed.subscribers.add(self.request.user)
        feed.save()

        return super(AddView, self).form_valid(form)

class FetchView(View):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(FetchView, self).dispatch(*args, **kwargs)

    def post(self, request, pk):
        feed = Feed.objects.get(pk=pk)
        feed.fetch()
        return redirect('feeds')

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super(LoginForm, self).clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                cleaned_data['user'] = user
                return cleaned_data
            else:
                raise forms.ValidationError("Inactive user")
        else:
            raise forms.ValidationError("Invalid login")

class AggregateView(ListView):
    template_name = 'feeds/posts.html'
    model = Post
    context_object_name = 'post_list'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(AggregateView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        queryset = list(Post.objects.filter(
                feed__subscribers=self.request.user).order_by('-received')[:30].values(
                    'received',
                    'published',
                    'title',
                    'author',
                    'content',
                    'feed__title',
                    'id',
                    ))

        read_flags = {post_read.post.pk for post_read in PostRead.objects.filter(user=self.request.user, post__in=[post['id'] for post in queryset])}

        def add_read_flag(post):
            post['read'] = (post['id'] in read_flags)
            return post

        queryset = [
                add_read_flag(post) for post in queryset]

        return queryset

class FeedsView(ListView):
    template_name = 'feeds/feeds.html'
    model = Feed

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(FeedsView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        return Feed.objects.filter(
                subscribers=self.request.user)

class FeedUnsubscribeView(TemplateView):
    template_name = 'feeds/unsubscribe.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(FeedUnsubscribeView, self).dispatch(*args, **kwargs)

    def post(self, request, pk):
        feed = Feed.objects.get(pk=pk)
        feed.subscribers.remove(self.request.user)
        return redirect('aggregate')

class MarkReadView(View):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(MarkReadView, self).dispatch(*args, **kwargs)

    def post(self, request, pk):
        try:
            pr = PostRead(user=request.user)
            pr.post_id = pk
            pr.save()
        except IntegrityError:
            # not unique; ignore and carry on
            pass
        return HttpResponse(status=204) # No Content

class MarkUnreadView(View):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(MarkUnreadView, self).dispatch(*args, **kwargs)

    def post(self, request, pk):
        PostRead.objects.filter(user=request.user, post__pk=pk).delete()
        return HttpResponse(status=204) # No Content
