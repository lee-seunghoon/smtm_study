"""
시뮬레이션을 위한 DataProvider 구현체
"""

import copy
import requests
from . import DataProvider
from . import LogManager

class SimulationDataProvider(DataProvider):
    """
    업비트 거래소로부터 과거 데이터를 수집해서 순차적으로 데이터 제공
    업비트의 OpenAPI -> 별도의 가입, 인증, token 없이 사용 가능
    https://docs.upbit.com/reference#%EC%8B%9C%EC%84%B8-%EC%BA%94%EB%93%A4-%EC%A1%B0%ED%9A%8C
    """

    URL="https://api.upbit.com/v1/candles/minutes/1"
    QUERY_STRING={"market":"KRW-BTC"}

    def __init__(self):
        self.logger=LogManager.get_logger(__class__.__name__)
        self.is_initialized=False
        self.data=[]
        self.index=0

    def initialize_simulation(self, end=None, count=100):
        """
        Upbit OpenAPI 사용하여 데이터 가져온 후 초기화
        """

        # index 초기화
        self.index=0
        query_string=copy.deepcopy(self.QUERY_STRING)

        if end is not None :
            query_string['to']=end

        query_string['count']=count

        try:
            res=requests.get(self.URL, params=query_string)
            res.raise_for_status()
            self.data=res.json()
            self.data.reverse()
            self.is_initialized=True
            self.logger.info(f"data is updated from server # end: {end}, count: {count}")
        # 전달 받은 데이터가 json 형식이 아닐때 에러 발생
        except ValueError as error:
            self.logger.error("Invalid data from server")
            raise UserWarning("Fail get data from server") from error
        # 서버에서 http 상태 코드로 오류 전달할 때 에러 발생
        except requests.exceptions.HTTPError as error:
            self.logger.error(error)
            raise UserWarning("Fail get data from server") from error
        except requests.exceptions.RequestException as error:
            self.logger.error(error)
            raise UserWarning("Fail get data from server") from error

    def get_info(self):
        """순차적으로 거래 정보 전달한다
        Returns: 거래 정보 딕셔너리
        {
            "market": 거래 시장 종류 BTC
            "date_time": 정보의 기준 시간
            "opening_price": 시작 거래 가격
            "high_price": 최고 거래 가격
            "low_price": 최저 거래 가격
            "closing_price": 마지막 거래 가격
            "acc_price": 단위 시간내 누적 거래 금액
            "acc_volume": 단위 시간내 누적 거래 양
        }
        """

        # 현재 순번
        now=self.index
        # 데이터의 개수가 현재 순번과 비교해서 작거나 같으면, 새로운 데이터를 가져오지 않았다는 의미
        if now >= len(self.data):
            return None

        # 새로운 데이터 가져오기 전에 index 갱신
        # get_info 메서드가 호출될 때마다 다음 데이터를 전달
        self.index=now+1
        self.logger.info(f'[DATA] @ {self.data[now]["candle_date_time_utc"]}')
        return self.__create_candle_info(self.data[now])

    # class의 메서드 명 앞에 __(언더바 2개)로 시작하면 privat 메서드를 의미
    def __create_candle_info(self, data):
        """
        Upbit에서 가져온 데이터 요구사항에 맞게 수정
        데이터의 형식을 바꾸는 이유는 다른 거래소에서 데이터 가져올 때
        각 변수명이 거래소마다 달라서 통일하기 위한 용도 (이후 확장성 고려)
        이해하기 쉬운 변수명으로 변경하고, 불필요한 데이터 제거, 필요한 데이터만 전달
        """
        try:
            return {
                "market":data["market"],
                "date_time":data['candle_date_time_kst'],
                "opening_price":data['opening_price'],
                "high_price":data["high_price"],
                "low_price":data["low_price"],
                "closing_price":data["trade_price"],
                "acc_price":data["candle_acc_trade_price"],
                "acc_volume":data["candle_acc_trade_colume"]
            }
        except KeyError:
            self.logger.warning("invalid data from candle info")
            return None
