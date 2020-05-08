from typing import List
from datetime import datetime, timedelta

import scheduler


class TimePeriod:
    """
    This class represents a time period between two points in time.
    The smallest unit of time in this representation is 30mins, and
    each time period is composed of 30 minute intervals.
    ---------------------------------------------------------------
    ++++++++++++++++++++++++ ARGS +++++++++++++++++++++++++++++++++
    ---------------------------------------------------------------
    (int) st: Start Time
    (int) et: End Time

    """
    num = 0

    def __init__(self, st: datetime, et: datetime):
        if et <= st:
            raise scheduler.TimeError(
                "End time needs to be later than start time.")
        self.st = st  # datetime
        self.et = et  # datetime
        self.dur = et - st  # timedelta in seconds
        self.comp = self._get_composition(self.dur)
        self._id = self.update(1)

    def __eq__(self, other):
        """
        Allows one to check equality with instances
            >>> start = datetime(1,1,1,1,30)
            >>> end = datetime(1,1,1,4,30)
            >>> TimePeriod(start, end) == TimePeriod(start, end)
            True
        """
        if isinstance(other, self.__class__):
            return str(self) == str(other)
        return False

    def __str__(self):
        return f'{self.st.strftime("%I:%M %p")} - {self.et.strftime("%I:%M %p")}'

    def __repr__(self):
        return f'{self.__class__}({self.st}, {self.et})'

    def __hash__(self):
        return hash(self._id)

    def _split(self, part: int) -> List:
        """ Split uses the partition argument to split the TimePeriod into
        equal parts by blocks of .5 """
        if part > len(self.comp):
            raise BaseException("Cannot divide time segment into that many parts")

        split_time = []
        part_size = len(self.comp) // part

        for i in range(part):
            if i == (part - 1):
                split_time.append(TimePeriod(self.comp[i * part_size],
                                  self.comp[-1]))
            else:
                split_time.append(TimePeriod(self.comp[i * part_size],
                                  self.comp[(i+1) * part_size]))
        return split_time

    def _contains(self, other_tp):
        if self.st <= other_tp.st and self.et >= other_tp.et:
            return True
        return False

    def _contains_time(self, dt):
        return self.st <= dt < self.et

    def _contains_time_include_end(self, dt):
        return self.st <= dt <= self.et

    def _coincides(self, other):
        return max(self.st, other.st) < min(self.et, other.et)

    def _get_composition(self, duration: timedelta) -> int:
        """ It splits the duration into 30 minute segments and creates/returns a list
        of the 30 minute segments the TimePeriod is composed from"""
        hours = duration.seconds // 3600
        mins = duration.seconds - (hours * 3600)
        quant = hours * 2
        quant = quant + 1 if int(mins) > 0 else quant
        comp = [self.st + i * timedelta(minutes=30) for i in range(quant + 1)]
        return comp

    @classmethod
    def update(cls, value):
        cls.num += value
        return cls.num


if __name__ == "__main__":
    shift1 = TimePeriod(1, 3)
    print(TimePeriod.num)
    shift2 = TimePeriod(1, 3)
    print(TimePeriod.num)
    print(hash(shift1))
    print(hash(shift2))
    print(shift1.comp)
    print(shift2.comp)
    shift_list = shift1.split(3)
    for shift in shift_list:
        print(shift.comp)

