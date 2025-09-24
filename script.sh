#!/usr/bin/env bash
set -euo pipefail

# ================== CONFIG RÁPIDA (ajusta si cambiaste algo) ==================
NS="blog"
IMG_USER="blog/user:dev"
IMG_POST="blog/post:dev"
IMG_COMMENTS="blog/comments:dev"
INGRESS_HOST="blog.local"

USER_KEY="./microservices/user/firestore_user.json"
POST_KEY="./microservices/post/firestore_post.json"
COMMENTS_KEY="./microservices/comments-service/commentservice-e0a2f-93c6325f974b.json"

# Pruebas reales por Ingress (se reescriben a /u..., /post..., /v1...)
TEST_USER_PATH="/api/users/exists"     # -> /u/exists
TEST_POST_PATH="/api/posts/limit/1"    # -> /post/limit/1
TEST_COMMENTS_PATH="/api/comments"     # -> /v1/comments  (ajústalo si tu ruta real es otra)
# ==============================================================================

PROJECT_ROOT="$(pwd)"
K8S_DIR="$PROJECT_ROOT/k8s"

banner(){ echo -e "\n=== $* ===\n"; }
need(){ command -v "$1" >/dev/null 2>&1 || { echo "❌ Falta $1. Instálalo y reintenta."; exit 1; }; }

# -------- 0) prereqs
need docker
need kubectl
need minikube
need curl
[[ -d "$K8S_DIR" ]] || { echo "❌ No encuentro la carpeta k8s/ en $PROJECT_ROOT"; exit 1; }

# -------- 1) build imágenes
banner "Construyendo imágenes locales"
[[ -f microservices/user/Dockerfile ]] || { echo "Falta Dockerfile en microservices/user"; exit 1; }
[[ -f microservices/post/Dockerfile ]] || { echo "Falta Dockerfile en microservices/post"; exit 1; }
[[ -f microservices/comments-service/Dockerfile ]] || { echo "Falta Dockerfile en microservices/comments-service"; exit 1; }

docker build -t "$IMG_USER" microservices/user
docker build -t "$IMG_POST" microservices/post
docker build -t "$IMG_COMMENTS" microservices/comments-service

# -------- 2) (opcional) probar en Docker local con docker compose si lo tienes
if [[ -f "$PROJECT_ROOT/docker-compose.yml" ]]; then
  banner "Levantando con docker compose (opcional)"
  docker compose up -d --build || true
  echo "Endpoints locales (host):"
  echo " - User:     http://localhost:8001/u/exists"
  echo " - Post:     http://localhost:8002/post/limit/1"
  echo " - Comments: http://localhost:8003/v1/comments (ajusta si tu ruta real es otra)"
fi

# -------- 3) minikube + cargar imágenes
banner "Iniciando minikube con driver docker (si no está iniciado)"
minikube status >/dev/null 2>&1 || minikube start --driver=docker

banner "Cargando imágenes locales a minikube"
minikube image load "$IMG_USER"
minikube image load "$IMG_POST"
minikube image load "$IMG_COMMENTS"

# -------- 4) namespace + configmap primero (si existen)
if [[ -f "$K8S_DIR/00-namespace.yaml" ]]; then
  banner "Aplicando namespace"
  kubectl apply -f "$K8S_DIR/00-namespace.yaml"
else
  kubectl get ns "$NS" >/dev/null 2>&1 || kubectl create ns "$NS"
fi

if [[ -f "$K8S_DIR/01-configmap.yaml" ]]; then
  banner "Aplicando ConfigMap(s)"
  kubectl apply -f "$K8S_DIR/01-configmap.yaml"
fi

# -------- 5) secrets (desde archivos locales)
banner "Creando Secrets de Firebase (reemplazando si existen)"
[[ -f "$USER_KEY" && -f "$POST_KEY" && -f "$COMMENTS_KEY" ]] || {
  echo "❌ No se encontraron todos los JSON:"
  echo "   $USER_KEY"
  echo "   $POST_KEY"
  echo "   $COMMENTS_KEY"
  exit 1
}
kubectl -n "$NS" delete secret firebase-user firebase-post firebase-comments >/dev/null 2>&1 || true
kubectl -n "$NS" create secret generic firebase-user     --from-file=serviceAccountKey.json="$USER_KEY"
kubectl -n "$NS" create secret generic firebase-post     --from-file=serviceAccountKey.json="$POST_KEY"
kubectl -n "$NS" create secret generic firebase-comments --from-file=serviceAccountKey.json="$COMMENTS_KEY"

# -------- 6) aplicar TODO lo de k8s/
banner "Aplicando manifiestos de k8s/"
kubectl apply -R -f "$K8S_DIR"

# -------- 7) esperar rollouts
banner "Esperando Deployments (hasta 2 min por servicio)"
kubectl -n "$NS" rollout status deploy/user --timeout=120s || true
kubectl -n "$NS" rollout status deploy/post --timeout=120s || true
kubectl -n "$NS" rollout status deploy/comments --timeout=120s || true
kubectl -n "$NS" get pods,svc

# -------- 8) habilitar ingress + /etc/hosts
banner "Habilitando NGINX Ingress en minikube"
minikube addons enable ingress >/dev/null

IP="$(minikube ip)"
if ! grep -q "$INGRESS_HOST" /etc/hosts; then
  echo "$IP  $INGRESS_HOST" | sudo tee -a /etc/hosts >/dev/null
else
  sudo sed -i "s/.*$INGRESS_HOST/$IP  $INGRESS_HOST/" /etc/hosts
fi

# Si tienes un Ingress único en k8s/99-ingress.yaml ya aplicado arriba, genial.
# Si no, puedes aplicar aquí un ingress por defecto (comenta si ya lo tienes personalizado):
if ! kubectl -n "$NS" get ingress >/dev/null 2>&1; then
  cat <<'EOF' | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: blog-ingress
  namespace: blog
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /$2
spec:
  ingressClassName: nginx
  rules:
    - host: blog.local
      http:
        paths:
          - path: /api/users(/|$)(.*)
            pathType: Prefix
            backend:
              service:
                name: user
                port:
                  number: 8080
          - path: /api/posts(/|$)(.*)
            pathType: Prefix
            backend:
              service:
                name: post
                port:
                  number: 8080
          - path: /api/comments(/|$)(.*)
            pathType: Prefix
            backend:
              service:
                name: comments
                port:
                  number: 8080
EOF
fi

kubectl -n "$NS" get ingress

# -------- 9) pruebas reales por Ingress (según tus rutas)
banner "Pruebas por Ingress (http://$INGRESS_HOST)"
echo "# USER   $TEST_USER_PATH  (-> /u/exists)"
curl -sS -i "http://$INGRESS_HOST$TEST_USER_PATH" || true
echo -e "\n# POST   $TEST_POST_PATH   (-> /post/limit/1)"
curl -sS -i "http://$INGRESS_HOST$TEST_POST_PATH" || true
echo -e "\n# CMMTS  $TEST_COMMENTS_PATH (-> /v1/... ajusta en el script si tu ruta real es otra)"
curl -sS -i "http://$INGRESS_HOST$TEST_COMMENTS_PATH" || true

banner "Listo ✅"
echo "Si algún servicio no responde:"
echo "  kubectl -n $NS logs deploy/user --tail=200"
echo "  kubectl -n $NS logs deploy/post --tail=200"
echo "  kubectl -n $NS logs deploy/comments --tail=200"
