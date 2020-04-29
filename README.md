# Scheduler

## About
This program was made in order to make scheduling for one of my first jobs easier.
There were three rooms in the facility that needed to be covered by staff while it
was open. This program takes a list of staff with information for each staff member,
and uses that to try and split the room into different times for the staff to be
there without overlapping them/ having them work the room more than once per shift.

Currently, the front end portion is only set to schedule for one room. The club house
which is open from 9AM-2:30PM. The goal is to add more algorithms in the back end in
order to get it to schedule all three rooms by splitting up their open times and
splitting up the staff who work that day evenyl amongst the rooms.

Eventually, I'll add more functionality to the break manager which will provide
staff with their breaks without it overlapping with the times they're covering a
room.


## Structure
This is the current file structure. It's probably overly done, but I was roughly
basing the structure on [pytest's](https://github.com/pytest-dev/pytest). Yeah,
they have a much much bigger code base, but I just wanted to learn about packaging
and wanted to have a nice file structure. 

```
scheduler
|_________ src
|          |________ scheduler
|          |        |________ __init__.py
|          |        |________ __main__.py
|          |
|          |_______ _scheduler
|                   |________ __init__.py
|                   |________ work.py
|                   |________ timemodule.py
|                   |________ manager.py
|_________testing
|
|_________setup.py
```

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
into the terminal:

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



