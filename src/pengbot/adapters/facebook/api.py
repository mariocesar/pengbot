import json

import requests
from pengbot.adapters.facebook.templates import GenericTemplate, ButtonTemplate


class Facebook:
    def __init__(self, adapter):
        self.adapter = adapter

    def setup_greeting_text(self, greeting_text):
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
