<template>
  <div class="min-h-screen bg-[#F8FAFC] flex text-gray-900">
    <AdminSidebar />

    <main class="flex-1 p-8 overflow-y-auto">
      <header class="mb-10 flex flex-col md:flex-row justify-between items-center gap-4">
        <div>
          <h1 class="text-3xl font-black text-gray-900 tracking-tight italic">Control de Constancias</h1>
          <p class="text-gray-500 font-medium italic tracking-tight">Aprobación, revisión y procesamiento de documentos universitarios.</p>
        </div>
        <div class="flex gap-2">
           <button @click="fetchSolicitudes" class="p-4 bg-white hover:bg-gray-50 rounded-2xl border border-gray-100 shadow-sm transition-all focus:outline-none focus:ring-4 focus:ring-blue-500/10 active:scale-95 group">
             <ArrowPathIcon :class="{'animate-spin': loading}" class="w-5 h-5 text-gray-400 group-hover:text-amber-500" />
           </button>
        </div>
      </header>

      <!-- Stats Bar -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-10">
        <div class="bg-white p-7 rounded-[32px] border border-gray-100 shadow-sm flex items-center gap-5 group hover:shadow-lg transition-all border-b-4 border-b-blue-500">
           <div class="h-14 w-14 rounded-2xl bg-blue-50 flex items-center justify-center text-blue-600 transition-colors group-hover:bg-blue-600 group-hover:text-white">
              <DocumentIcon class="w-7 h-7" />
           </div>
           <div>
              <div class="text-[10px] font-black uppercase text-gray-400 mb-1 tracking-widest">Solicitadas</div>
              <div class="text-2xl font-black text-gray-900 leading-none">{{ solicitudes.length }}</div>
           </div>
        </div>
        <div class="bg-white p-7 rounded-[32px] border border-gray-100 shadow-sm flex items-center gap-5 group hover:shadow-lg transition-all border-b-4 border-b-amber-500">
           <div class="h-14 w-14 rounded-2xl bg-amber-50 flex items-center justify-center text-amber-600 transition-colors group-hover:bg-amber-600 group-hover:text-white">
              <ClockIcon class="w-7 h-7" />
           </div>
           <div>
              <div class="text-[10px] font-black uppercase text-gray-400 mb-1 tracking-widest">En Cola</div>
              <div class="text-2xl font-black text-gray-900 leading-none">{{ solicitudes.filter(s => s.status === 'pending').length }}</div>
           </div>
        </div>
        <div class="bg-white p-7 rounded-[32px] border border-gray-100 shadow-sm flex items-center gap-5 group hover:shadow-lg transition-all border-b-4 border-b-indigo-500">
           <div class="h-14 w-14 rounded-2xl bg-indigo-50 flex items-center justify-center text-indigo-600 transition-colors group-hover:bg-indigo-600 group-hover:text-white">
              <ArrowPathIcon class="w-7 h-7" />
           </div>
           <div>
              <div class="text-[10px] font-black uppercase text-gray-400 mb-1 tracking-widest">En Proceso</div>
              <div class="text-2xl font-black text-gray-900 leading-none">{{ solicitudes.filter(s => s.status === 'processing').length }}</div>
           </div>
        </div>
        <div class="bg-white p-7 rounded-[32px] border border-gray-100 shadow-sm flex items-center gap-5 group hover:shadow-lg transition-all border-b-4 border-b-emerald-500">
           <div class="h-14 w-14 rounded-2xl bg-emerald-50 flex items-center justify-center text-emerald-600 transition-colors group-hover:bg-emerald-600 group-hover:text-white">
              <DocumentCheckIcon class="w-7 h-7" />
           </div>
           <div>
              <div class="text-[10px] font-black uppercase text-gray-400 mb-1 tracking-widest">Listas</div>
              <div class="text-2xl font-black text-gray-900 leading-none">{{ solicitudes.filter(s => ['ready', 'delivered'].includes(s.status)).length }}</div>
           </div>
        </div>
      </div>

      <!-- Search and Filter (Bonus for UX) -->
      <div class="flex flex-wrap gap-4 mb-6 bg-white p-4 rounded-3xl border border-gray-100 shadow-sm items-center">
        <div class="relative group">
           <input 
             v-model="search" 
             type="text" 
             placeholder="Buscar por nombre o carnet..." 
             class="bg-gray-50 border-transparent border focus:border-blue-100 rounded-xl px-5 py-2.5 text-sm font-bold shadow-none w-64 outline-none transition-all focus:ring-4 focus:ring-blue-500/5 placeholder:text-gray-400 font-mono"
           />
           <MagnifyingGlassIcon class="w-4 h-4 absolute right-4 top-3 text-gray-400" />
        </div>

        <select v-model="filterStatus" class="px-5 py-2.5 bg-gray-50 border border-transparent rounded-xl text-xs font-bold shadow-none outline-none focus:ring-4 focus:ring-blue-500/5 appearance-none cursor-pointer hover:bg-gray-100 transition-all text-gray-600">
          <option value="">TODOS LOS ESTADOS</option>
          <option value="pending">PENDIENTES</option>
          <option value="processing">EN PROCESO</option>
          <option value="ready">LISTAS (PDF)</option>
          <option value="delivered">ENTREGADAS</option>
          <option value="rejected">RECHAZADAS</option>
        </select>
        <div class="flex-1"></div>
      </div>

      <!-- Error State -->
      <div v-if="error" class="bg-red-50 p-6 rounded-[32px] border border-red-100 shadow-sm flex items-start gap-4 mb-6 animate-fade-in">
        <ServerIcon class="w-6 h-6 text-red-500 shrink-0 mt-1" />
        <div>
           <div class="font-black text-red-800 text-sm italic uppercase tracking-widest">Error de Conexión</div>
           <div class="text-[11px] text-red-600 mt-1 font-bold">{{ error }}</div>
        </div>
      </div>

      <!-- PrimeVue Table -->
      <div v-else class="bg-white rounded-[32px] border border-gray-100 shadow-sm overflow-hidden flex flex-col min-h-[500px]">
        <DataTable 
           :value="filteredSolicitudes" 
           :paginator="true" 
           :rows="10" 
           :rowsPerPageOptions="[10, 25, 50]"
           dataKey="code"
           :loading="loading"
           class="p-datatable-sm w-full"
           stripedRows
           removableSort
           paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
           currentPageReportTemplate="Mostrando {first} a {last} de {totalRecords} registros"
        >
          <template #empty>
            <div class="p-20 flex flex-col items-center justify-center text-center">
              <div class="w-16 h-16 bg-gray-50 rounded-2xl flex items-center justify-center mb-4 border border-gray-100 shadow-inner">
                <i class="pi pi-file-excel text-2xl text-gray-300"></i>
              </div>
              <p class="text-gray-400 font-black italic mb-1 uppercase tracking-widest text-xs">Sin registros</p>
              <p class="text-[10px] text-gray-300 font-bold uppercase">No hay solicitudes de constancias pendientes o que coincidan.</p>
            </div>
          </template>

          <Column field="user_name" header="ESTUDIANTE" sortable>
            <template #body="{ data }">
              <div class="flex flex-col">
                <div class="text-sm font-black text-gray-900 leading-tight italic">{{ data.user_name || 'Desconocido' }}</div>
                <div class="text-[10px] text-gray-400 font-bold font-mono">{{ data.user_email }}</div>
              </div>
            </template>
          </Column>

          <Column field="cert_type_display" header="DOCUMENTO" sortable>
            <template #body="{ data }">
              <div class="flex flex-col">
                <div class="text-[11px] font-black text-gray-700 uppercase tracking-tight">{{ data.cert_type_display }}</div>
                <div class="text-[9px] font-mono text-blue-400 font-bold">REF: {{ data.code }}</div>
              </div>
            </template>
          </Column>

          <Column field="created_at" header="SOLICITADO" sortable>
            <template #body="{ data }">
              <div class="text-[11px] font-bold text-gray-500 italic">{{ new Date(data.created_at).toLocaleDateString('es-ES', { day: 'numeric', month: 'short', year: 'numeric' }) }}</div>
            </template>
          </Column>

          <Column field="status" header="ESTADO" sortable>
            <template #body="{ data }">
              <select 
                v-model="data.status"
                @change="updateStatus(data.code, data.status)"
                class="text-[10px] font-black uppercase tracking-widest rounded-xl px-4 py-1.5 outline-none border transition-all cursor-pointer shadow-sm active:scale-95"
                :class="{
                  'text-amber-600 bg-amber-50 border-amber-200': data.status === 'pending',
                  'text-blue-700 bg-blue-50 border-blue-200': data.status === 'processing',
                  'text-green-700 bg-green-50 border-green-200': data.status === 'ready',
                  'text-purple-700 bg-purple-50 border-purple-200': data.status === 'delivered',
                  'text-red-700 bg-red-50 border-red-200': data.status === 'rejected'
                }"
              >
                <option value="pending">Pendiente</option>
                <option value="processing">En proceso</option>
                <option value="ready">Generada</option>
                <option value="delivered">Entregada</option>
                <option value="rejected">Rechazada</option>
              </select>
            </template>
          </Column>

          <Column header="ACCIÓN" class="text-right whitespace-nowrap">
            <template #body="{ data }">
              <a 
                v-if="data.status === 'ready' || data.status === 'delivered'" 
                :href="'/api/constancias/' + data.code + '/pdf/?token=' + authStore.token"
                target="_blank"
                class="inline-flex items-center gap-2 bg-[var(--upel-blue)] text-white px-4 py-2 rounded-xl text-[10px] font-black uppercase tracking-widest shadow-lg shadow-blue-500/20 hover:scale-105 active:scale-95 transition-all"
              >
                <DocumentIcon class="w-3.5 h-3.5" />
                Descargar
              </a>
              <div v-else class="text-[9px] text-gray-300 font-black italic uppercase tracking-widest pr-4">Documento en cola</div>
            </template>
          </Column>
        </DataTable>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import AdminSidebar from '@/components/AdminSidebar.vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import 'primeicons/primeicons.css'
