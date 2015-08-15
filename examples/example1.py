"""
Example robot

    Hello this robot

"""
from datetime import datetime
from pengbot.api import command, env


@command(alias=['hi', 'hello'])
def say_hi():
    return 'Hello'


@command(alias='now')
def say_time():
    """Return the current time"""
    return 'The current date and time is {}'.format(datetime.now())

@command
def dance():
    """Dancing music!"""
    return 'Dancing!'
