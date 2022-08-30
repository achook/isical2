FROM python:3.10-alpine

WORKDIR /usr/ical

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DB_PATH "/data/db.sqlite"

CMD [ "flask", "run", "--host=0.0.0.0", "--port=80" ]