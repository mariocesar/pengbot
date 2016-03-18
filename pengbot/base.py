import asyncio
import json
import logging
import sys
from collections import defaultdict
from functools import wraps

import websockets
from pip.utils import cached_property
from slacker import Slacker

from pengbot.utils import AttributeDict


class BotLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        return msg, kwargs


def getLogger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s [%(name)s] %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


logger = getLogger(__name__)


class Context(AttributeDict):
    """Context provides attribute-style access."""
    pass


class BaseBot:
    handlers = []
    running = False

    def __init__(self, name: str):
        self.name = name
        self.handlers = defaultdict(list)
        self.context = Context({'name': name})
        self.logger = logger

        BotLoggerAdapter(logger, {'context': self.context})

    def __call__(self, *args, **kwargs):
        return self.main_handler()

    def main_handler(self):
        # add cli options
        self.run()

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

    def dispatch(self, *args, **kwargs):
        raise NotImplementedError()

    def run(self):
        loop = asyncio.get_event_loop()
        logger.info('Starting %s', self.name)
        try:
            loop.run_until_complete(self.dispatch())
        except KeyboardInterrupt:
            logger.info('Closing')
            loop.close()
            sys.exit(0)
        except Exception as err:
            logger.exception('Error', exc_info=err)
            loop.close()
            sys.exit(0)

    # Directives

    def post_message(self, *args, **kwargs):
        raise NotImplementedError()

    @asyncio.coroutine
    def says(self, *args, **kwargs):
        if not self.running:
            return
        return self.post_message(*args, **kwargs)

    def hears(self, *matchs):
        def decorator(func):
            for match in matchs:
                self.logger.debug('Registering match %r for %s', match, func)

                @wraps(func)
                def callback(bot, *args, **kwargs):
                    self.logger.debug('%r: args=%r kwargs=%r', func.__name__, args, kwargs)
                    yield from func(bot, *args, **kwargs)

                self.handlers[match].append(callback)

        return decorator

    def ask(self, question):
        pass

    def command(self, name):
        pass


class SlackRobot(BaseBot):
    def __init__(self, name: str, api_token: str):
        super().__init__(name=name)
        self.api_token = api_token
        self.ws = None

    def dispatch(self):
        self._message_id = 0
        resp = self.slacker.rtm.start()

        self.context.update({
            'self': resp.body['self'],
            'team': resp.body['team'],
            'users': {user['id']: user for user in resp.body['users']},
            'channels': {channel['id']: channel for channel in resp.body['channels']},
            'groups': {group['id']: group for group in resp.body['groups']},
            'ims': {i['id']: i for i in resp.body['ims']},
            'bots': resp.body['bots'],
        })
        logger.info('Listening to slack')
        logger.debug(json.dumps(self.context, indent=2))
        return self.websocket_handler(resp.body['url'])

    @cached_property
    def slacker(self):
        return Slacker(self.api_token)

    @asyncio.coroutine
    def websocket_handler(self, url):
        self.ws = yield from websockets.connect(url)
        self.running = True

        while True:
            raw_message = yield from self.ws.recv()

            if not raw_message:
                break

            message = json.loads(raw_message)
            self.logger.debug('Received %s', message)

            for handler_match, handler_callbacks in self.handlers.items():
                if callable(handler_match):
                    handler_match = handler_match()

                if handler_match(context=self.context, data=message):
                    for callback in handler_callbacks:
                        task = asyncio.ensure_future(callback(self, message))
                        task.add_done_callback(self._done_callback)

    def post_message(self, text, channel: str = None):

        self._message_id += 1
        data = {'id': self._message_id,
                'type': 'message',
                'channel': channel,
                'text': text}

        logger.debug('robot says: %s', data)
        content = json.dumps(data)

        yield from self.ws.send(content)

    @asyncio.coroutine
    def ping(self):
        if not self.running:
            return

        self._message_id += 1
        data = {'tries': self._message_id, 'type': 'ping'}
        content = json.dumps(data)

        yield from self.ws.send(content)
