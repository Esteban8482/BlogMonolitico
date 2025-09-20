// ESM para Firebase v12: usa getAuth y funciones modulares
import { getAuth, onAuthStateChanged, signInWithEmailAndPassword, createUserWithEmailAndPassword, signOut } from "https://www.gstatic.com/firebasejs/12.3.0/firebase-auth.js";

// Inicialización y sincronización de sesión con el backend
(function () {
  function getFirebaseAuth() {
    if (!window.__FIREBASE_CONFIG__ || !window.__FIREBASE_APP_READY__) return null;
    try {
      return getAuth();
    } catch (_) {
      return null;
    }
  }

  function syncSession(idToken) {
    if (!idToken) return Promise.resolve();
    return fetch('/auth/session', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ idToken })
    }).then(r => r.json())
      .catch(() => ({}));
  }

  function updateNav(user) {
    const userLinks = document.getElementById('user-links');
    if (!userLinks) return;
    if (user) {
      userLinks.innerHTML = `
        <a href="/post/new">Nueva Publicación</a>
        <a href="/me">Perfil</a>
        <a href="#" id="logout-link">Salir</a>
      `;
      const logoutLink = document.getElementById('logout-link');
      if (logoutLink) {
        logoutLink.addEventListener('click', function (e) {
          e.preventDefault();
          const auth = getFirebaseAuth();
          if (!auth) return;
          signOut(auth).catch(err => alert('Error al cerrar sesión: ' + err.message));
        });
      }
    } else {
      userLinks.innerHTML = `
        <a href="/login">Entrar</a>
        <a href="/register">Registro</a>
      `;
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    const auth = getFirebaseAuth();
    if (!auth) return;

    // Adjuntar token a peticiones POST de formularios protegidos si es posible
    function attachTokenToForms() {
      const forms = document.querySelectorAll('form[method="post"]');
      forms.forEach(f => {
        if (f.__tokenAttached) return;
        f.__tokenAttached = true;
        f.addEventListener('submit', async function (ev) {
          const user = auth.currentUser;
          if (!user) return; // backend también valida sesión
          try {
            const token = await user.getIdToken();
            if (!f.querySelector('input[name="__firebase_id_token"]')) {
              const input = document.createElement('input');
              input.type = 'hidden';
              input.name = '__firebase_id_token';
              input.value = token;
              f.appendChild(input);
            }
          } catch (_) { /* noop */ }
        }, true);
      });
    }

    onAuthStateChanged(auth, async function (user) {
      updateNav(user);
      if (user) {
        try {
          const idToken = await user.getIdToken();
          sessionStorage.setItem('firebaseIdToken', idToken);
          await syncSession(idToken);
        } catch (e) { /* noop */ }
      } else {
        sessionStorage.removeItem('firebaseIdToken');
        // Avisar al backend para limpiar cookie de sesión
        fetch('/auth/logout', { method: 'POST' }).catch(() => { });
      }
      attachTokenToForms();
    });

    // Manejar formularios de login/registro con Firebase
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
      loginForm.addEventListener('submit', async function (e) {
        e.preventDefault();
        const email = loginForm.email.value;
        const password = loginForm.password.value;
        try {
          const cred = await signInWithEmailAndPassword(auth, email, password);
          const token = await cred.user.getIdToken();
          await syncSession(token);
          window.location.href = '/';
        } catch (err) {
          alert('Error al iniciar sesión: ' + err.message);
        }
      });
    }

    const registerForm = document.getElementById('register-form');
    if (registerForm) {
      registerForm.addEventListener('submit', async function (e) {
        e.preventDefault();
        const email = registerForm.email.value;
        const password = registerForm.password.value;
        try {
          const cred = await createUserWithEmailAndPassword(auth, email, password);
          const token = await cred.user.getIdToken();
          await syncSession(token);
          window.location.href = '/';
        } catch (err) {
          alert('Error al registrarse: ' + err.message);
        }
      });
    }
  });
})();
