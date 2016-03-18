from datetime import datetime

events = {
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


class SlackEvent:
    _type = None

    def __init__(self, data):
        self.data = data

    def __hash__(self):
        return hash(self.data['type'])


class User:
    @classmethod
    def build(cls, user_id):
        pass


class Channel:
    @classmethod
    def build(cls, channel_id):
        pass


class MessageEdit:
    def __init__(self, data):
        self.user = User.build(data['user'])
        self.timestamp = datetime.fromtimestamp(float(data['ts']))


class Anything(SlackEvent):
    def __eq__(self, other):
        return True


class Message(SlackEvent):
    """A message was sent to a channel."""
    _type = 'message'

    def __init__(self, data):
        super(Message, self).__init__(data)
        self.channel = Channel.build(data['channel'])
        self.user = User.build(data['user'])
        self.text = data['text']
        self.timestamp = datetime.fromtimestamp(float(data['ts']))
        self.edited = None

        if 'edited' in data:
            self.edited = MessageEdit(data['edited'])

        self.subtype = None
        if 'subtype' in data:
            self.subtype = data['subtype']
