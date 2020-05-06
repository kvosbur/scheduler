""" This module contains manager classes that are responsible for
assigning staff to rooms based on the required hard conditions"""
from collections import defaultdict
from copy import deepcopy
from typing import List, Dict
from datetime import datetime, timedelta

from _scheduler.work import Room, Staff, RType, EType, Shift
from _scheduler.timemodule import TimePeriod


class Manager():
    def __init__(self, staff: List):
        self.staff = staff

    def manage(self):
        raise NotImplementedError()

class ManyRoomsManager(Manager):
    SwapCutoff = timedelta(hours=1, minutes=30)

    def __init__(self, rooms: List[Room], staff: List[Staff]):
        super().__init__(staff)
        self.rooms = rooms
        # sort staff by their starttime
        sorted(self.staff, key=lambda x: x.shift.st)

    def get_room_early_start(self):
        return (sorted(self.rooms, key=lambda room: room.time_open.et))[0].time_open.st

    def get_room_late_end(self):
        return (sorted(self.rooms, key=lambda room: room.time_open.et))[-1].time_open.et

    def insert_into_room(self, curr_time: datetime, s: Staff):
        sorted(self.rooms, key=lambda room: room.curr_cap)
        for room in self.rooms:
            if room.curr_cap < room.max_cap and room.time_open._contains_time(curr_time):
                room.curr_cap += 1
                s.last_assigned = curr_time
                s.assigned_to = room.name
                print("Insert", s, "into room", room, "current cap:", room.curr_cap)
                return
        print("Could not find a match!")

    def new_staff(self, curr_time):
        ret = []
        for s in self.staff:
            if s.last_assigned is None and s.shift._contains_time(curr_time):
                ret.append(s)
        return ret

    def insert_new_staff(self, curr_time):
        staff_to_insert = self.new_staff(curr_time)
        for s in staff_to_insert:
            self.insert_into_room(curr_time, s)

    def get_staff_to_switch(self, curr_time: datetime) -> List[Staff]:
        ret = []
        for s in self.staff:
            if s.last_assigned is not None and (curr_time - s.last_assigned) >= ManyRoomsManager.SwapCutoff:
                ret.append(s)
        return ret

    def do_staff_swap(self, curr_time: datetime, staff_1: Staff, staff_2: Staff):
        print("Swap from:", staff_1, staff_1.assigned_to, ",", staff_2, staff_2.assigned_to)
        temp_room = staff_1.assigned_to
        staff_1.assigned_to = staff_2.assigned_to
        staff_2.assigned_to = temp_room
        staff_1.last_assigned = curr_time
        staff_2.last_assigned = curr_time
        print("to:", staff_1, staff_1.assigned_to, ",", staff_2, staff_2.assigned_to)


    def do_switch_staff(self, curr_time: datetime):
        staff_to_switch = self.get_staff_to_switch(curr_time)
        if len(staff_to_switch) > 0:
            staff_to_switch.sort(key=lambda s: s.last_assigned)
            print(staff_to_switch)
            index = 0
            while index < len(staff_to_switch) - 1:
                if staff_to_switch[index].last_assigned == curr_time:
                    index += 1
                    continue
                for attempt in range(index + 1, len(staff_to_switch)):
                    if staff_to_switch[attempt].last_assigned != curr_time and staff_to_switch[index].assigned_to != staff_to_switch[attempt].assigned_to:
                        self.do_staff_swap(curr_time, staff_to_switch[index], staff_to_switch[attempt])
                        break

                index += 1

    def resistuate_staff_to_room(self, room: Room):
        for r in self.rooms:
            if r.name != room.name and r.curr_cap > 1:
                temp_sort = sorted(self.staff, key=lambda s: s.last_assigned)
                for s in temp_sort:
                    if s.assigned_to == r.name:
                        print("Moving", s, "From", room, "To", r)
                        room.curr_cap += 1
                        s.assigned_to = room.name
                        r.curr_cap -= 1
                        return

    def decrement_room_capacity(self, room_name: RType):
        for r in self.rooms:
            if r.name == room_name:
                r.curr_cap -= 1
                print("decrementing capacity for", r, "to", r.curr_cap)
                if r.curr_cap == 0:
                    self.resistuate_staff_to_room(r)

    def leaving_staff(self, curr_time: datetime):
        for s in self.staff:
            if s.shift.et == curr_time:
                print(s, "is leaving")
                self.decrement_room_capacity(s.assigned_to)
                s.last_assigned = None
                s.assigned_to = None


    def manage(self):
        print(self.get_room_late_end())
        curr_time = self.get_room_early_start()
        end_time = self.get_room_late_end()
        print("start is at ", curr_time)
        delta = timedelta(minutes=30)

        # start main loop of events
        while curr_time <= end_time:
            print(curr_time)
            self.insert_new_staff(curr_time)
            self.leaving_staff(curr_time)
            # TODO check if a room closes
            self.do_switch_staff(curr_time)
            curr_time += delta



class RoomManager(Manager):
    def __init__(self, room: Room, staff: List):
        super().__init__(staff)
        self.room = room

    def manage(self) -> (List[TimePeriod], List[List[Staff]]):
        available_staff = []
        staff = self._get_available_staff(self.staff)
        while True:
            if not self._is_enough_coverage(staff):
                return {}

            breakdown = self._get_breakdown(staff)
            result = self._verify_breakdown(breakdown, len(staff))
            if result:
                return self.get_possible_shifts(breakdown)

            staff = self._remove_extra_staff(breakdown)
    
    def _get_available_staff(self, staff: List):
        """ Given a list of staff, this checks to see which
        ones are available """
        
        return [s for s in staff if s._coincides(self.room)]

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
            valid_staff.update(s)
        return len(valid_staff) == expected
    
    def _remove_extra_staff(self,
                            breakdown: Dict[TimePeriod, List[Staff]]
                            ) -> List[Staff]:
        valid_staff = set()
        for s in breakdown.values():
            valid_staff.update(s)
        return list(valid_staff)

    def _is_enough_coverage(self, staff: List) -> bool:
        """ Given a list of staff, this checks that their combined
        times cover the room's time"""
        room_time = set(self.room.time_open.comp)
        total_coverage = set()
        for s in staff:
            total_coverage.update(s.shift.comp)
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
    rooms = [Room(RType.SC), Room(RType.CH)]

    shift1 = Shift(datetime(1, 1, 1, 12, 0, 0), datetime(1, 1, 1, 20, 0, 0))
    isaac = Staff("Isaac", EType.COUNSELOR, shift=shift1)  # employee1

    shift3 = Shift(datetime(1, 1, 1, 9, 0, 0), datetime(1, 1, 1, 13, 0, 0))
    enpu = Staff("Enpu", EType.COUNSELOR, shift=shift3)  # employee2

    shift2 = Shift(datetime(1, 1, 1, 9, 0, 0), datetime(1, 1, 1, 15, 0, 0))
    michelle = Staff("Michelle", EType.COUNSELOR, shift=shift2)  # employee2

    todays_staff = [isaac, enpu, michelle]  # list of working employees

    chmanager = ManyRoomsManager(rooms, todays_staff)  # to manage room
    chmanager.manage()

    exit(0)
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
