<template>
  <div class="min-h-screen bg-[#F8FAFC] flex text-gray-900">
    <AdminSidebar />
    <main class="flex-1 p-8 overflow-y-auto">
      <header class="mb-10 flex flex-col md:flex-row justify-between items-center gap-4">
        <div>
          <h1 class="text-3xl font-black text-gray-900 tracking-tight italic">Oferta Académica</h1>
          <p class="text-gray-500 font-medium tracking-tight">
            Secciones activas
            <span v-if="activePeriodName" class="text-[var(--upel-blue)] font-bold">&mdash; {{ activePeriodName }}</span>
          </p>
        </div>
        <div class="flex gap-3">
          <button @click="fetchAll" class="p-4 bg-white hover:bg-gray-50 rounded-2xl border border-gray-100 shadow-sm transition-all focus:outline-none focus:ring-4 focus:ring-blue-500/10 active:scale-95 group">
            <ArrowPathIcon :class="{'animate-spin': loading}" class="w-5 h-5 text-gray-400 group-hover:text-blue-500" />
          </button>
          <button @click="openCreate" class="bg-[var(--upel-blue)] text-white px-6 py-3 rounded-2xl font-bold text-sm shadow-lg hover:scale-[1.02] transition-all flex items-center gap-2">
            <PlusIcon class="w-5 h-5" />
            Nueva Sección
          </button>
        </div>
      </header>

      <!-- Stats Bar -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-10">
        <div class="bg-white p-7 rounded-[32px] border border-gray-100 shadow-sm flex items-center gap-5 group hover:shadow-lg transition-all border-b-4 border-b-blue-500">
          <div class="h-14 w-14 rounded-2xl bg-blue-50 flex items-center justify-center text-blue-600 transition-colors group-hover:bg-blue-600 group-hover:text-white">
            <TableCellsIcon class="w-7 h-7" />
          </div>
          <div>
            <div class="text-[10px] font-black uppercase text-gray-400 mb-1 tracking-widest">Total Secciones</div>
            <div class="text-2xl font-black text-gray-900 leading-none">{{ sections.length }}</div>
          </div>
        </div>
        <div class="bg-white p-7 rounded-[32px] border border-gray-100 shadow-sm flex items-center gap-5 group hover:shadow-lg transition-all border-b-4 border-b-emerald-500">
          <div class="h-14 w-14 rounded-2xl bg-emerald-50 flex items-center justify-center text-emerald-600 transition-colors group-hover:bg-emerald-600 group-hover:text-white">
            <CheckBadgeIcon class="w-7 h-7" />
          </div>
          <div>
            <div class="text-[10px] font-black uppercase text-gray-400 mb-1 tracking-widest">Secciones Activas</div>
            <div class="text-2xl font-black text-gray-900 leading-none">{{ sections.filter(s => s.is_active).length }}</div>
          </div>
        </div>
        <div class="bg-white p-7 rounded-[32px] border border-gray-100 shadow-sm flex items-center gap-5 group hover:shadow-lg transition-all border-b-4 border-b-indigo-500">
          <div class="h-14 w-14 rounded-2xl bg-indigo-50 flex items-center justify-center text-indigo-600 transition-colors group-hover:bg-indigo-600 group-hover:text-white">
            <UsersIcon class="w-7 h-7" />
          </div>
          <div>
            <div class="text-[10px] font-black uppercase text-gray-400 mb-1 tracking-widest">Cupos Totales</div>
            <div class="text-2xl font-black text-gray-900 leading-none">{{ totalCupos }}</div>
          </div>
        </div>
        <div class="bg-white p-7 rounded-[32px] border border-gray-100 shadow-sm flex items-center gap-5 group hover:shadow-lg transition-all border-b-4 border-b-amber-500">
          <div class="h-14 w-14 rounded-2xl bg-amber-50 flex items-center justify-center text-amber-600 transition-colors group-hover:bg-amber-600 group-hover:text-white">
            <ChartBarIcon class="w-7 h-7" />
          </div>
          <div>
            <div class="text-[10px] font-black uppercase text-gray-400 mb-1 tracking-widest">Ocupación</div>
            <div class="text-2xl font-black text-gray-900 leading-none">{{ ocupacionPct }}%</div>
          </div>
        </div>
      </div>

      <!-- Filters -->
      <div class="flex flex-wrap gap-4 mb-6 bg-white p-5 rounded-[32px] border border-gray-100 shadow-sm items-center">
        <div class="relative flex-1 max-w-sm">
          <input
            v-model="search"
            type="text"
            placeholder="Código, materia o profesor..."
            class="w-full bg-gray-50 border border-transparent rounded-2xl px-5 py-3 text-sm font-bold outline-none focus:ring-4 focus:ring-blue-500/5 placeholder:text-gray-400 transition-all"
          />
          <MagnifyingGlassIcon class="w-5 h-5 absolute right-5 top-3 text-gray-300" />
        </div>

        <select v-model="filterPeriod" class="px-6 py-3 bg-gray-50 border border-transparent rounded-2xl text-[11px] font-black outline-none focus:ring-4 focus:ring-blue-500/5 appearance-none cursor-pointer hover:bg-gray-100 transition-all text-gray-600 uppercase tracking-widest">
          <option value="">TODOS LOS PERÍODOS</option>
          <option v-for="p in periods" :key="p.id" :value="p.id">{{ p.name }}</option>
        </select>

        <select v-model="filterCareer" class="px-6 py-3 bg-gray-50 border border-transparent rounded-2xl text-[11px] font-black outline-none focus:ring-4 focus:ring-blue-500/5 appearance-none cursor-pointer hover:bg-gray-100 transition-all text-gray-600 uppercase tracking-widest">
          <option value="">TODAS LAS CARRERAS</option>
          <option v-for="c in careers" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>

        <label class="flex items-center gap-2 cursor-pointer">
          <input type="checkbox" v-model="filterAvailable" class="h-4 w-4 rounded border-gray-300 text-[var(--upel-blue)] focus:ring-blue-500" />
          <span class="text-[11px] font-black text-gray-600 uppercase tracking-widest">Solo disponibles</span>
        </label>

        <div class="flex-1"></div>
      </div>

      <!-- DataTable -->
      <div class="bg-white rounded-[32px] border border-gray-100 shadow-sm flex flex-col min-h-[400px] overflow-hidden">
        <DataTable
          :value="filteredSections"
          :paginator="true"
          :rows="15"
          :rowsPerPageOptions="[15, 25, 50]"
          dataKey="id"
          :loading="loading"
          class="p-datatable-sm w-full"
          stripedRows
          removableSort
          paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
          currentPageReportTemplate="Mostrando {first} a {last} de {totalRecords} secciones"
        >
          <template #empty>
            <div class="p-10 flex flex-col items-center justify-center text-center">
              <div class="w-16 h-16 bg-gray-50 rounded-2xl flex items-center justify-center mb-4">
                <i class="pi pi-table text-2xl text-gray-300"></i>
              </div>
              <p class="text-gray-400 font-bold mb-1">No se encontraron secciones</p>
              <p class="text-xs text-gray-300">Ajusta los filtros o crea una nueva sección.</p>
            </div>
          </template>

          <Column field="uc_code" header="UC" sortable style="min-width: 220px">
            <template #body="{ data }">
              <div>
                <span class="text-[10px] font-mono font-black bg-gray-100 text-gray-600 px-2 py-0.5 rounded-md border border-gray-200">{{ data.uc_code }}</span>
                <div class="text-[13px] font-black text-gray-900 mt-1 leading-tight">{{ data.uc_name }}</div>
              </div>
            </template>
          </Column>

          <Column field="section_number" header="SECCIÓN" sortable>
            <template #body="{ data }">
              <div class="text-center text-sm font-black text-gray-700">{{ data.section_number }}</div>
            </template>
          </Column>

          <Column field="career_name" header="CARRERA" sortable style="max-width: 180px">
            <template #body="{ data }">
              <div class="text-[11px] font-medium text-gray-600 truncate max-w-[160px]" :title="data.career_name">{{ data.career_name || '—' }}</div>
            </template>
          </Column>

          <Column field="professor_name" header="PROFESOR" sortable>
            <template #body="{ data }">
              <span v-if="data.professor_name" class="text-[12px] font-bold text-gray-800">{{ data.professor_name }}</span>
              <span v-else class="text-[11px] font-medium text-gray-400 italic">Sin asignar</span>
            </template>
          </Column>

          <Column field="enrolled_count" header="CUPOS" sortable style="min-width: 130px">
            <template #body="{ data }">
              <div>
                <div class="flex justify-between text-[10px] font-black text-gray-500 mb-1">
                  <span>{{ data.enrolled_count || 0 }}/{{ data.max_students }}</span>
                  <span :class="getCupoTextClass(data)">{{ getCupoPct(data) }}%</span>
                </div>
                <div class="h-1.5 rounded-full bg-gray-100 overflow-hidden">
                  <div class="h-full rounded-full transition-all" :class="getCupoBarClass(data)" :style="{ width: getCupoPct(data) + '%' }"></div>
                </div>
              </div>
            </template>
          </Column>

          <Column field="is_active" header="ESTADO" sortable>
            <template #body="{ data }">
              <span class="px-3 py-1 rounded-full text-[10px] font-black tracking-widest uppercase border"
                :class="data.is_active
                  ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                  : 'bg-gray-50 text-gray-500 border-gray-200'">
                {{ data.is_active ? 'Activa' : 'Inactiva' }}
              </span>
            </template>
          </Column>

          <Column header="ACCIONES" alignFrozen="right">
            <template #body="{ data }">
              <div class="flex gap-1 justify-end">
                <button @click="openEdit(data)" class="h-8 w-8 flex items-center justify-center rounded-lg hover:bg-blue-50 text-gray-400 hover:text-blue-600 transition-colors" title="Editar">
                  <PencilSquareIcon class="w-4 h-4" />
                </button>
                <button @click="openInscritos(data)" class="h-8 w-8 flex items-center justify-center rounded-lg hover:bg-indigo-50 text-gray-400 hover:text-indigo-600 transition-colors" title="Ver inscritos">
                  <UsersIcon class="w-4 h-4" />
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
                <TableCellsIcon class="w-6 h-6" />
              </div>
              <div>
                <h2 class="text-xl font-black text-gray-900 leading-tight">
                  {{ editingSection ? 'Editar Sección' : 'Nueva Sección' }}
                </h2>
                <div class="text-[10px] font-bold text-gray-500 uppercase tracking-widest mt-0.5">Oferta académica</div>
              </div>
            </div>
            <button @click="closeModal" class="h-10 w-10 rounded-xl bg-white border border-gray-100 hover:bg-rose-50 hover:text-rose-500 hover:border-rose-100 flex items-center justify-center transition-all text-gray-400">
              <i class="pi pi-times"></i>
            </button>
          </div>

          <div class="p-8 space-y-4 max-h-[60vh] overflow-y-auto custom-scrollbar">
            <div class="space-y-1.5">
              <label class="text-[10px] font-black uppercase text-gray-400 tracking-widest ml-1">Período</label>
              <select v-model="form.period_id" class="w-full bg-gray-50 border border-gray-100 rounded-2xl px-5 py-3 text-sm font-bold outline-none focus:ring-4 focus:ring-blue-500/10 appearance-none">
                <option value="">Seleccionar período</option>
                <option v-for="p in periods" :key="p.id" :value="p.id">{{ p.name }}</option>
              </select>
            </div>

            <div class="space-y-1.5">
              <label class="text-[10px] font-black uppercase text-gray-400 tracking-widest ml-1">Unidad Curricular</label>
              <select v-model="form.curricular_unit" class="w-full bg-gray-50 border border-gray-100 rounded-2xl px-5 py-3 text-sm font-bold outline-none focus:ring-4 focus:ring-blue-500/10 appearance-none">
                <option value="">Seleccionar unidad curricular</option>
                <option v-for="uc in curricularUnits" :key="uc.id" :value="uc.id">{{ uc.code }} — {{ uc.name }}</option>
              </select>
            </div>

            <div class="space-y-1.5">
              <label class="text-[10px] font-black uppercase text-gray-400 tracking-widest ml-1">Carrera</label>
              <select v-model="form.career_id" class="w-full bg-gray-50 border border-gray-100 rounded-2xl px-5 py-3 text-sm font-bold outline-none focus:ring-4 focus:ring-blue-500/10 appearance-none">
                <option value="">Seleccionar carrera</option>
                <option v-for="c in careers" :key="c.id" :value="c.id">{{ c.name }}</option>
              </select>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div class="space-y-1.5">
                <label class="text-[10px] font-black uppercase text-gray-400 tracking-widest ml-1">Número de Sección</label>
                <input v-model="form.section_number" type="number" min="1" placeholder="Ej: 1" class="w-full bg-gray-50 border border-gray-100 rounded-2xl px-5 py-3 text-sm font-bold outline-none focus:ring-4 focus:ring-blue-500/10" />
              </div>
              <div class="space-y-1.5">
                <label class="text-[10px] font-black uppercase text-gray-400 tracking-widest ml-1">Máx. Estudiantes</label>
                <input v-model="form.max_students" type="number" min="1" placeholder="Ej: 30" class="w-full bg-gray-50 border border-gray-100 rounded-2xl px-5 py-3 text-sm font-bold outline-none focus:ring-4 focus:ring-blue-500/10" />
              </div>
            </div>

            <div class="space-y-1.5">
              <label class="text-[10px] font-black uppercase text-gray-400 tracking-widest ml-1">Profesor Asignado</label>
              <select v-model="form.professor_user_id" class="w-full bg-gray-50 border border-gray-100 rounded-2xl px-5 py-3 text-sm font-bold outline-none focus:ring-4 focus:ring-blue-500/10 appearance-none">
                <option value="">Sin asignar</option>
                <option v-for="prof in professors" :key="prof.id" :value="prof.id">{{ prof.first_name }} {{ prof.last_name }}</option>
              </select>
            </div>

            <div class="space-y-1.5">
              <label class="text-[10px] font-black uppercase text-gray-400 tracking-widest ml-1">Sede / Núcleo</label>
              <input v-model="form.sede_name" type="text" placeholder="Ej: Sede Maracay" class="w-full bg-gray-50 border border-gray-100 rounded-2xl px-5 py-3 text-sm font-bold outline-none focus:ring-4 focus:ring-blue-500/10" />
            </div>
          </div>

          <div class="p-6 bg-gray-50/50 flex justify-end gap-3 border-t border-gray-100">
            <button @click="closeModal" class="px-6 py-3 rounded-xl border border-gray-200 bg-white text-xs font-black text-gray-500 uppercase tracking-widest hover:bg-gray-50 transition-all shadow-sm">
              Cancelar
            </button>
            <button @click="submitForm" :disabled="saving" class="bg-[var(--upel-blue)] text-white px-8 py-3 rounded-2xl text-xs font-black uppercase tracking-widest shadow-lg hover:scale-[1.02] transition-all flex items-center gap-2">
              <ArrowPathIcon v-if="saving" class="w-4 h-4 animate-spin" />
              {{ saving ? 'Guardando...' : (editingSection ? 'Guardar Cambios' : 'Crear Sección') }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Inscritos Modal -->
    <Teleport to="body">
      <div v-if="showInscritos" class="fixed inset-0 bg-gray-900/60 backdrop-blur-sm z-[100] flex items-center justify-center p-4">
        <div class="bg-white rounded-[32px] w-full max-w-2xl shadow-2xl flex flex-col animate-scale-in overflow-hidden">
          <div class="p-8 border-b border-gray-50 flex justify-between items-center bg-gray-50/50">
            <div class="flex items-center gap-4">
              <div class="w-12 h-12 rounded-xl bg-indigo-100 flex items-center justify-center text-indigo-600">
                <UsersIcon class="w-6 h-6" />
              </div>
              <div>
                <h2 class="text-xl font-black text-gray-900 leading-tight">Estudiantes Inscritos</h2>
                <div class="text-[10px] font-bold text-gray-500 uppercase tracking-widest mt-0.5">
                  {{ selectedSection?.uc_code }} &mdash; Sección {{ selectedSection?.section_number }}
                </div>
              </div>
            </div>
            <button @click="showInscritos = false" class="h-10 w-10 rounded-xl bg-white border border-gray-100 hover:bg-rose-50 hover:text-rose-500 hover:border-rose-100 flex items-center justify-center transition-all text-gray-400">
              <i class="pi pi-times"></i>
            </button>
          </div>

          <div class="p-8 max-h-[60vh] overflow-y-auto custom-scrollbar">
            <div v-if="loadingInscritos" class="flex items-center justify-center py-10">
              <ArrowPathIcon class="w-6 h-6 text-gray-300 animate-spin" />
            </div>
            <div v-else-if="inscritos.length === 0" class="text-center py-10 text-gray-400 text-xs font-black uppercase tracking-widest bg-gray-50 rounded-3xl border border-dashed border-gray-200">
              No hay estudiantes inscritos en esta sección
            </div>
            <div v-else class="space-y-2">
              <div v-for="e in inscritos" :key="e.id" class="flex items-center justify-between bg-gray-50 rounded-2xl px-5 py-3 border border-gray-100">
                <div class="flex items-center gap-3">
                  <div class="h-8 w-8 rounded-xl bg-[var(--upel-blue)]/10 flex items-center justify-center text-[var(--upel-blue)] font-black text-[10px]">
                    {{ (e.student_carnet || '?').charAt(0) }}
                  </div>
                  <div>
                    <div class="text-[11px] font-mono font-bold text-gray-700">{{ e.student_carnet || e.student_id || '—' }}</div>
                    <div class="text-[10px] text-gray-400 font-medium">{{ e.uc_name || selectedSection?.uc_name }}</div>
                  </div>
                </div>
                <span class="px-3 py-1 rounded-full text-[10px] font-black tracking-widest uppercase border"
                  :class="{
                    'bg-emerald-50 text-emerald-700 border-emerald-200': e.status === 'enrolled' || e.status === 'active',
                    'bg-amber-50 text-amber-600 border-amber-200': e.status === 'pending',
                    'bg-blue-50 text-blue-700 border-blue-200': e.status === 'approved',
                    'bg-red-50 text-red-600 border-red-200': e.status === 'failed' || e.status === 'withdrawn',
                    'bg-gray-50 text-gray-500 border-gray-200': !e.status
                  }">
                  {{ statusLabel(e.status) }}
                </span>
              </div>
            </div>
            <div v-if="inscritosError" class="mt-4 text-center text-xs text-gray-400 font-medium italic">
              No se pudo cargar el listado de inscritos. Verifica que el servicio de inscripciones esté activo.
            </div>
          </div>

          <div class="p-6 bg-gray-50/50 flex justify-end border-t border-gray-100">
            <button @click="showInscritos = false" class="px-6 py-3 rounded-xl border border-gray-200 bg-white text-xs font-black text-gray-500 uppercase tracking-widest hover:bg-gray-50 transition-all shadow-sm">
              Cerrar
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
  MagnifyingGlassIcon,
  UsersIcon,
  CheckBadgeIcon,
  TableCellsIcon,
  ChartBarIcon
} from '@heroicons/vue/24/outline'

