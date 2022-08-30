from api import get_timetable
from data import process_raw_timetable
from classes import RawTimetable

import sentry_sdk

from os import environ
from time import sleep

sentry_sdk.init(
    "https://ac6da680c2b54f49ba8a6b626d5b3116@o254154.ingest.sentry.io/6222128",
    traces_sample_rate=1.0
)

db_path = environ['DB_PATH']
from_date = environ['FROM_DATE']
to_date = environ['TO_DATE']
link = environ["TIMETABLE_URL"]

while (True):
    raw = get_timetable(from_date, to_date, link)
    process_raw_timetable(raw, db_path)
    sleep(60*10)
