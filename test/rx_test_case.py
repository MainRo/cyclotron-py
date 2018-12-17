from unittest import TestCase


class RxTestCase(TestCase):
    def setUp(self):
        self.actual = {}

    def create_actual(self):
        return {
            'next': [],
            'error': None,
            'completed': False
        }

    def on_next(self, key, i):
        if key not in self.actual:
            self.actual[key] = self.create_actual()
        self.actual[key]['next'].append(i)

    def on_error(self, key, e):
        if key not in self.actual:
            self.actual[key] = self.create_actual()
        self.actual[key]['error'] = e

    def on_completed(self, key):
        if key not in self.actual:
            self.actual[key] = self.create_actual()
        self.actual[key]['completed'] = True
