#!/bin/bash


#ejecutamos cada test de cada modulo creado
python3 -m pytest sgpa/test_conexion.py
python3 -m pytest sgpa/apps/miembros/tests.py --html-report=miembros_test.html -s
python3 -m pytest sgpa/apps/proyectos/tests.py 
python3 -m pytest sgpa/apps/usuarios/tests.py 
python3 -m pytest sgpa/apps/roles/tests.py
python3 -m pytest sgpa/apps/tareas/tests.py 

#tenemos que ubicarnos en la carpeta donde se encuentra el proyecto 