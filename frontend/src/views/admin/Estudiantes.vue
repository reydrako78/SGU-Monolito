<template>
  <div class="min-h-screen bg-[#F8FAFC] flex text-gray-900">
    <AdminSidebar />
    <main class="flex-1 p-8 overflow-y-auto">
      <header class="mb-10 flex flex-col md:flex-row justify-between items-center gap-4">
        <div>
          <h1 class="text-3xl font-black text-gray-900 tracking-tight">Gestión de Estudiantes</h1>
          <p class="text-gray-500 font-medium">Listado de estudiantes admitidos y regulares en el sistema.</p>
        </div>
        <div class="flex gap-2">
           <button @click="fetchStudents" class="p-3 bg-white hover:bg-gray-50 rounded-2xl border border-gray-100 shadow-sm transition-all focus:outline-none focus:ring-4 focus:ring-blue-500/10">
             <ArrowPathIcon :class="{'animate-spin': loading}" class="w-5 h-5 text-gray-400" />
           </button>
        </div>
      </header>

      <!-- Stats Bar -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-10">
        <div class="bg-white p-7 rounded-[32px] border border-gray-100 shadow-sm flex items-center gap-5 group hover:shadow-lg transition-all">
           <div class="h-14 w-14 rounded-2xl bg-indigo-50 flex items-center justify-center text-indigo-600 transition-colors group-hover:bg-indigo-600 group-hover:text-white">
              <UsersIcon class="w-7 h-7" />
           </div>
           <div>
              <div class="text-[10px] font-black uppercase text-gray-400 mb-1 tracking-widest">Estudiantes</div>
              <div class="text-2xl font-black text-gray-900 leading-none">{{ students.length }}</div>
           </div>
        </div>
        <div class="bg-white p-7 rounded-[32px] border border-gray-100 shadow-sm flex items-center gap-5 group hover:shadow-lg transition-all">
           <div class="h-14 w-14 rounded-2xl bg-emerald-50 flex items-center justify-center text-emerald-600 transition-colors group-hover:bg-emerald-600 group-hover:text-white">
              <CheckBadgeIcon class="w-7 h-7" />
           </div>
           <div>
              <div class="text-[10px] font-black uppercase text-gray-400 mb-1 tracking-widest">Activos</div>
              <div class="text-2xl font-black text-gray-900 leading-none">{{ filterByStatus('active').length }}</div>
           </div>
        </div>
        <div class="bg-white p-7 rounded-[32px] border border-gray-100 shadow-sm flex items-center gap-5 group hover:shadow-lg transition-all">
           <div class="h-14 w-14 rounded-2xl bg-amber-50 flex items-center justify-center text-amber-600 transition-colors group-hover:bg-amber-600 group-hover:text-white">
              <ClockIcon class="w-7 h-7" />
           </div>
           <div>
              <div class="text-[10px] font-black uppercase text-gray-400 mb-1 tracking-widest">Inactivos</div>
              <div class="text-2xl font-black text-gray-900 leading-none">{{ filterByStatus('inactive').length }}</div>
           </div>
        </div>
        <div class="bg-white p-7 rounded-[32px] border border-gray-100 shadow-sm flex items-center gap-5 group hover:shadow-lg transition-all">
           <div class="h-14 w-14 rounded-2xl bg-blue-50 flex items-center justify-center text-blue-600 transition-colors group-hover:bg-blue-600 group-hover:text-white">
              <AcademicCapIcon class="w-7 h-7" />
           </div>
           <div>
              <div class="text-[10px] font-black uppercase text-gray-400 mb-1 tracking-widest">Graduados</div>
              <div class="text-2xl font-black text-gray-900 leading-none">{{ filterByStatus('graduated').length }}</div>
           </div>
        </div>
      </div>

      <!-- Advanced Tools -->
      <div class="flex flex-wrap gap-4 mb-6 bg-white p-5 rounded-[32px] border border-gray-100 shadow-sm items-center">
        
        <div class="relative group flex-1 max-w-sm">
           <input 
             v-model="search" 
             type="text" 
             placeholder="Buscar carnet, nombre o email..." 
             class="w-full bg-gray-50 border-transparent border focus:border-blue-100 rounded-2xl px-5 py-3 text-sm font-bold shadow-none outline-none transition-all focus:ring-4 focus:ring-blue-500/5 placeholder:text-gray-400 font-mono"
           />
           <MagnifyingGlassIcon class="w-5 h-5 absolute right-5 top-3 text-gray-300" />
        </div>

        <div class="flex gap-2">
          <select v-model="filterStatus" class="px-6 py-3 bg-gray-50 border border-transparent rounded-2xl text-[11px] font-black shadow-none outline-none focus:ring-4 focus:ring-blue-500/5 appearance-none cursor-pointer hover:bg-gray-100 transition-all text-gray-600 uppercase tracking-widest">
            <option value="">TODOS LOS ESTADOS</option>
            <option value="active">ACTIVOS (CURSANDO)</option>
            <option value="inactive">INACTIVOS</option>
            <option value="graduated">EGRESADOS</option>
            <option value="suspended">SUSPENDIDOS</option>
          </select>
          
          <select v-model="filterCareer" class="px-6 py-3 bg-gray-50 border border-transparent rounded-2xl text-[11px] font-black shadow-none outline-none focus:ring-4 focus:ring-blue-500/5 appearance-none cursor-pointer hover:bg-gray-100 transition-all text-gray-600 uppercase tracking-widest max-w-[250px]">
            <option value="">TODAS LAS CARRERAS</option>
            <option v-for="c in uniqueCareers" :key="c" :value="c">{{ c }}</option>
          </select>
        </div>
        
        <div class="flex-1"></div>
        <button class="bg-[var(--upel-blue)] text-white px-6 py-3 rounded-2xl font-bold text-sm shadow-lg shadow-blue-500/20 hover:scale-[1.02] transition-all flex items-center gap-2">
           <ArrowDownTrayIcon class="w-5 h-5 opacity-70" />
           Exportar Data
        </button>
      </div>

      <!-- Error State -->
      <div v-if="error" class="bg-red-50 p-6 rounded-[32px] border border-red-100 shadow-sm flex items-start gap-4 mb-6">
        <ServerIcon class="w-6 h-6 text-red-500 shrink-0 mt-1" />
        <div>
           <div class="font-black text-red-800 text-sm">Servicio de estudiantes no disponible.</div>
           <div class="text-xs text-red-600 mt-1 font-medium text-balance">No se pudo contactar con "students_service". Asegúrese de que los servicios estén en ejecución.</div>
        </div>
      </div>

      <!-- Table View -->
      <div v-else class="bg-white rounded-[32px] border border-gray-100 shadow-sm flex flex-col min-h-[500px] overflow-hidden">
        <DataTable 
           :value="filteredStudents" 
           :paginator="true" 
           :rows="10" 
           :rowsPerPageOptions="[10, 25, 50]"
           dataKey="id"
           :loading="loading"
           class="p-datatable-sm w-full"
           stripedRows
           removableSort
           paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
           currentPageReportTemplate="Mostrando {first} a {last} de {totalRecords} estudiantes"
        >
          <template #empty>
            <div class="p-10 flex flex-col items-center justify-center text-center">
              <div class="w-16 h-16 bg-gray-50 rounded-2xl flex items-center justify-center mb-4">
                <i class="pi pi-users text-2xl text-gray-300"></i>
              </div>
              <p class="text-gray-400 font-bold mb-1">No se encontraron estudiantes</p>
              <p class="text-xs text-gray-300">Ajusta los filtros de búsqueda o inténtalo de nuevo.</p>
            </div>
          </template>

          <Column field="full_name" header="ESTUDIANTE" sortable style="min-width: 200px">
            <template #body="{ data }">
              <div class="flex items-center gap-3">
                <div class="h-9 w-9 rounded-xl bg-green-50 flex items-center justify-center font-black text-[10px] text-green-600 shadow-sm border border-green-100/50 uppercase">
                  {{ (data.full_name?.[0] || 'U') }}
                </div>
                <div>
                  <div class="text-[13px] font-black text-gray-900">{{ data.full_name }}</div>
                  <div class="text-[10px] text-gray-400 font-bold bg-gray-50 px-1.5 py-0.5 rounded inline-block mt-0.5">{{ data.email }}</div>
                </div>
              </div>
            </template>
          </Column>

          <Column field="carnet" header="CARNET" sortable>
            <template #body="{ data }">
              <div class="text-[11px] font-mono font-bold text-gray-600 bg-gray-50 px-2 py-1 rounded-md inline-block border border-gray-100">
                {{ data.carnet || '—' }}
              </div>
            </template>
          </Column>

          <Column field="career_name" header="CARRERA ACTUAL" sortable>
            <template #body="{ data }">
              <div class="text-[11px] font-bold text-gray-700 truncate max-w-[250px]" :title="data.career_name">{{ data.career_name || '—' }}</div>
            </template>
          </Column>

          <Column field="status" header="ESTADO" sortable>
            <template #body="{ data }">
               <span class="px-3 py-1 rounded-full text-[10px] font-black tracking-widest uppercase border" :class="{
                  'bg-green-50 text-green-700 border-green-200': data.status === 'active',
                  'bg-gray-50 text-gray-500 border-gray-200': data.status === 'inactive',
                  'bg-blue-50 text-blue-700 border-blue-200': data.status === 'graduated',
                  'bg-red-50 text-red-600 border-red-200': data.status === 'suspended',
                }">{{ statusLabel(data.status) }}</span>
            </template>
          </Column>
          
          <Column header="ACCIÓN" class="text-right whitespace-nowrap">
            <template #body="{ data }">
              <div class="flex justify-end gap-2 pr-2">
                <button class="p-2.5 bg-gray-50 text-gray-400 hover:text-[var(--upel-blue)] hover:bg-blue-50 rounded-xl transition-all active:scale-90" title="Editar Perfil">
                  <PencilIcon class="w-5 h-5" />
                </button>
                <button class="p-2.5 bg-gray-50 text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-xl transition-all active:scale-90" title="Historio Académico">
                  <DocumentTextIcon class="w-5 h-5" />
                </button>
              </div>
            </template>
          </Column>
        </DataTable>
      </div>

    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import AdminSidebar from '@/components/AdminSidebar.vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import 'primeicons/primeicons.css'
