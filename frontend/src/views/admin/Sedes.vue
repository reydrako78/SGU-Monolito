<template>
  <div class="min-h-screen bg-[#F8FAFC] flex text-gray-900">
    <AdminSidebar />
    <main class="flex-1 p-8 overflow-y-auto">

      <!-- Header -->
      <header class="mb-10 flex flex-col md:flex-row justify-between items-center gap-4">
        <div>
          <h1 class="text-3xl font-black text-gray-900 tracking-tight">Sedes e Institutos</h1>
          <p class="text-gray-500 font-medium">Gestión territorial de la red UPEL</p>
        </div>
        <div class="flex gap-3">
          <button @click="fetchSedes" class="p-3 bg-white hover:bg-gray-50 rounded-2xl border border-gray-100 shadow-sm transition-all focus:outline-none focus:ring-4 focus:ring-blue-500/10 active:scale-95 group">
            <ArrowPathIcon :class="{ 'animate-spin': loading }" class="w-5 h-5 text-gray-400 group-hover:text-blue-500" />
          </button>
          <button @click="openCreateModal" class="px-6 py-3 bg-[var(--upel-blue)] text-white rounded-2xl hover:bg-blue-800 shadow-xl shadow-blue-900/20 transition-all text-xs font-black uppercase tracking-widest flex items-center gap-2 active:scale-95">
            <BuildingOfficeIcon class="w-5 h-5" /> Registrar Sede
          </button>
        </div>
      </header>

      <!-- Stats -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div class="bg-white p-6 rounded-[32px] border border-gray-100 shadow-sm flex flex-col items-center justify-center">
          <div class="text-[10px] font-black uppercase text-gray-400 mb-1">Total Sedes</div>
          <div class="text-2xl font-black text-gray-900">{{ sedes.length }}</div>
        </div>
        <div class="bg-emerald-50 p-6 rounded-[32px] border border-emerald-100 shadow-sm flex flex-col items-center justify-center">
          <div class="text-[10px] font-black uppercase text-emerald-500 mb-1">Activas</div>
          <div class="text-2xl font-black text-emerald-600">{{ sedes.filter(s => s.is_active).length }}</div>
        </div>
        <div class="bg-blue-50 p-6 rounded-[32px] border border-blue-100 shadow-sm flex flex-col items-center justify-center">
          <div class="text-[10px] font-black uppercase text-blue-500 mb-1">Total Núcleos</div>
          <div class="text-2xl font-black text-blue-600">{{ totalNucleos }}</div>
        </div>
      </div>

      <!-- Loading state -->
      <div v-if="loading" class="flex justify-center items-center py-20">
        <div class="w-8 h-8 border-4 border-blue-100 border-t-[var(--upel-blue)] rounded-full animate-spin"></div>
      </div>

      <!-- Empty state -->
      <div v-else-if="sedes.length === 0" class="flex flex-col items-center justify-center py-20 text-center">
        <div class="w-20 h-20 bg-gray-100 rounded-3xl flex items-center justify-center mb-4">
          <BuildingOfficeIcon class="w-10 h-10 text-gray-300" />
        </div>
        <p class="text-gray-400 font-black italic uppercase tracking-tighter">No hay sedes registradas</p>
        <p class="text-xs text-gray-300 mt-1">Crea la primera sede con el botón superior.</p>
      </div>

      <!-- Grid de Sedes -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        <div
          v-for="sede in sedes"
          :key="sede.id"
          class="bg-white rounded-[32px] p-8 border border-gray-100 shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all flex flex-col gap-4"
        >
          <!-- Card Header -->
          <div class="flex items-start justify-between">
            <div class="flex items-center gap-4">
              <div class="h-14 w-14 rounded-2xl bg-[var(--upel-blue)] flex items-center justify-center font-black text-white text-xl shadow-lg shadow-blue-900/20">
                {{ sede.sigla }}
              </div>
              <div>
                <h2 class="text-xl font-black text-gray-900 leading-tight">{{ sede.name }}</h2>
                <div class="flex items-center gap-1 mt-1">
                  <MapPinIcon class="w-3.5 h-3.5 text-gray-400" />
                  <span class="text-sm text-gray-400 font-medium">{{ sede.city }}</span>
                </div>
              </div>
            </div>
            <span
              class="px-3 py-1 rounded-full text-[9px] font-black uppercase tracking-widest border"
              :class="sede.is_active
                ? 'bg-emerald-50 text-emerald-600 border-emerald-100'
                : 'bg-gray-100 text-gray-400 border-gray-200'"
            >
              {{ sede.is_active ? 'Activa' : 'Inactiva' }}
            </span>
          </div>

          <!-- Nucleos count -->
          <div class="flex items-center gap-2 bg-gray-50 rounded-2xl px-4 py-3">
            <div class="h-7 w-7 bg-blue-100 rounded-xl flex items-center justify-center">
              <MapPinIcon class="w-3.5 h-3.5 text-blue-600" />
            </div>
            <span class="text-xs font-black text-gray-600">
              {{ (sede.nucleos || []).length }}
              {{ (sede.nucleos || []).length === 1 ? 'Núcleo' : 'Núcleos' }}
            </span>
          </div>

          <!-- Nucleos inline list (if any) -->
          <div v-if="(sede.nucleos || []).length > 0" class="space-y-1.5">
            <div
              v-for="nucleo in (sede.nucleos || []).slice(0, 3)"
              :key="nucleo.id"
              class="flex items-center gap-2"
            >
              <div class="h-1.5 w-1.5 rounded-full bg-blue-400 shrink-0"></div>
              <span class="text-xs text-gray-500 font-medium truncate">{{ nucleo.name }}</span>
            </div>
            <div v-if="(sede.nucleos || []).length > 3" class="text-[10px] text-gray-400 font-bold pl-3.5 italic">
              +{{ (sede.nucleos || []).length - 3 }} más...
            </div>
          </div>

          <!-- Card Footer Actions -->
          <div class="flex gap-2 pt-2 border-t border-gray-50 mt-auto">
            <button
              @click="openEditModal(sede)"
              class="flex-1 py-2.5 bg-gray-50 text-gray-600 text-[10px] font-black uppercase tracking-widest rounded-xl border border-gray-100 hover:bg-gray-100 transition-all"
            >
              Editar
            </button>
            <button
              @click="openNucleoPanel(sede)"
              class="flex-1 py-2.5 bg-[var(--upel-blue)]/10 text-[var(--upel-blue)] text-[10px] font-black uppercase tracking-widest rounded-xl border border-blue-100 hover:bg-[var(--upel-blue)] hover:text-white transition-all"
            >
              Ver Núcleos
            </button>
          </div>
        </div>
      </div>

    </main>

    <!-- ── Panel lateral de Núcleos ─────────────────────── -->
    <Teleport to="body">
      <div v-if="selectedSede" class="fixed inset-0 z-[100] flex">
        <!-- Overlay -->
        <div class="flex-1 bg-gray-900/50 backdrop-blur-sm" @click="selectedSede = null"></div>
        <!-- Aside panel -->
        <aside class="w-[420px] bg-white h-full flex flex-col shadow-2xl overflow-hidden animate-slide-in">
          <!-- Panel header -->
          <div class="p-8 border-b border-gray-100 bg-gray-50/50">
            <div class="text-[10px] font-black uppercase text-blue-500 tracking-widest mb-1 italic">Sede · {{ selectedSede.sigla }}</div>
            <h2 class="text-2xl font-black text-gray-900">{{ selectedSede.name }}</h2>
            <p class="text-xs text-gray-400 font-medium mt-1 flex items-center gap-1">
              <MapPinIcon class="w-3.5 h-3.5" /> {{ selectedSede.city }}
            </p>
          </div>

          <!-- Nucleos list -->
          <div class="flex-1 overflow-y-auto p-8 space-y-3 custom-scrollbar">
            <div class="text-[10px] font-black uppercase text-gray-400 tracking-widest mb-4">
              Núcleos ({{ nucleos.length }})
            </div>

            <div v-if="nucleosLoading" class="flex justify-center py-8">
              <div class="w-6 h-6 border-3 border-blue-100 border-t-blue-500 rounded-full animate-spin"></div>
            </div>

            <div v-else-if="nucleos.length === 0" class="text-center py-8">
              <p class="text-sm text-gray-400 font-bold italic">Sin núcleos registrados</p>
            </div>

            <div
              v-else
              v-for="nucleo in nucleos"
              :key="nucleo.id"
              class="bg-gray-50 rounded-2xl p-4 flex items-start justify-between gap-3 border border-gray-100"
            >
              <div class="flex-1 min-w-0">
                <div class="text-sm font-black text-gray-900 truncate">{{ nucleo.name }}</div>
                <div v-if="nucleo.address" class="text-[10px] text-gray-400 font-medium mt-0.5 truncate">
                  {{ nucleo.address }}
                </div>
                <span
                  class="mt-1 inline-block px-2 py-0.5 rounded-full text-[8px] font-black uppercase border"
                  :class="nucleo.is_active
                    ? 'bg-emerald-50 text-emerald-600 border-emerald-100'
                    : 'bg-gray-100 text-gray-400 border-gray-200'"
                >
                  {{ nucleo.is_active ? 'Activo' : 'Inactivo' }}
                </span>
              </div>
              <button
                @click="deleteNucleo(nucleo.id)"
                class="h-8 w-8 shrink-0 rounded-xl flex items-center justify-center text-gray-300 hover:bg-red-50 hover:text-red-500 transition-all"
                title="Eliminar núcleo"
              >
                <TrashIcon class="w-4 h-4" />
              </button>
            </div>

            <!-- Add nucleo form -->
            <div class="mt-6 bg-blue-50/60 rounded-2xl p-5 border border-blue-100">
              <div class="text-[10px] font-black uppercase text-blue-500 tracking-widest mb-4">Agregar Núcleo</div>
              <div class="space-y-3">
                <input
                  v-model="newNucleo.name"
                  type="text"
                  placeholder="Nombre del núcleo"
                  class="w-full bg-white border border-gray-200 rounded-xl px-4 py-3 text-sm font-bold text-gray-800 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 outline-none transition-all"
                />
                <input
                  v-model="newNucleo.address"
                  type="text"
                  placeholder="Dirección (opcional)"
                  class="w-full bg-white border border-gray-200 rounded-xl px-4 py-3 text-sm font-bold text-gray-800 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 outline-none transition-all"
                />
                <button
                  @click="saveNucleo"
                  :disabled="!newNucleo.name.trim() || savingNucleo"
                  class="w-full py-3 bg-[var(--upel-blue)] text-white rounded-xl text-[11px] font-black uppercase tracking-widest shadow-md shadow-blue-900/20 hover:bg-blue-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2"
                >
                  <ArrowPathIcon v-if="savingNucleo" class="w-4 h-4 animate-spin" />
                  {{ savingNucleo ? 'Guardando...' : '+ Agregar Núcleo' }}
                </button>
              </div>
            </div>
          </div>

          <!-- Close button -->
          <div class="p-6 border-t border-gray-100 flex justify-center">
            <button @click="selectedSede = null" class="text-[10px] font-black text-gray-400 hover:text-gray-900 uppercase underline decoration-2 underline-offset-4 tracking-widest transition-colors">
              Cerrar Panel
            </button>
          </div>
        </aside>
      </div>
    </Teleport>

    <!-- ── Modal crear/editar sede ─────────────────────── -->
    <Teleport to="body">
      <div v-if="showModal" class="fixed inset-0 bg-gray-900/60 backdrop-blur-sm z-[200] flex items-center justify-center p-4">
        <div class="bg-white rounded-[32px] w-full max-w-lg shadow-2xl flex flex-col animate-scale-in overflow-hidden">
          <!-- Modal header -->
          <div class="p-8 border-b border-gray-50 flex justify-between items-center bg-gray-50/50">
            <div class="flex items-center gap-4">
              <div class="w-12 h-12 rounded-xl bg-blue-100 flex items-center justify-center text-[var(--upel-blue)]">
                <BuildingOfficeIcon class="w-6 h-6" />
              </div>
              <div>
                <h2 class="text-xl font-black text-gray-900 leading-tight">
                  {{ editingSede ? 'Editar Sede' : 'Registrar Sede' }}
                </h2>
                <div class="text-[10px] font-bold text-gray-500 uppercase tracking-widest mt-0.5">
                  {{ editingSede ? 'Actualizar información' : 'Nueva sede UPEL' }}
                </div>
              </div>
            </div>
            <button @click="closeModal" class="h-10 w-10 rounded-xl bg-white border border-gray-100 hover:bg-rose-50 hover:text-rose-500 hover:border-rose-100 flex items-center justify-center transition-all text-gray-400">
              <XMarkIcon class="w-5 h-5" />
            </button>
          </div>

          <!-- Modal body -->
          <div class="p-8 space-y-5">
            <div class="grid grid-cols-2 gap-4">
              <div class="space-y-1.5">
                <label class="text-[10px] font-black uppercase text-gray-400 tracking-widest ml-1">Sigla (3–5 caracteres)</label>
                <input
                  v-model="sedeForm.sigla"
                  type="text"
                  maxlength="5"
                  placeholder="ej. IPC"
                  class="w-full bg-white border border-gray-200 rounded-xl px-4 py-3 text-sm font-black text-gray-800 uppercase focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 outline-none transition-all shadow-sm"
                  @input="sedeForm.sigla = sedeForm.sigla.toUpperCase()"
                />
              </div>
              <div class="space-y-1.5">
                <label class="text-[10px] font-black uppercase text-gray-400 tracking-widest ml-1">Ciudad</label>
                <input
                  v-model="sedeForm.city"
                  type="text"
                  placeholder="ej. Caracas"
                  class="w-full bg-white border border-gray-200 rounded-xl px-4 py-3 text-sm font-bold text-gray-800 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 outline-none transition-all shadow-sm"
                />
              </div>
            </div>

            <div class="space-y-1.5">
              <label class="text-[10px] font-black uppercase text-gray-400 tracking-widest ml-1">Nombre Completo</label>
              <input
                v-model="sedeForm.name"
                type="text"
                placeholder="ej. Instituto Pedagógico de Caracas"
                class="w-full bg-white border border-gray-200 rounded-xl px-4 py-3 text-sm font-bold text-gray-800 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 outline-none transition-all shadow-sm"
              />
            </div>

            <label class="flex items-center gap-4 bg-gray-50 p-4 rounded-2xl border border-gray-200 cursor-pointer">
              <div
                @click="sedeForm.is_active = !sedeForm.is_active"
                class="relative w-11 h-6 rounded-full transition-colors cursor-pointer shrink-0"
                :class="sedeForm.is_active ? 'bg-[var(--upel-blue)]' : 'bg-gray-300'"
              >
                <div
                  class="absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform"
                  :class="sedeForm.is_active ? 'translate-x-5' : 'translate-x-0'"
                ></div>
              </div>
              <div>
                <div class="text-[11px] font-black text-gray-900 uppercase">Estado de la Sede</div>
                <div class="text-[10px] text-gray-500 font-medium">
                  {{ sedeForm.is_active ? 'Activa y operativa' : 'Inactiva / fuera de servicio' }}
                </div>
              </div>
            </label>
          </div>

          <!-- Modal footer -->
          <div class="p-6 bg-gray-50/50 flex justify-end gap-3 border-t border-gray-100">
            <button @click="closeModal" class="px-6 py-3 rounded-xl border border-gray-200 bg-white text-xs font-black text-gray-500 uppercase tracking-widest hover:bg-gray-50 transition-all shadow-sm">
              Cancelar
            </button>
            <button
              @click="saveSede"
              :disabled="saving || !sedeForm.name.trim() || !sedeForm.sigla.trim()"
              class="bg-[var(--upel-blue)] text-white px-8 py-3 rounded-xl text-xs font-black uppercase tracking-widest shadow-md shadow-blue-900/20 hover:bg-blue-800 active:scale-95 transition-all flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ArrowPathIcon v-if="saving" class="w-4 h-4 animate-spin" />
              {{ saving ? 'Guardando...' : (editingSede ? 'Actualizar' : 'Registrar') }}
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
import {
  ArrowPathIcon,
  MapPinIcon,
  TrashIcon,
  XMarkIcon,
  BuildingOfficeIcon,
} from '@heroicons/vue/24/outline'

