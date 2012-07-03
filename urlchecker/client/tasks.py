# coding: utf-8
import datetime
import pytz
import requests
import socket
import urlparse
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.core.validators import URLValidator, ValidationError
from celery.task import task
from hashlib import md5
from raven.contrib.django.models import client
from .models import URLStatusHistory

@task(max_retries=5,ignore_result=True,time_limit=60)
def update_url_info(url,timeout=10):
    """ Update url status from URLCHECKER_SERVER.
        It update URLStatusHistory table and URLCHECKER_SERVER
    """
    server = getattr(settings,'URLCHECKER_SERVER')
    key = getattr(settings,'URLCHECKER_KEY')

    # it already is checked on __init__.py
    if not server or not key:
        raise ImproperlyConfigured(u"URLCHECKER: Configure URLCHECKER_SERVER "\
            "and URLCHECKER_KEY on settings.py.")

    try:
        URLValidator()(url)
    except ValidationError:
        raise ValidationError(u"'%s' is one invalid URL. Update aborted.")

    try:
        url_request = requests.post(server,data={'key':key,'url':url},
            timeout=timeout)
    except request.TIMEOUT as err:
        # capture exception to raven and try again
        sentry_id = client.get_ident(client.captureException())
        logger.error(u"Timeout processing url %s [Sentry ID '%s']",
            url,sentry_id)
    else:
        if url_request.status_code in (200,304):
            # request without errors
            urldata = url_request.json['data']
            print urldata
            urlstatus, created = URLStatusHistory.objects.get_or_create(url=url)
            urlstatus.update_time = datetime.datetime.now(pytz.utc)
            urlstatus.site_ip = urldata['site_ip']
            urlstatus.site_fqdn = urldata['site_fqdn']
            urlstatus.web_server_name = urldata['web_server_name']
            urlstatus.html_status_code = urldata['html_status_code']
            urlstatus.save()

            cache_key = 'urlchecker.client_%s' % md5(url).hexdigest()
            cache.set(cache_key,urlstatus,300)

        else:
            try:
                url_request.raise_for_status()
            except requests.HTTPError, err:
                # something happened, create a error in sentry if error is
                # unknow
                send_to_sentry=True

                if url_request.status_code == 412 and \
                        url_request.json.has_key('msg') and \
                        "is a PRIVATE IP and" in url_request.json['msg']:
                    # know error, is a internal IP, we just get url info
                    update_internal_url_info(url)
                    send_to_sentry=False

                if send_to_sentry:
                    import ipdb
                    ipdb.set_trace()
                    extra = {
                        'url': url,
                        'urlobj_id': getattr(urlobj,'id',None),
                        'code': url_request.status_code,
                        'method': 'post',
                        'json': url_request.json,
                        'text': url_request.text,
                        'request_dict': url_request.__dict__
                    }
                    sentry_id = client.get_ident(client.captureException(extra=extra))
                    logger.error(u"HTTP error %s on update_url_info. Msg was '%s'",
                        url_request.status_code,url_request.json.get('msg'))

def update_internal_url_info(url):
    urlstatus = URLStatusHistory.objects.get_or_create(url=url)
    url = urlparse.urlparse(urlstatus.url)
    urlstatus.hostname = url.hostname
    if urlstatus.hostname:
        urlstatus.site_ip = socket.gethostbyname(urlstatus.hostname)
        urlstatus.site_fqdn = socket.getfqdn(urlstatus.hostname)
    try:
        request = requests.get(urlstatus.url)
        urlstatus.web_server_name = request.headers.get('server','')
        urlstatus.html_status_code = request.status_code
    except requests.exceptions.Timeout:
        urlstatus.html_status_code = request.codes.timeout

    urlstatus.save()
    cache_key = 'urlchecker.client_%s' % md5(url).hexdigest()
    cache.set(cache_key,urldata,300)