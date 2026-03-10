<template>
  <div class="min-h-screen bg-[#F8FAFC] flex font-sans text-gray-900">
    <!-- Sophisticated Sidebar -->
    <aside class="w-28 bg-white border-r border-gray-100 flex flex-col items-center py-12 gap-12 sticky top-0 h-screen shadow-sm">
      <div class="h-14 w-14 bg-gradient-to-tr from-blue-600 to-indigo-500 rounded-2xl flex items-center justify-center text-white font-black text-2xl shadow-xl shadow-blue-500/20 transform hover:scale-105 transition-all cursor-pointer">U</div>
      
      <nav class="flex flex-col gap-8 flex-1">
        <div class="p-4 bg-blue-50 text-blue-600 rounded-[20px] cursor-pointer shadow-sm group hover:scale-110 transition-all">
          <HomeIcon class="w-7 h-7" />
        </div>
        <div class="p-4 text-gray-300 hover:text-blue-500 hover:bg-blue-50 rounded-[20px] cursor-pointer group hover:scale-110 transition-all">
          <BookOpenIcon class="w-7 h-7" />
        </div>
        <div class="p-4 text-gray-300 hover:text-blue-500 hover:bg-blue-50 rounded-[20px] cursor-pointer group hover:scale-110 transition-all">
          <UserGroupIcon class="w-7 h-7" />
        </div>
      </nav>

      <button @click="logout" class="p-4 text-gray-300 hover:text-red-500 hover:bg-red-50 rounded-[20px] transition-all group hover:scale-110">
        <ArrowLeftOnRectangleIcon class="w-7 h-7" />
      </button>
    </aside>

    <main class="flex-1 p-8 lg:p-16 overflow-y-auto">
      <!-- Header -->
      <header class="flex flex-col md:flex-row justify-between items-start md:items-center mb-16 gap-6">
        <div>
          <div class="flex items-center gap-2 mb-2">
             <span class="w-8 h-[2px] bg-blue-500"></span>
             <span class="text-[10px] font-black uppercase text-blue-500 tracking-[0.3em]">Portal del Docente</span>
          </div>
          <h1 class="text-5xl font-black text-gray-900 tracking-tighter italic">Hola, Prof. {{ authStore.lastName }}</h1>
          <p class="text-gray-400 mt-2 text-xl font-medium">Gestión académica y seguimiento de rendimiento.</p>
        </div>
        
        <div class="bg-white p-5 rounded-[28px] border border-gray-100 shadow-xl shadow-gray-200/20 flex items-center gap-5 group">
          <div class="text-right">
             <div class="text-[9px] font-black text-gray-300 uppercase tracking-widest mb-1 italic">Período 2026-I</div>
             <div class="text-sm font-black text-emerald-500 flex items-center gap-1.5 justify-end">
                <div class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
                Cierre en 12 días
             </div>
          </div>
          <div class="h-12 w-12 bg-emerald-50 text-emerald-600 rounded-2xl flex items-center justify-center transition-transform group-hover:rotate-12">
            <CalendarIcon class="w-6 h-6" />
          </div>
        </div>
      </header>

      <!-- Stats Grid -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
        <div class="bg-white p-8 rounded-[32px] shadow-sm border border-gray-100 hover:shadow-xl hover:-translate-y-1 transition-all border-b-4 border-b-blue-500 group">
          <div class="flex justify-between items-start mb-6">
            <div class="h-14 w-14 bg-blue-50 text-blue-600 rounded-2xl flex items-center justify-center group-hover:bg-blue-600 group-hover:text-white transition-colors">
              <AcademicCapIcon class="w-7 h-7" />
            </div>
            <span class="text-emerald-500 font-black text-[10px] uppercase tracking-widest bg-emerald-50 px-3 py-1.5 rounded-full border border-emerald-100">+2 esta semana</span>
          </div>
          <div class="text-[10px] font-black uppercase tracking-[0.2em] text-gray-400 mb-1">Cátedras Activas</div>
          <div class="text-4xl font-black text-gray-900 leading-none italic">{{ sections.length || 0 }}</div>
        </div>

        <div class="bg-white p-8 rounded-[32px] shadow-sm border border-gray-100 hover:shadow-xl hover:-translate-y-1 transition-all border-b-4 border-b-indigo-500 group">
          <div class="flex justify-between items-start mb-6">
            <div class="h-14 w-14 bg-indigo-50 text-indigo-600 rounded-2xl flex items-center justify-center group-hover:bg-indigo-600 group-hover:text-white transition-colors">
              <UserGroupIcon class="w-7 h-7" />
            </div>
          </div>
          <div class="text-[10px] font-black uppercase tracking-[0.2em] text-gray-400 mb-1">Estudiantes Bajo Cargo</div>
          <div class="text-4xl font-black text-gray-900 leading-none italic">{{ totalStudents }}</div>
        </div>

        <div class="bg-white p-8 rounded-[32px] shadow-sm border border-gray-100 hover:shadow-xl hover:-translate-y-1 transition-all border-b-4 border-b-amber-500 group">
          <div class="flex justify-between items-start mb-6">
            <div class="h-14 w-14 bg-amber-50 text-amber-600 rounded-2xl flex items-center justify-center group-hover:bg-amber-600 group-hover:text-white transition-colors">
              <ClipboardDocumentCheckIcon class="w-7 h-7" />
            </div>
          </div>
          <div class="text-[10px] font-black uppercase tracking-[0.2em] text-gray-400 mb-1">Actas x Procesar</div>
          <div class="text-4xl font-black text-amber-500 leading-none italic">3</div>
        </div>
      </div>

      <!-- Sections Grid -->
      <section>
        <div class="flex justify-between items-center mb-10">
          <h2 class="text-3xl font-black text-gray-900 tracking-tighter italic">Mis Cátedras</h2>
          <button class="px-8 py-3 bg-gray-900 text-white rounded-2xl text-[10px] font-black uppercase tracking-widest shadow-xl shadow-black/10 hover:bg-indigo-600 transition-all active:scale-95 flex items-center gap-2">
            <PlusIcon class="w-4 h-4" /> 
            Nueva Evaluación
          </button>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div v-if="loading" v-for="i in 2" :key="i" class="h-64 bg-white rounded-[32px] animate-pulse border border-gray-100"></div>
          
          <div v-else v-for="section in sections" :key="section.id" class="bg-white p-10 rounded-[32px] border border-gray-100 shadow-sm group hover:border-blue-500 hover:shadow-2xl hover:shadow-blue-500/5 transition-all flex flex-col justify-between relative overflow-hidden">
             <!-- Background logic icon -->
             <div class="absolute -right-10 -top-10 text-gray-50 opacity-[0.4] group-hover:opacity-100 transition-opacity">
                <BookOpenIcon class="w-48 h-48" />
             </div>

             <div class="relative z-10">
               <div class="flex justify-between items-start mb-8">
                 <div>
                    <div class="text-[10px] font-black text-blue-500 uppercase tracking-widest mb-1 italic">{{ section.uc_code }}</div>
                    <h3 class="text-2xl font-black text-gray-900 leading-[1.1] group-hover:text-blue-600 transition-colors uppercase">{{ section.uc_name }}</h3>
                 </div>
                 <div class="bg-gray-100 px-4 py-1.5 rounded-xl text-[10px] font-black text-gray-500 uppercase tracking-widest italic group-hover:bg-blue-600 group-hover:text-white transition-colors">Sección {{ section.section_number }}</div>
               </div>
               
               <div class="flex items-center justify-between">
                 <div class="flex items-center gap-3">
                   <div class="h-10 w-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center border border-blue-100 group-hover:scale-110 transition-transform">
                      <UsersIcon class="w-5 h-5" />
                   </div>
                   <div class="flex flex-col">
                      <span class="text-lg font-black text-gray-900 leading-none">{{ section.enrolled_count || 0 }}</span>
                      <span class="text-[9px] font-black uppercase tracking-widest text-gray-400">Inscritos</span>
                   </div>
                 </div>

                 <router-link 
                   :to="{ name: 'professor_section_grades', params: { id: section.id }}" 
                   class="px-6 py-3 bg-blue-50 text-blue-600 rounded-2xl text-[10px] font-black uppercase tracking-widest hover:bg-blue-600 hover:text-white transition-all shadow-sm flex items-center gap-2"
                 >
                   Gestionar Actas
                   <ArrowRightIcon class="w-4 h-4" />
                 </router-link>
               </div>
             </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'
