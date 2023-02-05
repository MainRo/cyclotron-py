import reactivex as rx
import reactivex.operators as ops
from reactivex.scheduler import CurrentThreadScheduler


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
        sink_scheduler = scheduler or CurrentThreadScheduler()

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
