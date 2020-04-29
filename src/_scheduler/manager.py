""" This module contains manager classes that are responsible for
assigning staff to rooms based on the required hard conditions"""
from collections import defaultdict
from copy import deepcopy
from typing import List, Dict

from _scheduler.work import Room, Staff, RType, EType, Shift
from _scheduler.timemodule import TimePeriod


class Manager():
    def __init__(self, staff: List):
        self.staff = staff

    def manage(self):
        raise NotImplementedError()


class RoomManager(Manager):
    def __init__(self, room: Room, staff: List):
        super().__init__(staff)
        self.room = room

    def manage(self) -> (List[TimePeriod], List[List[Staff]]):
        available_staff = []
        staff = self._get_available_staff(self.staff)
        while(True):
            if self._is_enough_coverage(staff):
                breakdown = self._get_breakdown(staff)
                result = self._verify_breakdown(breakdown, len(staff))
                if result:
                    return self.get_possible_shifts(breakdown)
                else:
                    staff = self._remove_extra_staff(breakdown)
            else:
                return {}
    
    def _get_available_staff(self, staff: List):
        """ Given a list of staff, this checks to see which
        ones are available """
        avail_staff = []
        for s in staff:
            if s._is_coincides(self.room):
                avail_staff.append(s)
        return avail_staff

    def _get_breakdown(self, staff: List) -> Dict[TimePeriod, List[Staff]]:
        room_schedule = defaultdict(list)
        avail_staff = self._get_available_staff(staff)
        num_of_staff = len(avail_staff)
        split_times = self.room.time_open._split(num_of_staff)
        for time in split_times:
            for staff in avail_staff:
                if staff._is_available(time):
                    room_schedule[time].append(staff)
        return room_schedule

    def _verify_breakdown(self,
                          breakdown: Dict[TimePeriod, List[Staff]],
                          expected: int) -> bool:
        valid_staff = set()
        for s in breakdown.values():
            valid_staff = valid_staff.union(set(s))
        return len(valid_staff) == expected
    
    def _remove_extra_staff(self, breakdown) -> List[Staff]:
        valid_staff = set()
        for s in breakdown.values():
            valid_staff = valid_staff.union(set(s))
        return list(valid_staff)

    def _is_enough_coverage(self, staff: List) -> bool:
        """ Given a list of staff, this checks that their combined
        times cover the room's time"""
        room_time = set(self.room.time_open.comp)
        total_coverage = set()
        for s in staff:
            total_coverage  = total_coverage.union(s.shift.comp)
        return room_time.issubset(total_coverage)

    def _find_valid_path(self, time_list: List,
                         curr_list: List, i: int,
                         valid_path: List) -> None:
        if i >= len(time_list):
            valid_path.append(curr_list)
            return
        staff_list = list(time_list.values())
        staff_list = staff_list[i]
        for staff in staff_list:
            if staff not in curr_list:
                new_list = deepcopy(curr_list)
                new_list.append(staff)
                self._find_valid_path(time_list, new_list, i + 1, valid_path)
            else:
                continue
        return
    
    def get_possible_shifts(self, time_list: List
                        )-> (List[TimePeriod], List[List[Staff]]):
        possible_schedules = []
        self._find_valid_path(time_list, [], 0, possible_schedules)
        times = list(time_list.keys())
        return times, possible_schedules


class BreakManager(Manager):
    def __init__(self, staff: List):
        super().__init__(staff)

    def manage(self):
        pass


if __name__ == "__main__":
    club_house = Room(RType.SC)  # room

    shift1 = Shift(12, 20)
    isaac = Staff("Isaac", EType.COUNSELOR, shift=shift1)  # employee1

    shift2 = Shift(9, 15)
    michelle = Staff("Michelle", EType.COUNSELOR, shift=shift2)  # employee2

    shift3 = Shift(9, 13)
    enpu = Staff("Enpu", EType.COUNSELOR, shift=shift3)  # employee2

    todays_staff = [isaac, michelle, enpu]  # list of working employees

    chmanager = Manager(club_house)  # to manage room
    possible_staff_times = chmanager.get_possible_staff(todays_staff)

    # for time in possible_staff_times.keys():
    #     output = f'{time}: '
    #     for staff in possible_staff_times[time]:
    #         output += f'| {staff} |'
    #     print(output)

    # time periods - list of people available at that time
    poss_schedule = chmanager.get_possible_shifts(possible_staff_times)
    print("Possible: ")

    for sched in poss_schedule:
        out = ""
        for staff in sched:
            out += str(staff) + " "
        print(out)
