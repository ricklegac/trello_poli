PS3="Elige un numero : "

select option in tests_miembros tests_proyectos tests_roles tests_tareas tests_usuarios
do
    echo "opcion seleccionada: $opcion"
    echo "opcion: $REPLY"
    if [ $REPLY -eq 1 ]
    then
      echo "test TESTS MIEMBROS "
      sleep 1
      pytest sgpa/apps/proyectos/tests_miembros.py
    fi
    if [ $REPLY -eq 2 ]
    then
      echo "test TESTS PROYECTOS "
      sleep 1
      pytest sgpa/apps/proyectos/tests_proyectos.py
    fi
    if [ $REPLY -eq 3 ]
    then
      echo "test TESTS ROLES "
      sleep 1
      pytest sgpa/apps/proyectos/tests_roles.py
    fi
    if [ $REPLY -eq 4 ]
    then
      echo "test TESTS TAREAS "
      sleep 1
      pytest sgpa/apps/proyectos/tests_tareas.py
    fi
    if [ $REPLY -eq 5 ]
    then
      echo "test TESTS USUARIOS "
      sleep 1
      pytest sgpa/apps/proyectos/tests_tareas.py
    fi
    if [ $REPLY -eq 6 ]
    then
      echo "test TESTS USUARIOS "
      sleep 1
      pytest sgpa/apps/usuarios/tests_usuarios.py
    fi
    echo "opcion seleccionada: $opcion"
    echo "opcion: $REPLY"

done