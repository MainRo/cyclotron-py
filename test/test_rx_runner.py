from unittest import TestCase

from collections import namedtuple
from rx import Observable
from cyclotron.rx_runner import run


class RunnerTestCase(TestCase):

    def test_run_1snk(self):
        ''' Creates a cycle with one sink driver.
        '''
        MainDrivers = namedtuple('MainDrivers', ['drv1'])
        MainSink = namedtuple('MainSink', ['drv1'])

        test_values = []

        def drv1(sinks):
            sinks.subscribe(lambda i: test_values.append(i))
            return None

        def main(sources):
            val = Observable.from_([1, 2, 3])
            return MainSink(drv1=val)

        drivers = MainDrivers(drv1=drv1)
        run(main, drivers)

        self.assertEqual(3, len(test_values))
        self.assertEqual(1, test_values[0])
        self.assertEqual(2, test_values[1])
        self.assertEqual(3, test_values[2])

    def test_run_1srcsnk(self):
        ''' Creates a cycle with one sink/source driver.
        '''
        Drv1Source = namedtuple('Drv1Source', ['counter'])

        MainDrivers = namedtuple('MainDrivers', ['drv1'])
        MainSource = namedtuple('MainSource', ['drv1'])
        MainSink = namedtuple('MainSink', ['drv1'])

        test_values = []

        def drv1(sinks):
            sinks.subscribe(lambda i: test_values.append(i))
            counter_stream = Observable.from_([1, 2, 3])
            return Drv1Source(counter=counter_stream)

        def main(sources):
            val = sources.drv1.counter
            return MainSink(drv1=val)

        drivers = MainDrivers(drv1=drv1)
        run(main, drivers, MainSource)

        self.assertEqual(3, len(test_values))
        self.assertEqual(1, test_values[0])
        self.assertEqual(2, test_values[1])
        self.assertEqual(3, test_values[2])

    def test_run_1src_1snk(self):
        ''' Creates a cycle with one sink driver and one source driver.
        '''
        Drv2Source = namedtuple('Drv2Source', ['counter'])

        MainDrivers = namedtuple('MainDrivers', ['drv1', 'drv2'])
        MainSource = namedtuple('MainSource', ['drv1', 'drv2'])
        MainSink = namedtuple('MainSink', ['drv1'])

        test_values = []

        def drv1(sinks):
            sinks.subscribe(lambda i: test_values.append(i))
            return None

        def drv2(sinks):
            counter_stream = Observable.from_([1, 2, 3])
            return Drv2Source(counter=counter_stream)

        def main(sources):
            val = sources.drv2.counter
            return MainSink(drv1=val)

        drivers = MainDrivers(drv1=drv1, drv2=drv2)
        run(main, drivers, MainSource)

        self.assertEqual(3, len(test_values))
        self.assertEqual(1, test_values[0])
        self.assertEqual(2, test_values[1])
        self.assertEqual(3, test_values[2])
