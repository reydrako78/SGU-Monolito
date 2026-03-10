<template>
  <div class="min-h-screen bg-gray-50 flex flex-col">
    <StudentNavbar />

    <main class="flex-1 w-full max-w-7xl mx-auto p-8 lg:p-14">
      <!-- Title Area -->
      <div class="mb-10 flex flex-col md:flex-row justify-between items-start md:items-center">
        <div>
          <h2 class="text-3xl font-bold text-gray-800">Mis Trámites</h2>
          <p class="text-gray-500 mt-2">Gestiona o solicita nuevas constancias académicas firmadas digitalmente.</p>
        </div>
        <button @click="showModal = true" class="mt-4 md:mt-0 bg-[var(--upel-blue)] text-white px-6 py-2.5 rounded-xl text-sm font-medium tracking-wide shadow-md hover:bg-[#082f70] transition-colors flex items-center gap-2">
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Nueva Solicitud
        </button>
      </div>

      <!-- State: Loading -->
      <div v-if="loading" class="flex flex-col items-center justify-center py-20 text-gray-400">
        <svg class="animate-spin h-10 w-10 text-[var(--upel-blue)] mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <p>Cargando constancias...</p>
      </div>

      <!-- State: Error -->
      <div v-else-if="error" class="bg-red-50 text-red-600 p-6 rounded-2xl border border-red-100 flex items-center gap-4">
        <svg class="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
        {{ error }}
      </div>

      <!-- State: Empty List -->
      <div v-else-if="certificados.length === 0" class="bg-white rounded-3xl p-16 text-center shadow-sm border border-gray-100 flex flex-col items-center">
        <div class="h-24 w-24 bg-blue-50 text-[var(--upel-blue)] rounded-full flex items-center justify-center mb-6">
          <svg class="h-10 w-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <h3 class="text-xl font-bold text-gray-800 mb-2">No tienes trámites activos</h3>
        <p class="text-gray-500 max-w-sm">Aún no has solicitado ninguna constancia en este período. Puedes generar una nueva presionando el botón superior.</p>
      </div>
      <!-- State: List Items (DataTable) -->
      <div v-else class="bg-white shadow-xl border border-gray-100 rounded-[32px] overflow-hidden">
        <div class="p-6 border-b border-gray-50 bg-gray-50/10 flex items-center gap-4">
           <div class="relative flex-1 max-w-sm">
              <input v-model="search" type="text" placeholder="Buscar trámite..." class="w-full bg-white border border-gray-200 rounded-2xl px-5 py-2.5 text-sm font-bold shadow-sm outline-none focus:ring-4 focus:ring-blue-500/5 transition-all" />
              <ArrowPathIcon v-if="loading" class="w-4 h-4 absolute right-4 top-3 text-blue-400 animate-spin" />
           </div>
        </div>

        <DataTable 
          :value="filteredCerts" 
          stripedRows 
          :paginator="true" 
          :rows="8"
          class="p-datatable-sm"
          responsiveLayout="stack"
        >
          <template #empty>
             <div class="p-10 text-center text-gray-400 italic font-black uppercase text-[10px]">No se encontraron registros</div>
          </template>

          <Column field="code" header="TRÁMITE" sortable>
            <template #body="{ data }">
              <div class="flex items-center gap-4 py-1">
                <div class="h-10 w-10 rounded-2xl bg-blue-50 text-[var(--upel-blue)] flex items-center justify-center border border-blue-100 italic transition-all group-hover:scale-110">
                   <DocumentTextIcon class="w-5 h-5" />
                </div>
                <div>
                   <div class="text-[11px] font-black text-gray-900 uppercase tracking-tighter">{{ data.cert_type_display }}</div>
                   <div class="text-[9px] font-mono text-gray-400 font-bold uppercase">{{ data.code }}</div>
                </div>
              </div>
            </template>
          </Column>

          <Column field="purpose_display" header="MOTIVO / DESTINO" sortable class="text-[10px] font-bold text-gray-500 italic">
            <template #body="{ data }">
               {{ data.purpose_display }}
            </template>
          </Column>

          <Column field="status" header="ESTADO" sortable class="text-center">
            <template #body="{ data }">
              <span :class="statusBadgeClasses(data.status)">
                {{ data.status_display }}
              </span>
            </template>
          </Column>

          <Column field="created_at" header="SOLICITADO" sortable class="text-center font-mono text-[10px] text-gray-400 font-bold">
            <template #body="{ data }">
               {{ new Date(data.created_at).toLocaleDateString() }}
            </template>
          </Column>

          <Column header="GESTIÓN" class="text-right">
            <template #body="{ data }">
              <a 
                v-if="data.status === 'ready' || data.status === 'delivered'" 
                :href="'/api/constancias/' + data.code + '/pdf/?token=' + authStore.token"
                target="_blank"
                class="inline-flex items-center justify-center p-3.5 bg-gray-50 hover:bg-[var(--upel-blue)] text-gray-400 hover:text-white rounded-2xl transition-all shadow-sm hover:shadow-blue-500/20 active:scale-95"
                title="Descargar PDF"
              >
                <ArrowDownTrayIcon class="w-5 h-5" />
              </a>
              <div v-else class="pr-4 italic text-[10px] font-black text-gray-300 uppercase animate-pulse">
                 En espera
              </div>
            </template>
          </Column>
        </DataTable>
      </div>
    </main>

    <!-- Modal Request -->
    <Teleport to="body">
      <div v-if="showModal" class="fixed inset-0 bg-gray-900/60 backdrop-blur-md flex items-center justify-center p-4 z-[100] transition-all overflow-y-auto">
        <div class="bg-white rounded-[40px] shadow-2xl w-full max-w-lg overflow-hidden animate-fade-in-up border border-white/20">
          <div class="p-10 pb-4 flex justify-between items-start">
            <div>
              <h3 class="text-2xl font-black text-gray-900 italic uppercase tracking-tighter">Nueva Solicitud</h3>
              <p class="text-[10px] text-gray-400 font-bold uppercase tracking-widest mt-1">Gestión de documentos oficiales</p>
            </div>
            <button @click="showModal = false" class="p-2 bg-gray-50 text-gray-400 hover:text-red-500 rounded-2xl transition-all">
              <XMarkIcon class="w-6 h-6" />
            </button>
          </div>

          <form @submit.prevent="submitRequest" class="p-10 pt-6 space-y-6">
            <div class="space-y-4">
              <div class="group">
                <label class="block text-[11px] font-black uppercase text-gray-400 mb-2 px-1">Tipo de Constancia</label>
                <div class="relative">
                  <select v-model="form.cert_type" required class="w-full bg-gray-50 border-gray-100 border rounded-2xl px-6 py-4 text-sm font-bold outline-none appearance-none focus:ring-4 focus:ring-blue-500/5 transition-all">
                    <option value="constancia_estudios">Constancia de Estudios</option>
                    <option value="record_notas">Certificación de Calificaciones</option>
                    <option value="buena_conducta">Carta de Buena Conducta</option>
                    <option value="carga_academica">Certificado de Carga Académica</option>
                  </select>
                  <div class="absolute right-6 top-4 pointer-events-none text-gray-400">
                    <DocumentTextIcon class="w-5 h-5" />
                  </div>
                </div>
              </div>

              <div class="group">
                <label class="block text-[11px] font-black uppercase text-gray-400 mb-2 px-1">Propósito / Destino</label>
                <div class="relative">
                  <select v-model="form.purpose" required class="w-full bg-gray-50 border-gray-100 border rounded-2xl px-6 py-4 text-sm font-bold outline-none appearance-none focus:ring-4 focus:ring-blue-500/5 transition-all">
                    <option value="beca">Becas y Ayudas</option>
                    <option value="empleo">Requerimiento Laboral</option>
                    <option value="pasaporte">Trámites de Identidad (SAIME)</option>
                    <option value="personal">Uso Informativo Personal</option>
                    <option value="otro">Otros Fines Específicos</option>
                  </select>
                  <div class="absolute right-6 top-4 pointer-events-none text-gray-400">
                    <CheckBadgeIcon class="w-5 h-5" />
                  </div>
                </div>
              </div>
            </div>

            <div class="pt-6 flex gap-4">
              <button type="button" @click="showModal = false" class="flex-1 px-8 py-4 rounded-2xl font-bold text-sm text-gray-500 hover:bg-gray-100 transition-all">
                Cerrar
              </button>
              <button type="submit" :disabled="submitting" class="flex-[2] bg-[var(--upel-blue)] text-white px-8 py-4 rounded-[24px] font-black text-xs uppercase tracking-widest shadow-xl shadow-blue-500/20 hover:shadow-blue-500/40 hover:scale-[1.02] active:scale-95 transition-all disabled:opacity-50 flex items-center justify-center gap-3">
                <ArrowPathIcon v-if="submitting" class="w-4 h-4 animate-spin" />
                {{ submitting ? 'Procesando...' : 'Generar Trámite' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import StudentNavbar from '@/components/StudentNavbar.vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import { 
  PlusIcon, 
  ArrowPathIcon, 
  DocumentTextIcon, 
  ArrowDownTrayIcon,
  XMarkIcon,
  CheckBadgeIcon,
  ExclamationCircleIcon
} from '@heroicons/vue/24/outline'

const authStore = useAuthStore()
const certificados = ref([])
const loading = ref(true)
const search = ref('')
const error = ref('')

// Modal
const showModal = ref(false)
const submitting = ref(false)
const form = ref({
  cert_type: 'constancia_estudios',
  purpose: 'personal'
})

const filteredCerts = computed(() => {
  if (!search.value) return certificados.value
  const q = search.value.toLowerCase()
  return certificados.value.filter(c => 
    (c.code || '').toLowerCase().includes(q) || 
    (c.cert_type_display || '').toLowerCase().includes(q)
  )
})

const fetchCertificados = async () => {
  try {
    const res = await axios.get('/api/student/constancias/', {
      headers: { Authorization: `Bearer ${authStore.token}` }
    })
    // Support paginated DRF responses (res.data.results) or plain list (res.data)
    certificados.value = res.data.results || res.data
  } catch (err) {
    error.value = 'No se pudieron cargar las constancias. Verifica tu conexión.'
  } finally {
    loading.value = false
  }
}

const submitRequest = async () => {
  submitting.value = true
  try {
    await axios.post('/api/student/constancias/', form.value, {
      headers: { Authorization: `Bearer ${authStore.token}` }
    })
    showModal.value = false
    loading.value = true
    await fetchCertificados() // Recargar lista
  } catch (err) {
    alert("Hubo un error al procesar tu solicitud.")
  } finally {
    submitting.value = false
  }
}

const statusBadgeClasses = (status) => {
  const map = {
    'pending': 'bg-amber-50 text-amber-600 border border-amber-100 px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-tighter shadow-sm',
    'processing': 'bg-blue-50 text-blue-600 border border-blue-100 px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-tighter shadow-sm',
    'ready': 'bg-emerald-50 text-emerald-600 border border-emerald-100 px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-tighter shadow-sm',
    'delivered': 'bg-indigo-50 text-indigo-600 border border-indigo-100 px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-tighter shadow-sm',
    'rejected': 'bg-rose-50 text-rose-600 border border-rose-100 px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-tighter shadow-sm'
  }
  return map[status] || map['pending']
}

onMounted(() => {
  fetchCertificados()
})
</script>

<style scoped>
.animate-fade-in-up {
  animation: fadeInUp 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); scale: 0.95; }
  to { opacity: 1; transform: translateY(0); scale: 1; }
}
</style>
