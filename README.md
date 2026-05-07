# TournamentSchedulerDjango

Python django website for running Canoepolo tournament.

## Install

* Pull it on server with docker and docker-compose installed.
* Point DNS A/AAAA record of your domain to this server.
* cd to docker folder
* cp env.template to .env and edit variables (`DJANGO_ALLOWED_HOSTS`, `CADDY_DOMAIN`, `CADDY_EMAIL`)
* rebuild image: docker compose build --pull
* create empty db: docker compose exec tournament_scheduler python /srv/django/manage.py migrate
* run with: docker compose up -d
* open https://your-domain.tld (Caddy provisions and renews Let's Encrypt certificates automatically)

## Create tournament
* Program your system
* run shell: docker compose exec tournament_scheduler python /srv/django/manage.py shell_plus
* run your script: from tournament.tournaments import Prague2025
