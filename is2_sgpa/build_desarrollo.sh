#!/bin/bash

# Ititialization

mainmenu () {
    des_db_name=sgpa
    #prod_db_name=is_prod
    db_user=$USER

    username="ricardolegac"
    password="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"

    red=`tput setaf 1`
    green=`tput setaf 2`
    reset=`tput sgr0`
    repo=is2_sgpa
    echo -e "${red}<<< GRUPO 1 >>>${reset}"

    rm -rf is2_project/

    git clone "https://${username}:${password}@github.com/renzoopy/is2_sgpa.git"

    cd "is2_sgpa"

    echo -e "${green}\n>>> Repository clonado${reset}"
    echo "Presione 1 para Desarrollo"
    #echo "Presione 2 para Producción"
    echo "Presione 3 para salir"

    read -n 1 -p "Seleccione:" mainmenuinput
    if [ "$mainmenuinput" = "1" ]
    then
        clear
        echo -e "${green}\n>>> Desarrollo${reset}"
        git checkout main
        git branch
        git pull origin main
        echo "Presione 1 para TAG v.0.0.1"
        echo "Presione 2 para TAG v.0.0.2"
        echo "Presione 3 para TAG v.0.0.3"
        echo "Presione 4 para TAG v.0.0.4"
        echo "Presione 5 para TAG v.0.0.5"
        #echo "Presione 6 para TAG v.0.0.6"
        read -n 1 -p "Seleccione el Tag:" tag

        echo -e "${green}\n>>> Desarrollo TAG Version: ${tag}:${reset}"
        echo


        
        #sudo docker-compose up -d
        #sleep 2
        #echo
        #sudo docker cp db.dump pg_container:/
        #echo -e "${green}\n>>> Copiando backup a la BD${reset}"
        #sudo docker exec -it pg_container dropdb -U ${db_user} --if-exists ${des_db_name}
        #sudo docker exec -it pg_container createdb -U ${db_user} ${des_db_name}
        #sudo docker exec -it pg_container psql -U ${db_user} -d ${des_db_name} -c "DROP SCHEMA public CASCADE;"
        #sudo docker exec -it pg_container psql -U ${db_user} -d ${des_db_name} -c "CREATE SCHEMA public;"
        #sudo docker exec -it pg_container pg_restore -U ${db_user} -d ${des_db_name} --no-owner db.dump
        #echo

       

        if [ "$tag" = "1" ]; then
            git switch --detach v.0.0.1
        elif [ "$tag" = "2" ]; then
            git switch --detach v.0.0.2
        elif [ "$tag" = "3" ]; then
            git switch --detach v.0.0.3
        elif [ "$tag" = "4" ]; then
            git switch --detach v.0.0.4
        elif [ "$tag" = "5" ]; then
            git switch --detach iteracion5
        #elif [ "$tag" = "6" ]; then
        #    git switch --detach v.0.0.6
        else 
            echo -e "${red}\n<<< Esa versión no existe >>>${reset}"
            sleep 2
            exit
        fi

         # prepare env and install dependencies
        echo -e "${green}\n>>> Creando entorno virtual${reset}"
        pipenv install
        echo "${green}>>> virtualenv fue creado${reset}"
        sleep 2
        echo "${green}>>> Activando el virtualenv${reset}"
        echo
        cd ..
        cd ..
        cd is2_sgpa
        pipenv shell
        python manage.py runserver

    else
        echo -e "\nOpción invalida"
        echo -e "\nPrueba de nuevo!!"
        echo ""
        echo "Presione una tecla"
        read -n 1
        clear
        mainmenu
    fi
    cd ..
}

# This builds the main menu and routs the user to the function selected.

mainmenu