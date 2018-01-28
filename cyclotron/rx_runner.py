from collections import namedtuple, OrderedDict
from rx.subjects import Subject

Program = namedtuple('Program', ['sinks', 'sources', 'run'])


def make_sink_proxies(drivers):
    sink_proxies = OrderedDict()
    if drivers is not None:
        for name in drivers._fields:
            sink_proxies[name] = Subject()
    return sink_proxies


def call_drivers(drivers, sink_proxies, source_factory):
    sources = OrderedDict()
    for name in drivers._fields:
        sources[name] = getattr(drivers, name)(sink_proxies[name])

    if source_factory is None:
        return None
    return source_factory(**sources)


def subscribe_sinks(sinks, sink_proxies):
    for name in sinks._fields:
        getattr(sinks, name).subscribe(sink_proxies[name])


def setup(main, drivers, source_factory):
    sink_proxies = make_sink_proxies(drivers)
    sources = call_drivers(drivers, sink_proxies, source_factory)
    sinks = main(sources)

    def _run():
        subscribe_sinks(sinks, sink_proxies)
        '''
        dispose_replication = replicate_many(sinks, sink_proxies)

        def dispose():
            dispose_sources(sources)
            dispose_replication()
        return dispose
        '''

    return Program(sinks=sinks, sources=sources, run=_run)


def run(main, drivers, source_factory=None):
    '''
    Takes a main function and circularly connects it to the given collection of
    driver functions.

    parameters:
    - main: the main function to call once the streams are configured.
    - drivers: a list of Drivers namedtuple.
    '''
    program = setup(main, drivers, source_factory)
    return program.run()