const authStore = useAuthStore()
const sections = ref([])
const periods = ref([])
const careers = ref([])
const curricularUnits = ref([])
const professors = ref([])
const loading = ref(true)
const saving = ref(false)

const search = ref('')
const filterPeriod = ref('')
const filterCareer = ref('')
const filterAvailable = ref(false)

const showModal = ref(false)
const editingSection = ref(null)

const showInscritos = ref(false)
const selectedSection = ref(null)
const inscritos = ref([])
const loadingInscritos = ref(false)
const inscritosError = ref(false)

const form = reactive({
  period_id: '',
  curricular_unit: '',
  career_id: '',
  section_number: '',
  max_students: '',
  professor_user_id: '',
  sede_name: ''
})

const activePeriodName = computed(() => {
  const active = periods.value.find(p => p.is_active)
  return active ? active.name : ''
})

const totalCupos = computed(() => sections.value.reduce((acc, s) => acc + (s.max_students || 0), 0))

const ocupacionPct = computed(() => {
  const totalMax = sections.value.reduce((acc, s) => acc + (s.max_students || 0), 0)
  const totalEnrolled = sections.value.reduce((acc, s) => acc + (s.enrolled_count || 0), 0)
  if (!totalMax) return 0
  return Math.round((totalEnrolled / totalMax) * 100)
})

