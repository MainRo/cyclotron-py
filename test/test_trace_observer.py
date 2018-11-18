from unittest import TestCase
import sys
import datetime
from io import StringIO

from cyclotron.debug import TraceObserver


class TraceObserverTestCase(TestCase):
    def setUp(self):
        self.saved_stdout = sys.stdout
        self.out = StringIO()
        sys.stdout = self.out

    def tearDown(self):
        sys.stdout = self.saved_stdout

    def test_base_on_next(self):
        observer = TraceObserver(prefix='foo')
        observer.on_next('bar', date=datetime.datetime(year=2018, month=8, day=3))
        self.assertEqual(
            '2018-08-03 00:00:00:foo - on_next: bar',
            self.out.getvalue().strip())

    def test_base_on_completed(self):
        observer = TraceObserver(prefix='foo')
        observer.on_completed(date=datetime.datetime(year=2018, month=8, day=3))
        self.assertEqual(
            '2018-08-03 00:00:00:foo - on_completed',
            self.out.getvalue().strip())

    def test_base_on_error(self):
        observer = TraceObserver(prefix='foo')
        observer.on_error('error', date=datetime.datetime(year=2018, month=8, day=3))
        self.assertEqual(
            '2018-08-03 00:00:00:foo - on_error: error',
            self.out.getvalue().strip())

    def test_no_trace_next(self):
        observer = TraceObserver(prefix='foo', trace_next=False)

        observer.on_next('bar', datetime.datetime(year=2018, month=8, day=3))
        self.assertEqual(
            '',
            self.out.getvalue().strip())

    def test_no_payload_next(self):
        observer = TraceObserver(prefix='foo', trace_next_payload=False)

        observer.on_next('bar', datetime.datetime(year=2018, month=8, day=3))
        self.assertEqual(
            '2018-08-03 00:00:00:foo - on_next',
            self.out.getvalue().strip())
