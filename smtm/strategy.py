"""데이터 기반으로 매매 결정을 생성하는 Strategy 추상클래스"""
from abc import ABCMeta, abstractmethod

class Strategy(metaclass=ABCMeta):
    """
    데이터 받아서 매매 판단하고 결과를 받아 다음 판단에 반영하는 전략 클래스
    """

    @abstractmethod
    def initialize(self, budget, min_price=100):
        """예산을 설정하고 초기화"""

    @abstractmethod
    def get_request(self):
        """
        전략에 따라 거래 요청 정보를 생성

        Returns: 배열에 한개 이상의 요청 정보를 전달
        [{
            "id": 요청정보 id "1607862457.560075"
            "type": 거래 유형 sell, buy, cancle
            "price": 거래 가격
            "amount": 거래 수량
            "date_time": 요청 데이터 생성 시간, 시뮬레이션 모드에서는 데이터 시간
        }]
        """
