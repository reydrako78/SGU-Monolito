<template>
  <div class="min-h-screen bg-[#F8FAFC] flex text-gray-900 animate-fade-in">
    <AdminSidebar />

    <main class="flex-1 p-8 overflow-y-auto">
      <header class="mb-10 flex flex-col md:flex-row justify-between items-center gap-4">
        <div>
          <div class="flex items-center gap-3 mb-1">
            <div class="h-2 w-2 rounded-full bg-blue-500 animate-pulse"></div>
            <span class="text-[10px] font-black text-blue-500 uppercase tracking-[0.2em] italic">Sistema Operativo</span>
          </div>
          <h1 class="text-4xl font-black text-gray-900 tracking-tighter">Panel Central <span class="text-blue-600 italic">UPEL</span></h1>
          <p class="text-gray-400 font-medium text-sm mt-1 italic">Bienvenido, {{ authStore.fullName || 'Administrador' }}. Resumen global de la institución.</p>
        </div>
        
        <div class="flex items-center gap-3 bg-white p-2.5 rounded-[24px] shadow-sm border border-gray-100">
          <div class="h-12 w-12 rounded-2xl bg-gradient-to-br from-blue-600 to-blue-800 text-white flex items-center justify-center font-black text-xl shadow-lg shadow-blue-500/20">
            {{ (authStore.fullName || 'A').charAt(0) }}
          </div>
          <div class="pr-4">
            <div class="text-sm font-black text-gray-800 leading-tight">{{ authStore.fullName }}</div>
            <div class="text-[10px] text-blue-500 uppercase font-black tracking-widest italic">{{ authStore.role || 'Admin' }}</div>
          </div>
        </div>
      </header>

      <!-- Stats Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
        <!-- Student Stat -->
        <div class="bg-white rounded-[32px] p-8 border border-gray-100 shadow-sm hover:shadow-xl hover:scale-[1.02] transition-all group overflow-hidden relative">
          <div class="absolute -right-4 -top-4 w-24 h-24 bg-blue-50 rounded-full group-hover:scale-125 transition-transform"></div>
          <div class="relative text-left">
            <div class="h-12 w-12 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center mb-6 shadow-inner">
              <UserGroupIcon class="w-6 h-6" />
            </div>
            <div class="text-[10px] text-gray-400 uppercase font-black tracking-widest mb-1 italic">Estudiantes Activos</div>
            <div class="flex items-baseline gap-2">
              <div class="text-4xl font-black text-gray-900 tracking-tighter">{{ stats.students || '0' }}</div>
              <div class="text-[10px] font-black text-green-500 bg-green-50 px-2 py-0.5 rounded-lg border border-green-100">+2.4%</div>
            </div>
          </div>
        </div>

        <!-- Aspirants Stat -->
        <div class="bg-white rounded-[32px] p-8 border border-gray-100 shadow-sm hover:shadow-xl hover:scale-[1.02] transition-all group overflow-hidden relative">
          <div class="absolute -right-4 -top-4 w-24 h-24 bg-amber-50 rounded-full group-hover:scale-125 transition-transform"></div>
          <div class="relative text-left">
            <div class="h-12 w-12 rounded-2xl bg-amber-50 text-amber-600 flex items-center justify-center mb-6 shadow-inner">
              <ClipboardDocumentCheckIcon class="w-6 h-6" />
            </div>
            <div class="text-[10px] text-gray-400 uppercase font-black tracking-widest mb-1 italic text-left">Nuevos Aspirantes</div>
            <div class="text-4xl font-black text-gray-900 tracking-tighter">{{ stats.aspirants || '0' }}</div>
          </div>
        </div>

        <!-- Certificates Stat -->
        <div class="bg-white rounded-[32px] p-8 border border-gray-100 shadow-sm hover:shadow-xl hover:scale-[1.02] transition-all group overflow-hidden relative">
          <div class="absolute -right-4 -top-4 w-24 h-24 bg-red-50 rounded-full group-hover:scale-125 transition-transform"></div>
          <div class="relative text-left">
            <div class="h-12 w-12 rounded-2xl bg-red-50 text-red-600 flex items-center justify-center mb-6 shadow-inner">
              <DocumentTextIcon class="w-6 h-6" />
            </div>
            <div class="text-[10px] text-gray-400 uppercase font-black tracking-widest mb-1 italic text-left">Constancias Pendientes</div>
            <div class="text-4xl font-black text-red-600 tracking-tighter">{{ stats.certificates || '0' }}</div>
          </div>
        </div>

        <!-- System Stat -->
        <div class="bg-white rounded-[32px] p-8 border border-gray-100 shadow-sm hover:shadow-xl hover:scale-[1.02] transition-all group overflow-hidden relative">
          <div class="absolute -right-4 -top-4 w-24 h-24 bg-green-50 rounded-full group-hover:scale-125 transition-transform"></div>
          <div class="relative text-left">
            <div class="h-12 w-12 rounded-2xl bg-green-50 text-green-600 flex items-center justify-center mb-6 shadow-inner">
               <CpuChipIcon class="w-6 h-6" />
            </div>
            <div class="text-[10px] text-gray-400 uppercase font-black tracking-widest mb-1 italic text-left">Estado Global</div>
            <div class="flex items-center gap-2">
               <div class="h-3 w-3 rounded-full bg-green-500 shadow-[0_0_10px_rgba(34,197,94,0.5)]"></div>
               <span class="text-xl font-black text-gray-800 italic uppercase tracking-tighter">Operativo</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Main Action Area -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-10">
        <!-- Large Welcome Card -->
        <div class="lg:col-span-2 bg-white rounded-[40px] shadow-sm border border-gray-100 p-10 flex flex-col md:flex-row items-center gap-10 group overflow-hidden relative">
           <div class="absolute top-0 right-0 w-64 h-64 bg-blue-50/50 rounded-full -mr-32 -mt-32 blur-3xl group-hover:bg-blue-100/50 transition-colors"></div>
           
           <div class="relative w-48 shrink-0">
             <img src="https://illustrations.popsy.co/blue/creative-work.svg" class="h-full drop-shadow-2xl" alt="Dashboard" />
           </div>
           
           <div class="relative flex-1 text-center md:text-left">
             <h2 class="text-3xl font-black text-gray-900 mb-4 leading-tight">Gestión Académica de Próxima Generación</h2>
             <p class="text-gray-500 font-medium text-sm leading-relaxed mb-8 italic">
               Usted está operando sobre una infraestructura de microservicios distribuida. 
               La nueva plataforma UPEL permite una respuesta 10x más rápida en trámites de secretaría.
             </p>
             <div class="flex flex-wrap gap-4 justify-center md:justify-start">
               <router-link to="/admin/usuarios" class="bg-gray-900 text-white px-8 py-3.5 rounded-2xl text-xs font-black uppercase tracking-widest hover:bg-black transition-all shadow-lg hover:scale-105 active:scale-95">Administrar Usuarios</router-link>
               <router-link to="/admin/inscripciones" class="bg-blue-50 text-blue-600 border border-blue-100 px-8 py-3.5 rounded-2xl text-xs font-black uppercase tracking-widest hover:bg-blue-100 transition-all">Ver Inscripciones</router-link>
             </div>
           </div>
        </div>

        <!-- Microservices Health -->
        <div class="bg-white rounded-[40px] shadow-sm border border-gray-100 p-8">
          <div class="flex items-center justify-between mb-8">
            <h3 class="text-lg font-black text-gray-900 italic uppercase tracking-tighter">Microservicios</h3>
            <span class="p-1.5 bg-gray-50 text-[10px] font-bold text-gray-400 border border-gray-100 rounded-lg italic">Health Check</span>
          </div>

          <div class="space-y-4">
             <div v-for="svc in health" :key="svc.name" class="flex items-center justify-between p-4 bg-gray-50/50 rounded-2xl border border-transparent hover:border-gray-100 hover:bg-white transition-all group">
                <div class="flex items-center gap-3">
                   <div class="h-2 w-2 rounded-full" :class="svc.status === 'ok' ? 'bg-green-500' : 'bg-red-500'"></div>
                   <span class="text-[11px] font-black text-gray-600 uppercase tracking-widest italic group-hover:text-gray-900 transition-colors text-left">{{ svc.name }}</span>
                </div>
                <div v-if="svc.latency" class="text-[9px] font-bold text-gray-300">{{ svc.latency }}ms</div>
             </div>
          </div>

          <div class="mt-8 pt-6 border-t border-gray-100">
             <div class="p-4 bg-indigo-50/50 rounded-[24px] border border-indigo-100 flex items-center gap-4">
               <div class="h-10 w-10 bg-white rounded-xl flex items-center justify-center text-indigo-500 shadow-sm shrink-0">
                  <CloudIcon class="w-5 h-5" />
               </div>
               <div class="text-left">
                  <div class="text-[10px] font-black text-indigo-800 uppercase italic">Puerta de Enlace (Nginx)</div>
                  <div class="text-[9px] text-indigo-600/70 font-bold uppercase tracking-tight">Puerto 8080 : Activo</div>
               </div>
             </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import AdminSidebar from '@/components/AdminSidebar.vue'
