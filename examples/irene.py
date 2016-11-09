import logging
from collections import namedtuple

import pengbot
from pengbot.adapters import shell

task = namedtuple('task', ['name', 'completed'])
tasks = []


@pengbot.robot(shell)
def irene():
    pengbot.logger.setLevel(logging.DEBUG)
    pengbot.logger.info('Hi')


@irene.listen()
def on_message(message):
    pengbot.logger.info('... %s', message)


@irene.receiver(on_message)
def command(message):
    match = re.match('^/(?P<name>\w+) (?P<arg>.+)', message['text'])
    pengbot.logger.info('... %s', message)


@irene.action
def whink():
    yield irene.say(';)')


@whink.timeout_callback(whink)
def list_read_timeout():
    yield irene.say('Are you there?')


@irene.command('list', on=received)
def list_tasks():
    for i, task in enumerate(tasks, 1):
        msg = '{} {}'.format('✔' if task.completed else ' ', task.name)
        yield irene.say('{}: {}'.format(i, msg)).readed(whink)


@irene.command('add', on=received)
def add_task(name):
    tasks.append(task(completed=False, name=' '.join(name)))
    yield irene.say('I added: {}'.format(task.name))


@irene.command('remove', on=received)
def remove_task(index):
    del tasks[index]

    yield irene.say('Removed: {}'.format(task.name))


@irene.command('complete', on=received)
def complete_task(index):
    tasks[index].completed = True
    yield irene.say('✔ {}'.format(task.name))


if __name__ == '__main__':
    irene()
