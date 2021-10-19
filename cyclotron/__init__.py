from collections import namedtuple

__author__ = """Romain Picard"""
__email__ = 'romain.picard@oakbits.com'
__version__ = '1.3.0'

from . import backpressure

Component = namedtuple('Component', ['call', 'input', 'output'])
Component.__new__.__defaults__ = (None, None)

Drain = namedtuple('Drain', [])
