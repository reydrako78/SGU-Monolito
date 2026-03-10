<template>
  <div class="min-h-screen bg-[#F8FAFC] flex text-gray-900">
    <AdminSidebar />
    <main class="flex-1 p-8 overflow-y-auto">
      <header class="mb-10 flex flex-col md:flex-row justify-between items-center gap-4">
        <div>
          <h1 class="text-3xl font-black text-gray-900 tracking-tight italic">Directorio de Usuarios</h1>
          <p class="text-gray-500 font-medium">Gestión de roles, permisos técnicos y ámbitos territoriales.</p>
        </div>
        <div class="flex gap-3">
           <button @click="fetchUsers" class="p-4 bg-white hover:bg-gray-50 rounded-2xl border border-gray-100 shadow-sm transition-all focus:outline-none focus:ring-4 focus:ring-blue-500/10 active:scale-95 group">
             <ArrowPathIcon :class="{'animate-spin': loading}" class="w-5 h-5 text-gray-400 group-hover:text-blue-500" />
           </button>
           <a href="http://localhost:8000/system-admin/core/customuser/" target="_blank" class="px-6 py-3 bg-gray-900 text-white rounded-2xl hover:bg-gray-800 shadow-xl shadow-black/10 transition-all text-xs font-black uppercase tracking-widest flex items-center gap-2 active:scale-95">
             <ShieldCheckIcon class="w-5 h-5 text-blue-400" /> Panel Avanzado
           </a>
        </div>
      </header>

      <!-- Stats Bar -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-10">
        <div class="bg-white p-7 rounded-[32px] border border-gray-100 shadow-sm flex items-center gap-5 group hover:shadow-lg transition-all border-b-4 border-b-blue-500">
           <div class="h-14 w-14 rounded-2xl bg-blue-50 flex items-center justify-center text-blue-600 transition-colors group-hover:bg-blue-600 group-hover:text-white">
              <UsersIcon class="w-7 h-7" />
           </div>
           <div>
              <div class="text-[10px] font-black uppercase text-gray-400 mb-1 tracking-widest">Total Usuarios</div>
              <div class="text-2xl font-black text-gray-900 leading-none">{{ users.length }}</div>
           </div>
        </div>
        <div class="bg-white p-7 rounded-[32px] border border-gray-100 shadow-sm flex items-center gap-5 group hover:shadow-lg transition-all border-b-4 border-b-emerald-500">
           <div class="h-14 w-14 rounded-2xl bg-emerald-50 flex items-center justify-center text-emerald-600 transition-colors group-hover:bg-emerald-600 group-hover:text-white">
              <CheckBadgeIcon class="w-7 h-7" />
           </div>
           <div>
              <div class="text-[10px] font-black uppercase text-gray-400 mb-1 tracking-widest">Activos</div>
              <div class="text-2xl font-black text-gray-900 leading-none">{{ users.filter(u => u.is_active).length }}</div>
           </div>
        </div>
        <div class="bg-white p-7 rounded-[32px] border border-gray-100 shadow-sm flex items-center gap-5 group hover:shadow-lg transition-all border-b-4 border-b-amber-500">
           <div class="h-14 w-14 rounded-2xl bg-amber-50 flex items-center justify-center text-amber-600 transition-colors group-hover:bg-amber-600 group-hover:text-white">
              <AcademicCapIcon class="w-7 h-7" />
           </div>
           <div>
              <div class="text-[10px] font-black uppercase text-gray-400 mb-1 tracking-widest">Docentes</div>
              <div class="text-2xl font-black text-gray-900 leading-none">{{ users.filter(u => u.role === 'professor').length }}</div>
           </div>
        </div>
        <div class="bg-white p-7 rounded-[32px] border border-gray-100 shadow-sm flex items-center gap-5 group hover:shadow-lg transition-all border-b-4 border-b-indigo-500">
           <div class="h-14 w-14 rounded-2xl bg-indigo-50 flex items-center justify-center text-indigo-600 transition-colors group-hover:bg-indigo-600 group-hover:text-white">
              <IdentificationIcon class="w-7 h-7" />
           </div>
           <div>
              <div class="text-[10px] font-black uppercase text-gray-400 mb-1 tracking-widest">Estudiantes</div>
              <div class="text-2xl font-black text-gray-900 leading-none">{{ users.filter(u => u.role === 'student').length }}</div>
           </div>
        </div>
      </div>

      <!-- Advanced Tools -->
      <div class="flex flex-wrap gap-4 mb-6 bg-white p-4 rounded-3xl border border-gray-100 shadow-sm items-center">
        
        <div class="relative group">
           <input 
             v-model="search" 
             type="text" 
             placeholder="Nombre, email o código..." 
             class="bg-gray-50 border-transparent border focus:border-blue-100 rounded-xl px-5 py-2.5 text-sm font-bold shadow-none w-64 outline-none transition-all focus:ring-4 focus:ring-blue-500/5 placeholder:text-gray-400"
           />
           <MagnifyingGlassIcon class="w-4 h-4 absolute right-4 top-3 text-gray-400" />
        </div>

        <select v-model="filterRole" class="px-5 py-2.5 bg-gray-50 border border-transparent rounded-xl text-xs font-bold shadow-none outline-none focus:ring-4 focus:ring-blue-500/5 appearance-none cursor-pointer hover:bg-gray-100 transition-all text-gray-600">
          <option value="">TODOS LOS ROLES</option>
          <option value="admin">ADMINISTRADOR</option>
          <option value="student">ESTUDIANTE</option>
          <option value="professor">PROFESOR</option>
          <option value="aspirant">ASPIRANTE</option>
          <option value="control_estudios">CONTROL DE ESTUDIOS</option>
          <option value="secretaria">SECRETARÍA</option>
        </select>

        <select v-model="filterActive" class="px-5 py-2.5 bg-gray-50 border border-transparent rounded-xl text-xs font-bold shadow-none outline-none focus:ring-4 focus:ring-blue-500/5 appearance-none cursor-pointer hover:bg-gray-100 transition-all text-gray-600">
          <option value="">CUALQUIER ESTADO</option>
          <option value="true">ACTIVOS</option>
          <option value="false">INACTIVOS</option>
        </select>
        
        <div class="flex-1"></div>
        
        <button class="bg-blue-600 text-white px-6 py-2.5 rounded-xl text-xs font-bold shadow-md shadow-blue-500/20 hover:shadow-blue-500/30 active:scale-95 transition-all">
           + Registrar Usuario
        </button>
      </div>

      <!-- PrimeVue DataTable -->
      <div class="bg-white rounded-[32px] border border-gray-100 shadow-sm flex flex-col min-h-[500px] overflow-hidden">
        <DataTable 
           :value="filteredUsers" 
           :paginator="true" 
           :rows="10" 
           :rowsPerPageOptions="[10, 25, 50]"
           dataKey="id"
           :loading="loading"
           class="p-datatable-sm w-full"
           stripedRows
           removableSort
           paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
           currentPageReportTemplate="Mostrando {first} a {last} de {totalRecords} usuarios"
        >
          <template #empty>
            <div class="p-10 flex flex-col items-center justify-center text-center">
              <div class="w-16 h-16 bg-gray-50 rounded-2xl flex items-center justify-center mb-4">
                <i class="pi pi-users text-2xl text-gray-300"></i>
              </div>
              <p class="text-gray-400 font-bold mb-1">No se encontraron registros</p>
              <p class="text-xs text-gray-300">Ajusta los filtros de búsqueda para ver más resultados.</p>
            </div>
          </template>

          <Column field="full_name" header="USUARIO" sortable style="min-width: 200px">
            <template #body="{ data }">
              <div class="flex items-center gap-3">
                <div class="h-9 w-9 rounded-xl bg-blue-50 flex items-center justify-center font-black text-[10px] text-blue-600 shadow-sm border border-blue-100/50">
                  {{ data.first_name?.[0] || '' }}{{ data.last_name?.[0] || '' }}
                </div>
                <div>
                  <div class="text-[13px] font-black text-gray-900">{{ data.first_name }} {{ data.last_name }}</div>
                  <div class="text-[10px] text-gray-400 font-bold bg-gray-50 px-1.5 py-0.5 rounded inline-block mt-0.5">{{ data.email }}</div>
                </div>
              </div>
            </template>
          </Column>

          <Column field="username" header="CÓDIGO / USERNAME" sortable>
            <template #body="{ data }">
              <div class="text-[11px] font-mono font-bold text-gray-600 bg-gray-50 px-2 py-1 rounded-md inline-block border border-gray-100">
                {{ data.code || data.username }}
              </div>
            </template>
          </Column>

          <Column field="role" header="ROL & ÁMBITO" sortable>
            <template #body="{ data }">
              <div class="flex flex-col items-start gap-1">
                 <Tag :severity="getRoleSeverity(data.role)" :value="formatRole(data.role)" />
                 <span v-if="data.scope_display" class="text-[9px] font-bold text-gray-400 uppercase tracking-widest bg-gray-50 px-1.5 py-0.5 rounded">
                   <i class="pi pi-map-marker text-[8px] mr-1"></i>{{ data.scope_display }}
                 </span>
              </div>
            </template>
          </Column>

          <Column field="is_active" header="ESTADO" sortable>
            <template #body="{ data }">
               <div class="flex items-center gap-1.5">
                  <div class="h-2 w-2 rounded-full shadow-inner" :class="data.is_active ? 'bg-emerald-400' : 'bg-rose-400'"></div>
                  <span class="text-[10px] font-black uppercase text-gray-600">{{ data.is_active ? 'ACTIVO' : 'INACTIVO' }}</span>
               </div>
            </template>
          </Column>

          <Column header="ACCIONES" alignFrozen="right">
            <template #body="{ data }">
              <div class="flex gap-1 justify-end">
                <button @click="editUser(data)" class="h-8 w-8 flex items-center justify-center rounded-lg hover:bg-blue-50 text-gray-400 hover:text-blue-600 transition-colors" title="Editar">
                  <PencilSquareIcon class="w-4 h-4" />
                </button>
                <a v-if="data.can_access_django_admin || data.is_superuser" :href="`http://localhost:8000/system-admin/core/customuser/${data.id}/change/`" target="_blank" class="h-8 w-8 flex items-center justify-center rounded-lg hover:bg-gray-100 text-gray-400 hover:text-gray-800 transition-colors" title="Django Admin">
                  <ShieldCheckIcon class="w-4 h-4" />
                </a>
              </div>
            </template>
          </Column>
        </DataTable>
      </div>

      <!-- User Edit Modal -->
      <Teleport to="body">
        <div v-if="selectedUser" class="fixed inset-0 bg-gray-900/60 backdrop-blur-sm z-[100] flex items-center justify-center p-4">
           <div class="bg-white rounded-[32px] w-full max-w-2xl shadow-2xl flex flex-col animate-scale-in overflow-hidden">
              <div class="p-8 border-b border-gray-50 flex justify-between items-center bg-gray-50/50">
                 <div class="flex items-center gap-4">
                    <div class="w-12 h-12 rounded-xl bg-blue-100 flex items-center justify-center text-blue-600">
                      <PencilSquareIcon class="w-6 h-6" />
                    </div>
                    <div>
                      <h2 class="text-xl font-black text-gray-900 leading-tight">Gestión de Perfil</h2>
                      <div class="text-[10px] font-bold text-gray-500 uppercase tracking-widest mt-0.5">Configuración de Cuenta</div>
                    </div>
                 </div>
                 <button @click="selectedUser = null" class="h-10 w-10 rounded-xl bg-white border border-gray-100 hover:bg-rose-50 hover:text-rose-500 hover:border-rose-100 flex items-center justify-center transition-all text-gray-400">
                    <i class="pi pi-times"></i>
                 </button>
              </div>

              <div class="p-8 space-y-6 max-h-[65vh] overflow-y-auto custom-scrollbar">
                 <div class="grid grid-cols-2 gap-4">
                    <div class="space-y-1.5">
                       <label class="text-[10px] font-black uppercase text-gray-400 tracking-widest ml-1">Nombre(s)</label>
                       <input v-model="editForm.first_name" type="text" class="w-full bg-white border border-gray-200 rounded-xl px-4 py-3 text-sm font-bold text-gray-800 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 outline-none transition-all shadow-sm" />
                    </div>
                    <div class="space-y-1.5">
                       <label class="text-[10px] font-black uppercase text-gray-400 tracking-widest ml-1">Apellido(s)</label>
                       <input v-model="editForm.last_name" type="text" class="w-full bg-white border border-gray-200 rounded-xl px-4 py-3 text-sm font-bold text-gray-800 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 outline-none transition-all shadow-sm" />
                    </div>
                 </div>

                 <div class="grid grid-cols-2 gap-4">
                    <div class="space-y-1.5">
                       <label class="text-[10px] font-black uppercase text-gray-400 tracking-widest ml-1">Rol de Sistema</label>
                       <select v-model="editForm.role" class="w-full bg-white border border-gray-200 rounded-xl px-4 py-3 text-sm font-bold text-gray-800 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 outline-none appearance-none transition-all shadow-sm">
                          <option value="admin">Administrador</option>
                          <option value="student">Estudiante</option>
                          <option value="professor">Profesor</option>
                          <option value="aspirant">Aspirante</option>
                          <option value="control_estudios">Control de Estudios</option>
                          <option value="secretaria">Secretaría</option>
                       </select>
                    </div>
                    <div class="space-y-1.5">
                       <label class="text-[10px] font-black uppercase text-gray-400 tracking-widest ml-1">Estado de Cuenta</label>
                       <select v-model="editForm.is_active" class="w-full bg-white border border-gray-200 rounded-xl px-4 py-3 text-sm font-bold text-gray-800 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 outline-none appearance-none transition-all shadow-sm">
                          <option :value="true">Activo / Operativo</option>
                          <option :value="false">Suspendido / Inactivo</option>
                       </select>
                    </div>
                 </div>

                 <div class="bg-gray-50/80 p-6 rounded-[24px] border border-gray-100 flex flex-col gap-5">
                    <h3 class="text-xs font-black text-gray-700 uppercase tracking-widest flex items-center gap-2">
                       <ShieldCheckIcon class="w-4 h-4 text-blue-500" /> Alcance y Permisos Técnicos
                    </h3>
                    
                    <label class="flex items-center gap-4 bg-white p-4 rounded-xl border border-gray-200 cursor-pointer shadow-sm">
                       <input type="checkbox" v-model="editForm.can_access_django_admin" class="h-5 w-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500" />
                       <div>
                          <div class="text-[11px] font-black text-gray-900 uppercase">Acceso a Panel Técnico (Django)</div>
                          <div class="text-[10px] text-gray-500 font-medium">Permite al usuario gestionar modelos base raw.</div>
                       </div>
                    </label>

                    <div class="space-y-2">
                       <div class="text-[10px] font-black uppercase text-gray-400 tracking-widest ml-1">Ámbito Organizacional</div>
                       <select v-model="editForm.scope_level" class="w-full bg-white border border-gray-200 rounded-xl px-4 py-3 text-sm font-bold text-gray-800 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 outline-none appearance-none shadow-sm">
                          <option value="global">Nivel Nacional / Global</option>
                          <option value="sede">Restringido a Sede</option>
                          <option value="nucleo">Restringido a Núcleo</option>
                       </select>
                    </div>
                 </div>
              </div>

              <div class="p-6 bg-gray-50/50 flex justify-end gap-3 border-t border-gray-100">
                 <button @click="selectedUser = null" class="px-6 py-3 rounded-xl border border-gray-200 bg-white text-xs font-black text-gray-500 uppercase tracking-widest hover:bg-gray-50 transition-all shadow-sm">Cancelar</button>
                 <button @click="saveUser" :disabled="saving" class="bg-blue-600 text-white px-8 py-3 rounded-xl text-xs font-black uppercase tracking-widest shadow-md shadow-blue-500/20 hover:shadow-blue-500/30 active:scale-95 transition-all flex items-center gap-2">
                    <ArrowPathIcon v-if="saving" class="w-4 h-4 animate-spin" />
                    {{ saving ? 'Guardando...' : 'Aplicar Cambios' }}
                 </button>
              </div>
           </div>
        </div>
      </Teleport>

    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import AdminSidebar from '@/components/AdminSidebar.vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Tag from 'primevue/tag'
