import json
import logging
import re

from collections import namedtuple

import pengbot
from pengbot.adapters import web

task = namedtuple('task', ['name', 'completed'])
tasks = []

cmdregexp = re.compile(r'^/(?P<name>\w+)?\s*(?P<args>[a-z-_ ]*)')


@pengbot.robot(web)
def jake():
    pengbot.logger.setLevel(logging.DEBUG)
    pengbot.logger.info('Hi')


def whink():
    return jake.say(';)')


@jake.signal()
def text_received(message):
    print('text received', message)
    return message


@jake.signal()
def command_received(message):
    print('command received', message)
    match = cmdregexp.match(message['message']['text'])
    groups = match.groupdict()
    name = groups['name']
    args = groups['args']

    return message, name, args


@jake.signal()
def message_received(message):
    if 'text' in message['message']:
        if cmdregexp.match(message['message']['text']):
            return command_received(message)
        else:
            return text_received(message)


@jake.listen()
def receive_request(request):
    is_json_post_request = all([
        request.method == 'POST',
        request.content_type == 'application/json'])

    is_json_post_request = True

    if is_json_post_request:
        payload = request.body.decode()
        data = json.loads(payload)

        assert 'sender_id' in data
        assert 'recipient_id' in data

        if 'message' in data:
            print('message received', data)
            return message_received(data)


def receive_greeting(message):
    jake.say('Hello!')
    whink()


def receive_goodbye(message):
    jake.say('Bye!')
    whink()


@jake.listen(text_received)
def receive_text(message):
    print('receive text', message)

    if message['message']['text'] == 'hi':
        receive_greeting(message)
    elif message['message']['text'] == 'bye':
        receive_goodbye(message)


def command_list_received(message):
    for i, task in enumerate(tasks, 1):
        msg = '{} {}'.format('✔' if task.completed else ' ', task.name)
        jake.say('{}: {}'.format(i, msg)).readed(whink)


def command_create_received(message, *args):
    tasks.append(task(completed=False, name=' '.join(args)))
    jake.say('I added: {}'.format(task.name))


def command_remove_received(message, *args):
    for arg in args:
        del tasks[arg]

        jake.say('Removed: {}'.format(task.name))


def command_complete_received(message, *args):
    for arg in args:
        del tasks[arg]
        tasks[arg].completed = True
        jake.say('✔ {}'.format(task.name))


@jake.listen(command_received)
def receive_command(message, name, args):
    print('receive command', message, name, args)

    if name == 'list':
        command_list_received(message)
    elif name == 'create':
        command_create_received(message, args)
    elif name == 'remove':
        command_remove_received(message, args)
    elif name == 'complete':
        command_complete_received(message, args)


if __name__ == '__main__':
    jake()
