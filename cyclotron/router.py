import functools
import rx
import rx.operators as ops
import cyclotron


def make_crossroad_router(source, drain=False):
    ''' legacy crossroad implementation. deprecated
    '''
    sink_observer = None

    def on_sink_subscribe(observer, scheduler):
        nonlocal sink_observer
        sink_observer = observer

        def dispose():
            nonlocal sink_observer
            sink_observer = None

        return dispose

    def route_crossroad(request):
        def on_response_subscribe(observer, scheduler):
            def on_next_source(i):
                if type(i) is cyclotron.Drain:
                    observer.on_completed()
                else:
                    observer.on_next(i)

            source_disposable = source.subscribe(
                on_next=on_next_source,
                on_error=lambda e: observer.on_error(e),
                on_completed=lambda: observer.on_completed()
            )

            def on_next_request(i):
                if sink_observer is not None:
                    sink_observer.on_next(i)

            def on_request_completed():
                if sink_observer is not None:
                    if drain is True:
                        sink_observer.on_next(cyclotron.Drain())
                    else:
                        sink_observer.on_completed()

            request_disposable = request.subscribe(
                on_next=on_next_request,
                on_error=observer.on_error,
                on_completed=on_request_completed
            )

            def dispose():
                source_disposable.dispose()
                request_disposable.dispose()

            return dispose

        return rx.create(on_response_subscribe)

    return rx.create(on_sink_subscribe), route_crossroad


def crossroad(source, drain=False):
    def _crossroad(request):
        """ Creates a crossroad router

        A crossroad is a cross-routing between two pair of sink/source
        observables. This allows to use drivers with less discruption on
        the Observable chain. A crossroad has the following structure:

        .. image:: ../docs/asset/crossroad.png
            :scale: 60%
            :align: center

        This function is a lettable operator.

        Parameters
        ----------
        request : Observable
            The observable coming from the observable chain.

        source : Observable
            The source observable of the driver to wrap.

        drain : Boolean
            Indicated whether items should be drained form the driver before
            forwarding completion events.

        Returns
        -------
        sink : Observable
            A sink observable that must be routed to the sink observable of the
            driver.

        response : Observable
            The response coming from the driver.

        """
        sink_observer = None

        def on_sink_subscribe(observer, scheduler):
            nonlocal sink_observer
            sink_observer = observer

        def on_response_subscribe(observer, scheduler):
                def on_next_source(i):
                    if type(i) is cyclotron.Drain:
                        observer.on_completed()
                    else:
                        observer.on_next(i)

                source_disposable = source.subscribe(
                    on_next=on_next_source,
                    on_error=lambda e: observer.on_error(e),
                    on_completed=lambda: observer.on_completed()
                )

                def on_next_request(i):
                    if sink_observer is not None:
                        sink_observer.on_next(i)

                def on_request_completed():
                    if sink_observer is not None:
                        if drain is True:
                            sink_observer.on_next(cyclotron.Drain())
                        else:
                            sink_observer.on_completed()

                request_disposable = request.subscribe(
                    on_next=on_next_request,
                    on_error=observer.on_error,
                    on_completed=on_request_completed
                )

                def dispose():
                    source_disposable.dispose()
                    request_disposable.dispose()

                return dispose

        return (
            rx.create(on_sink_subscribe),
            rx.create(on_response_subscribe)
        )

    return _crossroad


def make_error_router():
    """ Creates an error router

    An error router takes a higher order observable a input and returns two
    observables: One containing the flattened items of the input observable
    and another one containing the flattened errors of the input observable.

    .. image:: ../docs/asset/error_router.png
        :scale: 60%
        :align: center

    Returns
    -------
    error_observable: observable
        An observable emitting errors remapped.

    route_error: function
        A lettable function routing errors and taking three parameters:
        * source: Observable (higher order). Observable with errors to route.
        * error_map: function. Function used to map errors before routing them.
        * source_map: function. A function used to select the observable from each item is source.

    Examples
    --------

    >>> sink, route_error = make_error_router()
        my_observable.let(route_error, error_map=lambda e: e)

    """
    sink_observer = None
    sink_scheduler = None

    def on_subscribe(observer, scheduler):
        nonlocal sink_observer
        nonlocal sink_scheduler
        sink_observer = observer
        sink_scheduler = scheduler

        def dispose():
            nonlocal sink_observer
            sink_observer = None

        return dispose

    def route_error(obs, convert):
        """ Handles error raised by obs observable

        catches any error raised by obs, maps it to anther object with the
        convert function, and emits in on the error observer.

        """
        def catch_error(e, source):
            sink_scheduler.schedule(lambda _1, _2: sink_observer.on_next(convert(e)))
            return rx.empty()

        return obs.pipe(ops.catch(catch_error))

    def catch_or_flat_map(error_map, source_map=lambda i: i):
        def _catch_or_flat_map(source):
            return source.pipe(
                ops.flat_map(lambda i: route_error(source_map(i), error_map))
            )

        return _catch_or_flat_map

    return rx.create(on_subscribe), catch_or_flat_map
