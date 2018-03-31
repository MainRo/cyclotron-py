from unittest import TestCase

from collections import namedtuple
from cyclotron import Component


class ComponentTestCase(TestCase):

    def test_constructor(self):
        def test_main():
            pass

        component = Component(call=test_main, input=int)
        self.assertEqual(test_main, component.call)
        self.assertEqual(int, component.input)
        self.assertEqual(None, component.output)

        component = Component(call=test_main, output=float)
        self.assertEqual(test_main, component.call)
        self.assertEqual(None, component.input)
        self.assertEqual(float, component.output)

        self.assertRaises(TypeError , Component)
