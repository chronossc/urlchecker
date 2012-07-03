# coding: utf-8
try:
    import simplejson
except ImportError:
    from django.utils import simplejson

from django.core.http import HttpResponse, HttpResponseForbidden, \
    HttpResponseNotModified, HttpResponseBadRequest, HttpResponse, \
    HttpResponseNotAllowed, HttpResponseServerError
from django.utils import timezone
from django.core.validators import URLValidator, ValidationError
from raven.contrib.django.models import client

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

        urlobj, created = URL.objects.get_or_create(user=request.user,url=url)

        if created:
            try:
                urlobj.update_status()
            except Exeption as err:
                from .tasks import update_urls
                update_urls.delay(urlobj.url)
                return HttpResponseServerError(simplejson.dumps(
                    {'code':500,
                     'msg':'Server error. Task was sent to queue. '\
                        'Try again in some minutes.',
                      'error':unicode(err)}),
                    mimetype='application/json')

        try:
            url_data = urlobj.get_status()
            if not created and urlobj.update_time < urlobj.last_time_checked:
                return HttpResponseNotModified(simplejson.dumps({'code': 304,
                    'msg': 'OK', 'data': url_data}),mimetype='application/json')
            else:
                return HttpResponse(simplejson.dumps({'code': 200, 'msg': 'OK',
                    'data': url_data}),mimetype='application/json')
        except Exception, err:
            sentry_id = client.captureException()
            return HttpResponseServerError(simplejson.dumps(
                {'code':500,'msg':'Server error','error':unicode(err)}),
                mimetype='application/json')


