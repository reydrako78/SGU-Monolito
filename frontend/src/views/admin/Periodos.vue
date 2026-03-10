<template>
  <div class="min-h-screen bg-[#F8FAFC] flex text-gray-900">
    <AdminSidebar />
    <main class="flex-1 p-8 overflow-y-auto">
      <header class="mb-10 flex flex-col md:flex-row justify-between items-center gap-4">
        <div>
          <h1 class="text-3xl font-black text-gray-900 tracking-tight italic">Períodos Académicos</h1>
          <p class="text-gray-500 font-medium tracking-tight">Gestión de períodos y ciclos del calendario universitario.</p>
        </div>
        <div class="flex gap-3">
          <button @click="fetchPeriods" class="p-4 bg-white hover:bg-gray-50 rounded-2xl border border-gray-100 shadow-sm transition-all focus:outline-none focus:ring-4 focus:ring-blue-500/10 active:scale-95 group">
            <ArrowPathIcon :class="{'animate-spin': loading}" class="w-5 h-5 text-gray-400 group-hover:text-blue-500" />
          </button>
          <button @click="openCreate" class="bg-[var(--upel-blue)] text-white px-6 py-3 rounded-2xl font-bold text-sm shadow-lg hover:scale-[1.02] transition-all flex items-center gap-2">
            <PlusIcon class="w-5 h-5" />
            Nuevo Período
          </button>
        </div>
      </header>

      <!-- Active Period Banner -->
      <div v-if="activePeriod" class="mb-8 bg-gradient-to-r from-[var(--upel-blue)] to-blue-500 rounded-[32px] p-7 flex flex-col md:flex-row items-start md:items-center justify-between gap-5 shadow-xl shadow-blue-500/20 text-white">
        <div class="flex items-center gap-5">
          <div class="h-14 w-14 rounded-2xl bg-white/20 flex items-center justify-center shrink-0">
            <CalendarDaysIcon class="w-7 h-7 text-white" />
          </div>
          <div>
            <div class="flex items-center gap-3 mb-1">
              <span class="text-[10px] font-black uppercase tracking-[0.3em] text-blue-100">Período en Curso</span>
              <span class="flex items-center gap-1.5 bg-emerald-400 text-white text-[10px] font-black px-3 py-1 rounded-full uppercase tracking-wider">
                <span class="w-2 h-2 rounded-full bg-white animate-pulse"></span>
                ACTIVO
              </span>
            </div>
            <h2 class="text-2xl font-black tracking-tight italic">{{ activePeriod.name }}</h2>
            <p class="text-blue-100 text-sm mt-1 font-medium">
              {{ formatDate(activePeriod.start_date) }} &mdash; {{ formatDate(activePeriod.end_date) }}
            </p>
          </div>
        </div>
        <button @click="openEdit(activePeriod)" class="bg-white/20 hover:bg-white/30 text-white px-6 py-3 rounded-2xl font-bold text-sm transition-all border border-white/30 flex items-center gap-2 shrink-0">
          <PencilSquareIcon class="w-4 h-4" />
          Gestionar
        </button>
      </div>

      <!-- DataTable -->
      <div class="bg-white rounded-[32px] border border-gray-100 shadow-sm flex flex-col min-h-[400px] overflow-hidden">
        <DataTable
          :value="sortedPeriods"
          :paginator="true"
          :rows="10"
          :rowsPerPageOptions="[10, 25, 50]"
          dataKey="id"
          :loading="loading"
          class="p-datatable-sm w-full"
          stripedRows
          removableSort
          paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
          currentPageReportTemplate="Mostrando {first} a {last} de {totalRecords} períodos"
        >
          <template #empty>
            <div class="p-10 flex flex-col items-center justify-center text-center">
              <div class="w-16 h-16 bg-gray-50 rounded-2xl flex items-center justify-center mb-4">
                <i class="pi pi-calendar text-2xl text-gray-300"></i>
              </div>
              <p class="text-gray-400 font-bold mb-1">No hay períodos registrados</p>
              <p class="text-xs text-gray-300">Crea el primer período con el botón "Nuevo Período".</p>
            </div>
          </template>

          <Column field="name" header="PERÍODO" sortable style="min-width: 200px">
            <template #body="{ data }">
              <div class="text-[13px] font-black italic text-gray-900">{{ data.name }}</div>
            </template>
          </Column>

          <Column field="start_date" header="INICIO" sortable>
            <template #body="{ data }">
              <div class="text-[11px] font-medium text-gray-600">{{ formatDate(data.start_date) }}</div>
            </template>
          </Column>

          <Column field="end_date" header="FIN" sortable>
            <template #body="{ data }">
              <div class="text-[11px] font-medium text-gray-600">{{ formatDate(data.end_date) }}</div>
            </template>
          </Column>

          <Column field="is_active" header="ESTADO" sortable>
            <template #body="{ data }">
              <span class="px-3 py-1 rounded-full text-[10px] font-black tracking-widest uppercase border"
                :class="data.is_active
                  ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                  : 'bg-gray-50 text-gray-500 border-gray-200'">
                {{ data.is_active ? 'Activo' : 'Inactivo' }}
              </span>
            </template>
          </Column>

          <Column header="ACCIÓN" sortable>
            <template #body="{ data }">
              <div class="text-[10px] font-bold text-gray-400 italic">
                <span v-if="data.is_active" class="text-emerald-600 font-black">Período actual</span>
                <span v-else>Inactivo desde {{ formatDate(data.end_date) }}</span>
              </div>
            </template>
          </Column>

          <Column header="ACCIONES" alignFrozen="right">
            <template #body="{ data }">
              <div class="flex gap-1 justify-end">
                <button @click="openEdit(data)" class="h-8 w-8 flex items-center justify-center rounded-lg hover:bg-blue-50 text-gray-400 hover:text-blue-600 transition-colors" title="Editar">
                  <PencilSquareIcon class="w-4 h-4" />
                </button>
                <button
                  @click="toggleActive(data)"
                  class="h-8 w-8 flex items-center justify-center rounded-lg transition-colors"
                  :class="data.is_active
                    ? 'hover:bg-amber-50 text-amber-400 hover:text-amber-600'
                    : 'hover:bg-emerald-50 text-gray-400 hover:text-emerald-600'"
                  :title="data.is_active ? 'Desactivar' : 'Activar'"
                >
                  <BoltIcon class="w-4 h-4" />
                </button>
                <button @click="deletePeriod(data)" class="h-8 w-8 flex items-center justify-center rounded-lg hover:bg-red-50 text-gray-400 hover:text-red-500 transition-colors" title="Eliminar">
                  <TrashIcon class="w-4 h-4" />
                </button>
              </div>
            </template>
          </Column>
        </DataTable>
      </div>
    </main>

    <!-- Create / Edit Modal -->
    <Teleport to="body">
      <div v-if="showModal" class="fixed inset-0 bg-gray-900/60 backdrop-blur-sm z-[100] flex items-center justify-center p-4">
        <div class="bg-white rounded-[32px] w-full max-w-lg shadow-2xl flex flex-col animate-scale-in overflow-hidden">
          <div class="p-8 border-b border-gray-50 flex justify-between items-center bg-gray-50/50">
            <div class="flex items-center gap-4">
              <div class="w-12 h-12 rounded-xl bg-blue-100 flex items-center justify-center text-blue-600">
                <CalendarDaysIcon class="w-6 h-6" />
              </div>
              <div>
                <h2 class="text-xl font-black text-gray-900 leading-tight">
                  {{ editingPeriod ? 'Editar Período' : 'Nuevo Período' }}
                </h2>
                <div class="text-[10px] font-bold text-gray-500 uppercase tracking-widest mt-0.5">
                  {{ editingPeriod ? 'Actualizar datos del período' : 'Registrar período académico' }}
                </div>
              </div>
            </div>
            <button @click="closeModal" class="h-10 w-10 rounded-xl bg-white border border-gray-100 hover:bg-rose-50 hover:text-rose-500 hover:border-rose-100 flex items-center justify-center transition-all text-gray-400">
              <i class="pi pi-times"></i>
            </button>
          </div>

          <div class="p-8 space-y-5">
            <div class="space-y-1.5">
              <label class="text-[10px] font-black uppercase text-gray-400 tracking-widest ml-1">Nombre del Período</label>
              <input
                v-model="form.name"
                type="text"
                placeholder="Ej: 2026-I Semestre Regular"
                class="w-full bg-gray-50 border border-gray-100 rounded-2xl px-5 py-3 text-sm font-bold outline-none focus:ring-4 focus:ring-blue-500/10 focus:border-blue-200 transition-all"
              />
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div class="space-y-1.5">
                <label class="text-[10px] font-black uppercase text-gray-400 tracking-widest ml-1">Fecha de Inicio</label>
                <input
                  v-model="form.start_date"
                  type="date"
                  class="w-full bg-gray-50 border border-gray-100 rounded-2xl px-5 py-3 text-sm font-bold outline-none focus:ring-4 focus:ring-blue-500/10 focus:border-blue-200 transition-all"
                />
              </div>
              <div class="space-y-1.5">
                <label class="text-[10px] font-black uppercase text-gray-400 tracking-widest ml-1">Fecha de Fin</label>
                <input
                  v-model="form.end_date"
                  type="date"
                  class="w-full bg-gray-50 border border-gray-100 rounded-2xl px-5 py-3 text-sm font-bold outline-none focus:ring-4 focus:ring-blue-500/10 focus:border-blue-200 transition-all"
                />
              </div>
            </div>

            <label class="flex items-center gap-4 bg-gray-50 p-4 rounded-2xl border border-gray-100 cursor-pointer hover:border-blue-100 transition-all">
              <input type="checkbox" v-model="form.is_active" class="h-5 w-5 rounded border-gray-300 text-[var(--upel-blue)] focus:ring-blue-500" />
              <div>
                <div class="text-[11px] font-black text-gray-900 uppercase">Marcar como período activo</div>
                <div class="text-[10px] text-gray-500 font-medium mt-0.5">Al activar este período, el anterior será desactivado automáticamente.</div>
              </div>
            </label>
          </div>

          <div class="p-6 bg-gray-50/50 flex justify-end gap-3 border-t border-gray-100">
            <button @click="closeModal" class="px-6 py-3 rounded-xl border border-gray-200 bg-white text-xs font-black text-gray-500 uppercase tracking-widest hover:bg-gray-50 transition-all shadow-sm">
              Cancelar
            </button>
            <button @click="submitForm" :disabled="saving" class="bg-[var(--upel-blue)] text-white px-8 py-3 rounded-2xl text-xs font-black uppercase tracking-widest shadow-lg hover:scale-[1.02] transition-all flex items-center gap-2">
              <ArrowPathIcon v-if="saving" class="w-4 h-4 animate-spin" />
              {{ saving ? 'Guardando...' : (editingPeriod ? 'Guardar Cambios' : 'Crear Período') }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import AdminSidebar from '@/components/AdminSidebar.vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import 'primeicons/primeicons.css'
import {
  ArrowPathIcon,
  PlusIcon,
  PencilSquareIcon,
  TrashIcon,
  BoltIcon,
  CalendarDaysIcon
} from '@heroicons/vue/24/outline'

const authStore = useAuthStore()
const periods = ref([])
const loading = ref(true)
const saving = ref(false)
const showModal = ref(false)
const editingPeriod = ref(null)

const form = reactive({
  name: '',
  start_date: '',
  end_date: '',
  is_active: false
})

const activePeriod = computed(() => periods.value.find(p => p.is_active) || null)

const sortedPeriods = computed(() =>
  [...periods.value].sort((a, b) => new Date(b.start_date) - new Date(a.start_date))
)

const formatDate = (dateStr) => {
  if (!dateStr) return '—'
  return new Date(dateStr + 'T12:00:00').toLocaleDateString('es-VE', {
    day: '2-digit', month: 'short', year: 'numeric'
  })
}

const fetchPeriods = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/courses/periods/', {
      headers: { Authorization: 'Bearer ' + authStore.token }
    })
    periods.value = res.data.results || res.data
  } catch (err) {
    console.error('Fetch periods error:', err.response?.status, err.message)
  } finally {
    loading.value = false
  }
}

