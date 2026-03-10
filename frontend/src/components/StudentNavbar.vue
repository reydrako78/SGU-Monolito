<template>
  <header class="bg-white shadow-sm border-b border-gray-100 flex items-center justify-between px-6 lg:px-20 py-3.5 sticky top-0 z-20">
    <!-- Logo / Brand -->
    <div class="flex items-center space-x-3">
      <div class="h-8 w-8 bg-[var(--upel-blue)] rounded-lg flex items-center justify-center font-extrabold text-white shadow text-sm">U</div>
      <span class="text-xl font-bold tracking-tight text-gray-800 hidden sm:block">Portal Estudiantil</span>
    </div>

    <!-- Nav Links -->
    <nav class="hidden md:flex items-center space-x-1">
      <router-link
        v-for="link in links"
        :key="link.to"
        :to="link.to"
        class="px-3 py-2 rounded-lg text-sm font-medium transition-all"
        :class="$route.path.startsWith(link.to)
          ? 'bg-[var(--upel-blue)]/10 text-[var(--upel-blue)]'
          : 'text-gray-500 hover:text-gray-800 hover:bg-gray-100'"
      >
        {{ link.label }}
      </router-link>
    </nav>

    <!-- User area -->
    <div class="flex items-center gap-3">
      <div class="text-right hidden sm:block">
        <div class="text-sm font-semibold text-gray-800">{{ authStore.fullName }}</div>
        <div class="text-xs text-gray-400">Estudiante</div>
      </div>
      <div class="h-9 w-9 rounded-full bg-gradient-to-br from-[var(--upel-blue)] to-blue-400 flex items-center justify-center text-white font-bold text-sm shadow">
        {{ authStore.initials }}
      </div>
      <button @click="handleLogout" class="ml-1 text-sm text-red-500 hover:text-red-700 font-medium transition-colors hidden sm:block">
        Salir
      </button>
    </div>
  </header>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const links = [
  { to: '/student/dashboard',   label: 'Inicio' },
  { to: '/student/constancias', label: 'Constancias' },
  { to: '/student/inscripcion', label: 'Inscripción' },
]

const handleLogout = () => {
  authStore.logout()
  router.push('/')
}
</script>
