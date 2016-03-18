import asyncio
import json
import re

import websockets
from pip.utils import cached_property
from slacker import Slacker

from pengbot.adapters.base import BaseAdapter
from pengbot.matchers import PatternMatch as BasePatternMatch
from pengbot.utils import isbound

EVENTS = {
    "hello": "The client has successfully connected to the server",
    "message": "A message was sent to a channel",
    "user_typing": "A channel member is typing a message",
    "channel_marked": "Your channel read marker was updated",
    "channel_created": "A team channel was created",
    "channel_joined": "You joined a channel",
    "channel_left": "You left a channel",
    "channel_deleted": "A team channel was deleted",
    "channel_rename": "A team channel was renamed",
    "channel_archive": "A team channel was archived",
    "channel_unarchive": "A team channel was unarchived",
    "channel_history_changed": "Bulk updates were made to a channel's history",
    "dnd_updated": "Do not Disturb settings changed for the current user",
    "dnd_updated_user": "Do not Disturb settings changed for a team member",
    "im_created": "A direct message channel was created",
    "im_open": "You opened a direct message channel",
    "im_close": "You closed a direct message channel",
    "im_marked": "A direct message read marker was updated",
    "im_history_changed": "Bulk updates were made to a DM channel's history",
    "group_joined": "You joined a private group",
    "group_left": "You left a private group",
    "group_open": "You opened a group channel",
    "group_close": "You closed a group channel",
    "group_archive": "A private group was archived",
    "group_unarchive": "A private group was unarchived",
    "group_rename": "A private group was renamed",
    "group_marked": "A private group read marker was updated",
    "group_history_changed": "Bulk updates were made to a group's history",
    "file_created": "A file was created",
    "file_shared": "A file was shared",
    "file_unshared": "A file was unshared",
    "file_public": "A file was made public",
    "file_private": "A file was made private",
    "file_change": "A file was changed",
    "file_deleted": "A file was deleted",
    "file_comment_added": "A file comment was added",
    "file_comment_edited": "A file comment was edited",
    "file_comment_deleted": "A file comment was deleted",
    "pin_added": "A pin was added to a channel",
    "pin_removed": "A pin was removed from a channel",
    "presence_change": "A team member's presence changed",
    "manual_presence_change": "You manually updated your presence",
    "pref_change": "You have updated your preferences",
    "user_change": "A team member's data has changed",
    "team_join": "A new team member has joined",
    "star_added": "A team member has starred an item",
    "star_removed": "A team member removed a star",
    "reaction_added": "A team member has added an emoji reaction to an item",
    "reaction_removed": "A team member removed an emoji reaction",
    "emoji_changed": "A team custom emoji has been added or changed",
    "commands_changed": "A team slash command has been added or changed",
    "team_plan_change": "The team billing plan has changed",
    "team_pref_change": "A team preference has been updated",
    "team_rename": "The team name has changed",
    "team_domain_change": "The team domain has changed",
    "email_domain_changed": "The team email domain has changed",
    "team_profile_change": "Team profile fields have been updated",
    "team_profile_delete": "Team profile fields have been deleted",
    "team_profile_reorder": "Team profile fields have been reordered",
    "bot_added": "An integration bot was added",
    "bot_changed": "An integration bot was changed",
    "accounts_changed": "The list of accounts a user is signed into has changed",
    "team_migration_started": "The team is being migrated between servers",
    "reconnect_url": "Experimental",
    "subteam_created": "A user group has been added to the team",
    "subteam_updated": "An existing user group has been updated or its members changed",
    "subteam_self_added": "You have been added to a user group",
    "subteam_self_removed": "You have been removed from a user group",
}


class Event:
    def __init__(self, code):
        assert code in EVENTS, '%s is an unknown event' % code
        self.code = code

    def __call__(self, context, message):
        if 'type' in message:
            return message[self.code] == self.code


class Message:
    def __call__(self, context, message):
        if message.get('type', None) == 'message' and 'reply_to' not in message:
            # Dimiss messages from lost connections
            return True
        return False


class DirectMessage(Message):
    def __call__(self, context, message):
        if super().__call__(context, message):
            return message['channel'] in context['ims']


class Mention(Message):
    def __call__(self, context, message):
        if super().__call__(context, message):
            if 'text' in message:
                return '<@%s>' % context['self']['id'] in message['text']


class PatternMatch(Message, BasePatternMatch):
    def __init__(self, pattern):
        self.pattern = re.compile(pattern)

    def __call__(self, context, message):
        is_message = super().__call__(context, message)
        return is_message and self.pattern.match(message['text']) is not None


class SlackRobot(BaseAdapter):
    def receive(self):
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
        self.logger.info('Listening to slack')
        self.logger.debug(json.dumps(self.context, indent=2))
        return self.websocket_handler(resp.body['url'])

    @cached_property
    def slacker(self):
        return Slacker(self.context.api_token)

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
                self.logger.debug('Resolving message handler %s %s', handler_match, handler_callbacks)
                self.logger.debug('Handler match is bound? %s', isbound(handler_match))

                if not isbound(handler_match):
                    handler_match = handler_match()

                if handler_match(context=self.context, message=message):
                    for callback in handler_callbacks:
                        task = asyncio.ensure_future(callback(self, message))
                        task.add_done_callback(self._done_callback)

    @asyncio.coroutine
    def send(self, message):
        content = json.dumps(message)

        yield from self.ws.send(content)

    @asyncio.coroutine
    def ping(self):
        if not self.running:
            return

        self._message_id += 1
        data = {'tries': self._message_id, 'type': 'ping'}
        content = json.dumps(data)

        yield from self.ws.send(content)

    @asyncio.coroutine
    def says(self, text, channel):
        self._message_id += 1
        data = {
            'id': self._message_id,
            'type': 'message',
            'channel': channel,
            'text': text
        }

        yield from self.send(data)
