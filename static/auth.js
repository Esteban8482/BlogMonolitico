// Firebase Auth v12 + Google Provider (ESM)
import {
  getAuth,
  onAuthStateChanged,
  signOut,
  GoogleAuthProvider,
  signInWithPopup,
} from 'https://www.gstatic.com/firebasejs/12.3.0/firebase-auth.js'
;(function () {
  window.__SERVER_SESSION_OK__ = false

  function getFirebaseAuth() {
    if (!window.__FIREBASE_CONFIG__ || !window.__FIREBASE_APP_READY__) return null
    try {
      return getAuth()
    } catch (e) {
      console.error(e)
      return null
    }
  }

  async function syncSession(idToken) {
    if (!idToken) return false

    try {
      const res = await fetch('/auth/session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ idToken }),
      })

      if (!res.ok) {
        window.location.href = '/login'
        return false
      }

      const json = await res.json()
      return !!(json && json.ok)
    } catch {
      return false
    }
  }

  function updateNav(user) {
    const logoutLink = document.getElementById('logout-link')
    if (!logoutLink) return

    logoutLink.addEventListener('click', async (e) => {
      e.preventDefault()
      const auth = getFirebaseAuth()
      if (!auth) return

      try {
        await signOut(auth)
      } catch (err) {
        alert('Error al cerrar sesión: ' + err.message)
      }

      await fetch('/auth/logout', { method: 'POST' })
      window.location.href = '/login'
    })
  }

  function currentPath() {
    return window.location.pathname
  }

  function pathRequiresAuth(path) {
    return (
      path === '/me' ||
      path === '/post/new' ||
      /^\/post\/\d+\/(edit|delete|comment)$/.test(path) ||
      /^\/comment\/\d+\/delete$/.test(path)
    )
  }

  function redirectUnauthedToLogin(user) {
    const path = currentPath()
    const isLoginPage = path === '/login'
    const isAuthEndpoint = path.startsWith('/auth/')

    if (!user && !isLoginPage && !isAuthEndpoint && pathRequiresAuth(path)) {
      const next = encodeURIComponent(window.location.href)
      window.location.replace(`/login?next=${next}`)
      return true
    }

    return false
  }

  async function signInWithGoogleFlow() {
    const provider = new GoogleAuthProvider()
    provider.setCustomParameters({ prompt: 'select_account' })

    const auth = getFirebaseAuth()
    const statusEl = document.getElementById('login-status')

    if (!auth) {
      const msg = window.__FIREBASE_INIT_ERROR__ || ''

      if (statusEl) {
        statusEl.textContent = 'Error Interno al crear la sesión. ' + msg
        statusEl.style.color = '#b00020'
      }

      return
    }

    try {
      const cred = await signInWithPopup(auth, provider)
      const idToken = await cred.user.getIdToken()
      sessionStorage.setItem('firebaseIdToken', idToken)

      const ok = await syncSession(idToken)
      window.__SERVER_SESSION_OK__ = ok

      if (!ok) {
        if (statusEl) {
          statusEl.textContent = 'Error Interno al crear la sesión. Intenta de nuevo.'
          statusEl.style.color = '#b00020'
        }
        return
      }

      const nextUrl = new URLSearchParams(window.location.search).get('next')
      window.location.replace(nextUrl || '/')
    } catch (err) {
      alert('No se pudo iniciar sesión con Google: ' + err.message)
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    const auth = getFirebaseAuth()
    const googleBtn = document.getElementById('google-signin')

    if (googleBtn) {
      if (!auth) {
        googleBtn.disabled = true
        googleBtn.dataset.label = googleBtn.innerText
        googleBtn.innerText = 'Preparando Google…'
      }

      googleBtn.addEventListener('click', (e) => {
        e.preventDefault()
        signInWithGoogleFlow()
      })
    }

    if (!auth && googleBtn) {
      let retries = 20
      const iv = setInterval(() => {
        const a = getFirebaseAuth()

        if (a) {
          clearInterval(iv)

          googleBtn.disabled = false
          googleBtn.innerText = googleBtn.dataset.label || 'Continuar con Google'
        } else if (--retries <= 0) {
          clearInterval(iv)

          googleBtn.disabled = false
          googleBtn.innerText = googleBtn.dataset.label || 'Continuar con Google'
        }
      }, 500)
    }

    if (auth) {
      onAuthStateChanged(auth, async (user) => {
        window.__SERVER_SESSION_OK__ = false
        updateNav(user)

        if (user) {
          const idToken = await user.getIdToken()
          sessionStorage.setItem('firebaseIdToken', idToken)

          const ok = await syncSession(idToken)
          window.__SERVER_SESSION_OK__ = ok

          if (currentPath() === '/login') {
            if (ok) {
              const nextUrl = new URLSearchParams(window.location.search).get('next')
              window.location.replace(nextUrl || '/')
            } else {
              const statusEl = document.getElementById('login-status')

              if (statusEl) {
                statusEl.textContent = 'Error Interno al crear la sesión.'
                statusEl.style.color = '#b00020'
              }
            }
          }
        } else {
          sessionStorage.removeItem('firebaseIdToken')

          await fetch('/auth/logout', { method: 'POST' }).catch(() => {})
          window.__SERVER_SESSION_OK__ = false
          redirectUnauthedToLogin(user)
        }
      })
    } else {
      updateNav(null)
    }

    window.firebaseLoginWithGoogle = signInWithGoogleFlow
  })
})()
