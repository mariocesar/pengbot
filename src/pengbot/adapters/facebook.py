import json
from collections import namedtuple
from wsgiref.simple_server import make_server

import requests
from pengbot.adapters.base import BaseAdapter
from pengbot.decorators import wsgi_handler
from pengbot.utils import isbound


class Event:
    def __call__(self, context, message):
        return True


class Messages:
    def __call__(self, context, message):
        return all(['id' in message,
                    'time' in message,
                    'messaging' in message])


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


class Facebook:
    def __init__(self, adapter):
        self.adapter = adapter

    def setup_greeting_text(self, greeting_text):
        """
        Args:
            greeting_text:
                 {{user_first_name}}
                 {{user_last_name}}
                 {{user_full_name}}
        Returns:

        """
        return requests.post(
            "https://graph.facebook.com/v2.6/me/thread_settings",
            params={"access_token": self.adapter.context.access_token},
            headers={'Content-type': 'application/json'},
            data=json.dumps({"setting_type": "greeting",
                             "greeting": {"text": greeting_text}})
        )

    def setup_started_button(self):
        return requests.post(
            "https://graph.facebook.com/v2.6/me/thread_settings",
            params={"access_token": self.adapter.context.access_token},
            headers={'Content-type': 'application/json'},
            data=json.dumps({
                "setting_type": "call_to_actions",
                "thread_state": "new_thread",
                "call_to_actions": [{"payload": "NEW_THREAD"}]
            })
        )

    def setup_menu(self, elements: list):
        return requests.post(
            "https://graph.facebook.com/v2.6/me/thread_settings",
            params={"access_token": self.adapter.context.access_token},
            headers={'Content-type': 'application/json'},
            data=json.dumps({
                "setting_type": "call_to_actions",
                "thread_state": "existing_thread",
                "call_to_actions": elements
            })
        )

    def setup_whitelist(self, domain_urls):
        return requests.post(
            "https://graph.facebook.com/v2.6/me/thread_settings",
            params={"access_token": self.adapter.context.access_token},
            headers={'Content-type': 'application/json'},
            data=json.dumps({
                "setting_type": "domain_whitelisting",
                "whitelisted_domains": domain_urls,
                "domain_action_type": "add"
            })
        )

    def send_message(self, data):
        return requests.post(
            "https://graph.facebook.com/v2.6/me/messages",
            params={"access_token": self.adapter.context.access_token},
            headers={'Content-type': 'application/json'},
            data=json.dumps(data)
        )

    def send_attachment(self, recipient, attachment_url):
        attachment_types = {
            'image': ['.jpeg', '.jpg', '.gif', '.png'],
            'audio': ['.mp3', '.ogg', '.wav'],
            'video': ['.avi', '.mp4', '.mpeg', '.3gp', '.mpg', '.webm']
        }

        matching = [[ctype, any(map(lambda ext: attachment_url.endswith(ext), exts))] for ctype, exts in
                    attachment_types.items()]
        attachment_type = 'file'

        for ctype, is_match in matching:
            if is_match:
                attachment_type = ctype
                break

        self.send_message({
            'recipient': recipient,
            'message': {
                'attachment': {
                    'type': attachment_type,
                    'payload': {'url': attachment_url}
                }
            }
        })

    def send_template(self, recipient, template: GenericTemplate or ButtonTemplate):
        return self.send_message({
            'recipient': recipient,
            'message': {
                'type': 'template',
                'attachment': {'payload': dict(template)}
            }
        })

    def get_user_profile(self, user_id):
        return requests.get(
            "https://graph.facebook.com/v2.6/%s" % user_id,
            params={"access_token": self.adapter.context.access_token,
                    "fields": "first_name,last_name,profile_pic,locale,timezone,gender"},
            headers={'Content-type': 'application/json'})


class MainAdapter(BaseAdapter):
    def __setup__(self):
        self.facebook = Facebook(self)

    def receive(self):
        httpd = make_server('', 3000, self.wsgi_application)
        print("Serving on port 8000...")
        httpd.serve_forever()

    def wsgi_application(self, environ, start_response):
        if environ['REQUEST_METHOD'] == 'GET':
            return self.handle_verify_token(environ, start_response)
        elif environ['REQUEST_METHOD'] == 'POST':
            return self.handle_payload(environ, start_response)

        start_response('404 OK', [('Content-Type', 'text/plain')])
        return ''

    @wsgi_handler
    def handle_verify_token(self, request):
        verify_token = request.GET.get('hub.verify_token', None)
        challenge = request.GET.get('hub.challenge', None)

        if verify_token == self.context.verify_token:
            return challenge
        else:
            return json.dumps({"errors": ["Invalid Token"]})

    @wsgi_handler
    def handle_payload(self, request):
        payload = json.loads(request.body.decode())

        assert 'object' in payload, 'Missing object type in payload: %r' % payload
        assert payload['object'] == 'page', 'Unknown object type: %r' % payload['object']
        assert 'entry' in payload, 'Missing entry'

        for entry in payload['entry']:
            self.handle_message(entry)

    def handle_message(self, entry):
        assert 'id' in entry, 'Missing id in entry: %r' % entry
        assert 'time' in entry, 'Missing timestamp in entry: %r' % entry

        self.logger.debug('Message received: %s' % entry)

        for handler_match, handler_callbacks in self.handlers.items():
            self.logger.debug('Resolving message handler %s %s', handler_match, handler_callbacks)

            if not isbound(handler_match):
                handler_match = handler_match()

            if handler_match(context=self.context, message=entry):
                self.logger.debug('Handler match: %s' % handler_match)

                for callback in handler_callbacks:
                    callback(entry)

    def says(self, recipient, text):
        response = self.facebook.send_message({'recipient': {'id': recipient}, 'message': {'text': text}})
        self.logger.debug(response.content)
