import os
import sys
import json
import importlib
import logging

from contextlib import contextmanager
from types import ModuleType


__all__ = ('AttributeDict', 'abort', 'imported')


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
            return self[key]
        except KeyError:
            # to conform with __getattr__ spec
            raise AttributeError(key)

    def __setattr__(self, key, value):
        self[key] = value

    def __str__(self):
        return self._to_pretty_json()

    def _to_pretty_json(self):
        return json.dumps(self, indent=2,
            sort_keys=True, separators=(',', ': '),
            cls=ObjectEncoder)


def abort(message):
    import sys
    sys.stderr.write('%s\n' % message)
    exit(1)


@contextmanager
def imported(path):

    logger = logging.getLogger('pengbot')

    directory, filename = os.path.split(path)
    logger.debug('importing: %s', path)
    
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


codeCodes = {
    'black':     '0;30', 'bright gray':    '0;37',
    'blue':      '0;34', 'white':          '1;37',
    'green':     '0;32', 'bright blue':    '1;34',
    'cyan':      '0;36', 'bright green':   '1;32',
    'red':       '0;31', 'bright cyan':    '1;36',
    'purple':    '0;35', 'bright red':     '1;31',
    'yellow':    '0;33', 'bright purple':  '1;35',
    'dark gray': '1;30', 'bright yellow':  '1;33',
    'normal':    '0'
}

@contextmanager
def colorizer(color, out=None):
    """Colorize stdout"""
    stdout = out or sys.stdout

    assert color in codeCodes, 'Unknown color %s' % color

    stdout.write("\033[")
    stdout.write(codeCodes[color])
    stdout.write("m")

    yield

    stdout.write("\033[0m")
