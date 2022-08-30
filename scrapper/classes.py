from dataclasses import dataclass
from typing import List

from datetime import datetime
from uuid import UUID

@dataclass
class RawClass:
    start: datetime
    end: datetime
    subject: str
    group: str = None
    building: str = None
    room: str = None
    class_type: str = None
    lecturer: str = None
    title: str = None

@dataclass
class TimeOff:
    start: datetime
    end: datetime

@dataclass
class RawTimetable:
    classes: List[RawClass]

@dataclass
class Lecturer:
    id: UUID

    name: str
    title: str

@dataclass
class Class:
    id: UUID
    creation_date: datetime
    
    start: datetime
    end: datetime
    subject: str
    group: str = None
    building: str = None
    room: str = None
    class_type: str = None

    lecturer_id: UUID = None

@dataclass
class Timetable:
    classes: List[Class]
    lecturers: List[Lecturer]