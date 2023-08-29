import copy
import os
from log_manager import LogManager

class Analyzer:
    """
    (거래 요청) / (거래 결과 정보) '저장' 및 '결과 분석' 클래스

    Attributes:
        request_list: 거래 요청 목록
        result_list: 거래 결과 목록
        trading_info_list: 거래 정보 목록
        asset_info_list: 특정 시점에 기록된 자산 정보 목록
        score_list: 특정 시점에 기록된 수익률 데이터 목록
        get_asset_info_func: 자산 정보 업데이트를 위한 콜백 함수
    """

    ISO_DATEFORMAT = "%Y-%m-%dT%H:%M:%S"
    OUTPUT_FOLDER_NAME = "output"
    global OUTPUT_FOLDER_NAME
    RECORD_INTERVAL = 60    # 기록 주기는 60초
    SMA = (5, 20)

    def __init__(self):
        self.request_list = []
        self.result_list = []
        self.trading_info_list = []
        self.asset_info_list = []
        self.score_list = []
        self.get_asset_info_func = None
        self.logger = LogManager.get_logger(__class__.__name__)
        self.is_simulation = False

        # 결과 데이터 저장할 디렉토리 확인하고 없으면 생성
        if os.path.isdir(OUTPUT_FOLDER_NAME) is False:
            print("Create output folder")
            os.mkdir(OUTPUT_FOLDER_NAME)

    def initialize(self, get_asset_info_func):
        """
        콜백 함수 입력 받아 초기화

        Args:
            get_asset_info_func: 거래 데이터 요청하는 함수로 func(arg1) -> arg1은 정보 타입
        """
        self.get_asset_info_func = get_asset_info_func

    def save_trading_info(self, info: dict):
        """
        거래 정보 저장

        Args:
            info: 거래 정보

        kind: 보고서를 위한 데이터 종류
            0: 거래 데이터
            1: 매매 요청
            2: 매매 결과
            3: 수익률 정보
        """
        new_traiding_data = copy.deepcopy(info)
        new_traiding_data['kind'] = 0   # 거래 데이터라는 의미
        self.trading_info_list.append(new_traiding_data)
        self.make_periodic_record() # 주기적으로 수익률을 기록하기 위한 함수 호출

    def save_request_info(self, requests: list):
        """
        거래 요청 정보를 저장한다

        request:
            {
                "id": 요청 정보 id , str
                "type": 거래 유형 (sell, buy, cancel), str
                "price": 거래 가격, float or str
                "amount": 거래 수량, float or str
                "date_time": 요청 데이터 생성 시간, 시뮬레이션 모드에서는 데이터 시간
            }

        kind: 보고서를 위한 데이터 종류
            0: 거래 데이터
            1: 매매 요청
            2: 매매 결과
            3: 수익률 정보
        """
        for request in requests:
            new_req = copy.deepcopy(request)
            if request['type'] == 'cancel':
                new_req['price'], new_req['amount'] = 0, 0
            else:
                # 거래 요청 데이터에서 가격과 수량이 str 형태로 기록될 때도 있어서 float 형태로 통일 필요
                # type이 cancel이 아닌데 price와 amount가 0보다 작거나 같다면 이상이 있는 것이기 때문에 pass
                origin_price = request['price']
                origin_amount = request['amount']
                if float(origin_price) <= 0 or float(origin_amount) <= 0:
                    continue
                # 이상이 없으면 아래 로직 실행
                new_req['price'] = float(origin_price)
                new_req['amount'] = float(origin_amount)
            new_req['kind'] = 1 # 거래 요청 데이터의 type이 어떻든 현재 저장하려는 데이터 종류 정의
            self.request_list.append(new_req)

    def save_result_info(self, result):
        """
        거래 결과 정보 저장

        result:
            {
                "request": 요청 정보
                "type": 거래 유형
                "price": 거래 가격
                "amount": 거래 수량
                "state": 거래 상태 (requested, done)
                "msg": 거래 결과 메세지
                "date_time": 시뮬레이션 모드에서는 데이터 시간
            }
        """
        origin_price = result['price']
        origin_amount = result['amount']

        # 거래 결과 정보 중 가격이나 수량이 0인 경우 저장 X
        try:
            if float(origin_price) <= 0 or float(origin_amount) <= 0:
                return
        except KeyError:
            self.logger.warning("Invalid result")
            return

        new_result = copy.deepcopy(result)
        new_result['price'], new_result['amount'] = float(origin_price), float(origin_amount)
        new_result['kind'] = 2
        self.result_list.append(new_result)
        self.update_asset_info()    # 수익률 업데이트 함수 호출

    def update_asset_info(self):
        """
        자산 정보 저장
        수익률 변동, 자산 변동시 활용

        return:
            {
                balance: 계좌 현금 잔고, float
                asset: 자산 목록, 마켓 이름 -> key / (평균매입가격, 수량) -> value , dict
                quote: 종목별 현재 가격, dict
            }
        """
        if self.get_asset_info_func is None:
            self.logger.warning("get_asset_info_func is NOT SET")
            return

        asset_info = self.get_asset_info_func()
        new_asset = copy.deepcopy(asset_info)
        new_asset['balance'] = float(new_asset['balance'])
        # 시뮬레이션 상황이고, 거래 정보 리스트에 데이터가 있으면, 해당 거래 정보 리스트 중 제일 최근 데이터의 data time을 사용한다.
        if self.is_simulation is True and len(self.trading_info_list) > 0:
            new_asset['date_time'] = self.trading_info_list[-1]['date_time']
        self.asset_info_list.append(new_asset)
        self.make_scroe_record(new_asset)