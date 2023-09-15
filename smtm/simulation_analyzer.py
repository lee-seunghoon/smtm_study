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
        # 시뮬레이션 상황이고, 거래 정보 리스트에 데이터가 있으면, 해당 거래 정보 리스트 중 제일 최근 데이터의 date time을 사용한다.
        if self.is_simulation is True and len(self.trading_info_list) > 0:
            new_asset['date_time'] = self.trading_info_list[-1]['date_time']
        self.asset_info_list.append(new_asset)
        self.make_score_record(new_asset)   # 자산 정보를 바탕으로 수익률을 계산해서 결과로 도출된 내용을 저장한다.

    def make_score_record(self, new_info: dict):
        """
        수익률 기록 저장

        new_info : 자산 정보
            {
                balance: 계좌 현금 잔고, float
                asset(dict type): 자산 목록, 마켓 이름 -> key , (평균매입가격, 수량) -> value
                quote: 종목별 현재 가격, dict
            }

        return:
            score_record:
                balance: 계좌 현금 잔고
                cumulative_return: 기준 시점부터 누적 수익률
                price_change_ratio: 기준 시점부터 보유 종목별 가격 변동률. (dict)
                asset: 자산 정보. (tuple, list) => (종목, 평균 가격, 현재 가격, 수량, 수익률(소수점 3자리))
                date_time: 데이터 생성 시간, 시뮬레이션 모드에서는 데이터 시간
                kind: 3, 보고서를 위한 데이터 종류류
        """

        try:
            start_total=self.__get_start_property_value()   # 시작 시점의 자산 총액
            start_quote=self.asset_info_list[0]["quote"]    # 시작 시점의 시세 정보
            current_total=float(new_info["balance"])        # 현시점의 자산 총액
            current_quote=new_info["quote"]                 # 현시점의 시세 정보
            cumulative_return = 0   # 누적 수익률 초기화
            new_asset_list=[]
            price_change_ratio={}
            self.logger.debug(f"make_score_record new_info : {new_info}")

            # 현재까지 축적된 자산의 모든 정보를 for문으로 불러와 수익률 계산
            # 자산의 현시점 수익률, 가격 변동률, 전체 자산 총액 도출
            for name, item in new_info["asset"].items():
                item_yield = 0          # 현재 자산의 수익률 정의(초기화)
                amount = float(item[1]) # 현재 불러온 자산(주식)의 총량
                buy_avg = float(item[0]) # 현재 불러온 자산(주식)의 평균 매입 가격
                price = float(current_quote[name])  # 현재 종목의 가격
                current_total += amount * price     # 전체 자산 총액 모두 더하기
                item_price_diff = price - buy_avg   # 시세 대비 평균 매입가격의 차이

                # 보유한 자산의 현재 수익률 계산 (소수점 3자리)
                if item_price_diff != 0 and buy_avg != 0:
                    item_yield = round((price - buy_avg) / buy_avg * 100, 3)

                self.logger.debug(
                    f"yield record {name}\n buy_avg: {buy_avg} \n price: {price} \n amount: {amount} \n item_yield: {item_yield}"
                )

                # 현재 수익률까지 포함해서 자산 정보 추가
                new_asset_list.append((name, buy_avg, price, amount, item_yield))
                start_price = start_quote[name] # 현재 종목의 시작 시점의 가격
                price_change_ratio[name]=0      # 시세 변경률 업데이트 위한 초기화
                price_diff = price - start_price# 현재 시세와 시작 시점의 시세 차이
                if price_diff != 0:
                    price_change_ratio[name] = round(price_diff / start_price * 100, 3)   # 시세 변경률 업데이트

                self.logger.debug(
                    f"price change ratio : {start_price} -> {price}, {price_change_ratio}%"
                )

                # 현시점 자산 총액 - 시작 시점 자산 총액
                total_diff = current_total - start_total
                if total_diff != 0 :
                    # 누적 수익률
                    cumulative_return = round(total_diff / start_total * 100, 3)
                self.logger.info(
                    f"cumulative_return {start_total} -> {current_total}, {cumulative_return}%"
                )

                # 현재 수익률 및 자산 정보 저장
                self.score_list.append(
                    {
                        "balance": float(new_info["balance"]),
                        "cumulative_return": cumulative_return,
                        "price_change_ratio": price_change_ratio,
                        "asset": new_asset_list,
                        "date_time": new_info['date_time'],
                        "kind": 3
                    }
                )

        except (IndexError, AttributeError) as msg:
            self.logger.error(f"making score record fail : {msg}")
