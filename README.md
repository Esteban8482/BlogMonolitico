# Microservicio de Registro (Firebase Hosting Only)

Este microservicio expone una UI mínima para registro/autenticación con Firebase Authentication (Email/Password y Google), servida 100% desde Firebase Hosting (sin Functions ni Firestore).

- UI moderna y responsive.
- 100% cliente: fácil de enlazar o embeber.
- Deploy simple con Firebase Hosting y (opcional) GitHub Actions.

## Estructura

```
.
├─ firebase.json           # Configuración mínima de Hosting
└─ public/
   └─ index.html           # SPA con registro por email y Google
```

## Requisitos
- Proyecto en Firebase
- Firebase CLI

```bash
npm i -g firebase-tools
firebase login
```

## Configuración de Authentication
1. Firebase Console → Authentication → Sign-in method
2. Habilita Email/Password y Google (elige Project support email)
3. Guarda

## Deploy manual

```bash
firebase init hosting  # si no tienes firebase.json (elige tu proyecto, public: public, SPA: No)
firebase deploy --only hosting
```

Obtendrás `https://<tu-proyecto>.web.app`.

## CI/CD con GitHub Actions (opcional)

1) Crea el secret `FIREBASE_SERVICE_ACCOUNT` en el repo (Settings → Secrets → Actions)
   - Valor: contenido JSON de una Service Account con permisos para Hosting

2) Agrega `.github/workflows/firebase-hosting.yml` con:

```yaml
name: Deploy to Firebase Hosting on push to main
on:
  push:
    branches: [ "main" ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: FirebaseExtended/action-hosting-deploy@v0
        with:
          repoToken: "${{ secrets.GITHUB_TOKEN }}"
          firebaseServiceAccount: "${{ secrets.FIREBASE_SERVICE_ACCOUNT }}"
          channelId: live
          projectId: <tu-project-id>
          entryPoint: .
```

Cada push a `main` hará deploy automático.

## Integración en otros proyectos

- Enlace directo a `https://<tu-proyecto>.web.app`
- Embebido via iframe:

```html
<iframe
  src="https://<tu-proyecto>.web.app"
  style="width:100%;height:640px;border:0;border-radius:12px;overflow:hidden"
  allow="clipboard-write; web-share"
></iframe>
```

## Personalización
- Edita `public/index.html` para branding/estilos.
- Ajusta `firebase.initializeApp({...})` con tus credenciales (`apiKey`, `authDomain`, `projectId`).

## Notas
- Esto es cliente puro. Para lógica de negocio/servidor, añade backend (o Functions en plan Blaze) y valida ID tokens de Firebase.
