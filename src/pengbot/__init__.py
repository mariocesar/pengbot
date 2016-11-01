"""
Pengbot: For building robots with human manners
===============================================

:copyright: (c) 2016 by Mario César Señoranis Ayala.
:license: MIT, see LICENSE for more details.

"""

__title__ = 'pengbot'
__version__ = '0.1a1'
__author__ = 'Mario César Señoranis Ayala <mariocesar.c50@gmail.com>'
__license__ = 'MIT'
__copyright__ = 'Copyright 2016 Mario César Señoranis Ayala'

import logging

logger = logging.getLogger(__name__)

from .decorators import robot
