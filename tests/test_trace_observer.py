from unittest import TestCase
import sys
import datetime
from io import StringIO
import rx
from rx.subject import Subject

from cyclotron.debug import trace_observable


class TraceObserverTestCase(TestCase):
    def setUp(self):
        self.saved_stdout = sys.stdout
        self.out = StringIO()
        sys.stdout = self.out

    def tearDown(self):
        sys.stdout = self.saved_stdout

    def test_base_on_next(self):
        source = Subject()
        source.pipe(trace_observable(
            prefix='foo',
            date=datetime.datetime(year=2018, month=8, day=3))
        ).subscribe()
        source.on_next('bar')
        self.assertEqual(
            '2018-08-03 00:00:00:foo - on_subscribe\n'
            '2018-08-03 00:00:00:foo - on_next: bar',
            self.out.getvalue().strip())

    def test_base_on_completed(self):
        source = Subject()
        source.pipe(trace_observable(
            prefix='foo',
            date=datetime.datetime(year=2018, month=8, day=3))
        ).subscribe()
        source.on_completed()
        self.assertEqual(
            '2018-08-03 00:00:00:foo - on_subscribe\n'
            '2018-08-03 00:00:00:foo - on_completed\n'
            '2018-08-03 00:00:00:foo - dispose',
            self.out.getvalue().strip())

    def test_base_on_error(self):
        source = Subject()
        source.pipe(trace_observable(
            prefix='foo',
            date=datetime.datetime(year=2018, month=8, day=3))
        ).subscribe(on_error=lambda _: None)
        source.on_error('error')
        self.assertEqual(
            '2018-08-03 00:00:00:foo - on_subscribe\n'
            '2018-08-03 00:00:00:foo - on_error: error\n'
            '2018-08-03 00:00:00:foo - dispose',
            self.out.getvalue().strip())

    def test_no_trace_next(self):
        source = Subject()
        source.pipe(trace_observable(
            prefix='foo', trace_next=False,
            date=datetime.datetime(year=2018, month=8, day=3))
        ).subscribe()
        source.on_next('bar')
        self.assertEqual(
            '2018-08-03 00:00:00:foo - on_subscribe',
            self.out.getvalue().strip())

    def test_no_payload_next(self):
        source = Subject()
        source.pipe(trace_observable(
            prefix='foo', trace_next_payload=False,
            date=datetime.datetime(year=2018, month=8, day=3))
        ).subscribe()
        source.on_next('bar')
        self.assertEqual(
            '2018-08-03 00:00:00:foo - on_subscribe\n'
            '2018-08-03 00:00:00:foo - on_next',
            self.out.getvalue().strip())

    def test_no_subscribe(self):
        source = Subject()
        source.pipe(trace_observable(
            prefix='foo', trace_subscribe=False,
            date=datetime.datetime(year=2018, month=8, day=3))
        ).subscribe()
        source.on_next('bar')
        self.assertEqual(
            '2018-08-03 00:00:00:foo - on_next: bar',
            self.out.getvalue().strip())
