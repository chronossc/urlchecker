# coding: utf-8
from django.conf.urls import patterns, url

urlpatterns = patterns('urlchecker.server.views',
    url(r'^query_url$', 'query_url', name='query_url'),
)