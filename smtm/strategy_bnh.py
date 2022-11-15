import copy
import time
from datetime import datetime, time
from . import Strategy, LogManager

class StrategyBuyAndHold(Strategy):
    """
    분할 매수 후 홀딩하는 가벼운 전략

    isInitialized: 최초 잔고는 초기화 할 때만 갱신 된다
    data: 거래 데이터 리스트, OHLCV 데이터
    result: 거래 요청 결과 리스트
    request: 마지막 거래 요청
    budget: 시작 잔고
    balance: 현재 잔고
    min_price: 최소 주문 금액
    """

    ISO_DATEFORMAT = "%Y-%m-%dT%H:%M:%S"
    COMMISSION_RATIO = 0.0005

    def __init__(self):
        self.is_intialized = False
        self.is_simulation = False
        self.data = []
        self.budget = 0
        self.balance = 0.0
        self.min_price = 0
        self.result = []
        self.request = None
        self.logger = LogManager.get_logger(__class__.__name__)
        self.name = "BnH"
        self.waiting_requests = {}

    def get_request(self):
        """
        데이터 분석 결과에 따라 거래 요청 정보를 생성한다
        5번에 걸쳐 분할 매수 후 홀딩하는 전략
        마지막 종가로 처음 예산의 1/5에 해당하는 양 만큼 매수시도
        Returns: 배열에 한 개 이상의 요청 정보를 전달
        [{
            "id": 요청 정보 id "1607862457.560075"
            "type": 거래 유형 sell, buy, cancel
            "price": 거래 가격
            "amount": 거래 수량
            "date_time": 요청 데이터 생성 시간, 시뮬레이션 모드에서는 데이터 시간
        }]
        """
        if self.is_intialized is not True:
            return None

        try:
            if len(self.data)==0 or self.data[-1] is None:
                raise UserWarning("data is empty")
            last_closing_price=self.data[-1]['closing_price']
            # 현재 date
            now=datetime.now().strftime(self.ISO_DATEFORMAT)

            if self.is_simulation:
                now=self.data[-1]['date_time']
            
            target_budget=self.budget/5
            # 목표한 예산이 현재 잔고보다 많을 경우
            if target_budget>self.balance:
                target_budget=self.balance

        except (ValueError, KeyError) as msg:
            self.logger.error(f"invalid data {msg}")
        except IndexError:
            self.logger.error("empty data")
        except AttributeError as msg:
            self.logger.error(msg)
        except UserWarning as msg:
            self.logger.info(msg)
            if self.is_simulation:
                return [{
                    "id":str(round(time.time(),3)),
                    "type":"buy",
                    "price":0,
                    "amount":0,
                    "date_time":now
                }]
            return None
