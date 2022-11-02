# TDD 연습용 모듈

import requests

class TddExercise:
    URL="https://api.upbit.com/v1/candles/minutes/1"
    QUERY_STRING={"market":"KRW-BTC"}

    def __init__(self):
        self.data=[]
        self.to=None
        self.count=100

    def set_period(self, to, count):
        self.to=to
        self.count=count

    def initialize_from_server(self):
        # Open API 활용하여 데이터를 수집한다

        query_string=self.QUERY_STRING
        query_string['to']=self.to
        query_string['count']=self.count

        response=requests.get(self.URL, params=query_string)
        self.data=response.json()

        print(self.data)
        print(self.data[0])