FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY currency_monitor/ .
COPY .env .



ENV REDIS_HOST=redis://redis:6379/0


WORKDIR /app/

#CMD celery -A tasks worker --beat --loglevel=info
#CMD celery -A currency_monitor worker --beat --loglevel=info
CMD celery -A currency_monitor worker --beat -l debug
#CMD celery -A currency_monitor beat -l info & celery -A currency_monitor worker -l info