<template>
  <div class="min-h-screen bg-[#F8FAFC] flex text-gray-900">
    <AdminSidebar />
    <main class="flex-1 p-8 overflow-y-auto">
      <header class="mb-10 flex flex-col md:flex-row justify-between items-center gap-4">
        <div>
          <h1 class="text-3xl font-black text-gray-900 tracking-tight">Proceso de Admisión</h1>
          <p class="text-gray-500 font-medium">Procesamiento y resolución de solicitudes de admisión de aspirantes.</p>
        </div>
        <div class="flex gap-2">
          <button @click="fetchData" class="p-3 bg-white hover:bg-gray-50 rounded-2xl border border-gray-100 shadow-sm transition-all focus:outline-none focus:ring-4 focus:ring-blue-500/10 active:scale-95 group">
            <ArrowPathIcon :class="{ 'animate-spin': loading }" class="w-5 h-5 text-gray-400 group-hover:text-blue-500" />
          </button>
        </div>
      </header>

      <!-- Stats Bar -->
      <div class="grid grid-cols-1 md:grid-cols-5 gap-6 mb-8">
        <div class="bg-white p-6 rounded-[32px] border border-gray-100 shadow-sm flex flex-col items-center justify-center">
          <div class="text-[10px] font-black uppercase text-gray-400 mb-1 tracking-widest">Total en Proceso</div>
          <div class="text-2xl font-black text-gray-900">{{ aspirants.length }}</div>
        </div>
        <div class="bg-amber-50 p-6 rounded-[32px] border border-amber-100 shadow-sm flex flex-col items-center justify-center">
          <div class="text-[10px] font-black uppercase text-amber-500 mb-1 tracking-widest">Pendientes</div>
          <div class="text-2xl font-black text-amber-600">{{ countByStatus('pending') }}</div>
        </div>
        <div class="bg-blue-50 p-6 rounded-[32px] border border-blue-100 shadow-sm flex flex-col items-center justify-center">
          <div class="text-[10px] font-black uppercase text-blue-500 mb-1 tracking-widest">En Revisión</div>
          <div class="text-2xl font-black text-blue-600">{{ countByStatus('in_review') }}</div>
        </div>
        <div class="bg-green-50 p-6 rounded-[32px] border border-green-100 shadow-sm flex flex-col items-center justify-center">
          <div class="text-[10px] font-black uppercase text-green-500 mb-1 tracking-widest">Admitidos</div>
          <div class="text-2xl font-black text-green-600">{{ countByStatus('approved') }}</div>
        </div>
        <div class="bg-red-50 p-6 rounded-[32px] border border-red-100 shadow-sm flex flex-col items-center justify-center">
          <div class="text-[10px] font-black uppercase text-red-400 mb-1 tracking-widest">Rechazados</div>
          <div class="text-2xl font-black text-red-500">{{ countByStatus('rejected') }}</div>
        </div>
      </div>

      <!-- Filtros -->
      <div class="bg-white p-4 rounded-3xl border border-gray-100 shadow-sm flex flex-wrap gap-4 mb-6 items-center">
        <div class="relative">
          <input
            v-model="search"
            type="text"
            placeholder="Nombre, email o código..."
            class="bg-gray-50 border-transparent border focus:border-blue-100 rounded-xl px-5 py-2.5 text-sm font-bold w-64 outline-none transition-all focus:ring-4 focus:ring-blue-500/5 placeholder:text-gray-400"
          />
          <MagnifyingGlassIcon class="w-4 h-4 absolute right-4 top-3 text-gray-400" />
        </div>

        <select v-model="typeFilter" class="px-5 py-2.5 bg-gray-50 border border-transparent rounded-xl text-xs font-bold outline-none focus:ring-4 focus:ring-blue-500/5 appearance-none cursor-pointer hover:bg-gray-100 transition-all text-gray-600">
          <option value="">TODOS LOS TIPOS</option>
          <option value="ordinario">ORDINARIO</option>
          <option value="convalidacion">CONVALIDACIÓN</option>
          <option value="traslado">TRASLADO</option>
          <option value="reingreso">REINGRESO</option>
          <option value="equivalencia">EQUIVALENCIA</option>
        </select>

        <select v-model="statusFilter" class="px-5 py-2.5 bg-gray-50 border border-transparent rounded-xl text-xs font-bold outline-none focus:ring-4 focus:ring-blue-500/5 appearance-none cursor-pointer hover:bg-gray-100 transition-all text-gray-600">
          <option value="">TODOS LOS ESTADOS</option>
          <option value="pending">PENDIENTE</option>
          <option value="in_review">EN REVISIÓN</option>
          <option value="approved">ADMITIDO</option>
          <option value="rejected">RECHAZADO</option>
          <option value="accepted">ACEPTADO/CONFIRMADO</option>
        </select>

        <div class="flex-1"></div>
      </div>

      <!-- DataTable -->
      <div class="bg-white rounded-[32px] border border-gray-100 shadow-sm flex flex-col min-h-[500px] overflow-hidden">
        <DataTable
          :value="filteredAspirants"
          :paginator="true"
          :rows="15"
          :rowsPerPageOptions="[15, 30, 50]"
          dataKey="code"
          :loading="loading"
          class="p-datatable-sm w-full"
          stripedRows
          removableSort
          paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
          currentPageReportTemplate="Mostrando {first} a {last} de {totalRecords} aspirantes"
          responsiveLayout="scroll"
        >
          <template #empty>
            <div class="p-10 flex flex-col items-center justify-center text-center">
              <div class="w-16 h-16 bg-gray-50 rounded-2xl flex items-center justify-center mb-4">
                <i class="pi pi-id-card text-2xl text-gray-300"></i>
              </div>
              <p class="text-gray-400 font-bold mb-1">No se encontraron aspirantes</p>
              <p class="text-xs text-gray-300">Ajusta los filtros de búsqueda para ver más resultados.</p>
            </div>
          </template>

          <template #loading>
            <div class="p-10 flex flex-col items-center justify-center text-center">
              <div class="w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mb-4"></div>
              <p class="text-gray-400 font-bold text-sm">Cargando aspirantes...</p>
            </div>
          </template>

          <!-- CÓDIGO -->
          <Column field="code" header="CÓDIGO" sortable style="min-width: 120px">
            <template #body="{ data }">
              <span class="font-mono text-[11px] font-black text-[var(--upel-blue)] bg-blue-50 px-2.5 py-1 rounded-lg border border-blue-100 inline-block">
                {{ data.code }}
              </span>
            </template>
          </Column>

          <!-- ASPIRANTE -->
          <Column field="full_name" header="ASPIRANTE" sortable style="min-width: 200px">
            <template #body="{ data }">
              <div class="flex items-center gap-3">
                <div class="h-9 w-9 rounded-xl bg-blue-50 flex items-center justify-center font-black text-[10px] text-blue-600 shadow-sm border border-blue-100/50 shrink-0">
                  {{ data.first_name?.[0] || '' }}{{ data.last_name?.[0] || '' }}
                </div>
                <div>
                  <div class="text-[13px] font-black text-gray-900">{{ data.full_name }}</div>
                  <div class="text-[10px] text-gray-400 font-bold bg-gray-50 px-1.5 py-0.5 rounded inline-block mt-0.5">{{ data.email }}</div>
                </div>
              </div>
            </template>
          </Column>

          <!-- TIPO -->
          <Column field="admission_type" header="TIPO" sortable style="min-width: 130px">
            <template #body="{ data }">
              <span class="text-[10px] font-black uppercase tracking-wide px-2.5 py-1 rounded-lg border inline-block" :class="getTypeClass(data.admission_type)">
                {{ getTypeLabel(data.admission_type) }}
              </span>
            </template>
          </Column>

          <!-- OPCIONES DE CARRERA -->
          <Column header="OPCIONES" style="min-width: 200px">
            <template #body="{ data }">
              <div class="flex flex-col gap-1.5 py-1">
                <div class="flex items-center gap-2">
                  <span class="h-4 w-4 rounded bg-blue-100 text-blue-600 flex items-center justify-center text-[8px] font-black italic shrink-0">1</span>
                  <div class="text-[11px] font-black text-gray-700 truncate max-w-[160px] italic uppercase tracking-tighter" :title="data.career_name">{{ data.career_name || '—' }}</div>
                </div>
                <div v-if="data.career_name_2" class="flex items-center gap-2 opacity-60">
                  <span class="h-4 w-4 rounded bg-gray-100 text-gray-400 flex items-center justify-center text-[8px] font-black italic shrink-0">2</span>
                  <div class="text-[10px] font-bold text-gray-400 truncate max-w-[160px] italic uppercase tracking-tighter">{{ data.career_name_2 }}</div>
                </div>
                <div v-if="data.career_name_3" class="flex items-center gap-2 opacity-40">
                  <span class="h-4 w-4 rounded bg-gray-100 text-gray-300 flex items-center justify-center text-[8px] font-black italic shrink-0">3</span>
                  <div class="text-[10px] font-bold text-gray-300 truncate max-w-[160px] italic uppercase tracking-tighter">{{ data.career_name_3 }}</div>
                </div>
              </div>
            </template>
          </Column>

          <!-- ESTADO -->
          <Column field="admission_status" header="ESTADO" sortable style="min-width: 130px">
            <template #body="{ data }">
              <span class="text-[10px] font-black uppercase tracking-wide px-2.5 py-1 rounded-lg border inline-block" :class="getStatusClass(data.admission_status)">
                {{ getStatusLabel(data.admission_status) }}
              </span>
            </template>
          </Column>

          <!-- ADMITIDO EN -->
          <Column header="ADMITIDO EN" style="min-width: 150px">
            <template #body="{ data }">
              <span v-if="data.admitted_career_name" class="text-[11px] font-black text-green-700 bg-green-50 px-2 py-1 rounded-lg border border-green-100 inline-block italic uppercase tracking-tighter" :title="data.admitted_career_name">
                {{ data.admitted_career_name }}
              </span>
              <span v-else class="text-[11px] text-gray-300 font-black">—</span>
            </template>
          </Column>

          <!-- ACCIONES -->
          <Column header="ACCIONES" alignFrozen="right" style="min-width: 110px">
            <template #body="{ data }">
              <div class="flex justify-end">
                <button
                  @click="openModal(data)"
                  class="px-4 py-1.5 bg-[var(--upel-blue)] text-white text-[10px] font-black uppercase tracking-widest rounded-xl hover:opacity-90 hover:scale-[1.02] active:scale-95 transition-all shadow-sm"
                >
                  Procesar
                </button>
              </div>
            </template>
          </Column>
        </DataTable>
      </div>

      <!-- Modal de Procesamiento -->
      <Teleport to="body">
        <div
          v-if="modal.visible"
          class="fixed inset-0 bg-gray-900/70 backdrop-blur-md z-[100] flex items-center justify-center p-4"
          @click.self="closeModal"
        >
          <div class="bg-white rounded-[40px] w-full max-w-lg shadow-2xl overflow-hidden animate-fade-in border border-white/20">
            <!-- Header del modal -->
            <div class="p-8 border-b border-gray-50 bg-gray-50/50">
              <div class="text-[10px] font-black text-[var(--upel-blue)] uppercase tracking-widest mb-1 italic">Procesar Admisión</div>
              <h2 class="text-2xl font-black text-gray-900 leading-tight">{{ selectedAspirant?.full_name }}</h2>
              <div class="text-[11px] text-gray-400 font-bold mt-1">
                <span class="font-mono">{{ selectedAspirant?.code }}</span>
                <span class="mx-2 text-gray-200">|</span>
                <span class="uppercase">{{ getTypeLabel(selectedAspirant?.admission_type) }}</span>
              </div>
            </div>

            <!-- Cuerpo -->
            <div class="p-8 space-y-6 max-h-[60vh] overflow-y-auto custom-scrollbar">
              <!-- Estado -->
              <div class="space-y-2">
                <label class="text-[10px] font-black uppercase text-gray-400 tracking-widest ml-1">Nuevo Estado</label>
                <select
                  v-model="form.admission_status"
                  class="w-full bg-white border border-gray-200 rounded-xl px-4 py-3 text-sm font-bold text-gray-800 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 outline-none appearance-none transition-all shadow-sm"
                >
                  <option value="pending">Pendiente</option>
                  <option value="in_review">En Revisión</option>
                  <option value="approved">Admitido</option>
                  <option value="rejected">Rechazado</option>
                  <option value="accepted">Aceptado / Confirmado</option>
                </select>
              </div>

              <!-- Opción Admitida (solo cuando status = approved) -->
              <div v-if="form.admission_status === 'approved'" class="bg-blue-50/40 p-5 rounded-3xl border border-blue-100 space-y-3">
                <div class="text-[10px] font-black uppercase text-blue-500 tracking-widest italic mb-2">Opción Admitida</div>

                <!-- Opción 1 -->
                <label
                  v-if="selectedAspirant?.career_name"
                  class="flex items-center gap-3 p-3 rounded-2xl border cursor-pointer transition-all"
                  :class="form.admitted_option === 1 ? 'bg-[var(--upel-blue)] border-[var(--upel-blue)] shadow-md' : 'bg-white border-gray-200 hover:border-blue-200'"
                >
                  <input type="radio" v-model="form.admitted_option" :value="1" class="hidden" />
                  <div class="h-5 w-5 rounded-md flex items-center justify-center text-[9px] font-black shrink-0 italic"
                    :class="form.admitted_option === 1 ? 'bg-white/20 text-white' : 'bg-gray-100 text-gray-400'">1</div>
                  <span class="text-[11px] font-black uppercase tracking-tighter italic truncate"
                    :class="form.admitted_option === 1 ? 'text-white' : 'text-gray-700'">{{ selectedAspirant?.career_name }}</span>
                  <i v-if="form.admitted_option === 1" class="pi pi-check text-white text-[10px] ml-auto shrink-0"></i>
                </label>

                <!-- Opción 2 -->
                <label
                  v-if="selectedAspirant?.career_name_2"
                  class="flex items-center gap-3 p-3 rounded-2xl border cursor-pointer transition-all"
                  :class="form.admitted_option === 2 ? 'bg-[var(--upel-blue)] border-[var(--upel-blue)] shadow-md' : 'bg-white border-gray-200 hover:border-blue-200'"
                >
                  <input type="radio" v-model="form.admitted_option" :value="2" class="hidden" />
                  <div class="h-5 w-5 rounded-md flex items-center justify-center text-[9px] font-black shrink-0 italic"
                    :class="form.admitted_option === 2 ? 'bg-white/20 text-white' : 'bg-gray-100 text-gray-400'">2</div>
                  <span class="text-[11px] font-black uppercase tracking-tighter italic truncate"
                    :class="form.admitted_option === 2 ? 'text-white' : 'text-gray-700'">{{ selectedAspirant?.career_name_2 }}</span>
                  <i v-if="form.admitted_option === 2" class="pi pi-check text-white text-[10px] ml-auto shrink-0"></i>
                </label>

                <!-- Opción 3 -->
                <label
                  v-if="selectedAspirant?.career_name_3"
                  class="flex items-center gap-3 p-3 rounded-2xl border cursor-pointer transition-all"
                  :class="form.admitted_option === 3 ? 'bg-[var(--upel-blue)] border-[var(--upel-blue)] shadow-md' : 'bg-white border-gray-200 hover:border-blue-200'"
                >
                  <input type="radio" v-model="form.admitted_option" :value="3" class="hidden" />
                  <div class="h-5 w-5 rounded-md flex items-center justify-center text-[9px] font-black shrink-0 italic"
                    :class="form.admitted_option === 3 ? 'bg-white/20 text-white' : 'bg-gray-100 text-gray-400'">3</div>
                  <span class="text-[11px] font-black uppercase tracking-tighter italic truncate"
                    :class="form.admitted_option === 3 ? 'text-white' : 'text-gray-700'">{{ selectedAspirant?.career_name_3 }}</span>
                  <i v-if="form.admitted_option === 3" class="pi pi-check text-white text-[10px] ml-auto shrink-0"></i>
                </label>
              </div>

              <!-- Notas de admisión -->
              <div class="space-y-2">
                <label class="text-[10px] font-black uppercase text-gray-400 tracking-widest ml-1">Notas / Observaciones</label>
                <textarea
                  v-model="form.admission_notes"
                  rows="3"
                  placeholder="Añada notas sobre la revisión de documentos, motivos de decisión, etc."
                  class="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-xs font-bold text-gray-700 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 outline-none transition-all resize-none"
                ></textarea>
              </div>
            </div>

            <!-- Footer -->
            <div class="p-6 bg-gray-50/50 border-t border-gray-100 flex justify-end gap-3">
              <button
                @click="closeModal"
                class="px-6 py-3 rounded-2xl border border-gray-200 bg-white text-xs font-black text-gray-500 uppercase tracking-widest hover:bg-gray-50 transition-all shadow-sm"
              >
                Cancelar
              </button>
              <button
                @click="submitAdmission"
                :disabled="processing"
                class="bg-[var(--upel-blue)] text-white px-6 py-3 rounded-2xl font-black text-sm shadow-lg hover:scale-[1.02] active:scale-95 transition-all flex items-center gap-2 disabled:opacity-60 disabled:cursor-not-allowed"
              >
                <span v-if="processing" class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                {{ processing ? 'Guardando...' : 'Guardar Decisión' }}
              </button>
            </div>
          </div>
        </div>
      </Teleport>

    </main>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import AdminSidebar from '@/components/AdminSidebar.vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import 'primeicons/primeicons.css'
