<template>
  <div class="min-h-screen bg-[#F8FAFC] flex text-gray-900">
    <AdminSidebar />
    <main class="flex-1 p-8 overflow-y-auto">
      <header class="mb-10 flex flex-col md:flex-row justify-between items-center gap-4">
        <div>
          <h1 class="text-3xl font-black text-gray-900 tracking-tight italic">Control de Inscripciones</h1>
          <p class="text-gray-500 font-medium tracking-tight">Historial y estado de las inscripciones por período académico.</p>
        </div>
        <div class="flex gap-2">
           <button @click="fetchEnrollments" class="p-4 bg-white hover:bg-gray-50 rounded-2xl border border-gray-100 shadow-sm transition-all focus:outline-none focus:ring-4 focus:ring-blue-500/10 active:scale-95 group">
             <ArrowPathIcon :class="{'animate-spin': loading}" class="w-5 h-5 text-gray-400 group-hover:text-amber-500" />
           </button>
        </div>
      </header>

      <!-- Stats Bar -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-10">
        <div class="bg-white p-7 rounded-[32px] border border-gray-100 shadow-sm flex items-center gap-5 group hover:shadow-lg transition-all border-b-4 border-b-blue-500">
           <div class="h-14 w-14 rounded-2xl bg-blue-50 flex items-center justify-center text-blue-600 transition-colors group-hover:bg-blue-600 group-hover:text-white">
              <BookOpenIcon class="w-7 h-7" />
           </div>
           <div>
              <div class="text-[10px] font-black uppercase text-gray-400 mb-1 tracking-widest">Total Trámites</div>
              <div class="text-2xl font-black text-gray-900 leading-none">{{ enrollments.length }}</div>
           </div>
        </div>
        <div class="bg-white p-7 rounded-[32px] border border-gray-100 shadow-sm flex items-center gap-5 group hover:shadow-lg transition-all border-b-4 border-b-green-500">
           <div class="h-14 w-14 rounded-2xl bg-green-50 flex items-center justify-center text-green-600 transition-colors group-hover:bg-green-600 group-hover:text-white">
              <CheckBadgeIcon class="w-7 h-7" />
           </div>
           <div>
              <div class="text-[10px] font-black uppercase text-gray-400 mb-1 tracking-widest">Activas</div>
              <div class="text-2xl font-black text-gray-900 leading-none">{{ enrollments.filter(e => e.status === 'active').length }}</div>
           </div>
        </div>
        <div class="bg-white p-7 rounded-[32px] border border-gray-100 shadow-sm flex items-center gap-5 group hover:shadow-lg transition-all border-b-4 border-b-amber-500">
           <div class="h-14 w-14 rounded-2xl bg-amber-50 flex items-center justify-center text-amber-600 transition-colors group-hover:bg-amber-600 group-hover:text-white">
              <ClockIcon class="w-7 h-7" />
           </div>
           <div>
              <div class="text-[10px] font-black uppercase text-gray-400 mb-1 tracking-widest">Pendientes</div>
              <div class="text-2xl font-black text-gray-900 leading-none">{{ enrollments.filter(e => e.status === 'pending').length }}</div>
           </div>
        </div>
        <div class="bg-white p-7 rounded-[32px] border border-gray-100 shadow-sm flex items-center gap-5 group hover:shadow-lg transition-all border-b-4 border-b-rose-500">
           <div class="h-14 w-14 rounded-2xl bg-rose-50 flex items-center justify-center text-rose-600 transition-colors group-hover:bg-rose-600 group-hover:text-white">
              <XCircleIcon class="w-7 h-7" />
           </div>
           <div>
              <div class="text-[10px] font-black uppercase text-gray-400 mb-1 tracking-widest">Canceladas</div>
              <div class="text-2xl font-black text-gray-900 leading-none">{{ enrollments.filter(e => e.status === 'cancelled').length }}</div>
           </div>
        </div>
      </div>

      <!-- Advanced Tools -->
      <div class="flex flex-wrap gap-4 mb-6 bg-white p-5 rounded-[32px] border border-gray-100 shadow-sm items-center">
        <div class="relative group flex-1 max-w-sm">
           <input 
             v-model="search" 
             type="text" 
             placeholder="Buscar carnet o período..." 
             class="w-full bg-gray-50 border-transparent border focus:border-blue-100 rounded-2xl px-5 py-3 text-sm font-bold shadow-none outline-none transition-all focus:ring-4 focus:ring-blue-500/5 placeholder:text-gray-400 font-mono"
           />
           <MagnifyingGlassIcon class="w-5 h-5 absolute right-5 top-3 text-gray-300" />
        </div>

        <select v-model="filterStatus" class="px-6 py-3 bg-gray-50 border border-transparent rounded-2xl text-[11px] font-black shadow-none outline-none focus:ring-4 focus:ring-blue-500/5 appearance-none cursor-pointer hover:bg-gray-100 transition-all text-gray-600 uppercase tracking-widest">
          <option value="">TODOS LOS ESTADOS</option>
          <option value="pending">PENDIENTES</option>
          <option value="active">ACTIVAS</option>
          <option value="finished">FINALIZADAS</option>
          <option value="cancelled">CANCELADAS</option>
        </select>
        <div class="flex-1"></div>
      </div>

      <!-- Error State -->
      <div v-if="error" class="bg-red-50 p-6 rounded-[32px] border border-red-100 shadow-sm flex items-start gap-4 mb-6">
        <ServerIcon class="w-6 h-6 text-red-500 shrink-0 mt-1" />
        <div>
           <div class="font-black text-red-800 text-sm">Servicio de inscripciones no disponible.</div>
           <div class="text-xs text-red-600 mt-1 font-medium text-balance">No se pudo contactar con "enrollment_service". Asegúrese de que los servicios estén en ejecución.</div>
        </div>
      </div>

      <!-- Table View -->
      <div v-else class="bg-white rounded-[32px] border border-gray-100 shadow-sm flex flex-col min-h-[500px] overflow-hidden">
        <DataTable 
           :value="filteredEnrollments" 
           :paginator="true" 
           :rows="10" 
           :rowsPerPageOptions="[10, 25, 50]"
           dataKey="id"
           :loading="loading"
           class="p-datatable-sm w-full"
           stripedRows
           removableSort
           paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
           currentPageReportTemplate="Mostrando {first} a {last} de {totalRecords} registros"
        >
          <template #empty>
            <div class="p-10 flex flex-col items-center justify-center text-center">
              <div class="w-16 h-16 bg-gray-50 rounded-2xl flex items-center justify-center mb-4">
                <i class="pi pi-book text-2xl text-gray-300"></i>
              </div>
              <p class="text-gray-400 font-bold mb-1">No se encontraron inscripciones</p>
              <p class="text-xs text-gray-300">Ajusta los filtros de búsqueda o inténtalo de nuevo.</p>
            </div>
          </template>

          <Column field="student_carnet" header="CARNET" sortable>
            <template #body="{ data }">
              <div class="text-[11px] font-mono font-bold text-gray-600 bg-gray-50 px-2 py-1 rounded-md inline-block border border-gray-100">
                {{ data.student_carnet || data.student_id }}
              </div>
            </template>
          </Column>

          <Column field="period_name" header="PERÍODO" sortable>
            <template #body="{ data }">
              <div class="text-[12px] font-bold text-gray-800">{{ data.period_name || `ID: ${data.period_id}` }}</div>
            </template>
          </Column>

          <Column field="enrollment_date" header="FECHA INSCRIPCIÓN" sortable>
            <template #body="{ data }">
              <div class="text-[11px] font-medium text-gray-500">{{ formatDate(data.enrollment_date) }}</div>
            </template>
          </Column>

          <Column field="status" header="ESTADO" sortable>
             <template #body="{ data }">
               <span class="px-3 py-1 rounded-full text-[10px] font-black tracking-widest uppercase border" :class="{
                  'bg-amber-50 text-amber-600 border-amber-200': data.status === 'pending',
                  'bg-green-50 text-green-700 border-green-200': data.status === 'active',
                  'bg-blue-50 text-blue-700 border-blue-200': data.status === 'finished',
                  'bg-red-50 text-red-600 border-red-200': data.status === 'cancelled',
                }">{{ statusLabel(data.status) }}</span>
             </template>
          </Column>

          <Column header="ACCIÓN" alignFrozen="right">
            <template #body="{ data }">
              <div class="flex justify-start">
                 <button @click="selectedEnrollment = data" class="px-4 py-1.5 bg-blue-50 text-[10px] font-black text-[var(--upel-blue)] uppercase tracking-widest border border-blue-100 rounded-lg hover:bg-[var(--upel-blue)] hover:text-white transition-all">
                    Ver Detalles
                 </button>
              </div>
            </template>
          </Column>
        </DataTable>
      </div>
    </main>

    <!-- Detail Sidebar / Overlay -->
    <Transition name="slide">
      <div v-if="selectedEnrollment" class="fixed inset-0 z-[100] flex justify-end">
        <div class="absolute inset-0 bg-gray-900/40 backdrop-blur-sm" @click="selectedEnrollment = null"></div>
        <div class="relative w-full max-w-md bg-white h-full shadow-2xl p-8 overflow-y-auto">
          <div class="flex justify-between items-center mb-8">
            <h2 class="text-2xl font-bold text-gray-900 tracking-tight">Detalle de Inscripción</h2>
            <button @click="selectedEnrollment = null" class="p-2 hover:bg-gray-100 rounded-full text-gray-400 transition-colors">
              <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
            </button>
          </div>

          <div class="space-y-6">
            <div class="bg-gray-50 rounded-3xl p-6 border border-gray-100 shadow-sm">
              <div class="text-[10px] text-gray-400 uppercase font-black tracking-widest mb-1 italic">Estudiante</div>
              <div class="text-xl font-black text-gray-800 font-mono">{{ selectedEnrollment.student_carnet || selectedEnrollment.student_id }}</div>
              
              <div class="mt-4 grid grid-cols-2 gap-4 border-t border-gray-200 pt-4">
                <div>
                  <div class="text-[10px] text-gray-400 uppercase font-black tracking-widest mb-1 italic">Período</div>
                  <div class="text-xs font-bold text-gray-800">{{ selectedEnrollment.period_name || selectedEnrollment.period_id }}</div>
                </div>
                <div>
                  <div class="text-[10px] text-gray-400 uppercase font-black tracking-widest mb-1 italic">Estado</div>
                  <span class="px-2 py-0.5 rounded text-[10px] font-black tracking-widest uppercase border inline-block" :class="{
                    'bg-amber-50 text-amber-600 border-amber-200': selectedEnrollment.status === 'pending',
                    'bg-green-50 text-green-700 border-green-200': selectedEnrollment.status === 'active',
                    'bg-blue-50 text-blue-700 border-blue-200': selectedEnrollment.status === 'finished',
                    'bg-red-50 text-red-600 border-red-200': selectedEnrollment.status === 'cancelled',
                  }">{{ statusLabel(selectedEnrollment.status) }}</span>
                </div>
              </div>
            </div>

            <h3 class="font-black text-gray-700 flex items-center gap-2 italic uppercase tracking-wider text-sm">
              <BookmarkIcon class="w-5 h-5 text-[var(--upel-blue)]" />
              Unidades Inscritas
            </h3>

            <div v-if="selectedEnrollment.details?.length" class="space-y-4">
              <div v-for="d in selectedEnrollment.details" :key="d.id" class="bg-white border text-left border-gray-100 rounded-2xl p-4 shadow-sm relative overflow-hidden group">
                <div class="flex justify-between items-start mb-2">
                  <div class="pr-8">
                    <div class="font-bold text-sm text-gray-800 leading-tight mb-1">{{ d.uc_name || 'Unidad Curricular' }}</div>
                    <div class="text-[10px] text-gray-500 font-mono font-bold bg-gray-50 px-2 py-1 rounded-md inline-block">{{ d.uc_code || `ID: ${d.curricular_unit_id}` }} — Sec {{ d.section_number || d.section_id }}</div>
                  </div>
                  <div class="absolute top-4 right-4 text-[10px] font-black bg-blue-50 text-[var(--upel-blue)] px-2 py-1 rounded-lg border border-blue-100">{{ d.uc_credits || 0 }} UC</div>
                </div>
                <div class="mt-3 text-[11px] text-gray-600 flex items-center gap-1.5 font-bold">
                  <UserCircleIcon class="w-4 h-4 text-gray-400" />
                  {{ d.professor_name || 'Profesor por asignar' }}
                </div>
                <!-- Status specific for unit detail -->
                <div class="mt-2" v-if="d.status">
                  <span class="text-[9px] font-black uppercase tracking-widest" :class="{
                     'text-amber-500': d.status === 'pending',
                     'text-green-500': d.status === 'enrolled',
                     'text-blue-500': d.status === 'approved',
                     'text-red-500': d.status === 'failed',
                     'text-gray-400': d.status === 'withdrawn'
                  }">{{ {pending: 'Pendiente', enrolled: 'Cursando', approved: 'Aprobada', failed: 'Reprobada', withdrawn: 'Retirada'}[d.status] || d.status }}</span>
                </div>
              </div>
            </div>
            <div v-else class="text-center py-10 text-gray-400 text-xs font-black uppercase tracking-widest bg-gray-50 rounded-3xl border border-dashed border-gray-200">
              No hay unidades inscritas
            </div>
          </div>
        </div>
      </div>
    </Transition>
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
  BookmarkIcon,
  UserCircleIcon,
  BookOpenIcon,
  CheckBadgeIcon,
  ClockIcon,
  XCircleIcon
} from '@heroicons/vue/24/outline'

