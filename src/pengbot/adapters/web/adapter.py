import asyncio
import json
import pprint
import re
from functools import wraps
from wsgiref.simple_server import make_server
from pengbot.adapters.base import BaseAdapter
from webob import Request, Response


def wsgi_handler(func):
    """
    Set a instance method to be call as a wsgi application, adding common
    behavior and using webob.Request for practical use.


    @wsgi_handler
    def handle_verify_token(self, request):
        pass

    :param func:
    :return:
    """

    @wraps(func)
    def inner(*args):
        self, environ, start_response, *args = args
        request = Request(environ)

        try:
            response = func(self, request)
        except AssertionError as err:
            response = Response(body=repr(err), status=500)
            return response(environ, start_response)
        else:
            return response(environ, start_response)

    return inner


class WebHandlerMatch:
    def __repr__(self):
        return '%s %s %s' % (self.method, self.pattern, self.handler)

    def __init__(self, method, pattern, handler):
        self.method = method
        if isinstance(pattern, str):
            self.pattern = re.compile(pattern)
        else:
            self.pattern = pattern
        self.handler = handler

    def match(self, environ):
        request = Request(environ)

        if request.method == self.method.upper():
            if self.pattern.match(request.path):
                return True
        return False

    def __call__(self, *args, **kwargs):
        return self.handler(*args, **kwargs)


class WebAdapter(BaseAdapter):
    _webhandlers = None

    def receive(self):
        for handler in self.web_handlers:
            print(handler)

        httpd = make_server('', 3000, self.wsgi_application)
        print("Serving on port 3000...")
        httpd.serve_forever()

    @property
    def web_handlers(self):
        if self._webhandlers is None:
            self._webhandlers = []

            for attr in dir(self):
                obj = getattr(self, attr)
                if isinstance(obj, WebHandlerMatch):
                    self._webhandlers.append(obj)

        return self._webhandlers

    @wsgi_handler
    def not_found_handler(self, request):
        return Response('Not found', 404)

    @wsgi_handler
    def internal_error_handler(self, request, err=None):
        return Response('Internal Error %s' % err, 500)

    def wsgi_application(self, environ, start_response):
        for handler in self.web_handlers:
            if handler.match(environ):
                return handler(self, environ, start_response)
        else:
            return self.not_found_handler(environ, start_response)

    @classmethod
    def route(cls, method, pattern):
        def decorator(func):
            @wraps(func)
            @wsgi_handler
            def inner(*args, **kwargs):
                return func(*args, **kwargs)

            return WebHandlerMatch(method, pattern, inner)

        return decorator

    def say(self, message):
        print(message)

class Adapter(WebAdapter):
    @WebAdapter.route('POST', r'^/$')
    def handle_payload(self, request):
        self.handle_message(request)
        return Response('Ok', 200)

    @WebAdapter.route('GET', r'^/$')
    def handle_landing(self, request):
        body = 'Hello!\nhandlers = %s' % pprint.pformat(self.handlers, indent=4)
        return Response(body, 200, content_type='text/plain')

