from enum import Enum, auto
from datetime import datetime, timedelta
from typing import Dict, Any, List

from _scheduler.timemodule import TimePeriod


class EType(Enum):
    COUNSELOR = auto()
    FRONT_DESK = auto()


class RType(Enum):
    GH = auto()
    SC = auto()
    CH = auto()


Room_Mapping = {RType.GH: "GreatHall", RType.SC: "Subcellar", RType.CH: "ClubHouse"}


class Shift(TimePeriod):
    def __init__(self, st: datetime, et: datetime):
        super().__init__(st, et)
        hours = self.dur // timedelta(hours=1)
        if hours > 5:
            self.break_length = timedelta(hours=1)
        else:
            self.break_length = timedelta(hours=.5)

    def break_increments(self, time_increment: timedelta):
        return round(self.break_length / time_increment)

    def valid_shift_start(self, start_time: datetime):
        return self._contains_time_include_end(start_time) and self._contains_time_include_end(start_time + self.break_length)


class Staff:
    def __init__(self, name: str, emp_type: EType, st: int = None,
                 et: int = None, shift: Shift = None,):
        if shift:
            self.shift = shift
        else:
            self.shift = Shift(st, et)
        self.name = name
        self.emp_type = emp_type
        self.last_assigned = None

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

    def __repr__(self):
        return f'Room("{self.name}")'

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


class RoomAssignment:
    """
    Keeps track of which employees have been assigned to a given room
    """
    def __init__(self, room: Room):
        self.room = room
        self.staff = []

    def add_staff(self, s:Staff):
        self.staff.append(s)
        print("Insert", s, "into room", self.room, "current cap:", self.curr_cap)

    @property
    def curr_cap(self):
        return len(self.staff)

    @property
    def max_cap(self):
        return self.room.max_cap

    @property
    def time_open(self):
        return self.room.time_open

    def remove_staff(self, s: Staff):
        # assume that staff is in list
        for temp in range(len(self.staff)):
            if s.name == self.staff[temp].name:
                del self.staff[temp]
                break

    def contains_staff(self, s: Staff) -> bool:
        for temp in self.staff:
            if s.name == temp.name:
                return True
        return False


class TimeAssignment:
    """
    Keeps track of the assignments to all rooms at a given time value
    """
    def __init__(self, curr_time: datetime):
        self.curr_time = curr_time
        self.room_assignments = []

    def add_room_assignment(self, room_assignment: RoomAssignment):
        self.room_assignments.append(room_assignment)

    def contains_staff(self, s: Staff) -> bool:
        for room_assignment in self.room_assignments:
            if room_assignment.contains_staff(s):
                return True
        return False

    def fill_spot(self, target_room: RoomAssignment):
        for room_assignment in self.room_assignments:
            if room_assignment.curr_cap > 1:
                room_assignment.staff.sort(key=lambda s: s.last_assigned)
                s = room_assignment.staff.pop(0)
                print("Moving", s, "From", room_assignment.room, "To", target_room.room)
                s.last_assigned = self.curr_time
                target_room.add_staff(s)
                return

    def remove_staff(self, s: Staff):
        for room_assignment in self.room_assignments:
            if room_assignment.contains_staff(s):
                print(s, "is leaving")
                room_assignment.remove_staff(s)
                if room_assignment.curr_cap == 0:
                    self.fill_spot(room_assignment)
                return

    def find_staff_to_swap(self, cutoff: timedelta):
        ret = []
        for index, value in enumerate(self.room_assignments):
            for staff_index, staff in enumerate(value.staff):
                if self.curr_time - staff.last_assigned >= cutoff:
                    ret.append((index, staff_index, staff))
        return ret

    def _do_swap_staff(self, first, second):
        print("Swap from:", first[2], self.room_assignments[first[0]].room, ",",
              second[2], self.room_assignments[second[0]].room)
        temp = first[2]
        self.room_assignments[first[0]].staff[first[1]] = second[2]
        self.room_assignments[second[0]].staff[second[1]] = temp
        first[2].last_assigned = self.curr_time
        second[2].last_assigned = self.curr_time
        print("to:", self.room_assignments[second[0]].staff[first[1]], self.room_assignments[first[0]].room, ",",
              self.room_assignments[second[0]].staff[second[1]], self.room_assignments[second[0]].room)

    def swap_staff(self, cutoff: timedelta):
        staff_to_swap = self.find_staff_to_swap(cutoff)
        amount = len(staff_to_swap)
        if amount > 1:
            staff_to_swap.sort(key=lambda item: item[2].last_assigned)
            index = 0
            while index < amount - 1:
                current_item = staff_to_swap[index]
                if current_item[2].last_assigned == self.curr_time:
                    index += 1
                    continue
                for attempt in range(index +1, amount):
                    new_item = staff_to_swap[attempt]
                    if new_item[2].last_assigned != self.curr_time and new_item[0] != current_item[0]:
                        self._do_swap_staff(current_item, new_item)
                        break
                index += 1

    def get_room_assignment_for_staff(self, staff_name: str):
        for room in self.room_assignments:
            for staff in room.staff:
                if staff.name == staff_name:
                    return Room_Mapping[room.room.name]
        return "-"

    def amount_extra_staff(self):
        amount = 0
        for room in self.room_assignments:
            if room.curr_cap > 1:
                amount += room.curr_cap - 1
        return amount


