import unittest
from smtm_test import TddExercise
from unittest.mock import *

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

    @patch("requests.get")
    def test_initialize_from_server_update_data_with_empty_data(self, mock_get):
        # mock 사용할 경우 patch 데코레이터를 통해 입력한 메서드를 mock 객체로 전환 가능
        # requests.get -> mock_get

        ex=TddExercise()

        # 가짜 response 결과 값을 설정
        # MagicMock은 호출할 수 있는 메서드 객체를 만드는 데 사용한다.
        dummy_response=MagicMock()
        # requests를 통해 얻는 값이 json 메서드의 반환값으로 ex.data에 저장 되도록 세팅
        dummy_response.json.return_value=[{"market":"apple"}, {"market":"banana"}]
        # mock 객체의 반환값을 위 임의 생성한 response 값을 부여함
        mock_get.return_value=dummy_response

        # Test 시작
        # 업비트로부터 Open API를 통해 얻어온 값이 위에서 설정한 값으로 변경될 예정
        ex.initialize_from_server()
        self.assertEqual(len(ex.data), 2)
        self.assertEqual(ex.data[0], {"market":"apple"})
        self.assertEqual(ex.data[1], {"market":"banana"})

        # mock_get이라는 모의 객체가 정확한 값을 파라미터로 받아서 결과를 출력하고 있는지 확인해야 한다.
        # 이런 test가 없다면 파라미터로 들어가야 하는 값이 기대한 것과 다른 게 들어가도, 정상으로 테스트가 마무리된다.(mock 객체의 특성 때문에)
        
        # mock 객체가 정확한 파라미터 값으로 한번 호출됐는지 검사
        mock_get.assert_called_once_with(ex.URL, params=ANY)
        # mock 객체이 들어간 파라미터(인자) 값을 검증
        # mock 객체가 마지막으로 호출된 인자값
        self.assertEqual(mock_get.call_args[1]['params']['count'], 100)
        self.assertEqual(mock_get.call_args[1]['params']['to'], None)