import logging
from collections import namedtuple

from pengbot import robot
from pengbot.adapters import shell

task = namedtuple('task', ['name', 'completed'])
tasks = []


@robot(shell)
def irene(bot):
    bot.logger.setLevel(logging.DEBUG)
    bot.logger.info('Hi')


@irene.hear(shell.Event)
def hears_everything(bot, message):
    bot.logger.info('... %s', message)


@irene.command('list')
def reply_uptime(*args):
    for task in tasks:
        irene.says('[{0}] {1}'.format('x' if task.completed else ' ', task.name))


@irene.command('add')
def reply_uptime(*args):
    tasks.append(task(completed=False, name=' '.join(args)))
    irene.says('I added: {1}'.format('x' if task.completed else ' ', task.name))


if __name__ == '__main__':
    irene()