import { 
  ArrowPathIcon, 
  MagnifyingGlassIcon, 
  ServerIcon,
  DocumentIcon,
  ClockIcon,
  DocumentCheckIcon
} from '@heroicons/vue/24/outline'

const authStore = useAuthStore()
const solicitudes = ref([])
const loading = ref(true)
const error = ref('')
const search = ref('')
const filterStatus = ref('')

const filteredSolicitudes = computed(() => {
  let res = solicitudes.value
  
  if (search.value) {
    const q = search.value.toLowerCase()
    res = res.filter(s => 
      (s.user_name || '').toLowerCase().includes(q) ||
      (s.code || '').toLowerCase().includes(q)
    )
  }
  
  if (filterStatus.value) {
    res = res.filter(s => s.status === filterStatus.value)
  }
  
  return res
})

const fetchSolicitudes = async () => {
  loading.value = true
  error.value = ''
  try {
    const res = await axios.get('/api/admin/constancias/', {
      headers: { Authorization: `Bearer ${authStore.token}` }
    })
    solicitudes.value = res.data.results || res.data
  } catch (err) {
    error.value = 'Falla crítica al conectar con "constancias_service". Verifique los permisos administrativos.'
  } finally {
    loading.value = false
  }
}

const updateStatus = async (code, newStatus) => {
  try {
    await axios.patch(`/api/admin/constancias/${code}/`, { status: newStatus }, {
      headers: { Authorization: `Bearer ${authStore.token}` }
    })
  } catch (err) {
    console.error("Status update error", err)
    await fetchSolicitudes()
  }
}

onMounted(() => {
  if (authStore.token) {
    fetchSolicitudes()
  }
})
</script>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
