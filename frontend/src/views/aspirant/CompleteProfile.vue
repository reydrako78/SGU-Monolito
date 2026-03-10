<template>
  <div class="min-h-screen bg-gray-50 flex flex-col font-sans">
    <!-- Header -->
    <header class="bg-white/80 backdrop-blur-md border-b border-gray-100 px-8 py-5 sticky top-0 z-50 flex justify-between items-center">
      <div class="flex items-center gap-3">
        <div class="h-10 w-10 bg-gradient-to-tr from-[var(--upel-blue)] to-blue-500 rounded-2xl flex items-center justify-center shadow-lg shadow-blue-900/10">
          <span class="text-white font-black text-xl">U</span>
        </div>
        <div>
          <span class="text-xl font-black text-gray-900 tracking-tighter">UPEL <span class="text-blue-600 font-light">Perfil</span></span>
        </div>
      </div>
      <div class="flex items-center gap-4">
        <button @click="router.push('/aspirant/dashboard')" class="text-sm font-bold text-gray-500 hover:text-gray-900 transition-colors">Volver</button>
      </div>
    </header>

    <main class="flex-1 max-w-6xl mx-auto w-full p-6 lg:p-12">
      <div class="mb-10 text-center">
        <h1 class="text-4xl font-black text-gray-900 mb-2">Completa tu Expediente</h1>
        <p class="text-gray-500 text-lg">Para continuar con tu proceso de admisión, necesitamos validar tu información y documentos.</p>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-4 gap-8">
        <!-- Navigation Tabs -->
        <aside class="lg:col-span-1 space-y-2">
          <button 
            v-for="section in sections" 
            :key="section.id"
            @click="activeSection = section.id"
            class="w-full text-left px-6 py-4 rounded-2xl transition-all group flex items-center justify-between"
            :class="activeSection === section.id ? 'bg-blue-600 text-white shadow-xl shadow-blue-900/10' : 'bg-white text-gray-400 hover:bg-white hover:text-gray-900 border border-transparent'"
          >
            <div class="flex items-center gap-3">
              <component :is="section.icon" class="w-5 h-5" />
              <span class="font-bold text-sm">{{ section.name }}</span>
            </div>
            <div v-if="section.completed" class="w-2 h-2 rounded-full bg-green-400"></div>
          </button>
        </aside>

        <!-- Content Area -->
        <div class="lg:col-span-3 space-y-6">
          <!-- Section: Personal Info -->
          <div v-if="activeSection === 'personal'" class="bg-white rounded-3xl p-8 border border-gray-100 shadow-sm space-y-8 animate-fade-in">
            <div>
              <h2 class="text-2xl font-black text-gray-900 mb-6 flex items-center gap-3">
                <UserIcon class="w-6 h-6 text-blue-600" />
                Datos Personales
              </h2>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="space-y-2">
                  <label class="text-[10px] font-black uppercase text-gray-400 tracking-[0.2em] ml-1">Cédula de Identidad</label>
                  <input 
                    v-model="form.national_id" 
                    type="text" 
                    placeholder="V-12345678"
                    :disabled="!!aspirant?.national_id"
                    class="w-full bg-gray-50 border-0 rounded-2xl px-5 py-4 focus:ring-2 focus:ring-blue-500 transition-all font-bold text-gray-800 disabled:opacity-50"
                  />
                </div>
                <div class="space-y-2">
                  <label class="text-[10px] font-black uppercase text-gray-400 tracking-[0.2em] ml-1">Teléfono</label>
                  <input v-model="form.phone" type="text" placeholder="04XX-XXXXXXX" class="w-full bg-gray-50 border-0 rounded-2xl px-5 py-4 focus:ring-2 focus:ring-blue-500 transition-all font-bold text-gray-800" />
                </div>
                <div class="space-y-2">
                  <label class="text-[10px] font-black uppercase text-gray-400 tracking-[0.2em] ml-1">Fecha de Nacimiento</label>
                  <input v-model="form.birth_date" type="date" class="w-full bg-gray-50 border-0 rounded-2xl px-5 py-4 focus:ring-2 focus:ring-blue-500 transition-all font-bold text-gray-800" />
                </div>
                <div class="space-y-2 md:col-span-2">
                  <label class="text-[10px] font-black uppercase text-gray-400 tracking-[0.2em] ml-1">Dirección de Habitación</label>
                  <textarea v-model="form.address" rows="3" class="w-full bg-gray-50 border-0 rounded-2xl px-5 py-4 focus:ring-2 focus:ring-blue-500 transition-all font-bold text-gray-800"></textarea>
                </div>
              </div>
            </div>
            
            <div class="flex justify-end pt-4">
              <button @click="savePersonalData" :disabled="saving" class="bg-gray-900 text-white px-8 py-4 rounded-2xl font-black text-sm hover:bg-black transition-all disabled:opacity-50">
                {{ saving ? 'Guardando...' : 'Guardar y Continuar' }}
              </button>
            </div>
          </div>

          <!-- Section: Careers -->
          <div v-if="activeSection === 'careers'" class="bg-white rounded-3xl p-8 border border-gray-100 shadow-sm space-y-8 animate-fade-in">
            <div>
              <h2 class="text-2xl font-black text-gray-900 mb-2 flex items-center gap-3">
                <AcademicCapIcon class="w-6 h-6 text-blue-600" />
                Elección de Carrera
              </h2>
              <p class="text-gray-500 text-sm mb-8">Selecciona tu sede preferida y hasta tres especialidades de tu interés.</p>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-10">
                <div class="space-y-2">
                  <label class="text-[10px] font-black uppercase text-gray-400 tracking-[0.2em] ml-1">Sede Universitaria</label>
                  <select v-model="form.sede" @change="fetchNucleos" class="w-full bg-gray-50 border-0 rounded-2xl px-5 py-4 focus:ring-2 focus:ring-blue-500 transition-all font-bold text-gray-800 appearance-none">
                    <option value="">Seleccione Sede</option>
                    <option v-for="s in sedes" :key="s.id" :value="s.id">{{ s.name }}</option>
                  </select>
                </div>
                <div class="space-y-2">
                  <label class="text-[10px] font-black uppercase text-gray-400 tracking-[0.2em] ml-1">Núcleo / Campus</label>
                  <select v-model="form.nucleo" class="w-full bg-gray-50 border-0 rounded-2xl px-5 py-4 focus:ring-2 focus:ring-blue-500 transition-all font-bold text-gray-800 appearance-none">
                    <option value="">Seleccione Núcleo</option>
                    <option v-for="n in nucleos" :key="n.id" :value="n.id">{{ n.name }}</option>
                  </select>
                </div>
              </div>

              <div class="space-y-6">
                 <div v-for="i in [1, 2, 3]" :key="i" class="p-6 bg-gray-50 rounded-3xl border border-transparent hover:border-blue-100 transition-all">
                    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
                       <div class="flex items-center gap-4">
                         <div class="h-10 w-10 rounded-xl bg-white flex items-center justify-center font-black text-blue-600 shadow-sm border border-gray-100">{{ i }}</div>
                         <div>
                           <div class="text-[10px] font-black uppercase text-gray-400 tracking-[0.2em]">Carrera / Especialidad Option {{ i }}</div>
                           <h4 class="font-bold text-gray-900">{{ getCareerName(form[`career_id${i === 1 ? '' : '_' + i}`]) || 'No seleccionada' }}</h4>
                         </div>
                       </div>
                       <div class="md:w-64">
                         <select v-model="form[`career_id${i === 1 ? '' : '_' + i}`]" class="w-full bg-white border-0 rounded-xl px-4 py-2 font-bold text-xs shadow-sm focus:ring-2 focus:ring-blue-500">
                           <option value="">Cambiar Carrera...</option>
                           <option v-for="c in careers" :key="c.id" :value="c.id">{{ c.name }}</option>
                         </select>
                       </div>
                    </div>
                 </div>
              </div>
            </div>

            <div class="flex justify-end pt-4">
              <button @click="saveCareerData" :disabled="saving" class="bg-gray-900 text-white px-8 py-4 rounded-2xl font-black text-sm hover:bg-black transition-all disabled:opacity-50">
                {{ saving ? 'Guardando...' : 'Finalizar Selección' }}
              </button>
            </div>
          </div>

          <!-- Section: Documents -->
          <div v-if="activeSection === 'documents'" class="bg-white rounded-3xl p-8 border border-gray-100 shadow-sm space-y-8 animate-fade-in">
            <div>
              <h2 class="text-2xl font-black text-gray-900 mb-2 flex items-center gap-3">
                <DocumentIcon class="w-6 h-6 text-blue-600" />
                Expediente Digital
              </h2>
              <p class="text-gray-500 text-sm mb-8">Sube escaneos claros de tus documentos obligatorios (PDF, JPG, PNG).</p>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div v-for="docType in documentTypes" :key="docType.id" class="relative group">
                   <div class="p-6 bg-gray-50 rounded-3xl border border-dashed border-gray-200 transition-all" :class="uploadedDocuments[docType.id] ? 'bg-green-50/50 border-green-200' : 'hover:border-blue-300 hover:bg-blue-50/20'">
                      <div class="flex justify-between items-start mb-4">
                        <div class="h-12 w-12 rounded-2xl bg-white flex items-center justify-center shadow-sm border border-gray-100">
                          <component :is="uploadedDocuments[docType.id] ? CheckCircleIcon : DocumentIcon" :class="uploadedDocuments[docType.id] ? 'text-green-500' : 'text-gray-400'" class="w-6 h-6" />
                        </div>
                        <input type="file" :id="`file-${docType.id}`" class="hidden" @change="uploadDocument($event, docType.id)" />
                        <label :for="`file-${docType.id}`" class="cursor-pointer bg-white px-4 py-2 rounded-xl shadow-sm text-[10px] font-black uppercase tracking-widest text-gray-600 hover:bg-gray-50 transition-all border border-gray-100">
                          {{ uploadedDocuments[docType.id] ? 'Reemplazar' : 'Subir' }}
                        </label>
                      </div>
                      <h4 class="font-bold text-gray-900 mb-1">{{ docType.name }}</h4>
                      <p class="text-[10px] text-gray-400 leading-relaxed">{{ docType.description }}</p>
                      
                      <div v-if="uploadStatus[docType.id]" class="mt-4 h-1 bg-gray-200 rounded-full overflow-hidden">
                        <div class="h-full bg-blue-600 transition-all" :style="{ width: uploadStatus[docType.id] + '%' }"></div>
                      </div>
                   </div>
                </div>
              </div>
            </div>

            <div class="bg-blue-900 rounded-3xl p-8 text-white flex flex-col md:flex-row items-center gap-6 justify-between shadow-xl shadow-blue-900/20">
              <div class="flex gap-4 items-center">
                <div class="h-12 w-12 rounded-2xl bg-white/10 flex items-center justify-center">
                  <InformationCircleIcon class="w-6 h-6" />
                </div>
                <div>
                  <h4 class="font-bold">¿Listo para revisión?</h4>
                  <p class="text-white/60 text-xs">Una vez subas todos los documentos obligatorios, el comité será notificado.</p>
                </div>
              </div>
              <button 
                v-if="aspirant?.admission_status === 'pending'"
                @click="finishProfile" 
                :disabled="!canSubmit || saving"
                class="bg-white text-blue-900 px-8 py-3 rounded-xl font-black text-xs hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {{ saving ? 'Procesando...' : 'Finalizar y Enviar a Revisión' }}
              </button>
              <div v-else class="text-white font-bold text-sm bg-green-500/20 px-4 py-2 rounded-lg border border-green-500/30">
                 Expediente enviado a revisión
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Success Toast -->
    <Teleport to="body">
      <div v-if="toast" class="fixed bottom-10 right-10 bg-gray-900 text-white px-8 py-4 rounded-2xl shadow-2xl flex items-center gap-4 animate-slide-up z-[100]">
        <CheckCircleIcon class="w-6 h-6 text-green-400" />
        <span class="font-bold text-sm">{{ toast.message }}</span>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'
