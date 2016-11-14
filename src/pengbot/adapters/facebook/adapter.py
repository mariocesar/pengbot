import json

from pengbot.utils import isbound

from .api import Facebook
from ..web import WebAdapter


class Adapter(WebAdapter):
    _fbapi = None

    @property
    def fbapi(self):
        if not self._fbapi:
            self._fbapi = Facebook(self)
        return self._fbapi

    @WebAdapter.route('GET', r'/')
    def handle_verify_token(self, start_response, request):

        verify_token = request.GET.get('hub.verify_token', None)
        challenge = request.GET.get('hub.challenge', None)

        if verify_token == self.context.verify_token:
            start_response('200 OK', [('Content-Type', 'text/plain')])
            return challenge
        else:
            start_response('401 OK', [('Content-Type', 'text/plain')])
            return "Invalid Token"

    @WebAdapter.route('POST', r'/')
    def handle_payload(self, start_response, request):
        payload = json.loads(request.body.decode())

        assert 'object' in payload, 'Missing object type in payload: %r' % payload
        assert payload['object'] == 'page', 'Unknown object type: %r' % payload['object']
        assert 'entry' in payload, 'Missing entry'

        for entry in payload['entry']:
            try:
                assert 'id' in entry, 'Missing id in entry: %r' % entry
                assert 'time' in entry, 'Missing timestamp in entry: %r' % entry

                self.handle_message(entry)
            except Exception as err:
                start_response('500 OK', [('Content-Type', 'text/plain')])
                return '%r' % err
            else:
                start_response('200 OK', [('Content-Type', 'text/plain')])
                return ''

    def say(self, recipient, text):
        response = self.fbapi.send_message({
            'recipient': {'id': recipient},
            'message': {'text': text}}
        )

        self.logger.debug(response.content)
