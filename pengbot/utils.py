import importlib
import json
import logging
import os
import sys
from contextlib import contextmanager
from datetime import datetime
from datetime import timedelta, tzinfo
from types import ModuleType

try:
    import pytz
except ImportError:
    pytz = None

__all__ = ('AttributeDict', 'abort', 'imported', 'utc', 'now')


class ObjectEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (list, dict, str, int, float, bool, type(None))):
            return json.JSONEncoder.default(self, obj)
        elif isinstance(obj, ModuleType):
            return obj.__file__


class AttributeDict(dict):
    """
    Dictionary subclass enabling attribute lookup/assignment of keys/values.

    For example::

        >>> m = AttributeDict({'foo': 'bar'})
        >>> m.foo
        'bar'
        >>> m.foo = 'not bar'
        >>> m['foo']
        'not bar'
    """

    def __getattr__(self, key):
        try:
            # Throws exception if not in prototype chain
            return object.__getattribute__(self, key)
        except AttributeError:
            try:
                return self[key]
            except KeyError:
                raise AttributeError

    def __setattr__(self, key, value):
        self[key] = value
        try:
            object.__getattribute__(self, key)
        except AttributeError:
            try:
                self[key] = value
            except:
                raise AttributeError(key)
        else:
            object.__setattr__(self, key, value)

    def __delattr__(self, key):
        try:
            object.__getattribute__(self, key)
        except AttributeError:
            try:
                del self[key]
            except KeyError:
                raise AttributeError(key)
        else:
            object.__delattr__(self, key)

    def __repr__(self):
        return 'Context(%s)' % self.__json__()

    def __str__(self):
        return self.__json__(indent=2)

    def __call__(self, **kwargs):
        print(kwargs)
        new = self.__class__(self.items())
        new.update(**kwargs)
        return new

    def __json__(self, indent=None):
        return json.dumps(self, indent=indent,
                          sort_keys=True, separators=(',', ': '),
                          cls=ObjectEncoder)

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.context.pop()


def abort(message):
    import sys
    sys.stderr.write('%s\n' % message)
    exit(1)


@contextmanager
def imported(path):
    logger = logging.getLogger('pengbot')

    directory, filename = os.path.split(path)
    logger.debug('importing: %s', path)

    _added = False

    if directory not in sys.path:
        sys.path.insert(0, directory)
        _added = True

    try:
        # import_module(path/to/filename.py) -> import_module(filename)
        imported = importlib.import_module(os.path.splitext(filename)[0])
        yield imported
    finally:
        if _added:
            del sys.path[0]


color_codes = {
    'fg': {
        'black': '30',
        'red': '31',
        'green': '32',
        'yellow': '33',
        'blue': '34',
        'purple': '35',
        'magenta': '36',
        'bright gray': '37',

        'dark gray': '1;30',
        'bright red': '1;31',
        'bright green': '1;32',
        'bright yellow': '1;33',
        'bright blue': '1;34',
        'bright magenta': '1;35',
        'bright cyan': '1;36',
        'white': '1;37',
    },
    'bg': {
        'background black': '40',
        'background red': '41',
        'background green': '42',
        'background yellow': '43',
        'background blue': '44',
        'background magenta': '45',
        'background cyan': '46',
        'background white': '47',
    },
    'attr': {
        'normal': '00',
        'bold': '01',
        'underscore': '04',
        'blink': '05',
        'reverse': '06',
        'concealed': '08',
    }
}


@contextmanager
def colorize(bg=None, fg=None, attr=None, stream=None):
    """Colorize stdout"""
    stdout = stream or sys.stdout
    ansi_codes = []

    if attr:
        ansi_codes.append(color_codes['attr'][attr])
    if fg:
        ansi_codes.append(color_codes['fg'][fg])
    if bg:
        ansi_codes.append(color_codes['bg'][bg])
    stdout.write("\033[%sm" % ';'.join(ansi_codes))

    yield

    stdout.write("\033[0m")


ZERO = timedelta(0)


class UTC(tzinfo):
    """
    UTC implementation taken from Python's docs.
    Used only when pytz isn't available.
    """

    def __repr__(self):
        return "<UTC>"

    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return ZERO


utc = UTC()


def now():
    return datetime.utcnow().replace(tzinfo=utc)


def isbound(obj):
    if callable(obj):
        return hasattr(obj.__call__, '__self__')
    return False


class BotLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        return msg, kwargs
