<template>
  <aside class="w-64 min-h-screen bg-white border-r border-gray-100 flex flex-col py-6 sticky top-0 h-screen overflow-y-auto">
    <!-- Brand -->
    <div class="flex items-center space-x-3 px-6 mb-8">
      <div class="h-9 w-9 bg-[var(--upel-blue)] rounded-xl flex items-center justify-center font-extrabold text-white shadow text-sm">U</div>
      <div>
        <div class="text-sm font-bold text-gray-800">UPEL</div>
        <div class="text-xs text-gray-400">Panel de Gestión</div>
      </div>
    </div>

    <!-- User chip -->
    <div class="mx-4 mb-6 bg-gray-50 rounded-xl p-3 flex items-center gap-3">
      <div class="h-9 w-9 rounded-xl bg-gradient-to-br from-[var(--upel-blue)] to-blue-500 flex items-center justify-center text-white font-bold text-sm shadow-sm shrink-0">
        {{ authStore.initials }}
      </div>
      <div class="overflow-hidden">
        <div class="text-sm font-semibold text-gray-800 truncate">{{ authStore.fullName }}</div>
        <div class="text-xs text-gray-400 capitalize truncate">{{ authStore.role }}</div>
      </div>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 px-3 space-y-0.5">
      <router-link
        v-for="link in navLinks"
        :key="link.to"
        :to="link.to"
        class="flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-medium transition-all"
        :class="isActive(link.to)
          ? 'bg-[var(--upel-blue)]/10 text-[var(--upel-blue)]'
          : 'text-gray-500 hover:bg-gray-100 hover:text-gray-800'"
      >
        <span class="w-5 h-5 shrink-0" v-html="link.icon"></span>
        {{ link.label }}
      </router-link>
    </nav>

    <!-- Footer -->
    <div class="px-6 mt-6 pt-6 border-t border-gray-100">
      <button @click="handleLogout" class="w-full flex items-center gap-2 text-sm text-red-500 hover:text-red-700 font-medium transition-colors group">
        <svg class="w-4 h-4 group-hover:translate-x-0.5 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
        </svg>
        Cerrar Sesión
      </button>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route  = useRoute()
const authStore = useAuthStore()

const navLinks = computed(() => {
  const links = [
    {
      to: '/panel',
      label: 'Panel Principal',
      icon: '<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" /></svg>',
      roles: ['admin', 'control_estudios', 'docencia', 'secretaria']
    },
    {
      to: '/admin/curriculum',
      label: 'Gestión Curricular',
      icon: '<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" /></svg>',
      roles: ['admin', 'docencia']
    },
    {
      to: '/admin/constancias',
      label: 'Constancias',
      icon: '<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>',
      roles: ['admin', 'secretaria', 'control_estudios']
    },
    {
      to: '/admin/estudiantes',
      label: 'Estudiantes',
      icon: '<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" /></svg>',
      roles: ['admin', 'control_estudios']
    },
    {
      to: '/admin/inscripciones',
      label: 'Inscripciones',
      icon: '<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>',
      roles: ['admin', 'control_estudios']
    },
    {
      to: '/admin/aspirantes',
      label: 'Aspirantes',
      icon: '<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" /></svg>',
      roles: ['admin']
    },
    {
      to: '/admin/usuarios',
      label: 'Usuarios',
      icon: '<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" /></svg>',
      roles: ['admin']
    },
    {
      to: '/admin/configuracion',
      label: 'Configuración',
      icon: '<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>',
      roles: ['admin']
    },
  ]

  return links.filter(link => link.roles.includes(authStore.role))
})

const isActive = (to) => {
  if (to === '/panel') return route.path === '/panel'
  return route.path.startsWith(to)
}

const handleLogout = () => {
  authStore.logout()
  router.push('/')
}
</script>
