#!/bin/bash

# Ejecutar el proyecto localmente con todos los microservicios
# Ejecutar en segundo plano o mostrarlos en consola
# Permitir elegir los microservicios a mostrar o a ejecutar

while getopts "d:r:" opt; do
  case $opt in
    d) IFS=',' read -ra DISPLAY <<< "$OPTARG" ;;
    r) IFS=',' read -ra RUN <<< "$OPTARG" ;;
  esac
done

echo "Iniciando entorno local..."

# Crear entorno virtual si no existe
if [ ! -d ".venv" ]; then
  echo "Creando entorno virtual..."
  python3 -m venv .venv --system-site-packages || {
    echo "Error al crear el entorno virtual. Verifica tu instalación de Python."
    exit 1
  }
fi

# Activar entorno virtual
source .venv/Scripts/activate || {
  echo "No se pudo activar el entorno virtual."
  exit 1
}

# Instalar dependencias
if [ -f "requirements.txt" ]; then
  pip3 install -r requirements.txt
fi

# Definir servicios
declare -A SERVICES_PATH=(
  ["auth"]="."
  ["user"]="microservices/user"
  ["post"]="microservices/post"
  ["comments"]="microservices/comments-service"
)

declare -A PIDS=()

# Determinar qué servicios ejecutar
if [ ${#RUN[@]} -eq 0 ]; then
  RUN=("auth" "user" "post" "comments")
fi

# Ejecutar servicios
for svc in "${RUN[@]}"; do
  path=${SERVICES_PATH[$svc]}
  cmd="cd $path && source $(realpath .venv/bin/activate) && python3 app.py"

  if [[ " ${DISPLAY[@]} " =~ " $svc " ]]; then
    echo "Mostrando servicio: $svc"
    gnome-terminal -- bash -c "$cmd; exec bash"
  else
    echo "Ejecutando en segundo plano: $svc"
    bash -c "$cmd" &
    PIDS[$svc]=$!
  fi
done

echo -e "\nTodos los servicios han sido lanzados."
read -p "Presiona ENTER para detenerlos..."

# Detener servicios en segundo plano
for svc in "${!PIDS[@]}"; do
  pid=${PIDS[$svc]}
  echo "Deteniendo $svc (PID $pid)..."
  kill $pid 2>/dev/null
done

echo "Servicios detenidos."
