// ESM para Firebase v12: Auth modular + Proveedor de Google
import {
  getAuth,
  onAuthStateChanged,
  signOut,
  GoogleAuthProvider,
  signInWithPopup,
} from "https://www.gstatic.com/firebasejs/12.3.0/firebase-auth.js";

// Inicialización y sincronización de sesión con el backend
(function () {
  // Indica si la sesión del servidor está sincronizada con Firebase Auth
  window.__SERVER_SESSION_OK__ = false;

  function getFirebaseAuth() {
    // Permite que se intente obtener auth si la app está lista; si no, null.
    if (!window.__FIREBASE_CONFIG__ || !window.__FIREBASE_APP_READY__) {
      return null;
    }

    try {
      return getAuth();
    } catch (e) {
      console.error(e);
      return null;
    }
  }

  function syncSession(idToken) {
    if (!idToken) return Promise.resolve(false);

    return fetch("/auth/session", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ idToken }),
    })
      .then(async (r) => {
        if (!r.ok) return false;

        try {
          const j = await r.json();

          return !!(j && j.ok);
        } catch (_) {
          return false;
        }
      })
      .catch(() => false);
  }

  function updateNav(user) {
    const logoutLink = document.getElementById("logout-link");

    if (!logoutLink) {
      return;
    }

    logoutLink.addEventListener("click", function (e) {
      e.preventDefault();

      const auth = getFirebaseAuth();
      if (!auth) return;

      signOut(auth).catch((err) =>
        alert("Error al cerrar sesión: " + err.message)
      );

      // remover sesión del backend
      fetch("/auth/logout", { method: "POST" }).then(() => {
        window.location.href = "/login";
      });
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    const auth = getFirebaseAuth();
    const googleBtn = document.getElementById("google-signin");

    if (googleBtn) {
      // Deshabilitar hasta que Firebase esté listo y adjuntar listener de todos modos
      if (!auth) {
        googleBtn.disabled = true;
        googleBtn.dataset.label = googleBtn.innerText;
        googleBtn.innerText = "Preparando Google…";
      }
    }

    // Adjuntar token a peticiones POST de formularios protegidos si es posible
    // function attachTokenToForms() {
    //   const forms = document.querySelectorAll('form[method="post"]');

    //   forms.forEach((f) => {
    //     if (f.__tokenAttached) return;

    //     f.__tokenAttached = true;

    //     f.addEventListener(
    //       "submit",
    //       async (ev) => {
    //         const user = auth.currentUser;

    //         if (!user) return; // backend también valida sesión

    //         try {
    //           const token = await user.getIdToken();

    //           if (!f.querySelector('input[name="__firebase_id_token"]')) {
    //             const input = document.createElement("input");
    //             input.type = "hidden";
    //             input.name = "__firebase_id_token";
    //             input.value = token;

    //             f.appendChild(input);
    //           }
    //         } catch (e) {
    //           console.error(`Error al obtener token attachTokenToForms`);
    //         }
    //       },
    //       true
    //     );
    //   });
    // }

    function currentPath() {
      try {
        return new URL(window.location.href).pathname;
      } catch {
        return window.location.pathname;
      }
    }

    function pathRequiresAuth(path) {
      // Define aquí las rutas que sí requieren autenticación del lado cliente
      if (path === "/me" || path === "/post/new") return true;
      if (/^\/post\/\d+\/(edit|delete|comment)$/.test(path)) return true;
      if (/^\/comment\/\d+\/delete$/.test(path)) return true;

      return false;
    }

    function redirectUnauthedToLogin(user) {
      const path = currentPath();
      const isLoginPage = path === "/login";
      const isAuthEndpoint = path.startsWith("/auth/");

      if (!user && !isLoginPage && !isAuthEndpoint && pathRequiresAuth(path)) {
        const next = encodeURIComponent(window.location.href);
        window.location.replace(`/login?next=${next}`);

        return true;
      }

      return false;
    }

    if (auth) {
      onAuthStateChanged(auth, async function (user) {
        // Resetear estado por defecto al cambiar usuario
        window.__SERVER_SESSION_OK__ = false;
        updateNav(user);

        const path = currentPath();
        const isLoginPage = path === "/login";

        if (user) {
          // 1) Sincronizar sesión con backend ANTES de cualquier redirección
          let synced = false;

          try {
            const idToken = await user.getIdToken();
            sessionStorage.setItem("firebaseIdToken", idToken);

            setTimeout(() => {
              syncSession(token).then((ok) => {
                if (ok) {
                  window.location.href = "/";
                } else {
                  alert("No se pudo sincronizar la sesión. Intenta de nuevo.");
                }
              });
            }, 1500);
          } catch (e) {
            console.error(`Error al obtener token onAuthStateChanged: ${e}`);
          }

          window.__SERVER_SESSION_OK__ = !!synced;
          updateNav(user); // refrescar enlaces según estado de servidor

          // 2) Si estamos en /login y ya hay usuario, ahora sí redirigir
          if (isLoginPage && synced) {
            const params = new URLSearchParams(window.location.search);
            const nextUrl = params.get("next");
            window.location.replace(nextUrl || "/");

            return; // evitar más acciones en esta página
          }

          if (isLoginPage && !synced) {
            const el = document.getElementById("login-status");

            if (el) {
              el.textContent = "Error Interno al crear la sesión.";
              el.style.color = "#b00020";
            }
          }
        } else {
          // Usuario no autenticado: limpiar sesión del backend y, si procede, enviar a /login
          sessionStorage.removeItem("firebaseIdToken");

          fetch("/auth/logout", { method: "POST" }).catch(() => {});
          window.__SERVER_SESSION_OK__ = false;

          if (redirectUnauthedToLogin(user)) {
            return;
          }
        }

        // attachTokenToForms();
      });
    } else {
      // Si Firebase no está listo, no forzar redirecciones para evitar bucles en /login
      updateNav(null);
      // attachTokenToForms();
    }

    // Botón de Google Sign-In en /login
    async function signInWithGoogleFlow() {
      try {
        const provider = new GoogleAuthProvider();
        provider.setCustomParameters({ prompt: "select_account" });

        const currAuth = getFirebaseAuth();

        if (!currAuth) {
          const msg = window.__FIREBASE_INIT_ERROR__
            ? "Detalle: " + window.__FIREBASE_INIT_ERROR__
            : "";

          alert(
            "Firebase aún no está listo. Intenta de nuevo en unos segundos. " +
              msg
          );

          return;
        }

        const cred = await signInWithPopup(currAuth, provider);
        const token = await cred.user.getIdToken();
        // const synced = await syncSession(token);

        // Espera 1.5 segundos antes de sincronizar sesión
        setTimeout(() => {
          syncSession(token).then((ok) => {
            if (ok) {
              window.location.href = "/";
            } else {
              alert("No se pudo sincronizar la sesión. Intenta de nuevo.");
            }
          });
        }, 1500);

        window.__SERVER_SESSION_OK__ = !!synced;

        if (!synced) {
          const el = document.getElementById("login-status");

          if (el) {
            el.textContent =
              "Error Interno al crear la sesión. Intenta de nuevo.";
            el.style.color = "#b00020";
          }

          return; // no redirigimos si el servidor no tiene sesión
        }

        const params = new URLSearchParams(window.location.search);
        const nextUrl = params.get("next");

        window.location.replace(nextUrl || "/");
      } catch (err) {
        alert("No se pudo iniciar sesión con Google: " + err.message);
      }
    }

    if (googleBtn) {
      googleBtn.addEventListener("click", function (e) {
        e.preventDefault();
        signInWithGoogleFlow();
      });
    }

    // Si Firebase se inicializa después, habilitar botón
    if (!auth && googleBtn) {
      let retries = 20; // ~10s con 500ms

      const iv = setInterval(() => {
        const a = getFirebaseAuth();

        if (a) {
          clearInterval(iv);
          googleBtn.disabled = false;

          if (googleBtn.dataset.label)
            googleBtn.innerText = googleBtn.dataset.label;
        } else if (--retries <= 0) {
          clearInterval(iv);

          googleBtn.disabled = false; // permite click para mostrar alerta
          googleBtn.innerText =
            googleBtn.dataset.label || "Continuar con Google";
        }
      }, 500);
    }

    // Exponer en window por si se desea llamar desde HTML
    window.firebaseLoginWithGoogle = signInWithGoogleFlow;
  });
})();
