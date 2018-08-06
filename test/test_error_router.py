from unittest import TestCase
from rx import Observable
from rx.subjects import Subject
from cyclotron.router import make_error_router, catch_or_flat_map


class CrossroadTestCase(TestCase):

    def test_route_error(self):
        actual_sequence = []

        def on_chain_item(i):
            nonlocal actual_sequence
            actual_sequence.append(i)

        sink, route_error = make_error_router()

        origin = (
            Observable.from_([
                Observable.just(1),
                Observable.throw(-1)
            ])
            .do_action(lambda i: print)
            .let(catch_or_flat_map,
                error_map=lambda e: e.args[0] * 100,
                error_router=route_error
            )
            .do_action(lambda i: print)
        )

        result = Observable.merge(origin, sink)
        result.subscribe(on_chain_item)

        expected_sequence = [1, -100]
        self.assertEqual(actual_sequence, expected_sequence)
