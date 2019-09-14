import asyncio
from cyclotron.rx import setup


def run(entry_point, drivers, loop=None):
    ''' This is a runner wrapping the cyclotron "run" implementation. It takes
    an additional parameter to provide a custom asyncio mainloop.
    '''
    program = setup(entry_point, drivers)
    dispose = program.run()
    if loop is None:
        loop = asyncio.get_event_loop()

    loop.run_forever()
    dispose()
