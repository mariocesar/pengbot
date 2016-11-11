import logging
import re

from collections import namedtuple

import pengbot
from pengbot.adapters import shell

task = namedtuple('task', ['name', 'completed'])
tasks = []

cmdregexp = re.match('^/(?P<name>\w+)\s+(?P<arg>[a-z].+)')


@pengbot.robot(shell)
def jake():
    pengbot.logger.setLevel(logging.DEBUG)
    pengbot.logger.info('Hi')


async def whink():
    await jake.say(';)')


@jake.signal()
async def message_received(user):
    pass


@jake.listen(shell.message_received)
async def receive_message(message):
    pengbot.logger.info('... %s', message)

    if 'recipient' in message:
        user = message['received']

        await message_received(message, user)


@jake.signal()
async def greeting_received(message, user):
    await jake.say('Hello!')
    await whink()


@jake.signal()
async def command_received(message, user):
    pass


@jake.listen(message_received)
async def receive_user_message(message, user):
    if message['text'] == 'hi':
        await greeting_received(message, user)
    elif cmdregexp.match(message['text']):
        await command_received(message, user)


@jake.signal()
async def command_list_received(message, user):
    for i, task in enumerate(tasks, 1):
        msg = '{} {}'.format('✔' if task.completed else ' ', task.name)
        await jake.say('{}: {}'.format(i, msg)).readed(whink)


@jake.signal()
async def command_create_received(message, user, *args):
    tasks.append(task(completed=False, name=' '.join(args)))
    await jake.say('I added: {}'.format(task.name))


@jake.signal()
async def command_remove_received(message, user, *args):
    for arg in args:
        del tasks[args]

        await jake.say('Removed: {}'.format(task.name))


@jake.signal()
async def command_complete_received(message, user, *args):
    for arg in args:
        del tasks[args]
        tasks[arg].completed = True
        await jake.say('✔ {}'.format(task.name))


@jake.listen(command_received)
async def receive_command(message, user):
    match = cmdregexp.match(message)
    name = match.groups()['name']
    args = match.groups()['args'].split()

    if name == 'list':
        await command_list_received(message, user)
    elif name == 'create':
        await command_create_received(message, user, args)
    elif name == 'remove':
        await command_remove_received(message, user, args)
    elif name == 'complete':
        await command_complete_received(message, user, args)


if __name__ == '__main__':
    jake()
