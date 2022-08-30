from time import sleep
from typing import List

from datetime import datetime
from os import environ
import sqlite3

from google.cloud import storage
from icalendar import Calendar, Event
from pytz import timezone

tz = timezone('Europe/Warsaw')

db_name = environ['DB_PATH']
local_path = environ['LOCAL_PATH']

while (True):
    con = sqlite3.connect(db_name)
    cur = con.cursor()

    groups: List[str] = []

    for row in con.execute('SELECT DISTINCT group_name FROM mappings'):
        groups.append(row[0])


    for group in groups:
        cal = Calendar()

        # Some of this is not needed but some implementations
        # somehow need it
        cal.add('prodid', f'-//Kalendarz_{group.upper()}//ISI//achook.dev//PL')
        cal.add('version', '2.0')
        cal.add('calscale', 'GREGORIAN')
        cal.add('method', 'PUBLISH')
        cal.add('X-WR-TIMEZONE', 'Europe/Warsaw')
        cal.add('X-WR-CALNAME', f'Zajęcia {group.upper()}')

        for lecture in con.execute(f'''
            SELECT classes.*, lecturers.name, lecturers.title, mappings.group_name
                FROM classes
                INNER JOIN mappings ON classes.subject = mappings.class_name AND
                                        classes.class_group = mappings.class_group
                LEFT JOIN lecturers on classes.lecturer_id = lecturers.id
                WHERE mappings.group_name = "{group}"'''):

            # Some of this is not needed but some implementations
            # somehow need it (Apple mostly)
            event = Event()

            event.add('summary', lecture[2])
            event.add('dtstart', datetime.fromisoformat(lecture[0]))
            event.add('dtend', datetime.fromisoformat(lecture[1]))
            event.add('dtstamp', datetime.fromisoformat(lecture[9]))
            event.add('created', datetime.fromisoformat(lecture[9]))
            event.add('last-modified', datetime.fromisoformat(lecture[9]))
            event.add('sequence', 0)
            event.add('status', 'confirmed')
            event.add('transp', 'opaque')
            event.add('uid', lecture[8])

            # Make the description (not ugly)
            desc: str = ''
            if lecture[6] is not None:
                desc += 'Typ: ' + lecture[6] + '\n'
            if lecture[10] is not None:
                desc += 'Prowadzący: ' + lecture[10] + '\n'
            if lecture[4] is not None:
                desc += 'Budynek: ' + lecture[4] + '\n'
                event.add('location', f'AGH {lecture[4]}, Kraków')

            if lecture[5]is not None:
                desc += 'Sala: ' + lecture[5]
            
            
            event.add('description', desc)
            cal.add_component(event)

        file = cal.to_ical()

        # Save locally
        with open(f'{local_path}/{group}.ics', 'wb') as local:
            local.write(file)

        # Upload to GCP
        storage_client = storage.Client()
        bucket = storage_client.bucket('isi-ical')
        blob = bucket.blob(f'cal-{group}.ics')
        print(f'cal-{group}.ics')

        # Do not allow caching, otherwise updating doesn't work on Apple
        blob.cache_control = 'no-store; max-age=0'
        blob.upload_from_string(file, content_type='text/calendar')

    con.close()
    sleep(60*10)