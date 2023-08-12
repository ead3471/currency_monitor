FROM python:3.11-slim
WORKDIR /app
COPY ./requirements.txt .
RUN pip3 install -r ./requirements.txt --no-cache-dir
COPY . .
RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "currency_monitor.wsgi:application", "--bind", "0:8000"]

