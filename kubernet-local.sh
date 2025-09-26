#!/bin/bash
# set -e

# Activar entorno Docker de Minikube si se usa init o start
# if [[ "$1" == "init" || "$2" == "init" || "$3" == "init" ]]; then
#   echo "---------------------------------"
#   echo "Iniciando minikube con driver docker (si no estaba iniciado)"
#   minikube start --driver=docker --memory=3072 --cpus=4
#   eval "$(minikube docker-env)"
# fi

# if [[ "$1" == "start" || "$2" == "start" || "$3" == "start" ]]; then
#   echo "---------------------------------"
#   echo "Iniciando minikube"
#   minikube start --driver=docker
#   eval "$(minikube docker-env)"
# fi

# Despliegue si se incluye "build"
if [[ "$1" == "build" || "$2" == "build" ]]; then
  echo "---------------------------------"
  echo "---------------------------------"
  echo "Construyendo imágenes"
  docker build -t blog/monolith:dev . &
  docker build -t blog/user:dev ./microservices/user &
  docker build -t blog/post:dev ./microservices/post &
  docker build -t blog/comments:dev ./microservices/comments-service &
  wait


  echo "---------------------------------"
  echo "Aplicando namespace"
  kubectl apply -f k8s/00-namespace.yaml

  echo "---------------------------------"
  echo "Creando/actualizando secrets"

  # Comments
  kubectl -n blog delete secret firebase-comments --ignore-not-found
  kubectl -n blog create secret generic firebase-comments \
    --from-file=serviceAccountKey.json=./microservices/comments-service/commentservice-e0a2f-93c6325f974b.json

  # Post
  kubectl -n blog delete secret firebase-post --ignore-not-found
  kubectl -n blog create secret generic firebase-post \
    --from-file=serviceAccountKey.json=./microservices/post/firestore_post.json

  # User
  kubectl -n blog delete secret firebase-user --ignore-not-found
  kubectl -n blog create secret generic firebase-user \
    --from-file=serviceAccountKey.json=./microservices/user/firestore_user.json

  # Monolith
  kubectl -n blog delete secret firebase-monolith --ignore-not-found
  kubectl -n blog create secret generic firebase-monolith \
    --from-file=serviceAccountKey.json=./firebase-admin.json

  echo "---------------------------------"
  echo "Aplicando manifests"
  kubectl apply -f k8s/ -R

  echo "---------------------------------"
  echo "Actualizando imágenes en deployments"
  kubectl delete pod -l app=monolith -n blog
  kubectl delete pod -l app=user -n blog
  kubectl delete pod -l app=post -n blog
  kubectl delete pod -l app=comments -n blog

  echo "---------------------------------"
  echo "Esperando que los pods estén listos..."
  while [[ $(kubectl -n blog get pods --no-headers | grep -v 'Running' | wc -l) -ne 0 ]]; do
    kubectl -n blog get pods
    sleep 5
    echo "---------------------------------"
  done

  echo "Todos los pods están en Running"
  kubectl -n blog get pods

  echo "---------------------------------"
  kubectl -n blog get svc
fi

if [[ "$1" == "run" || "$2" == "run" ]]; then
  echo "---------------------------------"
  # minikube service monolith -n blog
  kubectl -n blog port-forward svc/monolith 5000
fi

if [[ "$1" == "deploy" ]]; then
  echo "---------------------------------"
  echo "Activando Ingress y aplicando configuración"
  echo "Instalando/actualizando Ingress nginx"
  minikube addons enable ingress
  kubectl apply -f k8s/99-ingress.yaml
  echo "Ingress aplicado. Ejecuta 'minikube tunnel' en otra terminal para exponerlo."
  echo "Verifica IP con: kubectl get ingress -n blog"
fi

if [[ "$1" == "stop" ]]; then
  echo "---------------------------------"
  echo "Parando minikube"
  eval "$(minikube docker-env -u)"
  minikube stop
  echo "---------------------------------"
  echo "Problemas al activar docker Cerrar y volver a abrir el terminal y ejecutar:"
  echo "docker info"
fi