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

    def handle_message(self, payload):
        for handler in self.handlers:
            if not isbound(handler):
                handler = handler()

            handler(payload)

    def receive(self, *args, **kwargs):
        raise NotImplementedError()

    def send(self, message):
        raise NotImplementedError()

    def say(self, *args, **kwargs):
        raise NotImplementedError()

    # Directives

    def signal(self):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                signal_setup, signal_args = False, None
                print('func=', func)

                hit = False

                for listener in self.signals.get(func.__qualname__, []):
                    hit = True
                    print('listener=', listener)
                    if not signal_setup:
                        signal_args = func(*args, **kwargs) or []

                    if isinstance(signal_args, tuple):
                        listener(*signal_args)
                    else:
                        listener(signal_args)

                if not hit:
                    print('no attached', func)
                    func(*args, **kwargs)

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
