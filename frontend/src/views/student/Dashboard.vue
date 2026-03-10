<template>
  <div class="min-h-screen bg-gray-50 flex flex-col font-sans">
    <StudentNavbar />

    <main class="flex-1 w-full max-w-7xl mx-auto p-6 lg:p-12">
      <!-- Welcome Header -->
      <section class="mb-10 flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
        <div>
          <h2 class="text-4xl font-black text-gray-900 tracking-tight">Hola, {{ authStore.firstName }}</h2>
          <p class="text-gray-500 mt-2 text-lg">Tu resumen académico y accesos rápidos del período.</p>
        </div>
        <div class="flex items-center gap-3 bg-white p-2 rounded-2xl shadow-sm border border-gray-100">
           <div class="px-4 py-1.5 bg-green-50 text-green-600 rounded-xl text-xs font-bold uppercase tracking-widest border border-green-100">
             {{ summary?.status || 'Estudiante Activo' }}
           </div>
           <div class="h-10 w-10 bg-[var(--upel-blue)] text-white rounded-xl flex items-center justify-center font-bold">
             {{ authStore.firstName?.charAt(0) }}{{ authStore.lastName?.charAt(0) }}
           </div>
        </div>
      </section>

      <!-- KPI Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
        <div class="bg-white p-6 rounded-3xl shadow-sm border border-gray-100 group hover:shadow-md transition-all">
          <div class="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">Ubicación Académica</div>
          <div class="text-2xl font-black text-gray-800">{{ summary?.semester || '—' }} Semestre</div>
          <div class="text-xs text-blue-500 mt-2 font-medium">{{ summary?.career || 'Cargando carrera...' }}</div>
        </div>
        
        <div class="bg-white p-6 rounded-3xl shadow-sm border border-gray-100 group hover:shadow-md transition-all">
          <div class="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">Índice Académico</div>
          <div class="text-2xl font-black text-gray-800">18.4 <span class="text-sm font-normal text-gray-400">/ 20</span></div>
          <div class="flex items-center gap-1 text-xs text-green-500 mt-2 font-medium">
            <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M12 7a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0V8.414l-4.293 4.293a1 1 0 01-1.414 0L8 10.414l-4.293 4.293a1 1 0 01-1.414-1.414l5-5a1 1 0 011.414 0L1win 10.586 12.586 7z" clip-rule="evenodd"/></svg>
            +0.4 este período
          </div>
        </div>

        <div class="bg-white p-6 rounded-3xl shadow-sm border border-gray-100 group hover:shadow-md transition-all">
          <div class="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">UC Aprobadas</div>
          <div class="text-2xl font-black text-gray-800">124 <span class="text-sm font-normal text-gray-400">/ 160</span></div>
          <div class="w-full bg-gray-100 h-1.5 rounded-full mt-3 overflow-hidden">
            <div class="bg-blue-500 h-full rounded-full" style="width: 77%"></div>
          </div>
        </div>

        <div class="bg-white p-6 rounded-3xl shadow-sm border border-gray-100 group hover:shadow-md transition-all">
          <div class="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">Carga Actual</div>
          <div class="text-2xl font-black text-gray-800">{{ currentEnrollment?.details?.length || 0 }} <span class="text-sm font-normal text-gray-400">Materias</span></div>
          <div class="text-xs text-gray-400 mt-2 font-medium">Período 2026-I</div>
        </div>
      </div>

      <!-- Main Layout -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-10">
        <!-- Center/Left Column -->
        <div class="lg:col-span-2 space-y-10">
          <section>
            <div class="flex justify-between items-center mb-6">
              <h3 class="text-xl font-bold text-gray-800">Mis Materias Activas</h3>
              <router-link to="/student/horario" class="text-sm font-bold text-[var(--upel-blue)] hover:underline">Ver Horario Completo</router-link>
            </div>
            
            <div v-if="loading" class="space-y-4">
              <div v-for="i in 3" :key="i" class="h-24 bg-white rounded-3xl border border-gray-100 animate-pulse"></div>
            </div>
            
            <div v-else-if="!currentEnrollment" class="bg-white p-12 rounded-3xl border border-gray-100 text-center">
              <div class="h-16 w-16 bg-gray-50 rounded-full flex items-center justify-center mx-auto mb-4 text-gray-300">
                <svg class="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" /></svg>
              </div>
              <p class="text-gray-500 font-medium">No tienes una inscripción activa para este período.</p>
              <router-link to="/student/inscripcion" class="mt-4 inline-block px-6 py-2.5 bg-[var(--upel-blue)] text-white rounded-xl text-sm font-bold">Ir a Inscripción</router-link>
            </div>

            <div v-else class="grid grid-cols-1 gap-4">
              <div v-for="subject in currentEnrollment.details" :key="subject.id" class="bg-white p-5 rounded-3xl border border-gray-100 hover:border-blue-100 transition-all flex items-center justify-between group">
                <div class="flex items-center gap-4">
                  <div class="h-12 w-12 rounded-2xl bg-gray-50 text-gray-400 flex items-center justify-center font-bold text-xs group-hover:bg-blue-50 group-hover:text-blue-500 transition-colors">
                    {{ subject.uc_code }}
                  </div>
                  <div>
                    <div class="font-bold text-gray-800">{{ subject.uc_name }}</div>
                    <div class="text-xs text-gray-400">Sección: {{ subject.section_number }} • Prof. {{ subject.professor_name || 'Sin asignar' }}</div>
                  </div>
                </div>
                <div class="text-right">
                  <div class="text-xs font-bold text-gray-300 uppercase tracking-widest mb-1">Créditos</div>
                  <div class="text-sm font-black text-gray-700">{{ subject.uc_credits }} UC</div>
                </div>
              </div>
            </div>
          </section>
        </div>

        <!-- Right Column (Sidebar) -->
        <div class="space-y-8">
          <section class="bg-[var(--upel-blue)] rounded-3xl p-8 text-white relative overflow-hidden">
            <div class="relative z-10">
              <h4 class="text-xl font-bold mb-2">Autogestión</h4>
              <p class="text-blue-100/80 text-sm mb-6">¿Necesitas un documento oficial? Solicítalo aquí.</p>
              <router-link to="/student/constancias" class="w-full py-3 bg-white text-[var(--upel-blue)] rounded-xl font-bold text-sm inline-flex items-center justify-center hover:bg-blue-50 transition-colors shadow-lg shadow-black/10">
                Solicitar Constancia
              </router-link>
            </div>
            <!-- Decorative circle -->
            <div class="absolute -right-8 -bottom-8 w-32 h-32 bg-white/10 rounded-full"></div>
          </section>

          <section class="bg-white rounded-3xl border border-gray-100 p-8 shadow-sm">
            <h4 class="text-sm font-bold text-gray-900 uppercase tracking-widest mb-6">Agenda Académica</h4>
            <div class="space-y-6">
              <div class="flex gap-4">
                <div class="h-12 w-12 rounded-2xl bg-amber-50 text-amber-600 flex flex-col items-center justify-center shrink-0 border border-amber-100">
                  <span class="text-[10px] font-bold uppercase">Hoy</span>
                  <span class="text-lg font-black leading-none">09</span>
                </div>
                <div>
                  <div class="text-sm font-bold text-gray-800">Entrega de Proyecto</div>
                  <div class="text-xs text-gray-400">Ingeniería de Software II</div>
                </div>
              </div>
              <div class="flex gap-4">
                <div class="h-12 w-12 rounded-2xl bg-red-50 text-red-500 flex flex-col items-center justify-center shrink-0 border border-red-100">
                  <span class="text-[10px] font-bold uppercase">Mar</span>
                  <span class="text-lg font-black leading-none">15</span>
                </div>
                <div>
                  <div class="text-sm font-bold text-gray-800">Cierre de Inscripción</div>
                  <div class="text-xs text-gray-400">Modificaciones finales</div>
                </div>
              </div>
              <div class="flex gap-4">
                <div class="h-12 w-12 rounded-2xl bg-blue-50 text-blue-500 flex flex-col items-center justify-center shrink-0 border border-blue-100">
                  <span class="text-[10px] font-bold uppercase">Abr</span>
                  <span class="text-lg font-black leading-none">02</span>
                </div>
                <div>
                  <div class="text-sm font-bold text-gray-800">Examen Parcial II</div>
                  <div class="text-xs text-gray-400">Matemática Discreta</div>
                </div>
              </div>
            </div>
          </section>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import StudentNavbar from '@/components/StudentNavbar.vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const loading = ref(true)
const summary = ref(null)
const currentEnrollment = ref(null)
const studentId = ref(null)

const fetchData = async () => {
  loading.value = true
  try {
    // 1. Obtener ID de estudiante vinculado al usuario
    const resStudent = await axios.get(`/api/students/students/by-user/${authStore.userId}/`)
    studentId.value = resStudent.data.id
    
    // 2. Obtener resumen y última inscripción en paralelo
    const [resSummary, resEnrollments] = await Promise.all([
      axios.get(`/api/students/students/${studentId.value}/academic-summary/`),
      axios.get(`/api/enrollments/student/${studentId.value}/`)
    ])
    
    summary.value = resSummary.data
    // Asumir que la más reciente es la última (ajustar lógica de periodo si es necesario)
    const enrolls = resEnrollments.data
    if (enrolls && enrolls.length > 0) {
      currentEnrollment.value = enrolls[enrolls.length - 1]
    }
    
  } catch (err) {
    console.error('Error fetching student dashboard data:', err)
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)
</script>
