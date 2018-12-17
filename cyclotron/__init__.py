from collections import namedtuple

Component = namedtuple('Component', ['call', 'input', 'output'])
Component.__new__.__defaults__ = (None, None)

Drain = namedtuple('Drain', [])
