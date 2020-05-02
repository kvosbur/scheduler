# Scheduler

## About
This program was made in order to make scheduling for one of my first jobs easier.
There were three rooms in the facility that needed to be covered by staff while it
was open. This program takes a list of staff with information for each staff member,
and uses that to try and split the room into different times for the staff to be
there without overlapping them/ having them work the room more than once per shift.

Currently, the front end portion is only set to schedule for one room. The club house
which is open from 9:30M-2:30PM. The goal is to add more algorithms in the back end in
order to get it to schedule all three rooms by splitting up their open times and
splitting up the staff who work that day evenyl amongst the rooms.

Eventually, I'll add more functionality to the break manager which will provide
staff with their breaks without it overlapping with the times they're covering a
room.

## Example

On a normal day, there would be around 6 people working between those three rooms.
The shifts looked like this normally.
* 9-5PM Staff1
* 9-5PM Staff2
* 9-3PM Staff3
* 10-3PM Staff4
* 1-9PM Staff5

|            | Staff1   |  Staff2  | Staff3     | Staff4      | Staff 5
-------------:|:----------:|:----------:|:------------:|:-------------:|:-------:
9:00-9:15AM | ClubHouse | Subcellar | GreatHall | -           | -
9:15-9:30AM | ClubHouse | Subcellar | GreatHall | -           | -
9:30-9:45AM | ClubHouse | Subcellar | GreatHall | -           | -
9:45-10:00AM | ClubHouse | Subcellar | GreatHall | -          | -
10:00-10:15AM | ClubHouse | Subcellar | GreatHall | GreatHall | -
10:15-10:30AM | ClubHouse | Subcellar | GreatHall | GreatHall | -
10:30-10:45AM | Subcellar | ClubHouse | GreatHall | GreatHall | -
10:45-11:00AM | Subcellar | ClubHouse | GreatHall | GreatHall | -
11:00-11:15AM | Subcellar | ClubHouse | Break | GreatHall | -
11:15-11:30AM | Subcellar | ClubHouse | Break | GreatHall | -
11:30-11:45AM | Subcellar | ClubHouse | Break | GreatHall | -
11:45-12:00PM | Subcellar | ClubHouse | Break | GreatHall | -
12:00-12:15PM | Break | GreatHall | ClubHouse | SubCellar | -
12:15-12:30PM | Break | GreatHall | ClubHouse | SubCellar | -
12:30-12:45PM | Break | GreatHall | ClubHouse | SubCellar | -
12:45-1:00PM  | Break | GreatHall | ClubHouse | SubCellar | -
1:00-1:15PM | GreatHall | Break     | SubCellar | Break | ClubHouse
1:15-1:30PM | GreatHall | Break     | SubCellar | Break | ClubHouse
1:30-1:45PM | GreatHall | Break     | SubCellar | GreatHall | ClubHouse
1:45-2:00PM | GreatHall | Break     | SubCellar | GreatHall | ClubHouse
2:00-2:15PM | GreatHall | GreatHall | SubCellar | GreatHall | ClubHouse
2:15-2:30PM | GreatHall | GreatHall | SubCellar | GreatHall | ClubHouse
2:30-2:45PM | GreatHall | GreatHall | GreatHall | GreatHall | GreatHall
2:45-3:00PM | GreatHall | GreatHall | GreatHall | GreatHall | GreatHall
3:00-3:15PM | GreatHall | GreatHall | - | - | GreatHall
3:15-3:30PM | GreatHall | GreatHall | - | - | GreatHall
3:30-3:45PM | GreatHall | GreatHall | - | - | GreatHall
3:45-4:00PM | GreatHall | GreatHall | - | - | GreatHall
4:00-4:15PM | GreatHall | GreatHall | - | - | Break
4:15-4:30PM | GreatHall | GreatHall | - | - | Break
4:30-4:45PM | GreatHall | GreatHall | - | - | Break
4:45-5:00PM | GreatHall | GreatHall | - | - | Break
5:00-6:00PM | - | - | - | - | GreatHall
6:00-7:00PM | - | - | - | - | GreatHall
7:00-8:00PM | - | - | - | - | GreatHall
8:00-9:00PM | - | - | - | - | GreatHall



## Structure

`timemodule.py` contains the unit of time for this project, the **TimePeriod**. 
TimePeriods have a start and end time which are
`datetime` objects. And they're composed of half hour blocks of time. This is so
that splitting TimePeriods into smaller TimePeriods and other computations between
TimePeriods are easier to do. The front end is configured to only offer Times like
9:00AM, 9:30AM, 10:AM, ..., 8:30PM, 9:00PM. That way people don't accidentally
put times that don't make sense for the TimePeriod.

In `work.py`, there are classes for Shift, Staff, and Room. I might rename the module
or even split the classes off into different modules to be clearer on what the module
is for.

## Setup and Running

In order to get the program running, install all of the dependencies by entering
into the terminal and make sure you have python3.7.6:

```pipenv install --dev```

Once everything is installed, you can run

``` streamlit run driver.py ```

Which will run `driver.py` and allow you to interact with the application on your
browser. When Interacting with the browser, It's important to remember that it's
only currently configured for one room which is open from 9:00AM - 2:30PM, so in
order to get valid results, you would need to add shifts that cover that time span.

## Testing

I've installed pytest into the repo and plan on adding test cases for the modules
in the testing/ directory.



