import functools
from .rx_test_case import RxTestCase
from rx.subject import Subject
from cyclotron.router import make_crossroad_router, crossroad


class CrossroadTestCase(RxTestCase):

    def test_item_factory(self):
        actual_sequence = []

        def on_chain_item(i):
            nonlocal actual_sequence
            actual_sequence.append(i)

        source = Subject()
        request = Subject()
        sink, route_crossroad = make_crossroad_router(source)

        response_disposable = request.pipe(
            route_crossroad
        ).subscribe(on_chain_item)

        sink_disposable = sink.subscribe(
            on_next=lambda i: source.on_next(i * 2))

        request.on_next(1)
        request.on_next(2)
        response_disposable.dispose()
        sink_disposable.dispose()

        expected_sequence = [2, 4]
        self.assertEqual(actual_sequence, expected_sequence)

    def test_item_lettable(self):
        actual_sequence = []

        def on_chain_item(i):
            nonlocal actual_sequence
            actual_sequence.append(i)

        source = Subject()
        request = Subject()

        sink, response = request.pipe(
            crossroad(source=source)
        )

        response_disposable = response.subscribe(on_chain_item)

        sink_disposable = sink.subscribe(
            on_next=lambda i: source.on_next(i * 2))

        request.on_next(1)
        request.on_next(2)
        response_disposable.dispose()
        sink_disposable.dispose()

        expected_sequence = [2, 4]
        self.assertEqual(actual_sequence, expected_sequence)

    def test_request_error(self):
        actual_sequence = []
        actual_error = None

        def on_chain_item(i):
            nonlocal actual_sequence
            actual_sequence.append(i)

        def on_error(e):
            nonlocal actual_error
            actual_error = e

        source = Subject()
        request = Subject()
        sink, route_crossroad = make_crossroad_router(source)

        response_disposable = request.pipe(
            route_crossroad
        ).subscribe(
                on_next=on_chain_item,
                on_error=on_error)

        sink_disposable = sink.subscribe(
            on_next=lambda i: source.on_next(i * 2))

        request.on_error(Exception("error"))
        response_disposable.dispose()
        sink_disposable.dispose()

        self.assertEqual(actual_error.args, ("error",))

    def test_source_error(self):
        actual_sequence = []
        actual_error = None

        def on_chain_item(i):
            nonlocal actual_sequence
            actual_sequence.append(i)

        def on_error(e):
            nonlocal actual_error
            actual_error = e

        source = Subject()
        request = Subject()
        sink, route_crossroad = make_crossroad_router(source)

        response_disposable = request.pipe(
            route_crossroad
        ).subscribe(
                on_next=on_chain_item,
                on_error=on_error)

        sink_disposable = sink.subscribe(
            on_next=lambda i: source.on_error(Exception("error")))

        request.on_next(1)
        request.on_next(2)
        response_disposable.dispose()
        sink_disposable.dispose()

        self.assertEqual(actual_error.args, ("error",))

    def test_completed(self):
        source = Subject()
        request = Subject()
        sink, route_crossroad = make_crossroad_router(source)

        sink.subscribe(
            on_next=functools.partial(self.on_next, 'sink'),
            on_error=functools.partial(self.on_error, 'sink'),
            on_completed=functools.partial(self.on_completed, 'sink'))

        request.pipe(
            route_crossroad,
        ).subscribe(
                on_next=functools.partial(self.on_next, 'response'),
                on_error=functools.partial(self.on_error, 'response'),
                on_completed=functools.partial(self.on_completed, 'response'))

        request.on_next(1)
        request.on_completed()

        self.assertEqual(1, len(self.actual['sink']['next']))
        self.assertEqual(1, self.actual['sink']['next'][0])
        self.assertTrue(self.actual['sink']['completed'])

        source.on_next(2)
        source.on_completed()
        self.assertEqual(1, len(self.actual['response']['next']))
        self.assertEqual(2, self.actual['response']['next'][0])
        self.assertTrue(self.actual['response']['completed'])
