from collections import namedtuple, OrderedDict
from reactivex.subject import Subject


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
            driver_sink = getattr(driver, 'input')
            if driver_sink is not None:
                driver_sink_proxies = OrderedDict()
                for name in driver_sink._fields:
                    driver_sink_proxies[name] = Subject()

                sink_proxies[driver_name] = driver.input(**driver_sink_proxies)
    return sink_proxies


def call_drivers(drivers, sink_proxies, source_factory):
    sources = OrderedDict()
    for name in drivers._fields:
        try:
            source = None
            # Source drivers have no sink
            if name in sink_proxies:
                source = getattr(drivers, name).call(sink_proxies[name])
            else:
                source = getattr(drivers, name).call()

            # sink drivers have no source
            if source is not None:
                sources[name] = source

        except Exception as e:
            raise RuntimeError('Unable to initialize {} driver'.format(name)) from e

    if source_factory is None:
        return None
    return source_factory(**sources)


def subscribe_sinks(sinks, sink_proxies, scheduler):
    for driver_name in sinks._fields:
        driver = getattr(sinks, driver_name)
        for sink_name in driver._fields:
            getattr(driver, sink_name).subscribe(
                getattr(sink_proxies[driver_name], sink_name),
                scheduler=scheduler)


def setup(entry_point, drivers):
    sink_proxies = make_sink_proxies(drivers)
    sources = call_drivers(drivers, sink_proxies, entry_point.input)
    sinks = entry_point.call(sources)

    def _run(scheduler=None):
        subscribe_sinks(sinks, sink_proxies, scheduler)

        def dispose():
            return
        return dispose

    return Program(sinks=sinks, sources=sources, run=_run)


def run(entry_point, drivers):
    '''
    Takes a function and circularly connects it to the given collection of
    driver functions.

    parameters:
    - entry_point (Component): the function to call once the streams are configured.
    - drivers: a list of Component namedtuple where each Component is a driver.
    '''
    program = setup(entry_point, drivers)
    return program.run()
