from unittest import TestCase
from rx import Observable
from rx.subjects import Subject
from cyclotron.rx import make_crossbar


class CrossbarTestCase(TestCase):

    def test_item(self):
        actual_sequence = []

        def on_chain_item(i):
            nonlocal actual_sequence
            actual_sequence.append(i)

        source = Subject()
        sink, crossbar = make_crossbar(source)

        Observable.from_([1, 2]) \
            .do_action(lambda i: print) \
            .let(crossbar) \
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
        sink, crossbar = make_crossbar(source)

        Observable.throw("error") \
            .let(crossbar) \
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
        sink, crossbar = make_crossbar(source)

        Observable.from_([1, 2]) \
            .let(crossbar) \
            .subscribe(
                on_next=on_chain_item,
                on_error= on_error)

        sink.subscribe(
            on_next=lambda i: source.on_error(Exception("error")))

        self.assertEqual(actual_error.args, ("error",))
