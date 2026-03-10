<template>
  <div class="min-h-screen bg-[#F8FAFC] flex text-gray-900">
    <AdminSidebar />
    <main class="flex-1 p-8 overflow-y-auto">
      <header class="mb-10 flex flex-col md:flex-row justify-between items-center gap-4">
        <div>
          <h1 class="text-3xl font-black text-gray-900 tracking-tight">Gestión de Admisiones</h1>
          <p class="text-gray-500 font-medium">Control y validación de expedientes de aspirantes nuevos.</p>
        </div>
        <div class="flex gap-2">
           <button @click="fetchAspirants" class="p-3 bg-white hover:bg-gray-50 rounded-2xl border border-gray-100 shadow-sm transition-all focus:outline-none focus:ring-4 focus:ring-blue-500/10">
             <ArrowPathIcon :class="{'animate-spin': loading}" class="w-5 h-5 text-gray-400" />
           </button>
        </div>
      </header>

      <!-- Stats Bar -->
      <div class="grid grid-cols-1 md:grid-cols-5 gap-6 mb-8">
        <div class="bg-white p-6 rounded-[32px] border border-gray-100 shadow-sm flex flex-col items-center justify-center">
           <div class="text-[10px] font-black uppercase text-gray-400 mb-1">Total Aspirantes</div>
           <div class="text-2xl font-black text-gray-900">{{ aspirants.length }}</div>
        </div>
        <div class="bg-amber-50 p-6 rounded-[32px] border border-amber-100 shadow-sm flex flex-col items-center justify-center">
           <div class="text-[10px] font-black uppercase text-amber-500 mb-1">Pendientes</div>
           <div class="text-2xl font-black text-amber-600">{{ filterByStatus('pending').length }}</div>
        </div>
        <div class="bg-green-50 p-6 rounded-[32px] border border-green-100 shadow-sm flex flex-col items-center justify-center">
           <div class="text-[10px] font-black uppercase text-green-500 mb-1">Admitidos</div>
           <div class="text-2xl font-black text-green-600">{{ filterByStatus('approved').length }}</div>
        </div>
        <div class="bg-emerald-500 p-6 rounded-[32px] border border-emerald-600 shadow-lg shadow-emerald-500/20 flex flex-col items-center justify-center text-white">
           <div class="text-[10px] font-black uppercase text-emerald-100 mb-1">Confirmados</div>
           <div class="text-2xl font-black">{{ filterByStatus('accepted').length }}</div>
        </div>
        <div class="bg-blue-50 p-6 rounded-[32px] border border-blue-100 shadow-sm flex flex-col items-center justify-center">
           <div class="text-[10px] font-black uppercase text-blue-500 mb-1">En Revisión</div>
           <div class="text-2xl font-black text-blue-600">{{ filterByStatus('in_review').length }}</div>
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

        <select v-model="filterStatus" class="px-5 py-2.5 bg-gray-50 border border-transparent rounded-xl text-xs font-bold shadow-none outline-none focus:ring-4 focus:ring-blue-500/5 appearance-none cursor-pointer hover:bg-gray-100 transition-all text-gray-600">
          <option value="">TODOS LOS ESTADOS</option>
          <option value="pending">PENDIENTES</option>
          <option value="in_review">EN REVISIÓN</option>
          <option value="approved">ADMITIDOS</option>
          <option value="accepted">ACEPTADOS/CONFIRMADOS</option>
          <option value="declined">DECLINADOS</option>
          <option value="rejected">RECHAZADOS</option>
        </select>

        <select v-model="filterSede" class="px-5 py-2.5 bg-gray-50 border border-transparent rounded-xl text-xs font-bold shadow-none outline-none focus:ring-4 focus:ring-blue-500/5 appearance-none cursor-pointer hover:bg-gray-100 transition-all text-gray-600">
          <option value="">TODAS LAS SEDES</option>
          <option v-for="sede in uniqueSedes" :key="sede" :value="sede">{{ sede }}</option>
        </select>
        
        <div class="flex-1"></div>
      </div>

      <!-- Table View -->
      <div class="bg-white rounded-[32px] border border-gray-100 shadow-sm flex flex-col min-h-[500px] overflow-hidden">
        <DataTable 
           :value="filteredAspirants" 
           :paginator="true" 
           :rows="10" 
           :rowsPerPageOptions="[10, 25, 50]"
           dataKey="code"
           :loading="loading"
           class="p-datatable-sm w-full"
           stripedRows
           removableSort
           paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
           currentPageReportTemplate="Mostrando {first} a {last} de {totalRecords} aspirantes"
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

          <Column field="full_name" header="ASPIRANTE" sortable style="min-width: 200px">
            <template #body="{ data }">
              <div class="flex items-center gap-3">
                <div class="h-9 w-9 rounded-xl bg-blue-50 flex items-center justify-center font-black text-[10px] text-blue-600 shadow-sm border border-blue-100/50">
                  {{ data.first_name?.[0] || '' }}{{ data.last_name?.[0] || '' }}
                </div>
                <div>
                  <div class="text-[13px] font-black text-gray-900">{{ data.full_name }}</div>
                  <div class="text-[10px] text-gray-400 font-bold bg-gray-50 px-1.5 py-0.5 rounded inline-block mt-0.5">{{ data.email }}</div>
                </div>
              </div>
            </template>
          </Column>

          <Column field="national_id" header="IDENTIFICACIÓN" sortable>
            <template #body="{ data }">
              <div class="text-[11px] font-mono font-bold text-gray-600 bg-gray-50 px-2 py-1 rounded-md inline-block border border-gray-100">
                {{ data.national_id || data.code }}
              </div>
            </template>
          </Column>

          <Column header="OPCIONES DE CARRERA" sortable class="min-w-[250px]">
            <template #body="{ data }">
              <div class="flex flex-col gap-1.5 py-2">
                 <div class="flex items-center gap-2">
                    <span class="h-4 w-4 rounded bg-blue-100 text-blue-600 flex items-center justify-center text-[8px] font-black italic">1</span>
                    <div class="text-[11px] font-black text-gray-700 truncate max-w-[180px] italic uppercase tracking-tighter" :title="data.career_name">{{ data.career_name }}</div>
                 </div>
                 <div v-if="data.career_name_2" class="flex items-center gap-2 opacity-60">
                    <span class="h-4 w-4 rounded bg-gray-100 text-gray-400 flex items-center justify-center text-[8px] font-black italic">2</span>
                    <div class="text-[10px] font-bold text-gray-400 truncate max-w-[180px] italic uppercase tracking-tighter">{{ data.career_name_2 }}</div>
                 </div>
                 <div v-if="data.career_name_3" class="flex items-center gap-2 opacity-40">
                    <span class="h-4 w-4 rounded bg-gray-100 text-gray-400 flex items-center justify-center text-[8px] font-black italic">3</span>
                    <div class="text-[10px] font-bold text-gray-400 truncate max-w-[180px] italic uppercase tracking-tighter">{{ data.career_name_3 }}</div>
                 </div>
              </div>
            </template>
          </Column>

          <Column field="sede_name" header="SEDE" sortable>
            <template #body="{ data }">
               <span class="text-[10px] font-black text-gray-400 uppercase tracking-widest bg-gray-50 px-2 py-1 rounded border border-gray-100 italic">
                 <i class="pi pi-map-marker text-[9px] mr-1 text-blue-400"></i>{{ data.sede_name || 'Sin Sede' }}
               </span>
            </template>
          </Column>

          <Column field="admission_status" header="ESTADO" sortable>
            <template #body="{ data }">
               <StatusBadge :status="data.admission_status" type="constancia" />
            </template>
          </Column>

          <Column header="ACCIONES" alignFrozen="right">
            <template #body="{ data }">
              <div class="flex justify-end">
                <button @click="openDetails(data)" class="px-4 py-1.5 bg-blue-50 text-[10px] font-black text-blue-600 uppercase tracking-widest border border-blue-100 rounded-lg hover:bg-blue-600 hover:text-white transition-all">
                  Gestionar
                </button>
              </div>
            </template>
          </Column>
        </DataTable>
      </div>

      <!-- Detail Modal -->
      <Teleport to="body">
        <div v-if="selectedAspirant" class="fixed inset-0 bg-gray-900/80 backdrop-blur-xl z-[100] flex items-center justify-center p-4">
          <div class="bg-white rounded-[48px] w-full max-w-5xl h-[90vh] shadow-2xl overflow-hidden flex animate-fade-in border border-white/20">
            <!-- Left: Info & Actions -->
            <div class="w-[450px] border-r border-gray-100 flex flex-col bg-[#FDFDFD]">
               <div class="p-10 border-b border-gray-50">
                  <div class="text-[10px] font-black text-blue-600 uppercase tracking-widest mb-2 italic">Perfil del Aspirante • {{ selectedAspirant.code }}</div>
                  <h2 class="text-3xl font-black text-gray-900 mb-1 leading-tight">{{ selectedAspirant.full_name }}</h2>
                  <div class="flex items-center gap-2 text-xs font-bold text-gray-400">
                     <IdentificationIcon class="w-4 h-4" /> {{ selectedAspirant.national_id }}
                     <span class="text-gray-200">|</span>
                     <MapPinIcon class="w-4 h-4 ml-1" /> {{ selectedAspirant.sede_name }}
                  </div>
               </div>

               <div class="flex-1 overflow-y-auto p-10 space-y-8 custom-scrollbar">
                  <section>
                    <h3 class="text-[10px] font-black text-gray-400 uppercase mb-4 tracking-widest">Estado del Proceso</h3>
                    <div class="p-6 rounded-3xl border border-gray-100 bg-white shadow-sm space-y-4">
                       <div class="flex items-center justify-between border-b border-gray-50 pb-4">
                          <span class="text-xs font-bold text-gray-500 italic">Estado Actual:</span>
                          <StatusBadge :status="selectedAspirant.admission_status" />
                       </div>
                       
                       <!-- Opciones de Carrera -->
                       <div class="py-2">
                          <label class="block text-[10px] font-black uppercase text-gray-400 mb-2 italic">Opciones seleccionadas por aspirante</label>
                          <ul class="space-y-2 text-xs font-medium text-gray-600">
                            <li><span class="font-bold text-[var(--upel-blue)]">Opción 1:</span> {{ selectedAspirant.career_name || 'No especificada' }}</li>
                            <li v-if="selectedAspirant.career_name_2"><span class="font-bold text-gray-500">Opción 2:</span> {{ selectedAspirant.career_name_2 }}</li>
                            <li v-if="selectedAspirant.career_name_3"><span class="font-bold text-gray-500">Opción 3:</span> {{ selectedAspirant.career_name_3 }}</li>
                          </ul>
                       </div>

                       <div class="border-t border-gray-50 pt-4">
                          <label class="block text-[10px] font-black uppercase text-gray-400 mb-2 italic">Observaciones del Comité</label>
                          <textarea 
                            v-model="adminForm.admission_notes" 
                            class="w-full bg-gray-50 border-0 rounded-2xl p-4 text-xs font-bold text-gray-700 focus:ring-2 focus:ring-blue-100 outline-none transition-all"
                            rows="3"
                            placeholder="Añada notas sobre la revisión de documentos o motivos..."
                          ></textarea>
                       </div>
                    </div>
                  </section>

                  <section>
                    <h3 class="text-[10px] font-black text-gray-400 uppercase mb-4 tracking-widest">Decisión de Admisión</h3>
                    <div class="space-y-6">
                       
                       <div class="bg-blue-50/30 p-5 rounded-3xl border border-blue-100 shadow-sm relative overflow-hidden">
                          <div class="absolute -right-4 -top-4 opacity-10">
                             <AcademicCapIcon class="w-16 h-16 text-blue-600" />
                          </div>
                          <label class="block text-[9px] font-black uppercase text-blue-500 mb-4 italic tracking-widest">Asignar Especialidad UPEL</label>
                          
                          <div class="space-y-4">
                            <!-- Radio Choice from 3 Options -->
                            <div class="space-y-2">
                               <div 
                                 v-for="i in [1, 2, 3]" 
                                 :key="i"
                                 @click="adminForm.admitted_career_id = selectedAspirant[`career_id${i>1?`_${i}`:''}`]"
                                 v-if="selectedAspirant[`career_name${i>1?`_${i}`:''}`]"
                                 class="p-4 rounded-2xl border cursor-pointer transition-all flex items-center justify-between group"
                                 :class="adminForm.admitted_career_id === selectedAspirant[`career_id${i>1?`_${i}`:''}`] 
                                    ? 'bg-blue-600 border-blue-600 shadow-lg shadow-blue-500/20' 
                                    : 'bg-white border-gray-100 hover:border-blue-200'"
                               >
                                  <div class="flex items-center gap-3">
                                     <div class="h-6 w-6 rounded-lg flex items-center justify-center text-[10px] font-black italic" :class="adminForm.admitted_career_id === selectedAspirant[`career_id${i>1?`_${i}`:''}`] ? 'bg-white/20 text-white' : 'bg-gray-50 text-gray-400'">{{ i }}</div>
                                     <div class="text-[10px] font-black uppercase tracking-tighter italic" :class="adminForm.admitted_career_id === selectedAspirant[`career_id${i>1?`_${i}`:''}`] ? 'text-white' : 'text-gray-700'">{{ selectedAspirant[`career_name${i>1?`_${i}`:''}`] }}</div>
                                  </div>
                                  <div v-if="adminForm.admitted_career_id === selectedAspirant[`career_id${i>1?`_${i}`:''}`]" class="h-5 w-5 bg-white/20 rounded-full flex items-center justify-center">
                                     <i class="pi pi-check text-[10px] text-white"></i>
                                  </div>
                               </div>
                            </div>

                            <div class="h-px bg-blue-100/50 my-4"></div>

                            <!-- Alternative Specialty -->
                            <div>
                               <label class="block text-[8px] font-black uppercase text-blue-400 mb-2 italic">Opción Alternativa (Decisión Institucional)</label>
                               <select 
                                 v-model="adminForm.admitted_career_id" 
                                 class="w-full bg-white border border-gray-200 rounded-xl px-4 py-3 text-xs font-black text-gray-700 outline-none transition-all focus:ring-4 focus:ring-blue-500/10 italic truncate"
                               >
                                 <option value="">-- Buscar otra especialidad --</option>
                                 <option v-for="c in careers" :key="c.id" :value="c.id">{{ c.name }}</option>
                               </select>
                            </div>
                          </div>
                       </div>

                       <div class="grid grid-cols-2 gap-3 pt-2">
                          <button @click="processStatus('approved')" :disabled="processing || !adminForm.admitted_career_id" class="py-4 bg-[var(--upel-blue)] text-white rounded-[24px] text-[11px] font-black shadow-xl shadow-blue-500/20 hover:scale-[1.03] active:scale-95 transition-all flex justify-center items-center gap-2 uppercase tracking-widest">
                             <span v-if="processing" class="w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                             Confirmar Admisión
                          </button>
                          <button @click="processStatus('rejected')" :disabled="processing" class="py-4 bg-red-50 text-red-500 rounded-[24px] text-[11px] font-black border border-red-100 hover:bg-red-500 hover:text-white transition-all flex justify-center items-center uppercase tracking-widest">
                             Rechazar Cupo
                          </button>
                       </div>
                       
                       <button @click="processStatus('in_review')" :disabled="processing" class="w-full py-3 bg-gray-50 text-gray-400 rounded-2xl text-[10px] font-black border border-transparent hover:border-gray-200 transition-all flex items-center justify-center gap-2 uppercase tracking-widest">
                         Mover a Revisión Manual
                       </button>
                    </div>
                  </section>
               </div>
               
               <div class="p-6 border-t border-gray-50 flex justify-center">
                  <button @click="selectedAspirant = null" class="text-[10px] font-black text-gray-400 hover:text-gray-900 uppercase underline decoration-2 underline-offset-4 tracking-widest">Cerrar Ventana</button>
               </div>
            </div>

            <!-- Right: Documents Grid -->
            <div class="flex-1 bg-gray-50/50 p-10 flex flex-col">
               <div class="flex justify-between items-center mb-10">
                  <h3 class="text-xl font-black text-gray-900 italic">Expediente Digital</h3>
                  <div class="flex items-center gap-2">
                     <span class="text-[10px] font-black text-gray-400 uppercase">{{ selectedAspirant.documents?.length || 0 }} Archivos</span>
                  </div>
               </div>

               <div v-if="selectedAspirant.documents?.length > 0" class="grid grid-cols-2 gap-6 overflow-y-auto pr-4 custom-scrollbar">
                  <div v-for="doc in selectedAspirant.documents" :key="doc.id" class="group relative bg-white rounded-3xl p-6 shadow-sm border border-gray-100 hover:shadow-xl hover:scale-[1.02] transition-all cursor-pointer overflow-hidden" @click="openPreview(doc)">
                     <div class="flex justify-between items-start mb-4">
                        <div class="h-12 w-12 rounded-2xl bg-gray-50 flex items-center justify-center font-black text-blue-600 transition-colors group-hover:bg-blue-600 group-hover:text-white">
                           <DocumentIcon v-if="!isImage(doc.file)" class="w-6 h-6" />
                           <img v-else :src="doc.file" class="h-full w-full object-cover rounded-2xl border-2 border-white shadow-sm" />
                        </div>
                        <span class="text-[9px] font-black bg-blue-50 text-blue-500 px-2 py-0.5 rounded-lg border border-blue-100 uppercase italic">{{ doc.doc_type_display }}</span>
                     </div>
                     <h4 class="text-xs font-black text-gray-800 mb-1 truncate">{{ doc.original_filename }}</h4>
                     <p class="text-[9px] text-gray-400 font-bold uppercase">{{ doc.file_size_display }} • {{ formatDate(doc.uploaded_at) }}</p>
                     
                     <!-- Hover Overlay -->
                     <div class="absolute inset-0 bg-[var(--upel-blue)]/90 opacity-0 group-hover:opacity-100 transition-all flex items-center justify-center backdrop-blur-sm -translate-y-4 group-hover:translate-y-0">
                        <span class="text-white text-[10px] font-black uppercase tracking-widest border border-white/30 px-4 py-2 rounded-xl">Ampliar Documento</span>
                     </div>
                  </div>
               </div>
               
               <div v-else class="flex-1 flex flex-col items-center justify-center">
                  <div class="h-24 w-24 bg-white rounded-full flex items-center justify-center shadow-lg border border-gray-50 mb-6 group animate-pulse">
                     <DocumentIcon class="w-10 h-10 text-gray-200" />
                  </div>
                  <p class="text-gray-400 font-black italic uppercase tracking-tighter text-sm">Aspirante sin documentos cargados</p>
               </div>
            </div>
          </div>
        </div>
      </Teleport>

      <!-- Preview Modal -->
      <Teleport to="body">
        <div v-if="previewDoc" class="fixed inset-0 bg-black/95 z-[200] flex flex-col items-center justify-center p-8">
           <div class="absolute top-10 right-10 flex gap-4">
              <a :href="previewDoc.file" target="_blank" class="bg-white/10 hover:bg-white/20 text-white p-4 rounded-3xl transition-all backdrop-blur-md border border-white/10 shadow-lg">
                <ArrowDownTrayIcon class="w-6 h-6" />
              </a>
              <button @click="previewDoc = null" class="bg-white/10 hover:bg-white/20 text-white p-4 rounded-3xl transition-all backdrop-blur-md border border-white/10 shadow-lg font-black text-xl leading-none">
                &times;
              </button>
           </div>
           
           <div class="w-full h-full flex items-center justify-center overflow-auto custom-scrollbar">
              <img v-if="isImage(previewDoc.file)" :src="previewDoc.file" class="max-w-full max-h-full object-contain shadow-2xl rounded-lg" />
              <embed v-else :src="previewDoc.file" type="application/pdf" class="w-full h-full max-w-4xl bg-white rounded-3xl" />
           </div>
           
           <div class="mt-8 text-center text-white/50 space-y-2">
              <div class="text-sm font-black italic">{{ previewDoc.original_filename }}</div>
              <div class="text-[10px] items-center flex gap-4 justify-center font-bold">
                 <span>TIPO: {{ previewDoc.doc_type_display }}</span>
                 <span class="h-1 w-1 bg-white/20 rounded-full"></span>
                 <span>TAMAÑO: {{ previewDoc.file_size_display }}</span>
              </div>
           </div>
        </div>
      </Teleport>

    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import AdminSidebar from '@/components/AdminSidebar.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import 'primeicons/primeicons.css'