const authStore = useAuthStore()

const sedes = ref([])
const nucleos = ref([])
const loading = ref(false)
const nucleosLoading = ref(false)
const saving = ref(false)
const savingNucleo = ref(false)

const selectedSede = ref(null)
const showModal = ref(false)
const editingSede = ref(null)

const sedeForm = reactive({
  name: '',
  sigla: '',
  city: '',
  is_active: true,
})

const newNucleo = reactive({
  name: '',
  address: '',
})

const totalNucleos = computed(() =>
  sedes.value.reduce((sum, s) => sum + (s.nucleos || []).length, 0)
)

const authHeaders = () => ({ Authorization: `Bearer ${authStore.token}` })

const fetchSedes = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/sedes/', { headers: authHeaders() })
    sedes.value = res.data.results || res.data
  } catch (err) {
    console.error('Fetch sedes error:', err)
  } finally {
    loading.value = false
  }
}

const fetchNucleos = async (sedeId) => {
  nucleosLoading.value = true
  nucleos.value = []
  try {
    const res = await axios.get(`/api/nucleos/?sede_id=${sedeId}`, { headers: authHeaders() })
    nucleos.value = res.data.results || res.data
  } catch (err) {
    console.error('Fetch nucleos error:', err)
  } finally {
    nucleosLoading.value = false
  }
}

