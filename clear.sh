# Detener y borrar todos los contenedores
echo "Deteniendo y borrando todos los contenedores"
docker stop $(docker ps -aq) 2>/dev/null
docker rm $(docker ps -aq) 2>/dev/null

# Borrar todas las imágenes
echo "\n-----------------------------"
echo "Borrando todas las imágenes"
docker rmi -f $(docker images -aq) 2>/dev/null

# Borrar volúmenes no usados
docker volume prune -f

# Borrar redes no usadas
docker network prune -f

# Limpieza general
docker system prune -a -f --volumes

# Apagar y borrar el clúster
echo "\n-----------------------------"
echo "Apagando y borrando el clúster"
minikube stop
minikube delete --all --purge
