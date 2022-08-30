from classes import RawClass, TimeOff, RawTimetable

from typing import List
from json import loads
from datetime import datetime

from pytz import timezone
from requests import get

tz = timezone('Europe/Warsaw')


def get_timetable(from_date: str, to_date: str, raw_link: str) -> RawTimetable:
    # The _ parameter is a timestamp but somehow it doesn't if it's correct
    # So why not hardcode it
    link = f'{raw_link}?start={from_date}&end={to_date}&_=1633638375065'
    print(link)

    # Get API response and parse
    # No https because it never works on macOS
    page = get(link, verify=False)
    loaded = loads(page.text)

    classes: List[RawClass] = []
    days_off: List[TimeOff] = []

    # The API response cosists of list of every given lecture in the requested time period
    # so traverse each and every one
    for element in loaded:
        splitted = []

        # Split 'titles' by commas or html line break tags because somehow they are used interchangibly
        # TODO: Make it less ulgy (note to self: regex won't be more efficent)
        temp = element['title'].split('<br/>')
        for el in temp:
            temp2 = el.split(',')
            for el2 in temp2:
                splitted.append(el2)

        # Find start and end of a lecture and make datetime objects from them
        start = datetime.fromisoformat(element['start'][:-5])
        start = tz.localize(start)
        end = datetime.fromisoformat(element['end'][:-5])
        end = tz.localize(end)

        # The first part of the stripped title is an actual name of the lecture
        name = splitted[0].strip()
        
        # Sometimes a lecture is not actually a lecture so find brakes
        # and save them for future, no more data will be available so continue
        if "Przerwa semestralna" in name:
            timeoff = TimeOff(start, end)
            days_off.append(timeoff)
            continue

        # type is a reserverd keyword so let's use some Ponglish
        # The second part of the stripped title is a type of the lecture
        typ = splitted[1].strip()

        # TODO: Make object here and update it later
        # not the ugly way
        building = None
        room = None
        lecturer = None
        title = None

        # Now begins the funny part
        for i in range(2, len(splitted)):
            # Check if the room name is available 
            if 'Sala' in splitted[i]:
                # Do me stripping and spliting to get the bare room number and...
                room = splitted[i]
                room = room[6:]
                room = room.strip()

                # Builidng name
                building = room.split(' ')[0]
                building = building.replace('-', '')

                if len(room.split(' ', maxsplit=1)) > 1:
                    room = room.split(' ', maxsplit=1)[1]

            # Check if the lecturer's name is available
            if 'prowadzący' in splitted[i]:
                # And do some splity splitting
                lecturer = splitted[i]
                lecturer = lecturer[12:]

                # Sometimes they put the lecturer's name differently
                # Why? Because they can. So adjust the lecturer's name accordingly
                if 'Informacja: prowadzący' in splitted[i]:
                    lecturer = lecturer[11:]

                # Check if there is one more part in the splitted title
                # If so - it's the lecturers title
                if i+1 < len(splitted):
                    title = splitted[i+1]
                    title = title.strip()
            
                # Remove whitespace
                lecturer = lecturer.strip()

        # Get the group for this lecture
        group = element['group']

        raw_class = RawClass(start, end, name, group, building, room, typ, lecturer, title)
        classes.append(raw_class)


    # Checking if the lectures doesn't overlap some time off
    # If so, discard them
    # TODO: Make it less ugly and more efficient
    proper_classes: List[RawClass] = []

    # Make variable function level
    is_ok = False

    # Check for days off
    for raw_class in classes:
        is_ok = True

        for day_off in days_off:
            if raw_class.end > day_off.start and raw_class.end < day_off.end:
                is_ok = False
            if raw_class.start < day_off.end and raw_class.start > day_off.start:
                is_ok = False
        
        if is_ok:
            proper_classes.append(raw_class)

    classes = proper_classes

    return RawTimetable(classes)