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
# Usa imágenes locales
kubernetes-local.sh

# reiniciar deployments
kubectl rollout restart deployment -n blog comments
kubectl rollout restart deployment -n blog post
kubectl rollout restart deployment -n blog user
# y cuando tengas el monolith:
kubectl rollout restart deployment -n blog monolith

# Eliminar services
kubectl delete pods -n blog --all

# Verifica los servicios expuestos
kubectl get svc -n blog

# Revisa el Ingress
kubectl get ingress -n blog

# actualizar secretos
kubectl -n blog create secret generic firebase-user --from-file=... --dry-run=client -o yaml | kubectl apply -f -

# compartir puerto
kubectl port-forward -n blog svc/monolith 5000:5000

kubectl port-forward -n blog svc/monolith 5000:5000 &
kubectl port-forward -n blog svc/user 8081:8080 &
kubectl port-forward -n blog svc/post 8082:8080 &
kubectl port-forward -n blog svc/comments 8083:8080

# recontruir imagen
docker build -t blog/monolith:dev .
```
