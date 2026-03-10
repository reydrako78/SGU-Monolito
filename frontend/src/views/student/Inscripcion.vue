<template>
  <div class="min-h-screen bg-gray-50 flex flex-col">
    <StudentNavbar />

    <main class="flex-1 w-full max-w-5xl mx-auto p-8 lg:p-14">
      <!-- Title -->
      <div class="mb-10 flex flex-col md:flex-row justify-between items-start md:items-center">
        <div>
          <h2 class="text-3xl font-bold text-gray-800">Inscripción de Materias</h2>
          <p class="text-gray-500 mt-2">Selecciona las unidades curriculares para el período activo.</p>
        </div>
      </div>

      <!-- Placeholder — Próximamente -->
      <div class="bg-white rounded-3xl p-16 text-center shadow-sm border border-gray-100 flex flex-col items-center">
        <div class="h-24 w-24 bg-blue-50 text-[var(--upel-blue)] rounded-full flex items-center justify-center mb-6">
          <svg class="h-10 w-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
        </div>
        <h3 class="text-xl font-bold text-gray-800 mb-2">Módulo de Inscripción</h3>
        <p class="text-gray-500 max-w-sm">
          Este módulo está en proceso de migración al nuevo sistema Vue 3.
          Mientras tanto, puedes gestionar tus inscripciones en el portal Django.
        </p>
        <a
          href="/student/inscripcion/"
          class="mt-8 bg-[var(--upel-blue)] text-white px-6 py-2.5 rounded-xl text-sm font-medium hover:bg-[#082f70] transition-colors"
        >
          Ir al portal anterior
        </a>
      </div>
    </main>
  </div>
</template>

<script setup>
import StudentNavbar from '@/components/StudentNavbar.vue'
</script>
