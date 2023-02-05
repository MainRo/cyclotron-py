import datetime
import traceback
import reactivex as rx
from reactivex.disposable import Disposable


def trace_observable(prefix,
                     trace_next=True, trace_next_payload=True,
                     trace_subscribe=True,
                     date=None):
    def _trace(source):
        def on_subscribe(observer, scheduler):
            def on_next(value):
                if trace_next is True:
                    if trace_next_payload is True:
                        print("{}:{} - on_next: {}".format(
                            date or datetime.datetime.now(),
                            prefix, value))
                    else:
                        print("{}:{} - on_next".format(
                            date or datetime.datetime.now(),
                            prefix))
                observer.on_next(value)

            def on_completed():
                print("{}:{} - on_completed".format(
                    date or datetime.datetime.now(),
                    prefix))
                observer.on_completed()

            def on_error(error):
                if isinstance(error, Exception):
                    print("{}:{} - on_error: {}, {}".format(
                        date or datetime.datetime.now(),
                        prefix, error,
                        traceback.print_tb(error.__traceback__)))
                else:
                    print("{}:{} - on_error: {}".format(
                        date or datetime.datetime.now(),
                        prefix, error))
                observer.on_error(error)

            def dispose():
                if trace_subscribe is True:
                    print("{}:{} - dispose".format(
                            date or datetime.datetime.now(),
                            prefix))

                disposable.dispose()

            if trace_subscribe is True:
                print("{}:{} - on_subscribe".format(
                        date or datetime.datetime.now(),
                        prefix))
            disposable = source.subscribe(
                on_next=on_next,
                on_error=on_error,
                on_completed=on_completed,
            )

            return Disposable(dispose)

        return rx.create(on_subscribe)

    return _trace