import {
  MagnifyingGlassIcon,
  ArrowPathIcon,
  ServerIcon,
  UsersIcon,
  CheckBadgeIcon,
  ClockIcon,
  AcademicCapIcon,
  ArrowDownTrayIcon,
  PencilIcon,
  DocumentTextIcon
} from '@heroicons/vue/24/outline'

const authStore = useAuthStore()
const students  = ref([])
const loading   = ref(true)
const error     = ref(false)
const search    = ref('')
const filterStatus = ref('')
const filterCareer = ref('')

const uniqueCareers = computed(() => {
  const careers = students.value.map(s => s.career_name).filter(c => c)
  return [...new Set(careers)].sort()
})

const filteredStudents = computed(() => {
  let res = students.value
  
  if (search.value) {
    const q = search.value.toLowerCase()
    res = res.filter(s =>
      (s.full_name || '').toLowerCase().includes(q) ||
      (s.email || '').toLowerCase().includes(q) ||
      (s.carnet || '').toLowerCase().includes(q) ||
      (s.career_name || '').toLowerCase().includes(q)
    )
  }
  
  if (filterStatus.value) {
    res = res.filter(s => s.status === filterStatus.value)
  }

  if (filterCareer.value) {
    res = res.filter(s => s.career_name === filterCareer.value)
  }
  
  return res
})

const filterByStatus = (status) => students.value.filter(s => s.status === status)

const statusLabel = (status) => ({
  active: 'Activo', inactive: 'Inactivo', graduated: 'Egresado', suspended: 'Suspendido'
}[status] || status)

const fetchStudents = async () => {
  loading.value = true
  error.value   = false
  try {
    const [stRes, usRes] = await Promise.all([
       axios.get('/api/students/students/', {
         headers: { Authorization: `Bearer ${authStore.token}` }
       }),
       axios.get('/api/users/', {
         headers: { Authorization: `Bearer ${authStore.token}` }
       })
    ])
    
    const rawStudents = stRes.data.results || stRes.data || []
    const rawUsers = usRes.data.results || usRes.data || []
    
    // Merge de datos: students no tienen full_name, está en auth_service (usuarios)
    students.value = rawStudents.map(st => {
       const user = rawUsers.find(u => u.id === st.user_id)
       return {
          ...st,
          full_name: user?.full_name || (user?.first_name ? `${user.first_name} ${user.last_name || ''}` : `Usuario #${st.user_id}`),
          email: user?.email || '—'
       }
    })
  } catch (err) {
    console.error(err)
    error.value = true
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (authStore.token) {
     fetchStudents()
  }
})
</script>
