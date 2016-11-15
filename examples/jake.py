import asyncio
import json
import logging
import re

from collections import namedtuple

import pengbot
import requests
from pengbot.adapters import web

task = namedtuple('task', ['name', 'completed'])
tasks = []

cmdregexp = re.compile(r'^/(?P<name>\w+)?\s*(?P<args>[a-z-_ ]*)')


@pengbot.robot(web)
def jake():
    pengbot.logger.setLevel(logging.DEBUG)
    pengbot.logger.info('Hi')


def say(recipient, text):
    requests.post('http://127.0.0.1:1500/', json={
        "sender_id": "1",
        "recipient_id": recipient,
        "message": {
            "text": text
        }})


def whink(recipient):
    say(recipient, '; )')


@jake.signal()
async def text_received(message):
    print('text received', message)
    return message


@jake.signal()
async def command_received(message):
    print('command received', message)
    match = cmdregexp.match(message['message']['text'])
    groups = match.groupdict()
    name = groups['name']
    args = groups['args']

    return message, name, args


@jake.signal()
async def message_received(message):
    # if 'text' in message['message']:
    #     if cmdregexp.match(message['message']['text']):
    #         jake.emit(command_received(message))
    #     else:
    #         jake.emit(text_received(message))
    await asyncio.sleep(0)


@jake.listen()
async def receive_request(request):
    is_json_post_request = all([
        request.method == 'POST',
        request.content_type == 'application/json'])

    is_json_post_request = True

    if is_json_post_request:
        payload = request.body.decode()
        message = json.loads(payload)

        assert 'sender_id' in message, 'missing sender'
        assert 'recipient_id' in message, 'missing recipient'

        if 'message' in message:
            print('message received', message)
            jake.emit(message_received(message))


def receive_greeting(message):
    say(message['sender_id'], 'Hello!')
    whink(message['sender_id'])


def receive_goodbye(message):
    say(message['sender_id'], 'Bye!')
    whink(message['sender_id'])


@jake.listen(text_received)
async def receive_text(message):
    print('receive text', message)

    if message['message']['text'] == 'hi':
        receive_greeting(message)
    elif message['message']['text'] == 'bye':
        receive_goodbye(message)


async def command_list_received(message):
    for i, task in enumerate(tasks, 1):
        msg = '{} {}'.format('✔' if task.completed else ' ', task.name)
        say(message['sender_id'], '{}: {}'.format(i, msg)).readed(whink)


async def command_create_received(message, *args):
    tasks.append(task(completed=False, name=' '.join(args)))
    say(message['sender_id'], 'I added: {}'.format(task.name))


async def command_remove_received(message, *args):
    for arg in args:
        del tasks[arg]

        say(message['sender_id'], 'Removed: {}'.format(task.name))


async def command_complete_received(message, *args):
    for arg in args:
        del tasks[arg]
        tasks[arg].completed = True
        say(message['sender_id'], '✔ {}'.format(task.name))


@jake.listen(command_received)
def receive_command(message, name, args):
    if name == 'list':
        jake.emit(command_list_received(message))
    elif name == 'create':
        jake.emit(command_create_received(message, args))
    elif name == 'remove':
        jake.emit(command_remove_received(message, args))
    elif name == 'complete':
        jake.emit(command_complete_received(message, args))


if __name__ == '__main__':
    jake.run()
