"""
DataProvider 추상클래스
거래 관련 데이터 수집 후 필요한 데이터 포맷에 맞게 정보 제공
"""
from abc import ABCMeta, abstractmethod

class DataProvider(metaclass=ABCMeta):
    """
    데이터 수집 후 정보 제공하는 추상 클래스
    """

    # 상속 받는 클래스에서 해당 메서드를 구현하도록 강제
    @abstractmethod
    def get_info(self):
        """
        현재 거래 정보 딕셔너리로 전달

        Returns: 거래 정보 딕셔너리
        {
            "market": 거래 시장 종류 BTC
            "data_time": 정보의 기준 시간
            "opening_price": 시작 거래 가격
            "high_price": 최고 거래 가격
            "low_price": 최저 거래 가격
            "closing_price": 마지막 거래 가격
            "acc_price": 단위 시간 내 누적 거래 가격
            "acc_volume": 단위 시간 내 누적 거래량
        }
        """