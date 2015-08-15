
__all__ = ('command',)

class Command:
    name = None
    aliases = None

    def __init__(self, callable, alias=None):
        
        if alias:
            assert isinstance(alias, (list, tuple, str)), 'Alias must be string or list'

        if isinstance(alias, str):
            self.aliases = [alias]
        elif isinstance(alias, (list, tuple)):
            self.aliases = alias

        self.wrapped = callable

        self.__name__ = self.name = callable.__name__
        self.__doc__ = callable.__doc__
        self.__module__ = callable.__module__

    def __call__(self, *args, **kwargs):
        return self.run(*args, **kwargs)

    def run(self, *args, **kwargs):
        return self.wrapped(*args, **kwargs)


def command(*args, **kwargs):
    # Support both ways of calling @command, and not @command()
    invoked = not args or kwargs

    if not invoked:
        func, args = args[0], ()

    def wrapper(func):
        return Command(func, *args, **kwargs)

    return wrapper if invoked else wrapper(func)