import 'primeicons/primeicons.css'

import {
  MagnifyingGlassIcon,
  ArrowPathIcon,
  PencilSquareIcon,
  ShieldCheckIcon,
  UsersIcon,
  CheckBadgeIcon,
  AcademicCapIcon,
  IdentificationIcon
} from '@heroicons/vue/24/outline'

const authStore = useAuthStore()
const users = ref([])
const loading = ref(true)
const saving = ref(false)
const search = ref('')
const filterRole = ref('')
const filterActive = ref('')
const selectedUser = ref(null)

const editForm = reactive({
  first_name: '',
  last_name: '',
  role: '',
  is_active: true,
  can_access_django_admin: false,
  scope_level: 'global',
  scope_sede: null,
  scope_nucleo: null
})

const fetchUsers = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/users/', {
      headers: { Authorization: `Bearer ${authStore.token}` }
    })
    users.value = res.data.results || res.data
  } catch (err) {
    console.error('Fetch users error:', err.response?.status, err.response?.data || err.message)
  } finally {
    loading.value = false
  }
}

const filteredUsers = computed(() => {
  let res = users.value
  if (search.value) {
    const q = search.value.toLowerCase()
    res = res.filter(u => 
      `${u.first_name} ${u.last_name}`.toLowerCase().includes(q) ||
      u.email.toLowerCase().includes(q) ||
      (u.code || '').toLowerCase().includes(q) ||
      (u.username || '').toLowerCase().includes(q)
    )
  }
  if (filterRole.value) {
    res = res.filter(u => u.role === filterRole.value)
  }
  if (filterActive.value !== '') {
    const isActive = filterActive.value === 'true'
    res = res.filter(u => u.is_active === isActive)
  }
  return res
})

