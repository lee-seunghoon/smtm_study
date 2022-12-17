"""시뮬레이션용 가상 거래 처리"""
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