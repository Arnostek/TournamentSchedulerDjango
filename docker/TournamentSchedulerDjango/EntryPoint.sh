#!/bin/bash
if [[ "$DJANGO_DEBUG" == "True" ]]; then
  python /srv/django/manage.py runserver 0.0.0.0:$DJANGO_PORT
else
  echo yes | python /srv/django/manage.py collectstatic
  uwsgi --http :$DJANGO_PORT --chdir /srv/django --static-map /static=/srv/staticroot --wsgi-file project/wsgi.py --master --processes 4 --threads 2
fi
