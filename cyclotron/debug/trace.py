import datetime
import traceback
from rx import Observer


class TraceObserver(Observer):
    def __init__(self, prefix, trace_next=True, trace_next_payload=True):
        self.prefix = prefix
        self.trace_next = trace_next
        self.trace_next_payload = trace_next_payload

    def on_next(self, value, date=None):
        if self.trace_next is True:
            if self.trace_next_payload is True:
                print("{}:{} - on_next: {}".format(
                    date or datetime.datetime.now(),
                    self.prefix, value))
            else:
                print("{}:{} - on_next".format(
                    date or datetime.datetime.now(),
                    self.prefix))

    def on_completed(self, date=None):
        print("{}:{} - on_completed".format(
            date or datetime.datetime.now(),
            self.prefix))

    def on_error(self, error, date=None):
        if isinstance(error, Exception):
            print("{}:{} - on_error: {}, {}".format(
                date or datetime.datetime.now(),
                self.prefix, error, 
                traceback.print_tb(error.__traceback__)))
        else:
            print("{}:{} - on_error: {}".format(
                date or datetime.datetime.now(),
                self.prefix, error))