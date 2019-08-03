from unittest import TestCase

from collections import namedtuple
import rx
from cyclotron import Component
from cyclotron.rx import run


class RunnerTestCase(TestCase):

    def test_run_1snk(self):
        ''' Creates a cycle with one sink driver.
        '''
        MainDrivers = namedtuple('MainDrivers', ['drv1'])
        MainSource = namedtuple('MainSource', [])
        MainSink = namedtuple('MainSink', ['drv1'])
        test_values = []

        def drv1(sink):
            sink.values.subscribe(lambda i: test_values.append(i))
            return None
        Drv1Sink = namedtuple('Drv1Sink', ['values'])
        Drv1Driver = Component(call=drv1, input=Drv1Sink)

        def main(sources):
            val = rx.from_([1, 2, 3])
            return MainSink(drv1=Drv1Sink(values=val))

        drivers = MainDrivers(drv1=Drv1Driver)
        dispose = run(Component(call=main, input=MainSource), drivers)
        dispose()

        self.assertEqual(3, len(test_values))
        self.assertEqual(1, test_values[0])
        self.assertEqual(2, test_values[1])
        self.assertEqual(3, test_values[2])

    def test_run_1srcsnk(self):
        ''' Creates a cycle with one sink/source driver.
        '''
        MainDrivers = namedtuple('MainDrivers', ['drv1'])
        MainSource = namedtuple('MainSource', ['drv1'])
        MainSink = namedtuple('MainSink', ['drv1'])
        test_values = []

        Drv1Source = namedtuple('Drv1Source', ['counter'])
        Drv1Sink = namedtuple('Drv1Sink', ['values'])

        def drv1(sink):
            sink.values.subscribe(lambda i: test_values.append(i))
            counter_stream = rx.from_([1, 2, 3])
            return Drv1Source(counter=counter_stream)
        Drv1Driver = Component(call=drv1, input=Drv1Sink)

        def main(sources):
            val = sources.drv1.counter
            return MainSink(drv1=Drv1Sink(values=val))

        drivers = MainDrivers(drv1=Drv1Driver)
        dispose = run(Component(call=main, input=MainSource), drivers)
        dispose()

        self.assertEqual(3, len(test_values))
        self.assertEqual(1, test_values[0])
        self.assertEqual(2, test_values[1])
        self.assertEqual(3, test_values[2])

    def test_run_1src_1snk(self):
        ''' Creates a cycle with one sink driver and one source driver.
        '''
        test_values = []
        Drv1Sink = namedtuple('Drv1Sink', ['values'])

        def drv1(sink):
            sink.values.subscribe(lambda i: test_values.append(i))
            return None
        Drv1Driver = Component(call=drv1, input=Drv1Sink)

        Drv2Source = namedtuple('Drv2Source', ['counter'])

        def drv2():
            counter_stream = rx.from_([1, 2, 3])
            return Drv2Source(counter=counter_stream)
        Drv2Driver = Component(call=drv2, input=None)

        MainDrivers = namedtuple('MainDrivers', ['drv1', 'drv2'])
        MainSource = namedtuple('MainSource', ['drv2'])
        MainSink = namedtuple('MainSink', ['drv1'])

        def main(sources):
            val = sources.drv2.counter
            return MainSink(drv1=Drv1Sink(values=val))

        drivers = MainDrivers(drv1=Drv1Driver, drv2=Drv2Driver)
        dispose = run(Component(call=main, input=MainSource), drivers)
        dispose()

        self.assertEqual(3, len(test_values))
        self.assertEqual(1, test_values[0])
        self.assertEqual(2, test_values[1])
        self.assertEqual(3, test_values[2])