import { 
  UserIcon, 
  AcademicCapIcon, 
  DocumentIcon, 
  InformationCircleIcon,
  CheckCircleIcon,
  CloudArrowUpIcon
} from '@heroicons/vue/24/outline'

const router = useRouter()
const authStore = useAuthStore()

const activeSection = ref('personal')
const saving = ref(false)
const aspirant = ref(null)
const sedes = ref([])
const nucleos = ref([])
const careers = ref([])
const toast = ref(null)

const form = reactive({
  national_id: '',
  phone: '',
  birth_date: '',
  address: '',
  sede: '',
  nucleo: '',
  career_id: '',
  career_id_2: '',
  career_id_3: '',
  admission_type: 'general'
})

const sections = computed(() => [
  { id: 'personal', name: 'Información Personal', icon: UserIcon, completed: !!aspirant.value?.national_id },
  { id: 'careers', name: 'Selección de Carrera', icon: AcademicCapIcon, completed: !!aspirant.value?.career_id },
  { id: 'documents', name: 'Expediente Digital', icon: DocumentIcon, completed: (aspirant.value?.documents?.length || 0) > 0 }
])

const documentTypes = [
  { id: 'cedula', name: 'Cédula de Identidad', description: 'Copia legible y vigente.' },
  { id: 'titulo', name: 'Título Universitario / Bachiller', description: 'Título que acredita el grado anterior.' },
  { id: 'notas_cert', name: 'Notas Certificadas', description: 'Récord académico completo de la institución de origen.' },
  { id: 'otro', name: 'Certificado RUSNIES / OPSU', description: 'Comprobante de registro nacional de ingresos.' },
]

