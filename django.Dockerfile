FROM python:3.11-slim

WORKDIR /app

COPY ./requirements.txt .

RUN pip3 install -r ./requirements.txt --no-cache-dir

COPY ./currency_monitor .
RUN python manage.py collectstatic --noinput

#CMD ["gunicorn", "currency_monitor.wsgi:application", "--bind", "0:8000"]
CMD ["gunicorn", "currency_monitor.wsgi:application", "--bind", "0:8000", "--preload", "--timeout", "300", "--workers", "4", "--threads", "2", "--worker-class", "gthread", "--worker-tmp-dir", "/dev/shm"]
