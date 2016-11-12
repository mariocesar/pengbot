from functools import wraps

from webob import Request


def robot(adapterModule, **kwargs):
    def wrapper(func):
        assert hasattr(adapterModule, 'Adapter')
        bot = adapterModule.Adapter(func, **kwargs)
        return wraps(func)(bot)

    return wrapper


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
            self.logger.exception(err)
            start_response('400 OK', [('Content-Type', 'text/plain')])
            return '%r' % err
        except Exception as err:
            self.logger.exception(err)
            start_response('500 OK', [('Content-Type', 'text/plain')])
            return '%r' % err

        start_response('200 OK', [('Content-Type', 'text/plain')])
        if response is None:
            response = ''
        return response

    return inner