const openNucleoPanel = (sede) => {
  selectedSede.value = sede
  newNucleo.name = ''
  newNucleo.address = ''
  fetchNucleos(sede.id)
}

const openCreateModal = () => {
  editingSede.value = null
  Object.assign(sedeForm, { name: '', sigla: '', city: '', is_active: true })
  showModal.value = true
}

const openEditModal = (sede) => {
  editingSede.value = sede
  Object.assign(sedeForm, {
    name: sede.name,
    sigla: sede.sigla,
    city: sede.city,
    is_active: sede.is_active,
  })
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingSede.value = null
}

const saveSede = async () => {
  saving.value = true
  try {
    if (editingSede.value) {
      const res = await axios.patch(`/api/sedes/${editingSede.value.id}/`, sedeForm, { headers: authHeaders() })
      const idx = sedes.value.findIndex(s => s.id === editingSede.value.id)
      if (idx !== -1) sedes.value[idx] = { ...sedes.value[idx], ...res.data }
    } else {
      const res = await axios.post('/api/sedes/', sedeForm, { headers: authHeaders() })
      sedes.value.unshift(res.data)
    }
    closeModal()
  } catch (err) {
    console.error('Save sede error:', err)
    alert(err.response?.data?.detail || 'Error al guardar la sede.')
  } finally {
    saving.value = false
  }
}

