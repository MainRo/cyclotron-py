from rx import Observable


def make_crossroad_router(source):
    """ Creates a crossroad router

        A crossroad is a cross-routing between two pair of sink/source
        observables. This allows to use wrap drivers without breaking the
        Observable chain. A crossreaod has the following structure:

                     ________________
                    |                |
                    |   | --------|  |
        request ----|---(----|    |--|---> response
                    |   |    |       |
                    |   |    |       |
        source  ----|---|    |-------|---> sink
                    |                |
                    |    crossroad   |
                    |________________|

        The crossroad function returned by this factory takes a request object
        as input and returns a response object as output. Items received on the
        request observable are routed to the sink Observable. Items received on
        the source observable are routed on the response observable.

        Parameters
        ----------
        source : Observable
            The source observable of the driver to wrap.

        Returns
        -------
        sink : Observable
            A sink observable that must be routed to the sink observable of the
            driver.

        crossroad : function
            An operator function that can be used with the let operator. It
            takes an observable as input an returned a observable, routing
            their items as described above.
    """
    sink_observer = None
    response_observer = None
    request_observable = None
    request_disposable = None
    source_disposable = None

    def on_sink_subscribe(observer):
        nonlocal sink_observer
        sink_observer = observer
        crossroad_subscribe(sink_observer, response_observer, request_observable)

        def dispose():
            request_disposable.dispose()

        return dispose

    def on_response_subscribe(observer, request):
        nonlocal response_observer
        nonlocal request_observable
        response_observer = observer
        request_observable = request
        crossroad_subscribe(sink_observer, response_observer, request_observable)

        def dispose():
            source_disposable.dispose()

        return dispose

    def crossroad_subscribe(sink_observer, response_observer, request):
        nonlocal request_disposable
        nonlocal source_disposable

        if sink_observer is None \
            or response_observer is None \
            or request is None:
            return

        request_disposable = request.subscribe(
            on_next=lambda i: sink_observer.on_next(i),
            on_error=lambda e: response_observer.on_error(e),
            on_completed=lambda: sink_observer.on_completed()
        )

        source_disposable = source.subscribe(
            on_next=lambda i: response_observer.on_next(i),
            on_error=lambda e: response_observer.on_error(e),
            on_completed=lambda: response_observer.on_completed()
        )

    def route_crossroad(request):
        return Observable.create(lambda o: on_response_subscribe(o, request))

    return Observable.create(on_sink_subscribe), route_crossroad


def make_error_router():
    sink_observer = None

    def on_subscribe(observer):
        nonlocal sink_observer
        sink_observer = observer

        def dispose():
            sink_observer = None

        return dispose

    def route_error(item, convert):
        def catch_item(i):
            sink_observer.on_next(convert(i))
            return Observable.empty()

        return item.catch_exception(catch_item)

    return Observable.create(on_subscribe), route_error


def catch_or_flat_map(source, error_map, error_router, source_map=lambda i: i):
    return source.flat_map(lambda i: error_router(source_map(i), error_map))
