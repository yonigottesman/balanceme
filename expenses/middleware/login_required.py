from django.http import HttpResponseRedirect
from django.conf import settings
from re import compile

LOGIN_EXEMPT_URLS = (r'^accounts/',)

EXEMPT_URLS = [compile(settings.LOGIN_URL.lstrip('/'))]
EXEMPT_URLS += [compile(expr) for expr in LOGIN_EXEMPT_URLS]


class LoginRequiredMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print(compile(settings.LOGIN_URL.lstrip('/')))
        if not request.user.is_authenticated:
            path = request.path_info.lstrip('/')
            if not any(m.match(path) for m in EXEMPT_URLS):
                return HttpResponseRedirect(settings.LOGIN_URL)
        return self.get_response(request)

