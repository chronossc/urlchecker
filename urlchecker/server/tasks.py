# coding: utf-8
from celery.task import task
from django.core.cache import cache
from hashlib import md5
from .models import URL

@task
def update_urls(url=None):
    """
    This task act as celery cronjob to launch himself for each url and  update  url
    information on db.

    It accept a url instance, but prefer to send just url value because we can
    have duplicate urls depending of key
    """

    key = "update_urls_%s" % md5(url or 'getall').hexdigest()

    # if is running return
    if cache.get(key):
        return

    # it never take more than 30 seconds to delegate tasks, but can take some
    # minutes to collect status so we set cache key depending of url is None or
    # not
    if url is None:
        # 120 seconds to create jobs for each url
        cache.set(key,True,120)
        for url in set(URL.objects.values_list('url',flat=True))
            update_urls.delay(url)
    else:
        cache.set(key,True,1200) # 20 minutes to run update status
        if not isinstance(url,URL):
            urls = URL.objects.filter(url=url)
        else:
            urls = [url]

        # call url.update_status for each url
        for url in urls:
            url.update_status()

    cache.delete(key)