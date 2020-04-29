import streamlit as st
from _scheduler.work import Room, Staff, EType, RType
from _scheduler.manager import RoomManager
import graphviz as graphviz
import datetime as dt
from datetime import datetime, date, timedelta

import scheduler

def get_num_of_staff():
    num_of_staff = st.text_input("How many staff do you want?", "0")
    num_of_staff = int(num_of_staff)

    return num_of_staff


def setup_times():
    base_date = date(1, 1, 1)
    start_time = dt.time(9, 0)
    start_time = datetime.combine(base_date, start_time)
    avail_times = [start_time + (i * timedelta(minutes=30)) for i in range(25)]

    return avail_times


def create_staff_list(num_of_staff, avail_times):
    staff_list = []
    for i in range(num_of_staff):
        name = st.text_input("* Enter the Staff's name",
                            str(i*num_of_staff))

        start_time = st.selectbox(
            f"Please Choose a Starting Time for {name}",
            avail_times,
            index=i * num_of_staff + 1,
            format_func=lambda x: str(x.strftime("%I:%M %p")))

        end_time = st.selectbox(
            f"Please Choose an Ending Time for {name}",
            avail_times,
            index=i * num_of_staff + 2,
            format_func=lambda x: str(x.strftime("%I:%M %p")))
        try:
            staff_list.append(Staff(name,
                                    EType.COUNSELOR,
                                    st=start_time,
                                    et=end_time))
        except scheduler.TimeError:
            st.write("Please Pick A valid TIme")
            return None
    return staff_list


def setup_room_and_manager(staff_list):
    club_house = Room(RType.CH)  # room
    chmanager = RoomManager(club_house, staff_list)
    return chmanager


def draw_graph(times, order):
    graph = graphviz.Digraph()
    colorx = .000
    for current in order:
        final_color = f'{colorx} .999 .400'
        for i, v in enumerate(current):
            if i == len(current) - 1:
                continue
            time = str(times[i]).replace(":", " ")
            time2 = str(times[i+1]).replace(":", " ")
            node1 = v.name + " " + time
            node2 = current[i+1].name + " " + time2
            graph.edge(node1, node2, color=final_color)
        colorx += .070
    st.graphviz_chart(graph)

def get_schedule():
    times, order = [], []
    try:
        times, order = manager.manage()
    except Exception:
        st.write("Not A valid Schedule")
    return times, order

if __name__ == '__main__':
    st.title("Break Scheduler")
    number_of_staff = get_num_of_staff()
    if number_of_staff > 0:
        time_choices = setup_times()
        staff_list = create_staff_list(number_of_staff, time_choices)

        manager = setup_room_and_manager(staff_list)
        times, order = get_schedule()
        if len(times) > 0:
            draw_graph(times, order)
        else:
            st.write("""
            Please get more coverage. Can't make schedule from current shifts
            """)
    else:
        st.write("Please begin filling out the information above")
    
