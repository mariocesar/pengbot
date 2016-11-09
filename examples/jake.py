import os
import pengbot

from pengbot.adapters import socket


@pengbot.robot(facebook)
@pengbot.pass_context
def jake(context):
    context.api_token = os.environ.get('SLACK_API_TOKEN', None)


@jake.hears(facebook.Event)
def hears_everything(message):
    jake.logger.info('Everything callback %s', message)


@jake.command('uptime')
def reply_uptime(message):
    from datetime import timedelta

    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])
        uptime_string = str(timedelta(seconds=uptime_seconds))

    jake.says(uptime_string)


if __name__ == '__main__':
    jake.runserver()