const editUser = (u) => {
  selectedUser.value = u
  Object.assign(editForm, {
    first_name: u.first_name,
    last_name: u.last_name,
    role: u.role,
    is_active: u.is_active,
    can_access_django_admin: u.can_access_django_admin,
    scope_level: u.scope_level || 'global',
    scope_sede: u.scope_sede,
    scope_nucleo: u.scope_nucleo
  })
}

const saveUser = async () => {
  if (!selectedUser.value) return
  saving.value = true
  try {
    const res = await axios.patch(`/api/users/${selectedUser.value.id}/`, editForm, {
      headers: { Authorization: `Bearer ${authStore.token}` }
    })
    const idx = users.value.findIndex(u => u.id === selectedUser.value.id)
    if (idx !== -1) users.value[idx] = res.data
    selectedUser.value = null
  } catch (err) {
    console.error('Save user error:', err)
  } finally {
    saving.value = false
  }
}

const formatRole = (role) => {
  const roles = {
    'admin': 'Administrador',
    'student': 'Estudiante',
    'professor': 'Profesor',
    'aspirant': 'Aspirante',
    'control_estudios': 'Control de Estudios',
    'secretaria': 'Secretaría',
    'docencia': 'Docencia'
  }
  return (roles[role] || role).toUpperCase()
}

const getRoleSeverity = (role) => {
  switch(role) {
     case 'admin': return 'danger';
     case 'student': return 'success';
     case 'professor': return 'info';
     case 'aspirant': return 'warn';
     case 'control_estudios': return 'secondary';
     case 'secretaria': return 'contrast';
     default: return 'secondary';
  }
}

onMounted(fetchUsers)
</script>

<style scoped>
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
