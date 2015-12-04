"""
Example robot

    Hello this robot

"""
from pengbot.api import command, env
# from pengbot.api import listen


@command(alias=['hi'])
def hello():
    return 'Hello'


@command(alias=['good bye'])
def bye():
    return 'Good bye'


@command(alias=['now', 'what time is it?'])
def say_time():
    """Return the current time"""
    from datetime import datetime

    return 'The current date and time is {}'.format(datetime.now())

@command
def uptime():
    """Uptime of the host machine"""
    from datetime import timedelta

    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])
        uptime_string = str(timedelta(seconds = uptime_seconds))

    return uptime_string


# @listen
# def jira_issue(message, context):
#     if message.match('(?P<issue>[A-Z]{2,}-\d+)'):
#         pass