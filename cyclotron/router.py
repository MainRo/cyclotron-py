from rx import Observable


def make_crossroad_router(source):
    """ Creates a crossroad router

    A crossroad is a cross-routing between two pair of sink/source
    observables. This allows to use drivers without breaking the
    Observable chain. A crossroad has the following structure:

    .. image:: ../docs/asset/crossroad.png
        :scale: 60%
        :align: center

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
    """ Creates an error router

    Returns
    -------
    error_observable: observable
        An observable emitting errors remapped.

    route_error: function
        A function taking two parameters: obs, and convert. The obs parameter
        is an observable whose error must be catch. The convert parameter is 
        a function used to map the error.

    Examples
    --------

    >>> sink, route_error = make_error_router()

    """
    sink_observer = None

    def on_subscribe(observer):
        nonlocal sink_observer
        sink_observer = observer

        def dispose():
            sink_observer = None

        return dispose

    def route_error(obs, convert):
        """ Handles error raised by obs observable

        catches any error raised by obs, maps it to anther object with the
        convert function, and emits in on the error observer. 

        """
        def catch_error(e):
            sink_observer.on_next(convert(e))
            return Observable.empty()

        return obs.catch_exception(catch_error)

    return Observable.create(on_subscribe), route_error


def catch_or_flat_map(source, error_map, error_router, source_map=lambda i: i):
    """ Wraps an error router in a alettable function 

    Parameters
    ----------
    source: Observable (higher order)
        Observable with errors to route.

    error_map: function
        Function used to map errors before routing them.

    error_router: function
        An error router obtained by with make_error_router.

    source_map: function
        A function used to select the observable from each item is source.

    Examples
    ---------

    >>> sink, route_error = make_error_router()
    >>> Observable.from_([
            Observable.just(1),
            Observable.throw(-1)
        ])
        .let(catch_or_flat_map,
            error_map=lambda e: e.args[0] * 100,
            error_router=route_error
        )

    """
    return source.flat_map(lambda i: error_router(source_map(i), error_map))