import {
  MagnifyingGlassIcon,
  ArrowPathIcon
} from '@heroicons/vue/24/outline'

const authStore = useAuthStore()

const aspirants = ref([])
const loading = ref(false)
const processing = ref(false)
const search = ref('')
const statusFilter = ref('')
const typeFilter = ref('')
const selectedAspirant = ref(null)

const modal = reactive({ visible: false })

const form = reactive({
  admission_status: '',
  admitted_option: null,
  admission_notes: ''
})

// ─── Fetch ────────────────────────────────────────────────────────────────────

const fetchData = async () => {
  loading.value = true
  try {
    const params = {}
    if (statusFilter.value) params.admission_status = statusFilter.value
    if (typeFilter.value) params.admission_type = typeFilter.value
    if (search.value) params.search = search.value

    const { data } = await axios.get('/api/aspirants/', {
      headers: { Authorization: 'Bearer ' + authStore.token },
      params
    })
    aspirants.value = data.results || data
  } catch (err) {
    console.error('fetchData error:', err)
  } finally {
    loading.value = false
  }
}

// ─── Computed ─────────────────────────────────────────────────────────────────

const filteredAspirants = computed(() => {
  let res = aspirants.value
  if (search.value) {
    const q = search.value.toLowerCase()
    res = res.filter(a =>
      a.full_name?.toLowerCase().includes(q) ||
      a.email?.toLowerCase().includes(q) ||
      a.code?.toLowerCase().includes(q)
    )
  }
  return res
})

