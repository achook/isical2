from datetime import datetime
from typing import List

from classes import RawTimetable, Timetable, Class, Lecturer

import sqlite3
from uuid import uuid4


def process_raw_timetable(raw_timetable: RawTimetable, db_name: str) -> None:
    
    raw_classes = raw_timetable.classes

    con = sqlite3.connect(db_name)
    cur = con.cursor()
    cur2 = con.cursor()
    cur3 = con.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS lecturers 
               (name text NOT NULL UNIQUE, title text, id text PRIMARY KEY)''')

    con.commit()


    cur.execute('''CREATE TABLE IF NOT EXISTS classes 
               (start timestamp NOT NULL, end timestamp NOT NULL, subject text NOT NULL, class_group text NOT NULL,
               building text, room text,
               class_type text,
               lecturer_id text, id text PRIMARY KEY, updated timestamp  NOT NULL)''')

    con.commit()

    cur.execute('DROP TABLE IF EXISTS raw_classes')

    cur.execute('''CREATE TABLE raw_classes
               (start timestamp NOT NULL, end timestamp NOT NULL, subject text NOT NULL, class_group text NOT NULL,
               building text, room text,
               class_type text, lecturer text, title text)''')
    
    con.commit()
    
    for raw_class in raw_classes:
        #print(raw_class)

        cur.execute('INSERT INTO raw_classes VALUES (?,?,?,?,?,?,?,?,?)', (
            raw_class.start, raw_class.end,
            raw_class.subject, raw_class.group,
            raw_class.building, raw_class.room ,
            raw_class.class_type,
            raw_class.lecturer, raw_class.title)
        )

    con.commit()

    cur.execute('''DELETE FROM raw_classes
                        WHERE rowid NOT IN (
                        SELECT MIN(rowid) 
                        FROM raw_classes
                        GROUP BY subject,class_group,start,end
        )''')

    con.commit()

    cur.execute('DROP TABLE IF EXISTS raw_lecturers')

    cur.execute('''CREATE TABLE raw_lecturers
               (id text, name text UNIQUE, title text, to_update boolean)''')

    cur.execute('''INSERT INTO raw_lecturers(name, title)
                    SELECT lecturer, title FROM raw_classes WHERE lecturer IS NOT NULL 
                    GROUP BY lecturer''')

    cur.execute('''UPDATE raw_lecturers
                    SET to_update = TRUE ''')

    con.commit()

    # pair lecturers with thieir counterparts from good table

    for new_lecturer in cur.execute('''
        SELECT raw_lecturers.name, raw_lecturers.title FROM raw_lecturers 
        WHERE raw_lecturers.name NOT IN (SELECT name FROM lecturers)
        '''):
        print(new_lecturer)
        new_key = uuid4().hex
        cur2.execute('INSERT INTO lecturers VALUES (?,?,?)', (new_lecturer[0], new_lecturer[1], new_key) )


    con.commit()

    cur.execute('DROP TABLE raw_lecturers')

    # raw_classes.lecturer = (SELECT TOP 1 lecturer.name FROM lecturers WHERE id = classes.lecturer_id) AND 

    # print(cur.execute('SELECT id FROM lecturers WHERE name = None'))

    for to_insert in cur.execute('''SELECT raw_classes.* FROM raw_classes
        LEFT JOIN classes ON 
        raw_classes.start = classes.start AND 
        raw_classes.end = classes.end AND 
        raw_classes.subject = classes.subject AND 
        raw_classes.class_group = classes.class_group
        WHERE classes.start IS NULL AND 
        classes.end IS NULL'''):

        raw_lecturer = None
        if (to_insert[7]):
            raw_lecturer = cur2.execute(f'SELECT id FROM lecturers WHERE name = "{to_insert[7]}"').fetchone()[0]
        
        new_key = uuid4().hex
        date = datetime.now()

        #print(to_insert)

        cur3.execute('INSERT INTO classes VALUES (?,?,?,?,?,?,?,?,?,?)', (to_insert[0], to_insert[1], to_insert[2], to_insert[3], to_insert[4], to_insert[5], str(to_insert[6]), raw_lecturer, new_key, date))

    con.commit()

    for to_delete in cur.execute('''SELECT classes.* FROM classes
        LEFT JOIN raw_classes ON 
        raw_classes.start = classes.start AND 
        raw_classes.end = classes.end AND 
        raw_classes.subject = classes.subject AND 
        raw_classes.class_group = classes.class_group
        WHERE raw_classes.start IS NULL AND 
        raw_classes.end IS NULL'''):

        cur2.execute('DELETE FROM classes WHERE start = ? AND end = ? AND subject = ? AND class_group = ?', (to_delete[0], to_delete[1], to_delete[2], to_delete[3]))

    con.commit()

    cur.execute('DROP TABLE raw_classes')

    con.close()