import {
  MagnifyingGlassIcon,
  ArrowPathIcon,
  IdentificationIcon,
  MapPinIcon,
  DocumentIcon,
  ArrowDownTrayIcon
} from '@heroicons/vue/24/outline'

const authStore = useAuthStore()
const aspirants = ref([])
const careers = ref([])
const loading = ref(false)
const processing = ref(false)
const search = ref('')
const filterStatus = ref('')
const filterSede = ref('')
const selectedAspirant = ref(null)
const previewDoc = ref(null)

const adminForm = reactive({
  admission_status: '',
  admission_notes: '',
  admitted_career_id: null,
  admitted_career_name: '',
  admitted_option: null
})

const fetchAspirants = async () => {
  loading.value = true
  try {
    const [aspRes, carRes] = await Promise.all([
      axios.get('/api/aspirants/', {
        headers: { Authorization: `Bearer ${authStore.token}` }
      }),
      axios.get('/api/students/careers/', {
        headers: { Authorization: `Bearer ${authStore.token}` }
      })
    ])
    aspirants.value = aspRes.data.results || aspRes.data
    careers.value = carRes.data.results || carRes.data
  } catch (err) {
    console.error('Fetch error:', err)
  } finally {
    loading.value = false
  }
}

const uniqueSedes = computed(() => {
   const sedes = aspirants.value.map(a => a.sede_name).filter(s => s)
   return [...new Set(sedes)].sort()
})

