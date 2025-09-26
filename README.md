# Guía rápida

## Ejecución local

Requisitos: Python 3.8+ y pip

Windows:

```powershell
./run.ps1
```

## Docker

```powershell
docker compose up --build

# limpiar imágenes y contenedores
docker compose down --rmi all -v
```

Puertos: monolito 5000; microservicios: user 5002, post 5003, comments 8091.

## Kubernetes

### Requisitos

Requisitos: Kubernetes y kubectl

```bash
minikube start --driver=docker
eval "$(minikube docker-env)"

# Ejecutar
# -build construye y carga las imágenes, carga la configuración y reinicia el clúster
# -run comparte el puerto del servicio principal en localhost:5000
./kubernetes-local.sh build run
```
