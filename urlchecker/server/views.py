# coding: utf-8
try:
    import simplejson
except ImportError:
    from django.utils import simplejson
from django.conf import settings
from django.core.cache import cache
from django.core.validators import URLValidator, ValidationError
from django.http import HttpResponse, HttpResponseForbidden, \
    HttpResponseNotModified, HttpResponseBadRequest, HttpResponse, \
    HttpResponseNotAllowed, HttpResponseServerError

from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from raven.contrib.django.models import client

from .models import Key, URL

def cache_and_send(urlobj,json,code):
    """ cache response content and return response """
    cache_key = "%s:%s" % (urlobj.user.username,urlobj.url)
    cached = cache.has_key(cache_key)
    response = simplejson.dumps(json)
    if code in (200,304):
        timeout=1800 # 30 minutes
    else:
        timeout=180 # 3 minutes
    cache.set(cache_key,(code,response),timeout) 

    if code == 200 and cached:
        cache.set(cache_key,(304,response),timeout)

    return response_from_cache(urlobj.url,urlobj.user.username)

class CacheKeyError(KeyError):
    pass

def response_from_cache(url,username):
    """ Get response code and text from cache and return it """
    cache_key = "%s:%s" % (username,url)

    if not cache.has_key(cache_key):
        raise CacheKeyError(u"%s isn't in cache." % cache_key)

    code,response = cache.get(cache_key)

    if code == 200:
        return HttpResponse(response,mimetype='application/json')

    if code == 304:
        return HttpResponseNotModified(response,mimetype='application/json')

    if code == 400:
        return HttpResponseBadRequest(response,mimetype='application/json')

    if code == 403:
        return HttpResponseForbidden(response,mimetype='application/json')

    if code == 412:
        return HttpResponseBadRequest(response,mimetype='application/json')

    return HttpResponse(response,status=code,mimetype='application/json')

@csrf_exempt
def query_url(request):
    """
    This view returns status for url.

    This view returns appropriate responses for each possible status of a query.
    Remarkably 304 and 200 for success responses and 400, 403 and 500 for errors.

    You would like to read it: http://en.wikipedia.org/wiki/List_of_HTTP_status_codes
    """
    messages = {
        'key_not_send': u"You need to send a key in POST data to be valid "\
            "request. The key should be requested to system administrator.",
        'key_invalid': u"Your key is invalid or not found. Contact system "\
            "administrator for more information.",
        'url_invalid_parameter': u"You need to send a url in POST data to be tested. "\
            "Use 'url' field for that.",
        'url_malformed': u"You sent a malformed url in POST. Check and try again.",
    }

    if not request.method == 'POST':
        if not request.is_ajax():
            return HttpResponseBadRequest('This url should be requested via'\
                ' Ajax POST requests ')
        return HttpResponseNotAllowed(['POST'])

    # TODO: if you have more views that use key put it in a decorator
    request.key = None
    key = request.POST.get('key',None)
    if not key:
        return HttpResponseForbidden(simplejson.dumps(
            {'code':403,'msg':messages['key_not_send']}),
            mimetype="application/json")
    else:
        try:
            keyobj = Key.objects.get(key=key,active=True,
                valid_until__gte=timezone.now())
        except Key.DoesNotExist:
            return HttpResponseForbidden(simplejson.dumps(
                {'code':403,'msg':messages['key_invalid']}),
                mimetype="application/json")
        else:
            request.user = keyobj.user
            request.key = keyobj

    if request.key:
        if 'url' not in request.POST:
            return HttpResponseBadRequest(simplejson.dumps(
                {'code':400,'msg':messages['url_invalid_parameter']}),
                mimetype="application/json")

        url = request.POST['url']
        url_validator = URLValidator()
        try:
            url_validator(url)
        except ValidationError:
            return HttpResponseBadRequest(simplejson.dumps(
                {'code':400,'msg':messages['url_malformed']}),
                mimetype='application/json')

        try:
            return response_from_cache(url,request.user.username)
        except CacheKeyError:
            pass

        urlobj, created = URL.objects.get_or_create(user=request.user,url=url)
        if not urlobj.last_time_checked:
            try:
                urlobj.update_status()
            except Exception, err:
                from .tasks import update_urls
                update_urls.delay(urlobj.url)
                return cache_and_send(urlobj,
                    {'code':500,
                     'msg':'Server error. Task was sent to queue. '\
                        'Try again in some minutes.',
                      'error':unicode(err)},500)

        if urlobj.get_ip_type() in ["RESERVED","SPECIALPURPOSE","LOOPBACK"]:
            msg = u"%s is a %s IP and will not be checked." % (
                urlobj.site_ip, urlobj.get_ip_type())
            return cache_and_send(urlobj,{'code':412,'msg':msg},412)
        if not getattr(settings,"URLCHECK_ALLOW_PRIVATE_IPS",False) and \
            urlobj.get_ip_type() == "PRIVATE":
            msg = u"%s is a %s IP and will not be checked. Set "\
                "URLCHECK_ALLOW_PRIVATE_IPS in settings.py to check this IPs." % (
                    urlobj.site_ip,urlobj.get_ip_type())
            return cache_and_send(urlobj,{'code':412,'msg':msg},412)

        try:
            url_data = urlobj.get_status()
            if not created and urlobj.update_time < urlobj.last_time_checked:
                return cache_and_send(urlobj,{'code': 304,
                    'msg': 'OK', 'data': url_data},304)
            else:
                return cache_and_send(urlobj,{'code': 200, 'msg': 'OK',
                    'data': url_data},200)
        except Exception, err:
            sentry_id = client.captureException()
            return cache_and_send(urlobj,{'code':500,'msg':'Server error',
                'error':unicode(err)},500)