const authStore = useAuthStore()
const enrollments = ref([])
const loading = ref(true)
const error = ref(false)
const search = ref('')
const filterStatus = ref('')
const selectedEnrollment = ref(null)

const filteredEnrollments = computed(() => {
  let res = enrollments.value
  
  if (search.value) {
    const q = search.value.toLowerCase()
    res = res.filter(e => 
      (e.student_carnet || '').toLowerCase().includes(q) ||
      (e.student_id?.toString() || '').includes(q) ||
      (e.period_name || '').toLowerCase().includes(q)
    )
  }
  
  if (filterStatus.value) {
    res = res.filter(e => e.status === filterStatus.value)
  }
  
  return res
})

const formatDate = (dateStr) => {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleDateString('es-ES', {
    day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit'
  })
}

const statusLabel = (status) => ({
  pending: 'Pendiente', active: 'Activa', finished: 'Finalizada', cancelled: 'Cancelada'
}[status] || status)

const fetchEnrollments = async () => {
  loading.value = true
  error.value = false
  try {
    const res = await axios.get('/api/enrollments/enrollments/', {
      headers: { Authorization: `Bearer ${authStore.token}` }
    })
    enrollments.value = res.data.results || res.data
  } catch (err) {
    console.error('Fetch enrollments error:', err.response?.status, err.message)
    error.value = true
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (authStore.token) {
     fetchEnrollments()
  }
})
</script>

<style scoped>
.slide-enter-active, .slide-leave-active {
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
.slide-enter-from, .slide-leave-to {
  transform: translateX(100%);
}
</style>
