web: gunicorn clikhome_fbbot.wsgi --log-file -
fbbotworker: python manage.py celery worker --app clikhome_fbbot -l INFO -Q fb-bot
