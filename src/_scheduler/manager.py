""" This module contains manager classes that are responsible for
assigning staff to rooms based on the required hard conditions"""
from collections import defaultdict
from copy import deepcopy
from typing import List, Dict
from datetime import datetime, timedelta
from copy import deepcopy

from _scheduler.work import Room, Staff, RType, EType, Shift, RoomAssignment, TimeAssignment, Schedule
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
        self.schedule = Schedule()

    def get_room_early_start(self) -> datetime:
        return (sorted(self.rooms, key=lambda room: room.time_open.et))[0].time_open.st

    def get_room_late_end(self) -> datetime:
        return (sorted(self.rooms, key=lambda room: room.time_open.et))[-1].time_open.et

    def insert_into_room(self, time_assignment: TimeAssignment, s: Staff):
        sorted_rooms = sorted(time_assignment.room_assignments, key=lambda room_assignment: room_assignment.curr_cap)
        for room_assignment in sorted_rooms:
            if room_assignment.curr_cap < room_assignment.max_cap and room_assignment.time_open._contains_time(time_assignment.curr_time):
                s.last_assigned = time_assignment.curr_time
                room_assignment.add_staff(s)
                return

        # not the best, but it seems it is okay in certain circumstances to go over max capacity if there is no
        # capacity open in any room. So put in room with lowest current capacity
        for room_assignment in sorted_rooms:
            if room_assignment.time_open._contains_time(time_assignment.curr_time):
                s.last_assigned = time_assignment.curr_time
                room_assignment.add_staff(s)
                return

        raise Exception("Could not find spot to insert employee to. There were no open rooms")

    def new_staff(self, time_assignment: TimeAssignment) -> List[Staff]:
        ret = []
        for s in self.staff:
            if not time_assignment.contains_staff(s) and s.shift._contains_time(time_assignment.curr_time):
                ret.append(s)
        return ret

    def insert_new_staff(self, time_assignment: TimeAssignment):
        staff_to_insert = self.new_staff(time_assignment)
        for s in staff_to_insert:
            self.insert_into_room(time_assignment, s)

    def leaving_staff(self, time_assignment: TimeAssignment):
        for s in self.staff:
            if s.shift.et < time_assignment.curr_time:
                time_assignment.remove_staff(s)
                s.last_assigned = None

    def room_closes(self, time_assignment: TimeAssignment):
        for r in time_assignment.room_assignments:
            if r.time_open.et < time_assignment.curr_time:
                print("Found room close for:", r.room)
                # must move all staff from room since it is closing
                while len(r.staff) > 0:
                    self.insert_into_room(time_assignment, r.staff.pop())

    """
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
    """

    def manage(self):
        print(self.get_room_late_end())
        curr_time = self.get_room_early_start()
        end_time = self.get_room_late_end()
        print("start is at ", curr_time)
        delta = timedelta(minutes=30)
        base = TimeAssignment(curr_time)
        # assume all rooms start at same time right now
        for r in self.rooms:
            temp = RoomAssignment(r)
            base.add_room_assignment(temp)

        # start main loop of events
        while curr_time <= end_time:
            print(curr_time)
            self.insert_new_staff(base)      # Done swap
            self.leaving_staff(base)         # Done swap
            self.room_closes(base)           # Done swap
            base.swap_staff(ManyRoomsManager.SwapCutoff)
            curr_time += delta

            # copy current time assignment obejct to be used for the next run as the base
            prev_base = base
            base = TimeAssignment(curr_time)
            base.room_assignments = deepcopy(prev_base.room_assignments)
            self.schedule.add_time_assignment(prev_base)

        self.schedule.pretty_print_schedule()




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
    rooms = [Room(RType.SC), Room(RType.CH), Room(RType.GH)]

    shift1 = Shift(datetime(1, 1, 1, 9, 0, 0), datetime(1, 1, 1, 17, 0, 0))
    enpu = Staff("Enpu", EType.COUNSELOR, shift=shift1)

    michelle = Staff("Michelle", EType.COUNSELOR, shift=shift1)

    shift2 = Shift(datetime(1, 1, 1, 9, 0, 0), datetime(1, 1, 1, 15, 0, 0))
    isaac = Staff("Isaac", EType.COUNSELOR, shift=shift2)

    shift2 = Shift(datetime(1, 1, 1, 10, 0, 0), datetime(1, 1, 1, 15, 0, 0))
    alice = Staff("Alice", EType.COUNSELOR, shift=shift2)

    shift2 = Shift(datetime(1, 1, 1, 13, 0, 0), datetime(1, 1, 1, 21, 0, 0))
    bob = Staff("Bob", EType.COUNSELOR, shift=shift2)

    todays_staff = [isaac, enpu, michelle, alice, bob]  # list of working employees

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
