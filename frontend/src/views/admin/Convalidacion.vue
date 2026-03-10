<template>
  <div class="min-h-screen bg-[#F8FAFC] flex text-gray-900">
    <AdminSidebar />
    <main class="flex-1 p-8 overflow-y-auto">
      <header class="mb-10 flex flex-col md:flex-row justify-between items-center gap-4">
        <div>
          <h1 class="text-3xl font-black text-gray-900 tracking-tight">Convalidación de Estudios</h1>
          <p class="text-gray-500 font-medium">Gestión de expedientes de convalidación de estudios previos ante comisiones y consejo.</p>
        </div>
        <div class="flex gap-2">
          <button @click="fetchData" class="p-3 bg-white hover:bg-gray-50 rounded-2xl border border-gray-100 shadow-sm transition-all focus:outline-none focus:ring-4 focus:ring-blue-500/10 active:scale-95 group">
            <ArrowPathIcon :class="{ 'animate-spin': loading }" class="w-5 h-5 text-gray-400 group-hover:text-blue-500" />
          </button>
        </div>
      </header>

      <!-- Stats Bar -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div class="bg-white p-6 rounded-[32px] border border-gray-100 shadow-sm flex items-center gap-4 group hover:shadow-md transition-all border-b-4 border-b-blue-500">
          <div class="h-12 w-12 rounded-2xl bg-blue-50 flex items-center justify-center text-blue-600 group-hover:bg-blue-600 group-hover:text-white transition-colors shrink-0">
            <DocumentDuplicateIcon class="w-6 h-6" />
          </div>
          <div>
            <div class="text-[10px] font-black uppercase text-gray-400 mb-0.5 tracking-widest">Total Convalidaciones</div>
            <div class="text-2xl font-black text-gray-900 leading-none">{{ aspirants.length }}</div>
          </div>
        </div>

        <div class="bg-white p-6 rounded-[32px] border border-gray-100 shadow-sm flex items-center gap-4 group hover:shadow-md transition-all border-b-4 border-b-amber-500">
          <div class="h-12 w-12 rounded-2xl bg-amber-50 flex items-center justify-center text-amber-600 group-hover:bg-amber-600 group-hover:text-white transition-colors shrink-0">
            <ClockIcon class="w-6 h-6" />
          </div>
          <div>
            <div class="text-[10px] font-black uppercase text-gray-400 mb-0.5 tracking-widest">Pend. de Comisión</div>
            <div class="text-2xl font-black text-gray-900 leading-none">{{ countByStatus('pending') }}</div>
          </div>
        </div>

        <div class="bg-white p-6 rounded-[32px] border border-gray-100 shadow-sm flex items-center gap-4 group hover:shadow-md transition-all border-b-4 border-b-indigo-500">
          <div class="h-12 w-12 rounded-2xl bg-indigo-50 flex items-center justify-center text-indigo-600 group-hover:bg-indigo-600 group-hover:text-white transition-colors shrink-0">
            <BuildingLibraryIcon class="w-6 h-6" />
          </div>
          <div>
            <div class="text-[10px] font-black uppercase text-gray-400 mb-0.5 tracking-widest">En Proc. de Consejo</div>
            <div class="text-2xl font-black text-gray-900 leading-none">{{ countByStatus('in_review') }}</div>
          </div>
        </div>

        <div class="bg-white p-6 rounded-[32px] border border-gray-100 shadow-sm flex items-center gap-4 group hover:shadow-md transition-all border-b-4 border-b-green-500">
          <div class="h-12 w-12 rounded-2xl bg-green-50 flex items-center justify-center text-green-600 group-hover:bg-green-600 group-hover:text-white transition-colors shrink-0">
            <CheckCircleIcon class="w-6 h-6" />
          </div>
          <div>
            <div class="text-[10px] font-black uppercase text-gray-400 mb-0.5 tracking-widest">Resueltas</div>
            <div class="text-2xl font-black text-gray-900 leading-none">{{ countResolved }}</div>
          </div>
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

        <select v-model="statusFilter" class="px-5 py-2.5 bg-gray-50 border border-transparent rounded-xl text-xs font-bold outline-none focus:ring-4 focus:ring-blue-500/5 appearance-none cursor-pointer hover:bg-gray-100 transition-all text-gray-600">
          <option value="">TODOS LOS ESTADOS</option>
          <option value="pending">PENDIENTE</option>
          <option value="in_review">EN REVISIÓN</option>
          <option value="approved">ADMITIDO</option>
          <option value="rejected">RECHAZADO</option>
          <option value="accepted">ACEPTADO</option>
        </select>

        <div class="flex-1"></div>
      </div>

      <!-- Layout: tabla + panel lateral -->
      <div class="flex gap-6 items-start">
        <!-- DataTable -->
        <div class="flex-1 bg-white rounded-[32px] border border-gray-100 shadow-sm overflow-hidden min-h-[500px]">
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
            currentPageReportTemplate="Mostrando {first} a {last} de {totalRecords} expedientes"
            responsiveLayout="scroll"
          >
            <template #empty>
              <div class="p-10 flex flex-col items-center justify-center text-center">
                <div class="w-16 h-16 bg-gray-50 rounded-2xl flex items-center justify-center mb-4">
                  <i class="pi pi-file text-2xl text-gray-300"></i>
                </div>
                <p class="text-gray-400 font-bold mb-1">No se encontraron expedientes de convalidación</p>
                <p class="text-xs text-gray-300">Ajusta los filtros de búsqueda para ver más resultados.</p>
              </div>
            </template>

            <template #loading>
              <div class="p-10 flex flex-col items-center justify-center text-center">
                <div class="w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mb-4"></div>
                <p class="text-gray-400 font-bold text-sm">Cargando expedientes...</p>
              </div>
            </template>

            <!-- CÓDIGO ASPIRANTE -->
            <Column field="code" header="CÓDIGO" sortable style="min-width: 120px">
              <template #body="{ data }">
                <span class="font-mono text-[11px] font-black text-[var(--upel-blue)] bg-blue-50 px-2.5 py-1 rounded-lg border border-blue-100 inline-block cursor-pointer hover:bg-[var(--upel-blue)] hover:text-white transition-all"
                  @click="openDetail(data)"
                  :title="'Ver expediente de ' + data.full_name"
                >
                  {{ data.code }}
                </span>
              </template>
            </Column>

            <!-- ASPIRANTE -->
            <Column field="full_name" header="ASPIRANTE" sortable style="min-width: 200px">
              <template #body="{ data }">
                <div class="flex items-center gap-3">
                  <div class="h-9 w-9 rounded-xl bg-purple-50 flex items-center justify-center font-black text-[10px] text-purple-600 shadow-sm border border-purple-100/50 shrink-0">
                    {{ data.first_name?.[0] || '' }}{{ data.last_name?.[0] || '' }}
                  </div>
                  <div>
                    <div class="text-[13px] font-black text-gray-900">{{ data.full_name }}</div>
                    <div class="text-[10px] text-gray-400 font-bold bg-gray-50 px-1.5 py-0.5 rounded inline-block mt-0.5">{{ data.email }}</div>
                  </div>
                </div>
              </template>
            </Column>

            <!-- INSTITUCIÓN ORIGEN -->
            <Column header="INSTITUCIÓN ORIGEN" style="min-width: 160px">
              <template #body="{ data }">
                <span v-if="data.institution_name" class="text-[11px] font-black text-gray-700 italic uppercase tracking-tighter">
                  {{ data.institution_name }}
                </span>
                <span v-else class="text-[11px] text-gray-300 font-bold italic">No especificada</span>
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

            <!-- ITEMS (materias) -->
            <Column header="ITEMS" style="min-width: 80px">
              <template #body>
                <span class="text-[11px] text-gray-300 font-black">—</span>
              </template>
            </Column>

            <!-- FECHA SOLICITUD -->
            <Column field="created_at" header="FECHA SOLICITUD" sortable style="min-width: 130px">
              <template #body="{ data }">
                <span class="text-[11px] font-bold text-gray-500">{{ formatDate(data.created_at) }}</span>
              </template>
            </Column>

            <!-- ACCIONES -->
            <Column header="ACCIONES" alignFrozen="right" style="min-width: 120px">
              <template #body="{ data }">
                <div class="flex justify-end">
                  <button
                    @click="openDetail(data)"
                    class="px-4 py-1.5 text-[10px] font-black uppercase tracking-widest rounded-xl transition-all border"
                    :class="selectedAspirant?.code === data.code
                      ? 'bg-[var(--upel-blue)] text-white border-[var(--upel-blue)] shadow-md'
                      : 'bg-indigo-50 text-indigo-600 border-indigo-100 hover:bg-indigo-600 hover:text-white hover:border-indigo-600'"
                  >
                    Ver Expediente
                  </button>
                </div>
              </template>
            </Column>
          </DataTable>
        </div>

        <!-- Panel lateral de detalle -->
        <aside
          v-if="selectedAspirant"
          class="w-96 bg-white rounded-[32px] border border-gray-100 shadow-xl flex flex-col animate-slide-in shrink-0 overflow-hidden"
          style="max-height: calc(100vh - 12rem); position: sticky; top: 2rem;"
        >
          <!-- Header del panel -->
          <div class="p-6 border-b border-gray-50 bg-gray-50/50 flex justify-between items-start gap-3">
            <div class="flex-1 min-w-0">
              <div class="text-[9px] font-black text-purple-500 uppercase tracking-widest mb-1 italic">Expediente de Convalidación</div>
              <h3 class="text-lg font-black text-gray-900 leading-tight truncate">{{ selectedAspirant.full_name }}</h3>
              <div class="flex items-center gap-2 mt-1">
                <span class="font-mono text-[10px] font-black text-[var(--upel-blue)] bg-blue-50 px-2 py-0.5 rounded border border-blue-100">{{ selectedAspirant.code }}</span>
              </div>
            </div>
            <button @click="selectedAspirant = null" class="h-8 w-8 rounded-xl bg-white border border-gray-200 hover:bg-rose-50 hover:text-rose-500 hover:border-rose-100 flex items-center justify-center transition-all text-gray-400 shrink-0 mt-0.5">
              <XMarkIcon class="w-4 h-4" />
            </button>
          </div>

          <!-- Cuerpo del panel -->
          <div class="flex-1 overflow-y-auto custom-scrollbar p-6 space-y-6">

            <!-- Datos del aspirante -->
            <section>
              <div class="text-[9px] font-black text-gray-400 uppercase tracking-widest mb-3">Datos del Aspirante</div>
              <div class="bg-gray-50 rounded-2xl p-4 space-y-3 text-xs font-bold text-gray-600">
                <div class="flex justify-between">
                  <span class="text-gray-400 uppercase text-[9px] tracking-widest">Email</span>
                  <span class="truncate max-w-[180px] text-right">{{ selectedAspirant.email }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-400 uppercase text-[9px] tracking-widest">Cédula</span>
                  <span>{{ selectedAspirant.national_id || '—' }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-400 uppercase text-[9px] tracking-widest">Institución Origen</span>
                  <span class="truncate max-w-[160px] text-right italic">{{ selectedAspirant.institution_name || 'No especificada' }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-400 uppercase text-[9px] tracking-widest">Carrera Solicitada</span>
                  <span class="truncate max-w-[160px] text-right italic uppercase tracking-tighter text-[10px]">{{ selectedAspirant.career_name || '—' }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-400 uppercase text-[9px] tracking-widest">Estado Actual</span>
                  <span class="text-[10px] font-black uppercase px-2 py-0.5 rounded border" :class="getStatusClass(selectedAspirant.admission_status)">
                    {{ getStatusLabel(selectedAspirant.admission_status) }}
                  </span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-400 uppercase text-[9px] tracking-widest">Fecha Solicitud</span>
                  <span>{{ formatDate(selectedAspirant.created_at) }}</span>
                </div>
              </div>
            </section>

            <!-- Cambio de estado -->
            <section>
              <div class="text-[9px] font-black text-gray-400 uppercase tracking-widest mb-3">Cambio de Estado</div>
              <div class="space-y-3">
                <select
                  v-model="detailForm.admission_status"
                  class="w-full bg-white border border-gray-200 rounded-xl px-4 py-3 text-sm font-bold text-gray-800 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 outline-none appearance-none transition-all shadow-sm"
                >
                  <option value="pending">Pendiente</option>
                  <option value="in_review">En Revisión / Consejo</option>
                  <option value="approved">Admitido / Aprobado</option>
                  <option value="rejected">Rechazado</option>
                  <option value="accepted">Aceptado / Resuelto</option>
                </select>
              </div>
            </section>

            <!-- Observaciones del Consejo -->
            <section>
              <div class="text-[9px] font-black text-gray-400 uppercase tracking-widest mb-3">Observaciones del Consejo</div>
              <textarea
                v-model="detailForm.admission_notes"
                rows="4"
                placeholder="Añada las observaciones del consejo universitario o comisión de convalidación..."
                class="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-xs font-bold text-gray-700 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 outline-none transition-all resize-none"
              ></textarea>
            </section>

          </div>

          <!-- Footer del panel -->
          <div class="p-5 border-t border-gray-100 bg-gray-50/30">
            <button
              @click="saveDetail"
              :disabled="saving"
              class="w-full bg-[var(--upel-blue)] text-white px-6 py-3 rounded-2xl font-black text-sm shadow-lg hover:scale-[1.01] active:scale-95 transition-all flex items-center justify-center gap-2 disabled:opacity-60 disabled:cursor-not-allowed"
            >
              <span v-if="saving" class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
              {{ saving ? 'Guardando...' : 'Guardar Cambios' }}
            </button>
          </div>
        </aside>
      </div>

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
  ArrowPathIcon,
  XMarkIcon,
  DocumentDuplicateIcon,
  ClockIcon,
  CheckCircleIcon,
  BuildingLibraryIcon
} from '@heroicons/vue/24/outline'

const authStore = useAuthStore()

const aspirants = ref([])
const loading = ref(false)
const saving = ref(false)
const search = ref('')
const statusFilter = ref('')
const selectedAspirant = ref(null)

const detailForm = reactive({
  admission_status: '',
  admission_notes: ''
})

// ─── Fetch ────────────────────────────────────────────────────────────────────

const fetchData = async () => {
  loading.value = true
  try {
    const params = { admission_type: 'convalidacion' }
    if (statusFilter.value) params.admission_status = statusFilter.value
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

const countResolved = computed(() =>
  aspirants.value.filter(a => ['approved', 'rejected', 'accepted'].includes(a.admission_status)).length
)

// ─── Panel lateral ────────────────────────────────────────────────────────────

const openDetail = (aspirant) => {
  selectedAspirant.value = aspirant
  detailForm.admission_status = aspirant.admission_status || 'pending'
  detailForm.admission_notes = aspirant.admission_notes || ''
}

const saveDetail = async () => {
  if (!selectedAspirant.value) return
  saving.value = true
  try {
    const payload = {
      admission_status: detailForm.admission_status,
      admission_notes: detailForm.admission_notes
    }
    await axios.patch(`/api/aspirants/${selectedAspirant.value.code}/`, payload, {
      headers: { Authorization: 'Bearer ' + authStore.token }
    })

    // Actualizar en la lista local
    const idx = aspirants.value.findIndex(a => a.code === selectedAspirant.value.code)
    if (idx !== -1) {
      aspirants.value[idx] = { ...aspirants.value[idx], ...payload }
      selectedAspirant.value = { ...selectedAspirant.value, ...payload }
    }

    alert(`Expediente actualizado a: ${getStatusLabel(payload.admission_status)}`)
  } catch (err) {
    console.error('saveDetail error:', err)
    alert(err.response?.data?.detail || 'Error al guardar los cambios.')
  } finally {
    saving.value = false
  }
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

const getStatusClass = (status) => {
  const map = {
    pending:   'bg-amber-50 text-amber-600 border-amber-100',
    in_review: 'bg-indigo-50 text-indigo-600 border-indigo-100',
    approved:  'bg-green-50 text-green-700 border-green-100',
    rejected:  'bg-red-50 text-red-500 border-red-100',
    accepted:  'bg-emerald-50 text-emerald-700 border-emerald-100'
  }
  return map[status] || 'bg-gray-50 text-gray-500 border-gray-100'
}

const getStatusLabel = (status) => {
  const map = {
    pending:   'Pendiente',
    in_review: 'En Consejo',
    approved:  'Aprobado',
    rejected:  'Rechazado',
    accepted:  'Resuelto'
  }
  return map[status] || status || '—'
}

const formatDate = (date) => {
  if (!date) return '—'
  return new Date(date).toLocaleDateString('es-VE', {
    day: '2-digit',
    month: 'short',
    year: 'numeric'
  })
}

onMounted(fetchData)
</script>

<style scoped>
:root {
  --upel-blue: #004A99;
}

.animate-slide-in {
  animation: slideIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes slideIn {
  from { opacity: 0; transform: translateX(24px); }
  to   { opacity: 1; transform: translateX(0); }
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
