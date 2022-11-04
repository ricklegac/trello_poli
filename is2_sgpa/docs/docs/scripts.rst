Scripts
=====

.. automodule:: script_poblacion
    :members:
    

=============
script_pytest
=============

Simplemente ejecute el script y automáticamente se correrán todos los tests

=================
produccion
=================

**script.sh**

Ejecutar este script primero, para clonar el proyecto y realizar procesos iniciales

**create_and_populate_db.sh**

Ejecutar este script si desea poblar la base de datos

**init_server.sh**

Ejecutar luego este script. Para correr el sistema

=========================
ambiente_desarollo
=========================

**ambiente_desarrollo.sh**

Instala dependencias, crea base de datos de desarrollo y pobla la nueva db
utiliza el scrip crear_db.sh


====================
burndown_chart a pdf
====================

.. function:: downloadPDF()
   :module: registro_actividad.templates.registro_actividad.burndown_chart
   
   Convierte el grafico del burndown chart a pdf y descarga
   
   :Devuelve: **un pdf**


===========
crear_db
===========

**crear_db.sh**

Ejecutar este script simplemente crea la base de datos.

================
reset_migrations
================

**reset_migrations.sh**

Ejecutar este script resetea las migraciones.
   
   
================
script_loaddata
================

**script_loaddata.sh**

Ejecutar este script carga datos de un dump a la base de datos de desarrollo
