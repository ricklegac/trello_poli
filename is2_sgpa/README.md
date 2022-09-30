# SGPA

## Requerimientos
- Python 3.8 o superior.
- Pipenv para manejar entorno virtual `sudo apt install pipenv`.
- PostgreSQL para manejo de base de datos:
  ```
    sudo apt-get install postgresql postgresql-contrib
    sudo apt-get install libpq-dev python3-dev
  ```
## Instrucciones
1. Crear la base de datos y el usuario en PostgreSQL para el proyecto con los siguientes datos:
  ```
    nombre: is2,
    user: is2,
    password: is2
  ```
2. Instalar las dependencias `pipevn install`.
3. Correr las migraciones `python manage.py migrate`.
4. Crear super usuario `python manage.py createsuperuser`.
5. Correr el servidor `python manage.py runserver`.