const uploadedDocuments = ref({})
const uploadStatus = ref({})

const canSubmit = computed(() => {
  // Al menos 3 documentos básicos (cedula, titulo, notas) y datos personales
  return Object.keys(uploadedDocuments.value).length >= 3 && 
         form.national_id && 
         form.sede && 
         form.career_id
})

const showToast = (message) => {
  toast.value = { message }
  setTimeout(() => toast.value = null, 3000)
}

const fetchInitialData = async () => {
  try {
    const [aspRes, sedRes, carRes] = await Promise.all([
      axios.get('/api/aspirants/'),
      axios.get('/api/sedes/'),
      axios.get('/api/careers/')
    ])
    
    const data = aspRes.data.results ? aspRes.data.results[0] : aspRes.data
    aspirant.value = data
    
    // Fill form
    form.national_id = data.national_id || ''
    form.phone = data.phone || ''
    form.birth_date = data.birth_date || ''
    form.address = data.address || ''
    form.sede = data.sede || ''
    form.nucleo = data.nucleo || ''
    form.career_id = data.career_id || ''
    form.career_id_2 = data.career_id_2 || ''
    form.career_id_3 = data.career_id_3 || ''
    form.admission_type = data.admission_type || 'general'
    
    sedes.value = sedRes.data
    careers.value = carRes.data.results || carRes.data
    
    // Map uploaded docs
    if (data.documents) {
      data.documents.forEach(d => {
        uploadedDocuments.value[d.doc_type] = d
      })
    }
    
    if (form.sede) fetchNucleos()
  } catch (err) {
    console.error('Error fetching data:', err)
  }
}

