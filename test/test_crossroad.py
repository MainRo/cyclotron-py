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
        sink, route_crossroad = make_crossroad_router(source)

        Observable.from_([1, 2]) \
            .do_action(lambda i: print) \
            .let(route_crossroad) \
            .do_action(lambda i: print) \
            .subscribe(on_chain_item)

        sink.subscribe(
            on_next=lambda i: source.on_next(i * 2))


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
        sink, route_crossroad = make_crossroad_router(source)

        Observable.throw("error") \
            .let(route_crossroad) \
            .subscribe(
                on_next=on_chain_item,
                on_error= on_error)

        sink.subscribe(
            on_next=lambda i: source.on_next(i * 2))

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
        sink, route_crossroad = make_crossroad_router(source)

        Observable.from_([1, 2]) \
            .let(route_crossroad) \
            .subscribe(
                on_next=on_chain_item,
                on_error= on_error)

        sink.subscribe(
            on_next=lambda i: source.on_error(Exception("error")))

        self.assertEqual(actual_error.args, ("error",))
