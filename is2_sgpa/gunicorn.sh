sleep 3
gunicorn -c conf/gunicorn.conf.py gestorProyectos.wsgi
python3 manage.py runserver 127.0.0.1:8000