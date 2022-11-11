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

        self.index=0
        query_string=copy.deepcopy(self.QUERY_STRING)

        


        

