web: gunicorn theraq.wsgi --chdir backend --limit-request-line 8188 --log-file -
worker: celery worker --workdir backend --app=theraq -B --loglevel=info