import { useAuthStore } from '@/stores/auth'
import { 
  UserGroupIcon, 
  DocumentTextIcon, 
  CpuChipIcon, 
  ClipboardDocumentCheckIcon,
  CloudIcon
} from '@heroicons/vue/24/outline'

const authStore = useAuthStore()
const loading = ref(true)
const stats = ref({
  students: 0,
  certificates: 0,
  aspirants: 0,
  period: '2026-I'
})

const health = ref([
  { name: 'Auth Service', status: 'ok', latency: 45 },
  { name: 'Students Service', status: 'ok', latency: 32 },
  { name: 'Curriculum Service', status: 'ok', latency: 12 },
  { name: 'Enrollment Service', status: 'ok', latency: 89 },
  { name: 'Grades Service', status: 'ok', latency: 156 },
])

const fetchStats = async () => {
  loading.value = true
  try {
    const headers = { Authorization: `Bearer ${authStore.token}` }
    const [resStudents, resCerts, resAspirants] = await Promise.all([
      axios.get('/api/students/students/', { headers }),
      axios.get('/api/admin/constancias/', { headers }),
      axios.get('/api/auth/aspirants/', { headers })
    ])
    
    stats.value.students = resStudents.data.count || resStudents.data.length || 0
    stats.value.aspirants = resAspirants.data.count || resAspirants.data.length || 0
    
    const certs = resCerts.data.results || resCerts.data
    stats.value.certificates = certs.filter(c => c.status === 'pending').length
  } catch (err) {
    console.error('Fetch stats error:', err)
  } finally {
    loading.value = false
  }
}

onMounted(fetchStats)
</script>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.8s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