const filteredAspirants = computed(() => {
  let res = aspirants.value
  
  if (search.value) {
    const q = search.value.toLowerCase()
    res = res.filter(a => 
      a.full_name?.toLowerCase().includes(q) ||
      a.national_id?.toLowerCase().includes(q) ||
      a.code?.toLowerCase().includes(q) ||
      a.email?.toLowerCase().includes(q)
    )
  }
  
  if (filterStatus.value) {
    res = res.filter(a => a.admission_status === filterStatus.value)
  }
  
  if (filterSede.value) {
    res = res.filter(a => a.sede_name === filterSede.value)
  }
  
  return res
})

const filterByStatus = (status) => aspirants.value.filter(a => a.admission_status === status)

const openDetails = (asp) => {
  selectedAspirant.value = asp
  adminForm.admission_status = asp.admission_status
  adminForm.admission_notes = asp.admission_notes || ''
  adminForm.admitted_career_id = asp.admitted_career_id || asp.career_id || ''
  adminForm.admitted_career_name = asp.admitted_career_name || asp.career_name || ''
  adminForm.admitted_option = asp.admitted_option || 1
}

const processStatus = async (status) => {
  if (!selectedAspirant.value) return
  processing.value = true
  adminForm.admission_status = status
  
  if (adminForm.admitted_career_id) {
     const selectedCareer = careers.value.find(c => c.id === adminForm.admitted_career_id)
     if (selectedCareer) {
        adminForm.admitted_career_name = selectedCareer.name
        
        if (adminForm.admitted_career_id === selectedAspirant.value.career_id) adminForm.admitted_option = 1
        else if (adminForm.admitted_career_id === selectedAspirant.value.career_id_2) adminForm.admitted_option = 2
        else if (adminForm.admitted_career_id === selectedAspirant.value.career_id_3) adminForm.admitted_option = 3
        else adminForm.admitted_option = 4 // Carrera alternativa elegida por secretaria
     }
  }
  
  try {
    const res = await axios.patch(`/api/aspirants/${selectedAspirant.value.code}/`, adminForm, {
      headers: { Authorization: `Bearer ${authStore.token}` }
    })
    Object.assign(selectedAspirant.value, res.data)
    await fetchAspirants() // Refresh total list
    alert(`Aspirante marcado como ${status === 'approved' ? 'ADMITIDO' : status === 'rejected' ? 'RECHAZADO' : 'EN REVISIÓN'}.`)
  } catch (err) {
    console.error('Update status error:', err)
    alert(err.response?.data?.detail || 'Error al actualizar el estado.')
  } finally {
    processing.value = false
  }
}

const openPreview = (doc) => {
  previewDoc.value = doc
}

const isImage = (url) => {
  const ext = url.split('.').pop().toLowerCase()
  return ['jpg', 'jpeg', 'png', 'webp', 'gif'].includes(ext)
}

const formatDate = (date) => {
  if (!date) return '—'
  return new Date(date).toLocaleDateString('es-VE', { 
    day: '2-digit', 
    month: 'short', 
    year: 'numeric'
  })
}

onMounted(fetchAspirants)
</script>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes fadeIn {
  from { opacity: 0; transform: scale(0.98) translateY(10px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
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

:root {
  --upel-blue: #004A99;
}
</style>
