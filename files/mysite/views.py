from django.http import HttpResponse, Http404
import datetime

def hello(request):
    return HttpResponse("Hello world")

def current_datetime(request):
    now = datetime.datetime.now()
    html = '<html><body>The time is %s </body></html>' % now
    return HttpResponse(html)

def hours_ahead(request, offset):
    try:
        offset = int(offset)

    except ValueError:
        raise Http404()

    now = datetime.datetime.now() + datetime.timedelta(hours=offset)

    html = '<html><body>It is now %s. <html><body>' %now
    return HttpResponse(html)