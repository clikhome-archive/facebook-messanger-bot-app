web: gunicorn clikhome_fbbot.wsgi --log-file -
worker: celery worker --app clikhome_fbbot -l INFO -Q fb-bot
