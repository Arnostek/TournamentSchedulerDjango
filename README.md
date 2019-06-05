# TournamentSchedulerDjango

Python django website for running Canoepolo tournament.

## Install

* Pull it on server with docker and docker-compose installed.
* cd to docker folder
* cp env.template to .env and edit variables
* create empty db: docker-compose exec tournament_scheduler python /srv/django/manage.py migrate
* run with docker-compose up
