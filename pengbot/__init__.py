from functools import wraps

from pengbot.base import SlackRobot


def robot(**kwargs):
    bot = SlackRobot(**kwargs)

    def wrapper(func):
        return wraps(func)(bot)

    return wrapper