const filteredSections = computed(() => {
  let res = sections.value

  if (search.value) {
    const q = search.value.toLowerCase()
    res = res.filter(s =>
      (s.uc_code || '').toLowerCase().includes(q) ||
      (s.uc_name || '').toLowerCase().includes(q) ||
      (s.professor_name || '').toLowerCase().includes(q)
    )
  }

  if (filterPeriod.value) {
    res = res.filter(s => {
      const periodId = s.period?.id ?? s.period_id ?? s.period
      return String(periodId) === String(filterPeriod.value)
    })
  }

  if (filterCareer.value) {
    res = res.filter(s => String(s.career_id) === String(filterCareer.value))
  }

  if (filterAvailable.value) {
    res = res.filter(s => (s.enrolled_count || 0) < (s.max_students || 0))
  }

  return res
})

const getCupoPct = (section) => {
  const max = section.max_students || 0
  if (!max) return 0
  return Math.min(100, Math.round(((section.enrolled_count || 0) / max) * 100))
}

const getCupoBarClass = (section) => {
  const pct = getCupoPct(section)
  if (pct >= 100) return 'bg-red-500'
  if (pct >= 90) return 'bg-red-400'
  if (pct >= 70) return 'bg-amber-400'
  return 'bg-emerald-400'
}

const getCupoTextClass = (section) => {
  const pct = getCupoPct(section)
  if (pct >= 90) return 'text-red-500'
  if (pct >= 70) return 'text-amber-500'
  return 'text-emerald-500'
}

