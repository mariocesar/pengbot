import asyncio
import os
import re

import pengbot
from pengbot.adapters import slack


@pengbot.slack_robot()
def vvbot(bot):
    bot.logger.info('Hi')
    api_token = os.environ.get('SLACK_API_TOKEN', None)

    if not api_token:
        print('Missing api token')
        exit(1)

    return {
        'name': 'vvbot',
        'api_token': api_token
    }


@vvbot.hears(slack.Everything)
def hears_everything(bot, message):
    bot.logger.info('Everything callback %s', message)


@asyncio.coroutine
def count_to_10(bot, message, limit):
    bot.logger.info('Contare hasta %s' % limit)
    channel = message['channel']

    if limit > 20:
        yield from bot.says('... solo se contar hasta 20 :\'(', channel)
    elif limit <= 0:
        yield from bot.says('... lo siento, no se contar hasta %s :(' % limit, channel)
    else:
        yield from bot.says('Seguro! contare hasta %s!' % limit, channel)

        for n in range(1, limit + 1):
            yield from asyncio.sleep(0.5)
            yield from bot.says('%s .. ' % n, channel)


@vvbot.hears(slack.Mention, slack.DirectMessage)
def hear_commands(bot, message):
    count_match = re.match(r'.*cuenta\s+hasta\s+(?P<limit>\-?\d+).*', message['text'], re.IGNORECASE)

    if count_match:
        limit = int(count_match.groupdict().get('limit'))
        yield from count_to_10(bot, message, limit)


@vvbot.hears(slack.DirectMessage)
def talking_parrot(bot, message):
    yield from bot.says(':bird: %s' % message['text'], message['channel'])


@vvbot.hears(slack.RegexpMatch(r'(?P<issue>#[1-9][0-9]+)'))
def link_issues(bot, message):
    pass


@vvbot.respond('uptime')
def reply_uptime(bot, message):
    from datetime import timedelta

    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])
        uptime_string = str(timedelta(seconds=uptime_seconds))

    bot.says(uptime_string)


@vvbot.respond('now')
def reply_now(bot, message):
    from datetime import datetime

    bot.says('The current date and time is {}'.format(datetime.now()))


if __name__ == '__main__':
    vvbot()
