import unittest
from smtm import SimulationDataProvider

class SimulationDataProviderIntegrationTest(unittest.TestCase):

    def test_ITG_get_info_use_server_data_without_end(self):
        dp=SimulationDataProvider()
        return_value=dp.initialize_simulation(count=50)

        # 만약 데이터가 초기화 되지 않았다면
        if dp.is_initialized is not True:
            self.assertEqual(dp.get_info(), None)
            self.assertEqual(return_value, None)
            # if 문 안에서 return 되면 다음 if 밖 코드들 실행 X
            return
        
        # 초기화가 잘 됐으면 위 if문을 그냥 건너띄어서 올 예정
        info=dp.get_info()
        self.assertEqual("market" in info, True)
        self.assertEqual("date_time" in info, True)
        self.assertEqual("opening_price" in info, True)
        self.assertEqual("high_price" in info, True)
        self.assertEqual("low_price" in info, True)
        self.assertEqual("closing_price" in info, True)
        self.assertEqual("acc_price" in info, True)
        self.assertEqual("acc_volume" in info, True)
        self.assertEqual(dp.is_initialized, True)
        self.assertEqual(len(dp.data), 50)

    def test_ITG_get_info_use_server_data(self):
        dp=SimulationDataProvider()
        end_date='2020-04-30T16:30:00'
        return_value = dp.initialize_simulation(end=end_date, count=50)

        # 만약 데이터가 초기화 되지 않았다면
        if dp.is_initialized is not True:
            self.assertEqual(dp.get_info(), None)
            self.assertEqual(return_value, None)
            # if 문 안에서 return 되면 다음 if 밖 코드들 실행 X
            return

        # 첫번째 데이터 가져오기
        info = dp.get_info()
        # 우선 데이터를 형식에 맞게 잘 가져왔다는 Test
        self.assertEqual("market" in info, True)
        self.assertEqual("date_time" in info, True)
        self.assertEqual("opening_price" in info, True)
        self.assertEqual("high_price" in info, True)
        self.assertEqual("low_price" in info, True)
        self.assertEqual("closing_price" in info, True)
        self.assertEqual("acc_price" in info, True)
        self.assertEqual("acc_volume" in info, True)
        self.assertEqual(dp.is_initialized, True)
        self.assertEqual(len(dp.data), 50)

        # 첫번째 data 실제 확인
        self.assertEqual(info["market"], "KRW-BTC")
        self.assertEqual(info["date_time"], "2020-05-01T00:40:00")
        self.assertEqual(info["opening_price"], 10662000.0)
        self.assertEqual(info["high_price"], 10676000.0)
        self.assertEqual(info["low_price"], 10662000.0)
        self.assertEqual(info["closing_price"], 10675000.0)
        self.assertEqual(info["acc_price"], 3411043.24676)
        self.assertEqual(info["acc_volume"], 0.31962699)

        # 두번째 data 확인
        info=dp.get_info()
        self.assertEqual(info["market"], "KRW-BTC")
        self.assertEqual(info["date_time"], "2020-05-01T00:41:00")
        self.assertEqual(info["opening_price"], 10675000.0)
        self.assertEqual(info["high_price"], 10676000.0)
        self.assertEqual(info["low_price"], 10675000.0)
        self.assertEqual(info["closing_price"], 10676000.0)
        self.assertEqual(info["acc_price"], 5225724.98887)
        self.assertEqual(info["acc_volume"], 0.48951155)