class Schedule:
    def __init__(self):
        self.time_assignments = []

    def add_time_assignment(self, time_assignement: TimeAssignment):
        self.time_assignments.append(time_assignement)

    def pretty_print_schedule(self):
        time_diff = self.time_assignments[1].curr_time - self.time_assignments[0].curr_time
        # print header
        print("{:>13}".format(""), end="|")
        for room in self.time_assignments[0].room_assignments:
            for i in range(room.max_cap):
                if i == 0:
                    print("{:>10}".format(room.room.name), end="")
                else:
                    print("{:>10}".format(""), end="")
            print("|", end = "")
        print("")

        for time_assignment in self.time_assignments:
            print("{} - {}".format(time_assignment.curr_time.strftime("%H:%M"), (time_assignment.curr_time + time_diff).strftime("%H:%M")), end="|")
            for room in time_assignment.room_assignments:
                for i in range(max(room.max_cap, room.curr_cap)):
                    if i < room.curr_cap:
                        print("{:>10}".format(room.staff[i].name), end="")
                    else:
                        print("{:>10}".format("-"), end="")
                print("|", end="")
            print("")

    def pretty_print_staff_pov(self, all_staff: List[Staff]):
        time_diff = self.time_assignments[1].curr_time - self.time_assignments[0].curr_time
        # print header
        print("{:>13}".format(""), end="|")
        for staff in all_staff:
            print("{:>15}".format(staff.name), end="|")
        print("")

        for time_assignment in self.time_assignments:
            print("{} - {}".format(time_assignment.curr_time.strftime("%H:%M"),
                                   (time_assignment.curr_time + time_diff).strftime("%H:%M")), end="|")
            for staff in all_staff:
                print("{:>15}".format(time_assignment.get_room_assignment_for_staff(staff.name)), end="|")
            print("")

    def print_dp_table(self, dp_table, time_diff):
        for time_assignment in self.time_assignments:
            print(" {} - {} ".format(time_assignment.curr_time.strftime("%H:%M"),
                                   (time_assignment.curr_time + time_diff).strftime("%H:%M")), end="|")
        print("")
        for line in dp_table:
            for entry in line:
                print("{:^15}".format(str(entry)), end="|")
            print("")

    def assign_breaks(self, all_staff: List[Staff]):
        time_diff = self.time_assignments[1].curr_time - self.time_assignments[0].curr_time
        end = [[DPWrapper(t.amount_extra_staff()) for t in self.time_assignments] for staff in range(len(all_staff) + 1)]
        # do 2 sorts instead of making custom comparator
        all_staff.sort(key=lambda staff: staff.shift.st)
        all_staff.sort(key=lambda staff: staff.shift.et)
        [print(staff.__repr__()) for staff in all_staff]

        for j, staff in enumerate(all_staff):
            index = j + 1
            n = staff.shift.break_increments(time_diff)
            for i, time_assignment in enumerate(self.time_assignments):
                if staff.shift.valid_shift_start(time_assignment.curr_time):
                    if end[index - 1][i].cap > 0:
                        temp_cap = end[index - 1][i].cap - 1
                        temp_val = end[index - 1][i].value + 1
                        temp_n = end[index - 1][i].next + [n]
                        if end[index][i].is_better(temp_cap, temp_val, temp_n):
                            end[index][i].update(temp_cap, temp_val, temp_n)

                    elif len(end[index - 1][i].next) > 0:
                        end[index - 1][i].next.sort()
                        temp = end[index - 1][i].next[0]
                        if i + temp < len(self.time_assignments) and staff.shift.valid_shift_start(time_assignment.curr_time + (temp * time_diff)):
                            temp_cap = end[index - 1][i].cap
                            temp_val = end[index - 1][i].value + 1
                            temp_n = end[index - 1][i].decrement_all(temp)
                            temp_n.append(n)
                            temp_cap += DPWrapper.remove_zeros(temp_n)
                            if end[index][i + temp].is_better(temp_cap, temp_val, temp_n):
                                end[index][i + temp].update(temp_cap, temp_val, temp_n)


                            for rest in range(i, i + temp):
                                if end[index][rest].is_better_object(end[index-1][rest]):
                                    end[index][rest].update_object(end[index-1][rest])
                    else:
                        end[index][i].update_object(end[index - 1][i])
        """
        for index, staff in enumerate(all_staff):
            print(index, staff)
        """
        self.print_dp_table(end, time_diff)



class DPWrapper:
    def __init__(self, cap):
        self.cap = cap
        self.value = 0
        self.next = []

    def __repr__(self):
        self.next.sort()
        return f'{self.cap},{self.value},{self.next}'

    def decrement_all(self, decrement: int):
        temp = self.next[1:]
        for i in range(len(temp)):
            temp[i] -= decrement
        return temp

    @staticmethod
    def remove_zeros(given: List[int]):
        index = 0
        count = 0
        while index < len(given):
            if given[index] == 0:
                count += 1
                given.pop(index)
                index -= 1
            index += 1
        return count

    def update(self, cap: int, value: int, n: List):
        self.cap = cap
        self.value = value
        self.next = n

    def update_object(self, obj):
        self.cap = obj.cap
        self.value = obj.value
        self.next = obj.next[:]

    def is_better_object(self, obj):
        return self.is_better(obj.cap, obj.value, obj.next)

    def is_better(self, cap: int, value: int, n: List):
        if value > self.value:
            return True
        elif value < self.value:
            return False
        elif cap > self.cap:
            return True
        elif cap < self.cap:
            return False
        elif sum(n) < sum(self.next):
            return True
        else:
            return False


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
