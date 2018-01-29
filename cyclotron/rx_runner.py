from collections import namedtuple, OrderedDict
from rx.subjects import Subject

Driver = namedtuple('Driver', ['call', 'sink'])
Program = namedtuple('Program', ['sinks', 'sources', 'run'])


def make_sink_proxies(drivers):
    ''' Build a list of sink proxies. sink proxies are a two-level ordered
    dictionary. The first level contains the lst of drivers, and the second
    level contains the list of sink proxies for each driver:

    drv1-->sink1
      | |->sink2
      |
    drv2-->sink1
        |->sink2
    '''
    sink_proxies = OrderedDict()
    if drivers is not None:
        for driver_name in drivers._fields:
            driver = getattr(drivers, driver_name)
            driver_sink = getattr(driver, 'sink')
            driver_sink_proxies = OrderedDict()
            for name in driver_sink._fields:
                driver_sink_proxies[name] = Subject()

            sink_proxies[driver_name] = driver.sink(**driver_sink_proxies)
    return sink_proxies


def call_drivers(drivers, sink_proxies, source_factory):
    sources = OrderedDict()
    for name in drivers._fields:
        sources[name] = getattr(drivers, name).call(sink_proxies[name])

    if source_factory is None:
        return None
    return source_factory(**sources)


def subscribe_sinks(sinks, sink_proxies):
    for driver_name in sinks._fields:
        driver = getattr(sinks, driver_name)
        for sink_name in driver._fields:
            print("driver {}, subscribe {}".format(driver_name, sink_name))
            getattr(driver, sink_name).subscribe( \
                getattr(sink_proxies[driver_name], sink_name))


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
