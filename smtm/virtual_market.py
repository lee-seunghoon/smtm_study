"""
업비트 거래소 과거 거래 정보를 이용한 가상 거래소

가상 거래소 요구사항
1. 거래 정보를 입력 받아서 운영
- 거래 정보를 실제 거래소에서 가져온다.
- 거래 정보 양만큼의 횟수만큼 거래 가능

2. 수수료 비율 설정 가능
- 기본 수수료 비율은 0.05로 설정한다.

3. 거래 요청을 받아, 가상의 거래 체결 결과를 생성한다.
- 보유 자산 상황을 반영하여 거래 요청 정보에 따른 체결량을 결정한다.
- 실제 거래 정보를 바탕으로 체결량과 가격을 산출한다.
- 수수료를 적용한 결과를 생성한다.

4. 현재 자산, 보유 종목 정보 조회 가능
- 거래와 자산의 입출금에 따라 자산, 보유 종목의 내역을 저장

5. 아무 거래 없이 다음 턴으로 넘어갈 수 있음
- 거래 금액 또는 가격이 0일 경우, 해당 턴은 넘어간다.
"""
import copy, requests
from .date_converter import DataConverter
from .log_manager import LogManager


class VirtualMarket:
    """
    거래 요청 정보를 받아서 처리하여 가상 거래 결과 정보를 생성

    return: {
        end: 거래기간 끝
        count: 거래기간까지 가져올 데이터 개수
        data: 사용될 거래 정보 목록
        turn_count: 현재까지 진행된 턴수
        balance: 잔고
        commision_rate: 수수료율
        asset: dict -> 자산 목록, 마켓 이름을 키값으로 갖고 (평균 매입 가격, 수량)을 갖는 dict
    }
    """

    URL="https://api.upbit.com/v1/candles/minute/1"
    QUERY_STRING={"market":"KRW-BTC", "to":"2020-04-30 00:00:00"}

    def __init__(self) -> None:
        self.logger=LogManager.get_logger(__class__.__name__)
        self.is_initialized=False
        self.data=None
        self.turn_count=0
        self.balance=0
        self.commission_ratio=0.0005
        self.asset={}

    def initialize(self, end: str=None, count: int=100, budget: int=0):
        """
        실제 거래소에서 거래 데이터를 가져와서 초기화한다
        
        end: 언제까지의 거래기간 정보를 사용할 것인지에 대한 날짜 시간 정보
        count: 거래기간까지 가져올 데이터 개수
        """

        # 만약 초기화가 돼 있다면 바로 return
        if self.is_initialized:
            return

        # 쿼리 str 복사
        query_str=copy.deepcopy(self.QUERY_STRING)

        # 특정 기간이 설정돼 있다면
        if end is not None:
            # 한국 시간 utc-9 적용 시간으로 변환
            query_str["to"]=DataConverter.from_kst_to_utc_str(end) + "Z"
        # TODO 설정 안한다면 default 값이 "2020-04-30 00:00:00" -> 추후 default값 변경 필요
        else:
            end=query_str["to"]

        # 가져올 데이터 개수 세팅
        query_str['count']=count

        try:
            res=requests.get(self.URL, params=query_str)
            res.raise_for_status()
            # 업비트 거래 정보 데이터
            self.data=res.json()
            # 오름차순 정렬일듯
            self.data.reverse()
            # 잔고 설정
            self.balance=budget
            # 초기화 상태 변환
            self.is_initialized=True
            # log debug
            self.logger.debug(f"Virtual Market is initialized - end:{end}, count:{count}")
        # ! ValueError -> 참조할만한 값이 없거나, 잘못된 값 or type이 인자로 넘어올 때 에러 발생
        except ValueError as e:
            self.logger.error("Invalid data")
            raise UserWarning("ValueError - Fail to get data") from e
        # ! API 통신 메서드가 잘못되면 발생하는 에러로 추청
        except requests.exceptions.HTTPError as e:
            self.logger.error(e)
            raise UserWarning("HTTPError(probably invalid api method) - Fail to get data") from e
        # ! API 통신 과정에서 모든 경우의 에러 처리
        except requests.exceptions.RequestException as e:
            self.logger.error(e)
            raise UserWarning("RequestException - all request error") from e

    def get_balance(self):
        """
        현금 포함 모든 자산 정보 제공

        returns:
            {
                balance: 계좌 현금 잔고
                asset: 자산 목록, 마켓 이름을 키값으로 갖고, (평균 매입 가격, 수량)을 갖는 dict
                quote: 종목별 현재 가격 dict
                date_time: 기준 데이터 시간
            }
        """
        asset_info={
            # 잔고 설정
            "balance":self.balance
        }

        # 종목별 현재가격을 세팅
        quote=None
        try:
            quote={
                # 현재 turn 수의 마켓 -> Key / 거래 가격 -> Value
                self.data[self.turn_count]['market']: self.data[self.turn_count]['trade_price']
            }
            # 
            for name, item in self.asset.items():
                # name : 마켓 이름 / item[0] : 평균 매입 가격 / item[1] : 수량
                self.logger.debug(f"asset item: {name}, item price: {item[0]}, amount: {item[1]}")
        # ? IndexError -> index의 범위를 벗어날 때 반환하는 error
        # ? KeyError -> 딕셔너리 자료구조에서 접근하려는 키값이 없을 대 반환하는 error
        except (KeyError, IndexError) as msg:
            self.logger.error(f"Invalid traiding data {msg}")

        # 자산 목록
        asset_info["asset"] = self.asset
        # 종목별 현재 가격
        asset_info["quote"] = quote
        # 기준 데이터 시간
        asset_info["date_time"] = self.data[self.turn_count]["candle_date_time_kst"]

        return asset_info

    def handle_request(self, request):
        """
        거래 요청을 처리해서 결과 반환

        request: 거래 요청 정보
        Returns:
        result:
            {
                "request": 요청 정보
                "type": 거래 유형 sell, buy, cancel
                "price": 거래 가격
                "amount": 거래 수량
                "state": 거래 상태 requested, done
                "msg": 거래 결과 메세지
                "date_time": 시뮬레이션 모드에서는 데이터 시간
                "balance": 거래 후 계좌 현금 잔고
            }
        """
        # 가상 거래소가 초기화 됐는지 확인
        if self.is_initialized is not True:
            self.logger.error("virtual market is NOT initialized")
            return None
        
        # 현재 턴의 시간
        now = self.data[self.turn_count]["candle_date_time_kst"]
        # 다음 턴으로 갱신
        self.turn_count += 1
        # 다음 턴으로 index 세팅
        next_index = self.turn_count

        # 다음 턴이 없고, 현재가 마지막 턴이라면
        if next_index >= len(self.data) - 1:
            return {
                "request": request,
                "type": request["type"],
                "price": 0,
                "amount": 0,
                "balance": self.balance,
                "msg": "game-over",
                "date_time": now,
                "state": "done",
            }

        # 요청 가격과 수량이 0이라면 거래가 끝났다는 의미
        if request["price"] == 0 or request["amount"] == 0:
            self.logger.warning("turn over")
            return "error!"

        # 실제 요청 type에 따라 요청 처리
        if request["type"] == "buy":
            result = self.__handle_buy_request(request, next_index, now)
        elif request["type"] == "sell":
            result = self.__handle_sell_request(request, next_index, now)
        else:
            self.logger.warning("invalid type request")
            result = "error!"

        return result
        
    def __handle_buy_request(self, request, next_index, dt):
        """
        매수 요청 처리 class
        Return:
            {
                "request": 요청 정보
                "type": 거래 유형 sell, buy, cancel
                "price": 거래 가격
                "amount": 거래 수량
                "state": 거래 상태 requested, done
                "msg": 거래 결과 메세지
                "date_time": 시뮬레이션 모드에서는 데이터 시간
                "balance": 거래 후 계좌 현금 잔고
            }
        """
        # 매수 값 (가격*수량)
        buy_value = request["price"] * request["amount"]
        # 매수 총 값(매수값 + 수수료)
        buy_total_value = buy_value * (1 + self.commission_ratio)
        # 현재 잔고
        old_balance = self.balance

        # 매수하려는 총 값이 잔고보다 크면 거래 X -> error
        if buy_total_value > self.balance:
            self.logger.info("no money")
            return "error!"

        try:
            # 만약 요청 가격이 현재 거래하려는 최저가보다 낮다면 거래 X --> error
            if request["price"] < self.data[next_index]["low_price"]:
                self.logger.info("not matched")
                return "error!"
            
            name = self.data[next_index]["market"]
            # asset값이 있을경우
            if name in self.asset:
                # 가격과 수량을 튜플 형식으로 가지고 있음
                asset = self.asset[name]
                # 거래 수량 업데이트
                new_amount = asset[1] + request["amount"]
                new_amount = round(new_amount, 6)
                # 거래 값 업데이트
                new_value = (request["amount"] * request["price"]) + (asset[0] * asset[1])
                # asset 업데이트 -> (평균 매입 가격, 거래 수량)
                self.asset[name] = (round(new_value / new_amount), new_amount)
            # asset 값이 없을 경우
            else:
                self.asset[name] = (request["price"], request["amount"])

            # 잔고 업데이트
            self.balance -= buy_total_value
            self.balance = round(self.balance)
            # 잔고 상태 print
            self.__print_balance_info("buy", old_balance, self.balance, buy_value)

            return {
                "request": request,
                "type": request["type"],
                "price": request["price"],
                "amount": request["amount"],
                "msg": "success",
                "balance": self.balance,
                "state": "done",
                "date_time": dt,
            }

        except KeyError as msg:
            self.logger.warning(f"internal error {msg}")
            return "error!"

    def __handle_sell_request(self, request, next_index, dt):
        old_balance = self.balance
        try:
            name = self.data[next_index]["market"]
            if name not in self.asset:
                self.logger.info("asset empty")
                return "error!"

            # 매도할 때는 고가를 기준으로 확인
            if request["price"] >= self.data[next_index]["high_price"]:
                self.logger.info("not matched")
                return "error!"
            
            # 매도량
            sell_amount = request["amount"]
            # 요청 매도량이 현재 거래하려는 주식수보다 많으면 매도량을 조정
            if request["amount"] > self.asset[name][1]:
                sell_amount = self.asset[name][1]
                self.logger.warning(
                    f"sell request is bigger than asset {request['amount']} > {sell_amount}"
                )
                del self.asset[name]
            # 그렇지 않다면 매도 요청 세팅
            else:
                new_amount = self.asset[name][1] - sell_amount
                new_amount = round(new_amount, 6)
                # 자산 정보 업데이트
                self.asset[name] = (
                    self.asset[name][0], # -> 평균 가격
                    new_amount, # -> 새로운 코인 수량
                )

            # 매도 값
            sell_value = sell_amount * request["price"]
            # 잔고 업데이트 (거래 수수료를 뺀 최종 거래 값이 잔고에 더해짐)
            self.balance += sell_value * (1 - self.commission_ratio)
            self.balance = round(self.balance)
            # 현재 잔고 상태 print
            self.__print_balance_info("sell", old_balance, self.balance, sell_value)

            return {
                "request": request,
                "type": request["type"],
                "price": request["price"],
                "amount": sell_amount,
                "msg": "success",
                "balance": self.balance,
                "state": "done",
                "date_time": dt,
            }
        except KeyError as msg:
            self.logger.error(f"invalid trading data {msg}")
            return "error!"

    def __print_balance_info(self, trading_type, old, new, total_asset_value):
        """현재 잔고 정보 출력"""
        # 거래 이전 잔고 정보
        self.logger.debug(f"[Balance] from {old}")
        # 매수 시
        if trading_type == "buy":
            self.logger.debug(f"[Balance] - {trading_type}_asset_value {total_asset_value}")
        # 매도 시
        elif trading_type == "sell":
            self.logger.debug(f"[Balance] + {trading_type}_asset_value {total_asset_value}")
        # 수수료가 반연된 잔고
        self.logger.debug(f"[Balance] - commission {total_asset_value * self.commission_ratio}")
        # 현재 잔고
        self.logger.debug(f"[Balance] to {new}")