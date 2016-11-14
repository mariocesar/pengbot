from .adapter import Adapter


class MessageReceived:
    def __call__(self, context, payload):
        if 'messaging' in payload:
            return True
