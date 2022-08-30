FROM python:3.10-alpine

WORKDIR /usr/ical

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DB_PATH "/data/db.sqlite"
ENV GOOGLE_APPLICATION_CREDENTIALS "/usr/ical/credentials.json"
ENV LOCAL_PATH "/data/out"

CMD [ "python", "./main.py" ]