const statusLabel = (status) => ({
  enrolled: 'Cursando',
  active: 'Activa',
  pending: 'Pendiente',
  approved: 'Aprobada',
  failed: 'Reprobada',
  withdrawn: 'Retirada'
}[status] || status || '—')

const fetchAll = async () => {
  loading.value = true
  try {
    const [sectRes, perRes, carRes, ucRes, profRes] = await Promise.all([
      axios.get('/api/courses/sections/', { headers: { Authorization: 'Bearer ' + authStore.token } }),
      axios.get('/api/courses/periods/', { headers: { Authorization: 'Bearer ' + authStore.token } }),
      axios.get('/api/students/careers/', { headers: { Authorization: 'Bearer ' + authStore.token } }),
      axios.get('/api/curriculum/curricular-units/', { headers: { Authorization: 'Bearer ' + authStore.token } }),
      axios.get('/api/users/', { params: { role: 'professor' }, headers: { Authorization: 'Bearer ' + authStore.token } })
    ])
    sections.value = sectRes.data.results || sectRes.data
    periods.value = perRes.data.results || perRes.data
    careers.value = carRes.data.results || carRes.data
    curricularUnits.value = ucRes.data.results || ucRes.data
    professors.value = profRes.data.results || profRes.data

    // Default filter to active period
    const active = periods.value.find(p => p.is_active)
    if (active && !filterPeriod.value) {
      filterPeriod.value = active.id
    }
  } catch (err) {
    console.error('Fetch sections error:', err.response?.status, err.message)
  } finally {
    loading.value = false
  }
}

