"""datetime을 거래 형태에 맞게 변경"""
from datetime import datetime, timedelta


class DataConverter:
    """날짜, 시간 변경해주는 클래스"""
    ISO_DATEFORMAT='%Y-%m-%dT%H:%M:%S'

    @classmethod
    def to_end_min(cls, from_dash_to):
        """
        숫자로 주어진 기간을 분으로 계산해서 마지막 날짜와 분을 반환

        Returns:
            (
                datetime: str, %Y-%m-%dT%H:%M:%S 형태의 datetime
                count: 주어진 기간을 분(minute)으로 변환
            )
        ex)
        to_end_min('200220-200320')
        to_end_min('200220.120015-200320')
        to_end_min('200220-200320.120015')
        to_end_min('200220.120015-200320.235510')
        """
        # ? 왜 count의 default 값이 -1일까?
        count=-1
        # 시작 datetime 과 끝 datetime 분리
        from_to=from_dash_to.split('-')
        # 시작 datetime
        from_dt=cls.num_2_datetime(from_to[0])
        # 끝 datetime
        to_dt=cls.num_2_datetime(from_to[1])
        # 끝 시간이 시작 시간보다 작거나 같다면
        if to_dt <= from_dt:
            return None
        # delta time == 주어진 기간
        delta=to_dt - from_dt
        # 분(minute) 단위로 변환
        count=round(delta.total_seconds()/60.0)
        return cls.to_iso_string(to_dt), count

    @classmethod
    def num_2_datetime(cls, num_string):
        """
        숫자로 주어진 시간을 datetime 객체로 변환 후 반환
        2가지 형태 지원 -> yymmdd , yymmdd.HHMMSS
        num_2_datetime('221217')
        num_2_datetime('221217.165950')
        """
        num_string=str(num_string)
        if len(num_string)==6:
            return datetime.strptime(num_string, '%y%m%d')
        if len(num_string)==13:
            return datetime.strptime(num_string, '%y%m%d.%H%M%S')

        # 에러 처리
        raise ValueError("Unsupport number string")

    @classmethod
    def to_iso_string(cls, dt):
        """datetime 객체를 %Y-%m-%dT%H:%M:%S 형태의 문자열로 변환하여 반환"""
        return dt.strftime(cls.ISO_DATEFORMAT)

    @classmethod
    def from_kst_to_utc_str(cls, datetime_str):
        """%Y-%m-%dT%H:%M:%S 형태에서 9시간 뺀 문자열 반환"""
        dt = datetime.strptime(datetime_str, cls.ISO_DATEFORMAT)
        dt -= timedelta(hours=9)
        return dt.strftime(cls.ISO_DATEFORMAT)