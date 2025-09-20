
document.addEventListener('DOMContentLoaded', function () {
  // Esperar a que el SDK de Firebase se cargue
  const firebaseApp = new Promise((resolve, reject) => {
    const unsubscribe = firebase.auth().onAuthStateChanged(user => {
      unsubscribe();
      resolve(firebase);
    });
  });

  firebaseApp.then(firebase => {
    const auth = firebase.auth();
    const userLinks = document.getElementById('user-links');

    auth.onAuthStateChanged(user => {
      if (user) {
        // Usuario está logueado
        user.getIdToken().then(idToken => {
          // Guardar el token para futuras peticiones
          sessionStorage.setItem('firebaseIdToken', idToken);
        });

        // Actualizar la UI para mostrar el estado de logueado
        userLinks.innerHTML = `
          <a href="/create-post">Nueva Publicación</a>
          <a href="/profile">Perfil</a>
          <a href="#" onclick="logout()">Salir</a>
        `;
      } else {
        // Usuario no está logueado
        sessionStorage.removeItem('firebaseIdToken');
        userLinks.innerHTML = `
          <a href="/login">Entrar</a>
          <a href="/register">Registro</a>
        `;
      }
    });

    // Manejar formularios de registro y login si existen en la página actual
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
      loginForm.addEventListener('submit', event => {
        event.preventDefault();
        const email = loginForm.email.value;
        const password = loginForm.password.value;
        auth.signInWithEmailAndPassword(email, password)
          .then(userCredential => {
            window.location.href = '/'; // Redirigir a la página principal
          })
          .catch(error => {
            alert('Error al iniciar sesión: ' + error.message);
          });
      });
    }

    const registerForm = document.getElementById('register-form');
    if (registerForm) {
      registerForm.addEventListener('submit', event => {
        event.preventDefault();
        const email = registerForm.email.value;
        const password = registerForm.password.value;
        auth.createUserWithEmailAndPassword(email, password)
          .then(userCredential => {
            window.location.href = '/'; // Redirigir a la página principal
          })
          .catch(error => {
            alert('Error al registrarse: ' + error.message);
          });
      });
    }
  });
});

function logout() {
  firebase.auth().signOut().then(() => {
    window.location.href = '/login';
  }).catch(error => {
    alert('Error al cerrar sesión: ' + error.message);
  });
}