const saveNucleo = async () => {
  if (!newNucleo.name.trim() || !selectedSede.value) return
  savingNucleo.value = true
  try {
    const payload = {
      name: newNucleo.name.trim(),
      address: newNucleo.address.trim(),
      sede_id: selectedSede.value.id,
    }
    const res = await axios.post('/api/nucleos/', payload, { headers: authHeaders() })
    nucleos.value.push(res.data)
    newNucleo.name = ''
    newNucleo.address = ''
    // Update count in the sede card
    const sede = sedes.value.find(s => s.id === selectedSede.value.id)
    if (sede) {
      if (!sede.nucleos) sede.nucleos = []
      sede.nucleos.push(res.data)
    }
  } catch (err) {
    console.error('Save nucleo error:', err)
    alert(err.response?.data?.detail || 'Error al agregar el núcleo.')
  } finally {
    savingNucleo.value = false
  }
}

const deleteNucleo = async (id) => {
  if (!confirm('¿Eliminar este núcleo?')) return
  try {
    await axios.delete(`/api/nucleos/${id}/`, { headers: authHeaders() })
    nucleos.value = nucleos.value.filter(n => n.id !== id)
    // Sync sede card
    const sede = sedes.value.find(s => s.id === selectedSede.value?.id)
    if (sede && sede.nucleos) {
      sede.nucleos = sede.nucleos.filter(n => n.id !== id)
    }
  } catch (err) {
    console.error('Delete nucleo error:', err)
    alert(err.response?.data?.detail || 'Error al eliminar el núcleo.')
  }
}

onMounted(fetchSedes)
</script>

<style scoped>
:root {
  --upel-blue: #004A99;
}

.animate-slide-in {
  animation: slideIn 0.35s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes slideIn {
  from { transform: translateX(100%); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}

.animate-scale-in {
  animation: scaleIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes scaleIn {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
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
