PS3="Elige una iteracion : "

select option in iteracion1 iteracion2 iteracion3 iteracion4 iteracion5 iteracion6 salir
do
    echo "Iteracion $opcion"
    echo "opcion: $REPLY"
    if [ $REPLY -eq 1 ]
    then
      echo "Cambiando a la Iteracion 1 "
      sleep 1
      git checkout version0.1
    fi
    if [ $REPLY -eq 2 ]
    then
      echo "Cambiando a la Iteracion 2 "
      sleep 1
      git checkout version0.2
    fi
    if [ $REPLY -eq 3 ]
    then
      echo "Cambiando a la Iteracion 3 "
      sleep 1
      git checkout 3.2
    fi
    if [ $REPLY -eq 4 ]
    then
      echo "Cambiando a la Iteracion 4 "
      sleep 1
      git checkout 4.1
    fi
    if [ $REPLY -eq 5 ]
    then
      echo "Cambiando a la Iteracion 5 "
      sleep 1
      git checkout 5.1
    fi
    if [ $REPLY -eq 6 ]
    then
      echo "Cambiando a la Iteracion 6 "
      sleep 1
      git checkout 6.0
    fi
    if [ $REPLY -lt 1 ] | [ $REPLY -gt 6 ]
    then
      echo "saliendo del script"
      break
    fi
    echo "opcion seleccionada: $opcion"
    echo "opcion: $REPLY"

done