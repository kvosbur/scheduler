from enum import Enum, auto
from datetime import datetime, timedelta
from typing import Dict, Any

from _scheduler.timemodule import TimePeriod


class EType(Enum):
    COUNSELOR = auto()
    FRONT_DESK = auto()


class RType(Enum):
    GH = auto()
    SC = auto()
    CH = auto()


class Shift(TimePeriod):
    def __init__(self, st: int, et: int):
        super().__init__(st, et)
        hours = self.dur // timedelta(hours=1)
        if hours > 5:
            self.break_length = timedelta(hours=1)
        else:
            self.break_length = timedelta(hours=.5)


class Staff:
    def __init__(self, name: str, emp_type: EType, st: int = None,
                 et: int = None, shift: Shift = None,):
        if shift:
            self.shift = shift
        else:
            self.shift = Shift(st, et)
        self.name = name
        self.emp_type = emp_type

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'Staff("{self.name}", {self.emp_type}, Shift={self.shift})'

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.name == other.name
    
    def __hash__(self):
        return hash(self.name)

    def _get_possible_break_periods(self):
        emp_shift = self.shift
        break_length = emp_shift.break_length
        shifts = []
        i = emp_shift.st + break_length
        while i <= emp_shift.et:
            shifts.append(Shift(i-break_length, i))
            i += .5
        return shifts

    def _coincides(self, shift: Any) -> bool:
        """ This function determins whether the staff object's
        shift happens within the same time as another TimePeriod
        returns true if it does, and false if it doesn't."""
        if type(shift) == Staff:
            shift = shift.shift
        elif type(shift) == Room:
            shift = shift.time_open
        coincides = self.shift._coincides(shift)
        return coincides

    def _is_available(self, shift: Any) -> bool:
        """ This function determins whether the staff object's
        shift contains the entire period. If it does, then the staff
        is available"""
        if type(shift) == Staff:
            shift = shift.shift
        elif type(shift) == Room:
            shift = shift.time_open
        is_available = self.shift._contains(shift)
        return is_available


class Room:
    def __init__(self, name: RType):
        room_info = self._room_assignment(name)
        self.name = name

    def _room_assignment(self, name: RType) -> Dict[str, Any]:
        times = [datetime(1, 1, 1, 9, 30),
                 datetime(1, 1, 1, 21, 0),
                 datetime(1, 1, 1, 14, 30, 0)]

        if name == RType.CH:
            self.max_cap = 2
            self.time_open = TimePeriod(times[0], times[2])
        elif name == RType.GH:
            self.max_cap = 3
            self.time_open = TimePeriod(times[0], times[1])
        elif name == RType.SC:
            self.max_cap = 1
            self.time_open = TimePeriod(times[0], times[2])


if __name__ == "__main__":

    # tplist1 = []
    # tplist2 = []
    # tplist3 = []

    # for i in range(5):
    #     tplist1.append(Shift(i, i+1))
    #     tplist2.append(Shift(i, i+1))
    #     tplist3.append(Shift(i*10, i+1))

    # print(tplist1 == tplist2)  # should return true because they have the same start and end times

    # print(tplist2 == tplist3)  # these two should return false
    # print(tplist3 == tplist1)  # because they don't have the same start and end time

    # new1 = Shift(1, 4)
    # new2 = Shift(2, 5)
    # new3 = Shift(6, 10)

    # print(is_conflict(new1, new2))  # should have a conflict
    # print(is_conflict(new1, new3))  # should've have a conflict

    shift1 = Shift(12, 20)
    print(shift1.comp)
    isaac = Staff("Isaac", EType.COUNSELOR, shift=shift1)
    shift_set = isaac.get_possible_break_periods()
    for s in shift_set:
        print(str(s))  # prints out all available shifts for this time

    # first_shift = Shift(8,12)
    # isaac = Staff("Isaac", EType.FRONT_DESK, shift=first_shift)
    # print(isaac.name)
    """
    The plan for the algorithm is to get the list of all possible break time for all shifts
    and maybe use genetic algorithms to see which one is the best one?
    """

    # Need to give shifts ranks so that the algorithm is more inclined to give shifts
    # closer to the middle of their shift
