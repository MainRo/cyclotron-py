from collections import namedtuple
from cyclotron import Component
import asyncio

Sink = namedtuple('Sink', ['control'])


def make_driver(loop=None):
    ''' Returns a stop driver.

    The optional loop argument can be provided to use the driver in another
    loop than the default one.

    Parameters
    -----------
    loop: BaseEventLoop
        The event loop to use instead of the default one.
    '''
    loop = loop or asyncio.get_event_loop()

    def stop(i=None):
        loop.stop()

    def driver(sink):
        ''' The stop driver stops the asyncio event loop.
        The event loop is stopped as soon as an event is received on the
        control observable or when it completes (both in case of success or
        error).

        Parameters
        ----------
            sink: Sink
        '''
        sink.control.subscribe(
            on_next=stop,
            on_error=stop,
            on_completed=stop)
        return None

    return Component(call=driver, input=Sink)
