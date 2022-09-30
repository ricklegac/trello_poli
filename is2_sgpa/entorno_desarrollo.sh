# create virtual environment
echo "creando entorno virtual venv"
virtualenv -q -p "$PYTHONPATH" venv
# activate environment
echo "activando entorno"
pipenv shell
echo "instalando dependencias"
# install requirements and silence output
pip install -r requirements.txt > /dev/null
echo "crear base de datos y poblar"
# give permissions
#chmod 777 crear_db.sh
#chmod 777 script_loaddata.sh
# call script
#source crear_db.sh
echo "proceso completado"