import asyncio
from collections import defaultdict
from functools import wraps

from pengbot import logger
from pengbot.context import Context
from pengbot.utils import isbound


class UnknownCommand(Exception):
    pass


class BaseAdapter:
    handlers = []
    signals = {}
    running = False
    name = None
    loop = None

    def __init__(self, setup_method, **kwargs):
        self.context = Context()
        self.setup_method = setup_method

    def __call__(self, *args, **kwargs):
        try:
            self.run()
        except KeyboardInterrupt:
            exit(0)

    @property
    def name(self):
        return self.context.get('name', None) or self.setup_method.__name__

    def run(self):
        self.setup_method()
        self.receive()

    async def handle_message(self, payload):
        for handler in self.handlers:
            coroutine = handler(payload)
            print('handler=', handler)
            print('create_task=', coroutine)
            task = self.emit(coroutine)
            print('task=', task)
            print()

    def emit(self, coroutine):
        print('emit=', coroutine)
        self.loop.create_task(coroutine)

    def receive(self, *args, **kwargs):
        raise NotImplementedError()

    def send(self, message):
        raise NotImplementedError()

    def say(self, *args, **kwargs):
        raise NotImplementedError()

    # Directives

    def signal(self):
        adapter = self

        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                print('func=', func)
                result = await func(*args, **kwargs)

                for listener in adapter.signals.get(func.__qualname__, []):
                    print('listener=', listener)

                    if isinstance(result, tuple):
                        adapter.emit(listener(*result))
                    else:
                        adapter.emit(listener(result))

                return result

            return wrapper

        return decorator

    def listen(self, signal=None):
        def decorator(func):

            @wraps(func)
            def callback(*args, **kwargs):
                return func(*args, **kwargs)

            if not signal:
                self.handlers.append(callback)
            else:
                if signal in self.signals:
                    self.signals[signal.__qualname__].append(callback)
                else:
                    self.signals[signal.__qualname__] = [callback]

        return decorator


class SocketAdapter(BaseAdapter):
    pass


class ProcessAdapter(BaseAdapter):
    pass
