import asyncio
import json
import re
from wsgiref.simple_server import make_server

import requests
from pengbot.adapters.base import BaseAdapter
from pengbot.matchers import PatternMatch as BasePatternMatch
from pengbot.utils import isbound

EVENTS = {
    "message": "A message has been sent to your page",
    "postback": "Postbacks occur when a Postback button, "
                "Get Started button, Persistent menu or Structured Message is tapped.",
    "optin": "This callback will occur when the Send-to-Messenger plugin has been tapped",
    "account_linking": "This callback will occur when the Linked Account or Unlink Account "
                       "call-to-action have been tapped.",
    "delivery": "This callback will occur when a message a page has sent has been delivered.",
    "read": "This callback will occur when a message a page has sent has been read by the user.",
}


class Event:
    def __call__(self, context, message):
        try:
            assert message['object'] == 'page'
        except (KeyError, TypeError) as err:
            print(err)
        except AssertionError as err:
            return False
        else:
            return True
        return False


class Message(Event):
    def __call__(self, context, message):
        is_event = super(Message, self).__call__(context, message)
        return is_event and 'message' in message


class MessageReceived(Event):
    def __call__(self, context, message):
        is_event = super(MessageReceived, self).__call__(context, message)
        return is_event and 'postback' in message


class MessageThroughParam(Event):
    def __call__(self, context, message):
        is_event = super(MessageThroughParam, self).__call__(context, message)
        return is_event and 'optin' in message


class MessageRead(Event):
    def __call__(self, context, message):
        is_event = super(MessageRead, self).__call__(context, message)
        return is_event and 'optin' in message


class MessageEcho(Event):
    def __call__(self, context, message):
        is_event = super(MessageEcho, self).__call__(context, message)
        return is_event and ('is_echo' in context['message']) and (context['message'])


class PatternMatch(Message, BasePatternMatch):
    def __init__(self, pattern):
        self.pattern = re.compile(pattern)

    def __call__(self, context, message):
        is_message = super().__call__(context, message)
        return is_message and self.pattern.match(message['text']) is not None


class MainAdapter(BaseAdapter):
    def receive(self):
        self.runserver()

    def wsgi_application_handler(self, environ, start_response):
        try:
            request_body = environ['wsgi.input'].read()
            message = json.loads(request_body)
            self.handle_message(message)
        except Exception as err:
            self.logger.exception(err)
            start_response('500 OK', [('Content-Type', 'text/html')])
            return 'error'
        else:
            start_response('200 OK', [('Content-Type', 'text/html')])
            return 'ok'

    def runserver(self):
        httpd = make_server('', 3000, self.wsgi_application_handler)
        print("Serving on port 8000...")
        httpd.serve_forever()

    def handle_message(self, message):
        for handler_match, handler_callbacks in self.handlers.items():
            self.logger.debug('Resolving message handler %s %s', handler_match, handler_callbacks)
            self.logger.debug('Handler match is bound? %s', isbound(handler_match))

            if not isbound(handler_match):
                handler_match = handler_match()

            if handler_match(context=self.context, message=message):
                for callback in handler_callbacks:
                    callback(self, message)

    @asyncio.coroutine
    def send(self, message):
        response = requests.post("https://graph.facebook.com/v2.6/me/messages",
                                 params={"access_token": self.context.access_token},
                                 data=json.dumps(message),
                                 headers={'Content-type': 'application/json'})
        return response.content

    @asyncio.coroutine
    def says(self, recipient, text):
        self.send({'recipient': recipient, 'text': text})
