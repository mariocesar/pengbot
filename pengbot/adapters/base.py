import asyncio
from collections import defaultdict
from functools import wraps

from pengbot import logger
from pengbot.context import Context
from pengbot.utils import BotLoggerAdapter


class UnknownCommand(Exception):
    pass


class BaseAdapter:
    handlers = []
    running = False

    def __init__(self):
        self.handlers = defaultdict(list)
        self.context = Context()
        self.logger = logger

        BotLoggerAdapter(logger, {'context': self.context})

    def __call__(self, *args, **kwargs):
        return self.cli_handler()

    @property
    def name(self):
        if self.context.get('name', None):
            return self.context['name']
        return self.__name__

    def cli_handler(self):
        # add cli options
        try:
            self.run()
        except KeyboardInterrupt:
            exit(0)

    def before_reply(self, message):
        logger.debug('before_reply: %r', message)

    def after_reply(self, message):
        logger.debug('after_reply: %r', message)

    def _done_callback(self, future):
        exc_info = future.exception()

        if exc_info:
            # handle exception
            logger.exception('Exception for %r', future, exc_info=exc_info)
        else:
            logger.debug('Done callback for %r', future)

    def receive(self, *args, **kwargs):
        raise NotImplementedError()

    def send(self, message):
        raise NotImplementedError()

    def says(self, *args, **kwargs):
        raise NotImplementedError()

    def run(self):
        loop = asyncio.get_event_loop()
        logger.info('Starting %s', self.name)
        try:
            loop.run_until_complete(self.receive())
        except KeyboardInterrupt:
            logger.info('Closing')
            loop.close()
            raise
        except Exception as err:
            logger.exception('Error', exc_info=err)
            loop.close()
            raise

    # Directives

    def hears(self, *matchs):
        def decorator(func):
            for match in matchs:
                self.logger.debug('Registering match %r for %s', match, func)

                @wraps(func)
                @asyncio.coroutine
                def callback(bot, *args, **kwargs):
                    self.logger.debug('%r: args=%r kwargs=%r', func.__name__, args, kwargs)

                    func(bot, *args, **kwargs)

                self.handlers[match].append(callback)

        return decorator

    def ask(self, question):
        def decorator(func):
            return asyncio.coroutine(func)

        return decorator

    def command(self, name):
        def decorator(func):
            return asyncio.coroutine(func)

        return decorator