const openCreate = () => {
  editingPeriod.value = null
  Object.assign(form, { name: '', start_date: '', end_date: '', is_active: false })
  showModal.value = true
}

const openEdit = (period) => {
  editingPeriod.value = period
  Object.assign(form, {
    name: period.name,
    start_date: period.start_date,
    end_date: period.end_date,
    is_active: period.is_active
  })
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingPeriod.value = null
}

const submitForm = async () => {
  if (!form.name || !form.start_date || !form.end_date) return
  saving.value = true
  try {
    if (editingPeriod.value) {
      const res = await axios.patch(`/api/courses/periods/${editingPeriod.value.id}/`, form, {
        headers: { Authorization: 'Bearer ' + authStore.token }
      })
      const idx = periods.value.findIndex(p => p.id === editingPeriod.value.id)
      if (idx !== -1) periods.value[idx] = res.data
      if (form.is_active) {
        periods.value = periods.value.map(p =>
          p.id !== res.data.id ? { ...p, is_active: false } : p
        )
      }
    } else {
      const res = await axios.post('/api/courses/periods/', form, {
        headers: { Authorization: 'Bearer ' + authStore.token }
      })
      periods.value.push(res.data)
      if (form.is_active) {
        periods.value = periods.value.map(p =>
          p.id !== res.data.id ? { ...p, is_active: false } : p
        )
      }
    }
    closeModal()
  } catch (err) {
    console.error('Save period error:', err.response?.data || err.message)
  } finally {
    saving.value = false
  }
}

const toggleActive = async (period) => {
  try {
    const res = await axios.patch(`/api/courses/periods/${period.id}/`, { is_active: !period.is_active }, {
      headers: { Authorization: 'Bearer ' + authStore.token }
    })
    if (!period.is_active) {
      // Activating: deactivate others locally
      periods.value = periods.value.map(p =>
        p.id !== period.id ? { ...p, is_active: false } : res.data
      )
    } else {
      const idx = periods.value.findIndex(p => p.id === period.id)
      if (idx !== -1) periods.value[idx] = res.data
    }
  } catch (err) {
    console.error('Toggle period error:', err.response?.data || err.message)
  }
}

const deletePeriod = async (period) => {
  if (!confirm(`¿Eliminar el período "${period.name}"? Esta acción no se puede deshacer.`)) return
  try {
    await axios.delete(`/api/courses/periods/${period.id}/`, {
      headers: { Authorization: 'Bearer ' + authStore.token }
    })
    periods.value = periods.value.filter(p => p.id !== period.id)
  } catch (err) {
    console.error('Delete period error:', err.response?.data || err.message)
  }
}

onMounted(fetchPeriods)
</script>

<style scoped>
.animate-scale-in {
  animation: scaleIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
@keyframes scaleIn {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}
</style>