const openCreate = () => {
  editingSection.value = null
  const active = periods.value.find(p => p.is_active)
  Object.assign(form, {
    period_id: active?.id || '',
    curricular_unit: '',
    career_id: '',
    section_number: '',
    max_students: '',
    professor_user_id: '',
    sede_name: ''
  })
  showModal.value = true
}

const openEdit = (section) => {
  editingSection.value = section
  Object.assign(form, {
    period_id: section.period?.id ?? section.period_id ?? '',
    curricular_unit: section.curricular_unit || '',
    career_id: section.career_id || '',
    section_number: section.section_number,
    max_students: section.max_students,
    professor_user_id: section.professor_user_id || '',
    sede_name: section.sede_name || ''
  })
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingSection.value = null
}

const submitForm = async () => {
  saving.value = true
  try {
    const payload = {
      period: form.period_id,
      curricular_unit: form.curricular_unit,
      career: form.career_id,
      section_number: form.section_number,
      max_students: form.max_students,
      professor_user_id: form.professor_user_id || null,
      sede_name: form.sede_name
    }

    if (editingSection.value) {
      const res = await axios.patch(`/api/courses/sections/${editingSection.value.id}/`, payload, {
        headers: { Authorization: 'Bearer ' + authStore.token }
      })
      const idx = sections.value.findIndex(s => s.id === editingSection.value.id)
      if (idx !== -1) sections.value[idx] = res.data
    } else {
      const res = await axios.post('/api/courses/sections/', payload, {
        headers: { Authorization: 'Bearer ' + authStore.token }
      })
      sections.value.push(res.data)
    }
    closeModal()
  } catch (err) {
    console.error('Save section error:', err.response?.data || err.message)
  } finally {
    saving.value = false
  }
}

const openInscritos = async (section) => {
  selectedSection.value = section
  showInscritos.value = true
  inscritos.value = []
  inscritosError.value = false
  loadingInscritos.value = true
  try {
    const res = await axios.get('/api/enrollments/enrollments/', {
      params: { section_id: section.id },
      headers: { Authorization: 'Bearer ' + authStore.token }
    })
    const data = res.data.results || res.data
    // Flatten: each enrollment may have details array, or be a flat record
    if (data.length && data[0].details) {
      inscritos.value = data.flatMap(e =>
        (e.details || []).map(d => ({ ...d, student_carnet: e.student_carnet || e.student_id }))
      )
    } else {
      inscritos.value = data
    }
  } catch (err) {
    console.error('Fetch inscritos error:', err.response?.status, err.message)
    inscritosError.value = true
  } finally {
    loadingInscritos.value = false
  }
}

onMounted(fetchAll)
</script>

<style scoped>
.animate-scale-in {
  animation: scaleIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
@keyframes scaleIn {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}
.custom-scrollbar::-webkit-scrollbar { width: 5px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #E2E8F0; border-radius: 10px; }
</style>
