from unittest import TestCase
import rx
import rx.operators as ops
from rx.scheduler import CurrentThreadScheduler
from cyclotron.router import make_error_router


class ErrorRouterTestCase(TestCase):

    def test_route_error(self):
        actual_sequence = []

        def on_chain_item(i):
            nonlocal actual_sequence
            actual_sequence.append(i)

        sink, route_error = make_error_router()

        origin = rx.from_([
                rx.just(1),
                rx.throw(-1)
        ]).pipe(
            route_error(error_map=lambda e: e.args[0] * 100),
        )

        result = rx.merge(origin, sink)
        disposable = result.subscribe(
            on_chain_item,
            scheduler=CurrentThreadScheduler())
        disposable.dispose()

        expected_sequence = [1, -100]
        self.assertEqual(actual_sequence, expected_sequence)
