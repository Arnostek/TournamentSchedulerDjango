FROM python:3-bookworm

RUN apt-get update; \
    apt-get upgrade -y; \
    apt-get install -y \
      build-essential python-dev; \
    pip install --upgrade pip; \
    pip install django numpy pandas ortools uwsgi "ipython[notebook]" django_extensions pytz pyyaml

COPY EntryPoint.sh /EntryPoint.sh

ENTRYPOINT /EntryPoint.sh
