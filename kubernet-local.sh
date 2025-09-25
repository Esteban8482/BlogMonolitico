#!/bin/bash
# set -e

# params
# $1: init true minikube start y eval $(minikube docker-env)

if [[ $1 == "init" ]]; then
  echo "---------------------------------"
  echo "Iniciando minikube con driver docker (si no estaba iniciado)"
  minikube start --driver=docker --memory=3072 --cpus=4
  eval "$(minikube docker-env)"
  exit 0
fi

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
echo "Reiniciando deployments"
kubectl -n blog rollout restart deployment

while [[ $(kubectl -n blog get pods --no-headers | grep -v 'Running' | wc -l) -ne 0 ]]; do
  echo "Esperando que los pods estén listos..."
  sleep 5
done

echo "Todos los pods están en Running"
kubectl -n blog get pods

echo "---------------------------------"
kubectl -n blog get svc
echo "---------------------------------"
kubectl -n blog get pods
