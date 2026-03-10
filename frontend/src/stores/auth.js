import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

// Roles que dan acceso al panel administrativo (Gestión Central)
const ADMIN_ROLES = new Set([
  'admin', 'staff', 'control_estudios', 'coordinador',
  'director', 'secretaria', 'docencia'
])

const PROFESSOR_ROLES = new Set(['profesor', 'professor'])

export const useAuthStore = defineStore('auth', () => {
  // ── Estado persistido ──────────────────────────────────
  const token     = ref(localStorage.getItem('access_token') || null)
  const role      = ref(localStorage.getItem('user_role') || null)
  const firstName = ref(localStorage.getItem('user_first_name') || '')
  const lastName  = ref(localStorage.getItem('user_last_name') || '')
  const email     = ref(localStorage.getItem('user_email') || '')
  const userId    = ref(localStorage.getItem('user_id') || null)

  // ── Getters ────────────────────────────────────────────
  const isAuthenticated = computed(() => !!token.value)
  const isStudent       = computed(() => role.value === 'student' || role.value === 'estudiante')
  const isAdmin         = computed(() => ADMIN_ROLES.has(role.value))
  const isProfessor     = computed(() => PROFESSOR_ROLES.has(role.value))
  const isAspirant      = computed(() => role.value === 'aspirant')

  const fullName = computed(() => {
    const name = `${firstName.value} ${lastName.value}`.trim()
    return name || email.value || 'Usuario'
  })

  const initials = computed(() => {
    if (firstName.value && lastName.value) {
      return (firstName.value[0] + lastName.value[0]).toUpperCase()
    }
    if (firstName.value) return firstName.value.slice(0, 2).toUpperCase()
    if (email.value)     return email.value.slice(0, 2).toUpperCase()
    return 'US'
  })

  // ── Acciones ───────────────────────────────────────────
  function login(newToken, userData) {
    token.value     = newToken
    role.value      = userData.role
    firstName.value = userData.first_name || ''
    lastName.value  = userData.last_name  || ''
    email.value     = userData.email      || ''
    userId.value    = userData.id         || null

    localStorage.setItem('access_token',     newToken)
    localStorage.setItem('user_role',        userData.role)
    localStorage.setItem('user_first_name',  userData.first_name || '')
    localStorage.setItem('user_last_name',   userData.last_name  || '')
    localStorage.setItem('user_email',       userData.email      || '')
    localStorage.setItem('user_id',          userData.id         || '')
  }

  function logout() {
    token.value     = null
    role.value      = null
    firstName.value = ''
    lastName.value  = ''
    email.value     = ''
    userId.value    = null

    localStorage.removeItem('access_token')
    localStorage.removeItem('user_role')
    localStorage.removeItem('user_first_name')
    localStorage.removeItem('user_last_name')
    localStorage.removeItem('user_email')
    localStorage.removeItem('user_id')
  }

  return {
    token, role, firstName, lastName, email, userId,
    isAuthenticated, isStudent, isAdmin, isProfessor, isAspirant,
    fullName, initials,
    login, logout,
  }
})

