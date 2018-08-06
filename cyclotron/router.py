from rx import Observable


def make_crossroad_router(source):
    sink_observer = None
    response_observer = None
    request_observable = None

    def on_sink_subscribe(observer):
        nonlocal sink_observer
        sink_observer = observer
        crossroad_subscribe(sink_observer, response_observer, request_observable)

    def on_response_subscribe(observer, request):
        nonlocal response_observer
        nonlocal request_observable
        response_observer = observer
        request_observable = request
        crossroad_subscribe(sink_observer, response_observer, request_observable)

    def crossroad_subscribe(sink_observer, response_observer, request):
        if sink_observer is None \
            or response_observer is None \
            or request is None:
            return

        request.subscribe(
            on_next=lambda i: sink_observer.on_next(i),
            on_error=lambda e: response_observer.on_error(e),
            on_completed=lambda: sink_observer.on_completed()
        )

        source.subscribe(
            on_next=lambda i: response_observer.on_next(i),
            on_error=lambda e: response_observer.on_error(e),
            on_completed=lambda: response_observer.on_completed()
        )

    def route_crossroad(request):
        return Observable.create(lambda o: on_response_subscribe(o, request))

    return Observable.create(on_sink_subscribe), route_crossroad