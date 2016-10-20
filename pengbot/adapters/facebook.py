import asyncio
import json
import re
from collections import namedtuple
from urllib.parse import parse_qs
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
        return True


class Message:
    def __call__(self, context, message):
        return all(['id' in message,
                    'time' in message,
                    'message' in message])


class Authentication:
    def __call__(self, context, message):
        return 'optin' in message


class DeliveryConfirmation:
    def __call__(self, context, message):
        return 'delivery' in message


class PostbackReceived:
    def __call__(self, context, message):
        return 'postback' in message


class MessageRead:
    def __call__(self, context, message):
        return 'read' in message


class AccountLink:
    def __call__(self, context, message):
        return 'account_linking' in message


class MessageEcho:
    def __call__(self, context, message):
        return ('is_echo' in context['message']) and (context['message'])


class PatternMatch(Message, BasePatternMatch):
    def __init__(self, pattern):
        self.pattern = re.compile(pattern)

    def __call__(self, context, message):
        is_message = super().__call__(context, message)
        return is_message and self.pattern.match(message['text']) is not None


WebURLButton = namedtuple('web_url', ['url', 'title', 'webview_height_ratio', 'messenger_extensions', 'fallback_url'])
PostbackButton = namedtuple('postback', ['payload', 'title'])
CallButton = namedtuple('phone_number', ['payload', 'title'])
ShareButton = namedtuple('element_share', [])


class TemplateBase:
    template_type = None
    _buttons = []

    @property
    def buttons(self):
        return self._buttons

    @buttons.setter
    def buttons(self, elements: list):
        self._buttons = elements

    def _asdict(self):
        payload = super()._asdict()
        payload['buttons'] = [dict(button) for button in self.buttons]
        return {
            'type': 'template',
            'payload': {
                'template_type': self.template_type,
                'elements': [payload]
            }
        }


class GenericTemplate(TemplateBase, namedtuple('GenericTemplate', ['title', 'item_url', 'image_url', 'subtitle'])):
    template_type = 'generic'

    def _asdict(self):
        payload = super()._asdict()
        payload['buttons'] = [dict(button) for button in self.buttons]
        return {
            'type': 'template',
            'payload': {
                'template_type': self.template_type,
                'elements': [payload]  # TODO, suppor up to 10 elements
            }
        }


class ButtonTemplate(TemplateBase, namedtuple('ButtonTemplate', ['text'])):
    template_type = 'button'

    def _asdict(self):
        payload = super()._asdict()
        payload['buttons'] = [dict(button) for button in self.buttons]
        payload['template_type'] = self.template_type,

        return {
            'type': 'template',
            'payload': payload
        }


class MainAdapter(BaseAdapter):
    def receive(self):
        httpd = make_server('', 3000, self.wsgi_application_handler)
        print("Serving on port 8000...")
        httpd.serve_forever()

    def wsgi_application_handler(self, environ, start_response):
        if environ['REQUEST_METHOD'] == 'POST':
            try:
                self.handle_payload(environ, start_response)
            except Exception as err:
                self.logger.exception(err)
                start_response('500 OK', [('Content-Type', 'text/plain')])
                return 'error'
            else:
                start_response('200 OK', [('Content-Type', 'text/plain')])
                return 'ok'
        elif environ['REQUEST_METHOD'] == 'GET':
            return self.handle_verify_token(environ, start_response)

        start_response('400 OK', [('Content-Type', 'text/plain')])
        return 'unknown'

    def handle_verify_token(self, environ, start_response):
        qs = parse_qs(environ['QUERY_STRING'])
        verify_token = qs.get('hub.verify_token', None)
        challenge = qs.get('hub.challenge', None)

        if verify_token:
            verify_token = verify_token.pop()

        if challenge:
            challenge = challenge.pop()

        if verify_token == self.context.verify_token:
            start_response('200 OK', [('Content-Type', 'text/plain')])
            return challenge
        else:
            return json.dumps({"errors": ["Invalid Token"]})

    def handle_payload(self, environ, start_response):
        request_body = environ['wsgi.input'].read()
        payload = json.loads(request_body)

        print('>>> payload', payload)

        assert 'object' in payload, 'Missing object type in payload: %r' % payload
        assert payload['object'] == 'page', 'Unknown object type: %r' % payload['object']

        for entry in payload['entries']:
            self.handle_message(entry)

    def handle_message(self, entry):
        assert 'id' in entry, 'Missing id in entry: %r' % entry
        assert 'time' in entry, 'Missing timestamp in entry: %r' % entry

        for handler_match, handler_callbacks in self.handlers.items():
            self.logger.debug('Resolving message handler %s %s', handler_match, handler_callbacks)
            self.logger.debug('Handler match is bound? %s', isbound(handler_match))

            if not isbound(handler_match):
                handler_match = handler_match()

            if handler_match(context=self.context, message=entry):
                for callback in handler_callbacks:
                    callback(self, entry)

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

    @asyncio.coroutine
    def send_image(self, recipient, image_url):
        self.send({
            'recipient': recipient,
            'message': {
                'attachment': {
                    'type': 'image',
                    'payload': {'url': image_url}
                }
            }
        })

    @asyncio.coroutine
    def send_audio(self, recipient, audio_url):
        self.send({
            'recipient': recipient,
            'message': {
                'attachment': {
                    'type': 'audio',
                    'payload': {'url': audio_url}
                }
            }
        })

    @asyncio.coroutine
    def send_video(self, recipient, video_url):
        self.send({
            'recipient': recipient,
            'message': {
                'attachment': {
                    'type': 'video',
                    'payload': {'url': video_url}
                }
            }
        })

    @asyncio.coroutine
    def send_file(self, recipient, file_url):
        self.send({
            'recipient': recipient,
            'message': {
                'attachment': {
                    'type': 'file',
                    'payload': {'url': file_url}
                }
            }
        })

    @asyncio.coroutine
    def send_template(self, recipient, template: GenericTemplate or ButtonTemplate):
        return self.send({
            'recipient': recipient,
            'message': {
                'type': 'template',
                'attachment': {'payload': dict(template)}
            }
        })
