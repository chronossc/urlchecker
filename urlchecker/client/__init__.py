# coding: utf-8
import IPy
import requests
import urlparse
from django.conf import settings
from django.core.cache import cache
from django.core.validators import URLValidator, ValidationError

from hashlib import md5
from .models import URLStatusHistory
from .tasks import update_url_info

_server = getattr(settings,'URLCHECKER_SERVER')
_key = getattr(settings,'URLCHECKER_KEY')

if not _server or not _key:
    raise ImproperlyConfigured(u"URLCHECKER: Configure URLCHECKER_SERVER "\
        "and URLCHECKER_KEY on settings.py.")

def get_url_info(url,client_ip=None,force_update=False,retry=True):
    """ Get last url status. Source order is:
        - from cache.get(url)
        - from URLStatusHistory table

        Return True if status is good, False instead.

        If url isn't in cache it send a task to celery update info, so next time
        we have more precise information.
    """

    try:
        URLValidator()(url)
    except ValidationError:
        raise ValidationError(u"'%s' is one invalid URL." % url)

    if force_update:
        update_url_info(url)

    cache_key = 'urlchecker.client_%s' % md5(url).hexdigest()

    # try to get from cache
    urlobj = cache.get(cache_key)

    # if not in cache
    if urlobj is None:
        try:
            # try to get from db
            urlobj = URLStatusHistory.objects.get(url=url)
        except URLStatusHistory.DoesNotExist:
            # if not in db update status and get again.
            # in this case we let exceptions propagate.
            update_url_info(url)
            if retry:
                return get_url_info(url,client_ip=client_ip,
                    force_update=force_update,retry=False)

    return urlobj.html_status_code in (100,101,102,200,201,202,203,205,206,207,
        300,300,301,302,303,304,307,401)