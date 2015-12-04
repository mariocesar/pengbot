import sys
import os
import logging
import logging.config
from collections import OrderedDict
from optparse import OptionParser
from .utils import abort, imported, now

__all__ = ('main',)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(name)s:%(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(asctime)s %(name)s:%(module)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        }
    },
    'loggers': {
        'pengbot': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'INFO',
        }
    }
}

logging.config.dictConfig(LOGGING)


def find_botfile(names):
    botfile_path = names.pop()

    if not (botfile_path or os.path.exists(botfile_path)):
        abort('Invalid or not existing botfile %s' % botfile_path)

    return os.path.abspath(botfile_path)


def load_features(path):
    from .command import Command
    from .listener import Listener

    with imported(path) as module:
        module_vars = vars(module)

        directives = OrderedDict()
        listeners = OrderedDict()

        docstring = module.__doc__

        for tup in module_vars.items():
            name, obj = tup

            if isinstance(obj, Command):
                directives[name] = obj

                if obj.aliases:
                    for alias in obj.aliases:
                        directives[alias] = directives[name]

            if isinstance(obj, Listener):
                listeners[name] = obj

    return docstring, directives, listeners, module


def main():
    from .api import env

    logger = logging.getLogger('pengbot')

    parser = OptionParser(usage=("%prog [options] path/to/botfile.py"), version="%prog 1.0")

    parser.add_option(
        '--loglevel', '-L',
        choices=['ERROR', 'WARNING', 'INFO', 'DEBUG'],
        dest='loglevel',
        default='INFO'
    )

    parser.add_option(
        '-n', '--name',
        dest='name',
        default='bot',
        help='name of the Bot'
    )

    parser.add_option(
        '--adapter',
        dest='adapter',
        default='shell',
        help='Bot adapter where to listen for commands, by default a interactive "shell" session'
    )

    options, arguments = parser.parse_args()
    arguments = parser.largs
    remainder_arguments = parser.rargs

    logger.setLevel(logging.getLevelName(options.loglevel))

    logger.debug('options: {}'.format(options))
    logger.debug('arguments: {}'.format(arguments))

    if len(arguments) != 1:
        parser.error("incorrect number of arguments")

    logger.debug('remainder_arguments: {}'.format(remainder_arguments))

    botfile = find_botfile(arguments)
    docstring, directives, listeners, module = load_features(botfile)

    env.module = module
    env.docstring = docstring
    env.bot_name = options.name
    env.options = options

    logger.debug('env: {}'.format(env))
    logger.debug('botfile module: {}'.format(module))
    logger.debug('directives found: {}'.format(', '.join(directives.keys())))
    logger.debug('listeners found: {}'.format(', '.join(listeners.keys())))

    adapters_path = os.path.dirname(os.path.abspath(__file__))
    adapters_path = os.path.join(adapters_path, 'adapters', '{}.py'.format(options.adapter))

    assert os.path.exists(adapters_path), 'Unknown adapter %s' % options.adapter

    with imported(adapters_path) as adapter_module:
        adapter = adapter_module.Adapter(env=env, directives=directives, listeners=listeners)

    try:
        env.bot_start_date = now()
        adapter.run()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        sys.stderr.write("\nStopped.\n")
    except:
        sys.excepthook(*sys.exc_info())
        # we might leave stale threads if we don't explicitly exit()
        sys.exit(1)
    finally:
        adapter.close()

    sys.exit(0)
