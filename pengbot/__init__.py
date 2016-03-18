import logging
from functools import wraps

from pengbot.adapters.slack import SlackRobot


def getLogger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s [%(name)s] %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


logger = getLogger(__name__)


def slack_robot():
    # TODO: Make smarter and less ugly
    def wrapper(func):
        kwargs = wraps(func)()
        return SlackRobot(**kwargs)

    return wrapper
