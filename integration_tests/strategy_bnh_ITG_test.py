import os
import sys
import unittest
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from smtm.strategy_bnh import StrategyBuyAndHold

class StrategyBuyAndHoldTests(unittest.TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

    def test_ITG_get_request_after_update_info_and_result(self):
        strategy=StrategyBuyAndHold()

        # 초기화 전 정보를 요청하면 None 값을 반환
        self.assertEqual(strategy.get_request(), None)
        
        # 거래정보 초기화
        # 자산 500,000원 / 최소 거래 가격 5,000원
        strategy.initialize(budget=500000, min_price=5000)
        self.assertTrue(strategy.is_initialized)

        # 거래 정보 입력 - 1
        first_info={
            'market': 'KRW-BTC',
            'date_time': '2022-11-18T12:15:00',
            'opening_price': 22995000.0,
            'high_price': 23011000.0,
            'low_price': 22988000.0,
            'closing_price': 23011000.0,
            'acc_price': 26713154.14605,
            'acc_volume': 1.16127833
        }
        strategy.update_trading_info(first_info)
        self.assertEqual(strategy.data[0]['date_time'], '2022-11-18T12:15:00')

        # 거래 요청 정보 생성
        self.assertTrue(strategy.is_initialized)
        req=strategy.get_request()
        expected_result={
            "type":"buy",
            "price":23011000.0,
            "amount":0.0043
        }
        self.assertEqual(req[0]['type'], expected_result['type'])
        self.assertEqual(req[0]['price'], expected_result['price'])
        self.assertEqual(req[0]['amount'], expected_result['amount'])

        # 거래 결과 입력 - 정상 체결
        strategy.update_result(
            {
                "request":{
                    "id":req[0]['id'],
                    "type":"buy",
                    "price":23011000.0,
                    "amount":0.0043,
                    "date_time":"2022-11-18T12:15:00"
                },
                "type": "buy",
                "price": 23011000.0,
                "amount": 0.0043,
                "msg": "success",
                "balance": 0,
                "state": "done",
                "date_time": "2022-11-18T12:15:00"
            }
        )
        self.assertEqual(strategy.balance, 401003)

        #############################################

        """
        위 test 다음 거래 정보 세팅
        거래 요청 정보가 체결되지 않는 상황
        거래 결과가 'state':'requested' 상태로서
        거래가 체결되지 않았기 때문에 잔고 변수도 변화가 없어야 한다
        """
        # 2번째 거래 정보 업데이트
        second_info={
            'market': 'KRW-BTC', 
            'date_time': '2022-11-18T12:16:00', 
            'opening_price': 23188000.0, 
            'high_price': 23191000.0, 
            'low_price': 23176000.0, 
            'closing_price': 23178000.0, 
            'acc_price': 48185208.39304, 
            'acc_volume': 2.07831266
        }
        strategy.update_trading_info(second_info)

        # 거래 요청 정보 생성
        req=strategy.get_request()
        expected_request={
            'type': 'buy', 
            'price': 23178000.0, 
            'amount': 0.0043, 
        }
        self.assertEqual(req[0]['type'], expected_request['type'])
        self.assertEqual(req[0]['price'], expected_request['price'])
        self.assertEqual(req[0]['amount'], expected_request['amount'])

        # 거래 결과 입력 - 요청됐지만 체결 안 됨