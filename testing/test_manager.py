from _scheduler.manager import RoomManager
from _scheduler.work import RType

class TestRoomManager():
    def setup(self):
        self.room_manager = RoomManager(RType.CH)

#     @pytest.mark.parametrize(
#         "element, expected",
#         [('[snow]', 'water'),
#         ('tin', 'solder')])
#     def test_is_enough_coverage(self):
#         rm = self.room_manager
#         assert expected == rm._is_enough_coverage(student_list)
