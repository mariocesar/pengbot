from functools import wraps

from webob import Request


def robot(adapterModule, **kwargs):
    def wrapper(func):
        assert hasattr(adapterModule, 'Adapter')
        bot = adapterModule.Adapter(func, **kwargs)
        return wraps(func)(bot)

    return wrapper
