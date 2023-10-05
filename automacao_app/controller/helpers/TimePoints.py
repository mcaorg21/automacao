from datetime import timedelta, datetime as dt
from time import sleep
from typing import Dict


class TimePoints:
    def __init__(self):
        self.__time_points: Dict[str, float] = {}
        self.__point: int = 0

    @property
    def points(self) -> Dict[str, float]:
        return self.__time_points

    def set_time_point(self, name: str):
        if name in self.__time_points:
            return -1
        self.__time_points[name] = self.create_time_point()

    def update_time_point(self, name: str):
        self.__time_points[name] = self.create_time_point()

    def time_diff(self, ptf, pt1) -> float:
        return self.points[ptf] - self.points[pt1]

    def clear_points(self):
        self.__time_points: Dict[str, int] = {}

    def elapsed_since(self, timePt: str) -> float:
        return self.create_time_point() - self.points[timePt]

    @staticmethod
    def create_time_point() -> float:
        return timedelta(
            days=dt.now().day, hours=dt.now().hour,
            minutes=dt.now().minute, seconds=dt.now().second).total_seconds()

    def __repr__(self):
        return f"TimePoints: {self.points}"