const fetchNucleos = async () => {
  if (!form.sede) return
  try {
    const res = await axios.get(`/api/nucleos/?sede_id=${form.sede}`)
    nucleos.value = res.data
  } catch (err) {
    console.error('Error fetching nucleos:', err)
  }
}

const getCareerName = (id) => {
  const c = careers.value.find(x => x.id == id)
  return c ? c.name : ''
}

const savePersonalData = async () => {
  if (!aspirant.value) return
  saving.value = true
  try {
    const res = await axios.patch(`/api/aspirants/${aspirant.value.code}/`, {
      national_id: form.national_id,
      phone: form.phone,
      birth_date: form.birth_date,
      address: form.address
    })
    aspirant.value = res.data
    showToast('Datos personales guardados.')
    activeSection.value = 'careers'
  } catch (err) {
    console.error('Error saving personal data:', err)
  } finally {
    saving.value = false
  }
}

const saveCareerData = async () => {
  if (!aspirant.value) return
  saving.value = true
  try {
    // Buscamos nombres de carreras seleccionadas para enviar
    const career_name = getCareerName(form.career_id)
    const career_name_2 = getCareerName(form.career_id_2)
    const career_name_3 = getCareerName(form.career_id_3)

    const res = await axios.patch(`/api/aspirants/${aspirant.value.code}/`, {
      sede: form.sede,
      nucleo: form.nucleo,
      career_id: form.career_id,
      career_name: career_name,
      career_id_2: form.career_id_2,
      career_name_2: career_name_2,
      career_id_3: form.career_id_3,
      career_name_3: career_name_3,
      admission_type: form.admission_type
    })
    aspirant.value = res.data
    showToast('Preferencias académicas actualizadas.')
    activeSection.value = 'documents'
  } catch (err) {
    console.error('Error saving career data:', err)
  } finally {
    saving.value = false
  }
}

const uploadDocument = async (event, type) => {
  const file = event.target.files[0]
  if (!file || !aspirant.value) return
  
  const formData = new FormData()
  formData.append('file', file)
  formData.append('doc_type', type)
  formData.append('notes', `Carga desde portal web: ${file.name}`)
  
  uploadStatus.value[type] = 10
  
  try {
    const res = await axios.post(`/api/aspirants/${aspirant.value.code}/documents/upload/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (p) => {
        uploadStatus.value[type] = Math.round((p.loaded * 100) / p.total)
      }
    })
    uploadedDocuments.value[type] = res.data
    showToast(`Documento "${type}" cargado con éxito.`)
    
    // Refresh aspirant for document list
    const aspRes = await axios.get('/api/aspirants/')
    const data = aspRes.data.results ? aspRes.data.results[0] : aspRes.data
    aspirant.value = data
  } catch (err) {
    console.error('Error uploading document:', err)
    showToast('Error al subir el archivo.')
  } finally {
    setTimeout(() => delete uploadStatus.value[type], 2000)
  }
}

const finishProfile = async () => {
  if (!canSubmit.value) return
  saving.value = true
  try {
    await axios.post(`/api/aspirants/${aspirant.value.code}/submit/`)
    showToast('¡Expediente enviado formalmente para revisión!')
    setTimeout(() => {
      router.push('/aspirant/dashboard')
    }, 2000)
  } catch (err) {
    console.error('Submit error:', err)
    showToast('Error al enviar el expediente', 'error')
  } finally {
    saving.value = false
  }
}

onMounted(fetchInitialData)
</script>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes slideUp {
  from { transform: translateY(100%); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.animate-slide-up {
  animation: slideUp 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

.transition-all {
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}
</style>
