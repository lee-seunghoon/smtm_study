import unittest
from smtm_test import TddExercise
from unittest.mock import *

class TddExerciseIntegrationTests(unittest.TestCase):
    def setup(self):
        pass

    def tearDown(self):
        pass

    def test_initialize_correctly(self):
        ex=TddExercise()

        ex.to="2022-10-31T09:30:00Z"
        ex.count=60

        ex.initialize_from_server()

        self.assertEqual(len(ex.data), 60)
        self.assertEqual(ex.data[0]['candle_date_time_utc'], "2022-10-31T09:29:00")
        self.assertEqual(ex.data[-1]['candle_date_time_utc'], "2022-10-31T08:30:00")