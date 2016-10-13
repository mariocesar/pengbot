import logging
import os

import pengbot
from pengbot.adapters import facebook


@pengbot.robot(facebook)
def jake(bot):
    bot.logger.setLevel(logging.DEBUG)
    bot.logger.info('Hi')

    bot.context = bot.context(
        api_token=os.environ.get('SLACK_API_TOKEN', None)
    )


@jake.hears(facebook.Event)
def hears_everything(bot, message):
    bot.logger.info('Everything callback %s', message)


@jake.command('uptime')
def reply_uptime(bot, message):
    from datetime import timedelta

    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])
        uptime_string = str(timedelta(seconds=uptime_seconds))

    bot.says(uptime_string)


if __name__ == '__main__':
    jake.runserver()
