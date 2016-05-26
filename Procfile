web: gunicorn clikhome_fbbot.wsgi --log-file -
fbbotworker: celery worker --app clikhome_fbbot -c 10 -l INFO -Q fb-bot
