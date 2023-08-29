"""
시뮬레이션용 가상 거래 처리
거래소를 대신하여 매매 요청을 가상으로 처리할 수 있는 모듈

trader와 virtual market은 엄연히 다른 기능을 수행하는 독립적인 모듈로 구성한다.
Trader 모듈을 통해서 업비트, 코빗, 코인원, 빗썸 등 다양한 거래소에 맞게 교체할 수 있다.
거래 관련 기능 및 동작은 모두 Trader에서 이뤄진다.

Trader 모듈의 요구사항
1. 가상 거래소 초기화(시뮬레이션에서만 필요, 기간/횟수/예산 등 거래관련 중요 정보 초기화)
2. 거래소에 거래 요청을 전달하고, 요청에 대한 결과를 받아서 출력
3. 거래소에 계좌 정보를 요청하고, 결과를 받아서 출력

시뮬레이션, 가상 거래소의 한계
1. 과거 데이터 기반
2. 실제 환경을 제대로 반영하기 어려움 (과거 데이터 기반으로 현재 action을 취하는 가상 거래가 앞으로 나올 데이터에 영향을 미치지 않는다.)
   즉, 모두 과거 기반의 데이터이기 때문에 데이터가 정해져 있다.
"""
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from .log_manager import LogManager
from smtm_abs.trader import Trader
from .virtual_market import VirtualMarket

class SimulationTrader(Trader):
    """
    거래 요청 정보를 받아서 거래소에 요청하고 거래소에서 받은 결과를 제공해주는 클래스

    id: 요청 정보 id "1607862457.560075"
    type: 거래 유형 sell, buy, cancel
    price: 거래 가격
    amount: 거래 수량
    """

    def __init__(self):
        self.logger = LogManager.get_logger(__class__.__name__)
        self.market = VirtualMarket()
        self.is_initialized = False
        self.name = "Simulation"

    def initialize_simulation(self, end: str, count: int, budget: int):
        """가상 거래소의 기간, 횟수, 예산을 초기화 한다"""
        self.market.initialize(end, count, budget)
        self.is_initialized = True