const countByStatus = (status) => aspirants.value.filter(a => a.admission_status === status).length

// ─── Modal ────────────────────────────────────────────────────────────────────

const openModal = (aspirant) => {
  selectedAspirant.value = aspirant
  form.admission_status = aspirant.admission_status || 'pending'
  form.admitted_option = aspirant.admitted_option || null
  form.admission_notes = aspirant.admission_notes || ''
  modal.visible = true
}

const closeModal = () => {
  modal.visible = false
  selectedAspirant.value = null
}

const submitAdmission = async () => {
  if (!selectedAspirant.value) return
  processing.value = true
  try {
    const payload = {
      admission_status: form.admission_status,
      admission_notes: form.admission_notes
    }
    if (form.admission_status === 'approved' && form.admitted_option) {
      payload.admitted_option = form.admitted_option
    }

    await axios.patch(`/api/aspirants/${selectedAspirant.value.code}/`, payload, {
      headers: { Authorization: 'Bearer ' + authStore.token }
    })

    closeModal()
    await fetchData()
    alert(`Aspirante actualizado a: ${getStatusLabel(payload.admission_status)}`)
  } catch (err) {
    console.error('submitAdmission error:', err)
    alert(err.response?.data?.detail || 'Error al actualizar el estado del aspirante.')
  } finally {
    processing.value = false
  }
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

const getStatusClass = (status) => {
  const map = {
    pending:   'bg-amber-50 text-amber-600 border-amber-100',
    in_review: 'bg-blue-50 text-blue-600 border-blue-100',
    approved:  'bg-green-50 text-green-700 border-green-100',
    rejected:  'bg-red-50 text-red-500 border-red-100',
    accepted:  'bg-emerald-50 text-emerald-700 border-emerald-100'
  }
  return map[status] || 'bg-gray-50 text-gray-500 border-gray-100'
}

const getStatusLabel = (status) => {
  const map = {
    pending:   'Pendiente',
    in_review: 'En Revisión',
    approved:  'Admitido',
    rejected:  'Rechazado',
    accepted:  'Aceptado'
  }
  return map[status] || status || '—'
}

const getTypeClass = (type) => {
  const map = {
    ordinario:     'bg-blue-50 text-blue-600 border-blue-100',
    convalidacion: 'bg-purple-50 text-purple-600 border-purple-100',
    traslado:      'bg-amber-50 text-amber-600 border-amber-100',
    reingreso:     'bg-orange-50 text-orange-600 border-orange-100',
    equivalencia:  'bg-indigo-50 text-indigo-600 border-indigo-100'
  }
  return map[type] || 'bg-gray-50 text-gray-500 border-gray-100'
}

const getTypeLabel = (type) => {
  const map = {
    ordinario:     'Ordinario',
    convalidacion: 'Convalidación',
    traslado:      'Traslado',
    reingreso:     'Reingreso',
    equivalencia:  'Equivalencia'
  }
  return map[type] || type || '—'
}

onMounted(fetchData)
</script>

<style scoped>
:root {
  --upel-blue: #004A99;
}

.animate-fade-in {
  animation: fadeIn 0.35s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes fadeIn {
  from { opacity: 0; transform: scale(0.97) translateY(8px); }
  to   { opacity: 1; transform: scale(1) translateY(0); }
}

.custom-scrollbar::-webkit-scrollbar {
  width: 5px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #E2E8F0;
  border-radius: 10px;
}
</style>
