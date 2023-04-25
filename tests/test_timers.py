from unittest import TestCase

from tools.timers import TimedAction


class TestTimedAction(TestCase):
    def setUp(self) -> None:
        self.value = False
        self.action = TimedAction(0, 1, self.function)

    def function(self, _):
        self.value = True

    def test_run1(self):
        state = self.action.run(None, -1, -2)
        self.assertFalse(self.value)
        self.assertFalse(state)

    def test_run2(self):
        state = self.action.run(None, -0.5, -1)
        self.assertFalse(self.value)
        self.assertFalse(state)

    def test_run3(self):
        state = self.action.run(None, 0, -0.5)
        self.assertTrue(self.value)
        self.assertFalse(state)

    def test_run4(self):
        state = self.action.run(None, 0.5, 0)
        self.assertTrue(self.value)
        self.assertFalse(state)

    def test_run5(self):
        state = self.action.run(None, 1, 0.5)
        self.assertTrue(self.value)
        self.assertFalse(state)

    def test_run6(self):
        state = self.action.run(None, 1.5, 1)
        self.assertTrue(self.value)
        self.assertFalse(state)

    def test_zero(self):
        action = TimedAction(0, 0, self.function)

        state = action.run(None, 0, -1)
        self.assertTrue(self.value)
        self.assertFalse(state)

        state = action.run(None, 1, 0)
        self.assertTrue(self.value)
        self.assertTrue(state)
