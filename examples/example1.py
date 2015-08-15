"""
Example robot

    Hello this robot

"""
from datetime import datetime
from pengbot.api import command, env
# from pengbot.api import listen


@command(alias=['hi'])
def hello():
    return 'Hello'


@command
def bye():
    return 'Good bye'


@command(alias=['now', 'what time is it?'])
def say_time():
    """Return the current time"""
    return 'The current date and time is {}'.format(datetime.now())


@command
def dance():
    """Dancing music!"""
    return 'Dancing!'


# @listen
# def jira_issue(message, context):
#     if message.match('(?P<issue>[A-Z]{2,}-\d+)'):
#         pass