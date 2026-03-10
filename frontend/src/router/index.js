import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  scrollBehavior: () => ({ top: 0 }),
  routes: [
    // ── Autenticación ─────────────────────────────────────────
    {
      path: '/',
      name: 'login',
      component: () => import('@/views/Login.vue'),
      meta: { requiresGuest: true },
    },

    // ── Portal Estudiantil ────────────────────────────────────
    {
      path: '/student',
      meta: { requiresAuth: true, role: 'student' },
      children: [
        {
          path: 'dashboard',
          name: 'student_dashboard',
          component: () => import('@/views/student/Dashboard.vue'),
        },
        {
          path: 'constancias',
          name: 'student_constancias',
          component: () => import('@/views/student/Constancias.vue'),
        },
        {
          path: 'inscripcion',
          name: 'student_inscripcion',
          component: () => import('@/views/student/Inscripcion.vue'),
        },
      ],
    },

    // ── Portal Aspirante ─────────────────────────────────────
    {
      path: '/aspirant',
      meta: { requiresAuth: true, role: 'aspirant' },
      children: [
        {
          path: 'dashboard',
          name: 'aspirant_dashboard',
          component: () => import('@/views/aspirant/Dashboard.vue'),
        },
        {
          path: 'profile',
          name: 'aspirant_profile',
          component: () => import('@/views/aspirant/CompleteProfile.vue'),
        },
      ],
    },

    // ── Portal Docente ────────────────────────────────────────
    {
      path: '/professor',
      meta: { requiresAuth: true, role: 'professor' },
      children: [
        {
          path: 'dashboard',
          name: 'professor_dashboard',
          component: () => import('@/views/professor/Dashboard.vue'),
        },
        {
          path: 'section/:id/grades',
          name: 'professor_section_grades',
          component: () => import('@/views/professor/GradesManagement.vue'),
          props: true,
        },
      ],
    },

    // ── Panel Administrativo ──────────────────────────────────
    {
      path: '/panel',
      meta: { requiresAuth: true, role: 'admin' },
      children: [
        {
          path: '',
          name: 'admin_panel',
          component: () => import('@/views/admin/Dashboard.vue'),
        },
        {
          path: '/admin/curriculum',
          name: 'admin_curriculum',
          component: () => import('@/views/admin/Curriculum.vue'),
        },
        {
          path: '/admin/constancias',
          name: 'admin_constancias',
          component: () => import('@/views/admin/Constancias.vue'),
        },
        {
          path: '/admin/estudiantes',
          name: 'admin_estudiantes',
          component: () => import('@/views/admin/Estudiantes.vue'),
        },
        {
          path: '/admin/inscripciones',
          name: 'admin_inscripciones',
          component: () => import('@/views/admin/Inscripciones.vue'),
        },
        {
          path: '/admin/aspirantes',
          name: 'admin_aspirantes',
          component: () => import('@/views/admin/Aspirantes.vue'),
        },
        {
          path: '/admin/usuarios',
          name: 'admin_usuarios',
          component: () => import('@/views/admin/Usuarios.vue'),
        },
        {
          path: '/admin/configuracion',
          name: 'admin_configuracion',
          component: () => import('@/views/admin/Configuracion.vue'),
        },
      ],
    },

    // ── Catch-all (404) ───────────────────────────────────────
    {
      path: '/:pathMatch(.*)*',
      name: 'not_found',
      redirect: '/',
    },
  ],
})

// ── Navigation Guards ─────────────────────────────────────────
router.beforeEach((to) => {
  const authStore = useAuthStore()

  // Rutas de solo invitados (login) → redirigir al dashboard correcto
  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    if (authStore.isStudent)   return { name: 'student_dashboard' }
    if (authStore.isAdmin)     return { name: 'admin_panel' }
    if (authStore.isProfessor) return { name: 'professor_dashboard' }
    if (authStore.isAspirant)  return { name: 'aspirant_dashboard' }
    return true
  }

  // Rutas que requieren autenticación → redirigir a login
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return { name: 'login' }
  }

  // Control de acceso por rol
  if (to.meta.role) {
    const isAllowed = (() => {
      switch (to.meta.role) {
        case 'student':   return authStore.isStudent
        case 'admin':     return authStore.isAdmin
        case 'professor': return authStore.isProfessor
        case 'aspirant':  return authStore.isAspirant
        default: return false
      }
    })()
    if (!isAllowed) return { name: 'login' }
  }

  return true
})

export default router


