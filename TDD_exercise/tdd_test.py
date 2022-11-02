import unittest
from smtm_test import TddExercise

class TddExerciseTests(unittest.TestCase):

    def test_set_period_update_period(self):
        ex=TddExercise()

        # default value 확인
        self.assertEqual(ex.to, None)
        self.assertEqual(ex.count, 100)

        # update period
        ex.set_period('2022-02-21T09:30:00Z', 10)

        # chekck update value
        self.assertEqual(ex.to, '2022-02-21T09:30:00Z')
        self.assertEqual(ex.count, 10)

    def test_initialize_from_server_update_data(self):
        ex=TddExercise()

        # 실행 전 Test
        self.assertEqual(len(ex.data), 0)

        ex.initialize_from_server()
        # 실행 후 Test
        self.assertEqual(len(ex.data), 100)