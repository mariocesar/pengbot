"""
Pengbot: For building robots with human manners
===============================================

:copyright: (c) 2016 by Mario César Señoranis Ayala.
:license: MIT, see LICENSE for more details.

"""

__title__ = 'pengbot'
__version__ = '0.1a1'
__author__ = 'Mar'
__license__ = 'MIT'
__copyright__ = 'Copyright 2016 Mario César Señoranis Ayala'

import logging
from functools import wraps

logger = logging.getLogger(__name__).addHandler(logging.NullHandler)

__all__ = ['make_robot']


def make_robot(robotClass):
    def wrapper(func):
        bot = robotClass()
        func(bot)
        return wraps(func)(bot)

    return wrapper
