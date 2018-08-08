from unittest import TestCase
from rx import Observable
from rx.subjects import Subject
from cyclotron.router import make_crossroad_router


class CrossroadTestCase(TestCase):

    def test_item(self):
        actual_sequence = []

        def on_chain_item(i):
            nonlocal actual_sequence
            actual_sequence.append(i)

        source = Subject()
        request = Subject()
        sink, route_crossroad = make_crossroad_router(source)

        response_disposable = request \
            .let(route_crossroad) \
            .subscribe(on_chain_item)

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

        response_disposable = request \
            .let(route_crossroad) \
            .subscribe(
                on_next=on_chain_item,
                on_error= on_error)

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

        response_disposable = request \
            .let(route_crossroad) \
            .subscribe(
                on_next=on_chain_item,
                on_error= on_error)

        sink_disposable = sink.subscribe(
            on_next=lambda i: source.on_error(Exception("error")))

        request.on_next(1)
        request.on_next(2)
        response_disposable.dispose()
        sink_disposable.dispose()

        self.assertEqual(actual_error.args, ("error",))
