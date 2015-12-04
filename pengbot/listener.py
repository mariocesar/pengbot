__all__ = ('listener',)


class Listener:
    name = None

    def __init__(self, callable, async=False):
        self.wrapped = callable

        self.__name__ = self.name = callable.__name__
        self.__doc__ = callable.__doc__
        self.__module__ = callable.__module__

    def __call__(self, *args, **kwargs):
        return self.run(*args, **kwargs)

    def run(self, *args, **kwargs):
        return self.wrapped(*args, **kwargs)


def listener(*args, **kwargs):
    # Support both ways of calling @listener, and not @listener()
    invoked = not args or kwargs

    if not invoked:
        func, args = args[0], ()

    def wrapper(func):
        return Listener(func, *args, **kwargs)

    return wrapper if invoked else wrapper(func)