import { 
  HomeIcon, 
  BookOpenIcon, 
  UserGroupIcon, 
  ArrowLeftOnRectangleIcon,
  CalendarIcon,
  AcademicCapIcon,
  ClipboardDocumentCheckIcon,
  PlusIcon,
  UsersIcon,
  ArrowRightIcon
} from '@heroicons/vue/24/outline'

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(true)
const sections = ref([])

const totalStudents = computed(() => {
  return sections.value.reduce((acc, curr) => acc + (curr.enrolled_count || 0), 0)
})

const fetchData = async () => {
  loading.value = true
  try {
    // Buscar secciones donde este profesor está asignado
    // Nota: El auth_service puede no tener el ID de profesor directamente en el payload
    // pero podemos filtrar por el lastName o el code si coinciden.
    // Usamos el listado filtrado por el nombre del profesor por ahora o mock.
    const res = await axios.get('/api/courses/sections/', {
      params: { professor_name: authStore.lastName }
    })
    sections.value = res.data.results || res.data
  } catch (err) {
    console.error('Error fetching professor dashboard:', err)
  } finally {
    loading.value = false
  }
}

const logout = () => {
  authStore.logout()
  router.push('/')
}

onMounted(fetchData)
</script>

<style scoped>
.transition-all { transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1); }
</style>
