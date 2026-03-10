<template>
  <div class="min-h-screen bg-[#F8FAFC] flex text-gray-900">
    <AdminSidebar />
    <main class="flex-1 p-8 overflow-y-auto">
      <header class="mb-10">
        <h1 class="text-3xl font-black text-gray-900 tracking-tight">Configuración Global</h1>
        <p class="text-gray-500 font-medium">Personalización de marca, identidad institucional y parámetros del sistema.</p>
      </header>

      <div v-if="loading" class="flex flex-col items-center justify-center p-20 bg-white rounded-[40px] border border-gray-100 shadow-sm">
         <ArrowPathIcon class="w-12 h-12 text-blue-100 animate-spin mb-4" />
         <p class="text-gray-300 font-black uppercase tracking-widest text-sm italic">Cargando preferencias...</p>
      </div>

      <div v-else class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Identity Form -->
        <div class="lg:col-span-2 space-y-8">
          <section class="bg-white rounded-[40px] p-10 border border-gray-100 shadow-sm">
             <div class="flex items-center gap-3 mb-8">
                <div class="h-10 w-10 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center">
                   <IdentificationIcon class="w-6 h-6" />
                </div>
                <h2 class="text-xl font-black text-gray-900 italic uppercase tracking-tight">Identidad del Sistema</h2>
             </div>

             <div class="grid grid-cols-1 gap-6">
                <div class="space-y-2">
                   <label class="text-[10px] font-black uppercase text-gray-400 tracking-widest ml-1 italic text-blue-600">Nombre de la Plataforma</label>
                   <input v-model="form.system_name" type="text" class="w-full bg-gray-50 border-0 rounded-2xl px-6 py-4 text-sm font-bold text-gray-800 focus:ring-4 focus:ring-blue-500/5 outline-none transition-all" placeholder="Ej: Portal Académico BaseP" />
                </div>
                <div class="space-y-2">
                   <label class="text-[10px] font-black uppercase text-gray-400 tracking-widest ml-1 italic">Institución / Universidad</label>
                   <input v-model="form.university_name" type="text" class="w-full bg-gray-50 border-0 rounded-2xl px-6 py-4 text-sm font-bold text-gray-800 focus:ring-4 focus:ring-blue-500/5 outline-none transition-all" placeholder="Ej: Universidad Pedagógica Experimental Libertador" />
                </div>
             </div>
          </section>

          <section class="bg-white rounded-[40px] p-10 border border-gray-100 shadow-sm">
             <div class="flex items-center gap-3 mb-8">
                <div class="h-10 w-10 rounded-2xl bg-purple-50 text-purple-600 flex items-center justify-center">
                   <SwatchIcon class="w-6 h-6" />
                </div>
                <h2 class="text-xl font-black text-gray-900 italic uppercase tracking-tight">Paleta de Colores</h2>
             </div>

             <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div class="p-6 rounded-3xl border border-gray-50 bg-gray-50/30">
                   <label class="text-[10px] font-black uppercase text-gray-400 tracking-widest block mb-4 italic">Color Primario (Branding)</label>
                   <div class="flex items-center gap-4">
                      <input v-model="form.primary_color" type="color" class="h-14 w-14 rounded-xl border-0 cursor-pointer p-0 bg-transparent overflow-hidden shadow-lg" />
                      <input v-model="form.primary_color" type="text" class="flex-1 bg-white border-0 rounded-xl px-4 py-3 text-xs font-mono font-bold text-gray-600 focus:ring-2 focus:ring-blue-100 outline-none" />
                   </div>
                </div>
                <div class="p-6 rounded-3xl border border-gray-50 bg-gray-50/30">
                   <label class="text-[10px] font-black uppercase text-gray-400 tracking-widest block mb-4 italic">Color Secundario (Acentos)</label>
                   <div class="flex items-center gap-4">
                      <input v-model="form.secondary_color" type="color" class="h-14 w-14 rounded-xl border-0 cursor-pointer p-0 bg-transparent overflow-hidden shadow-lg" />
                      <input v-model="form.secondary_color" type="text" class="flex-1 bg-white border-0 rounded-xl px-4 py-3 text-xs font-mono font-bold text-gray-600 focus:ring-2 focus:ring-purple-100 outline-none" />
                   </div>
                </div>
             </div>
          </section>
        </div>

        <!-- Visual Preview & Logo -->
        <div class="space-y-8">
          <section class="bg-white rounded-[40px] p-10 border border-gray-100 shadow-sm flex flex-col items-center text-center">
             <div class="h-10 w-10 rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center mb-6">
                <PhotoIcon class="w-6 h-6" />
             </div>
             <h2 class="text-xl font-black text-gray-900 italic uppercase tracking-tight mb-2">Logotipo</h2>
             <p class="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-8">Formatos PNG o SVG sugeridos</p>

             <div class="relative group cursor-pointer w-full" @click="$refs.logoInput.click()">
                <div class="aspect-square bg-gray-50 rounded-[32px] border-2 border-dashed border-gray-100 flex items-center justify-center overflow-hidden transition-all group-hover:bg-blue-50/30 group-hover:border-blue-200">
                   <img v-if="logoPreview || form.logo_url" :src="logoPreview || form.logo_url" class="max-w-[80%] max-h-[80%] object-contain scale-in" />
                   <div v-else class="text-gray-300 flex flex-col items-center gap-2">
                      <CloudArrowUpIcon class="w-10 h-10" />
                      <span class="text-[9px] font-black uppercase">Click para subir</span>
                   </div>
                   
                   <div class="absolute inset-0 bg-blue-600/0 group-hover:bg-blue-600/10 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all">
                      <div class="bg-white p-3 rounded-2xl shadow-xl">
                         <PencilIcon class="w-4 h-4 text-blue-600" />
                      </div>
                   </div>
                </div>
                <input ref="logoInput" type="file" hidden accept="image/*" @change="handleLogoChange" />
             </div>

             <div v-if="logoFile" class="mt-6 flex items-center gap-3 bg-emerald-50 p-4 rounded-2xl border border-emerald-100 w-full animate-bounce-subtle">
                <div class="h-2 w-2 rounded-full bg-emerald-500 animate-ping"></div>
                <span class="text-[10px] font-black text-emerald-700 uppercase">Nuevo Logo Listo</span>
                <button @click="logoFile = null; logoPreview = null" class="ml-auto text-emerald-400 hover:text-red-500 transition-colors">&times;</button>
             </div>
          </section>

          <!-- Action Sidebar -->
          <div class="bg-gray-900 rounded-[40px] p-10 shadow-2xl shadow-blue-900/10 text-white relative overflow-hidden">
             <!-- Background Accents -->
             <div class="absolute -top-20 -right-20 w-40 h-40 bg-blue-600/20 blur-[100px] rounded-full"></div>
             
             <div class="relative z-10 space-y-6">
                <h3 class="text-sm font-black italic uppercase tracking-widest text-blue-400">Terminal de Control</h3>
                <p class="text-xs text-gray-400 leading-relaxed font-medium">Los cambios en los colores y logotipos se reflejarán instantáneamente en todas las sesiones activas del portal.</p>
                
                <div class="space-y-3 pt-4">
                  <button 
                    @click="updateSettings" 
                    :disabled="saving"
                    class="w-full bg-blue-600 text-white py-5 rounded-[24px] text-xs font-black uppercase tracking-widest shadow-xl shadow-blue-900/20 hover:bg-blue-500 active:scale-95 transition-all flex items-center justify-center gap-3"
                  >
                    <ArrowPathIcon v-if="saving" class="w-4 h-4 animate-spin" />
                    {{ saving ? 'Sincronizando...' : 'Publicar Cambios' }}
                  </button>
                  <button @click="fetchSettings" :disabled="saving" class="w-full bg-white/5 border border-white/10 text-gray-400 py-5 rounded-[24px] text-xs font-black uppercase tracking-widest hover:bg-white/10 transition-all">
                    Reiniciar Vista
                  </button>
                </div>
             </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import axios from 'axios'
import AdminSidebar from '@/components/AdminSidebar.vue'
import {
  IdentificationIcon,
  SwatchIcon,
  PhotoIcon,
  CloudArrowUpIcon,
  PencilIcon,
  ArrowPathIcon
} from '@heroicons/vue/24/outline'

const loading = ref(true)
const saving = ref(false)
const logoPreview = ref(null)
const logoFile = ref(null)

const form = reactive({
  system_name: '',
  university_name: '',
  primary_color: '#0052cc',
  secondary_color: '#6554c0',
  logo_url: ''
})

const fetchSettings = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/settings/')
    Object.assign(form, res.data)
    logoPreview.value = null
    logoFile.value = null
    
    // Aplicar colores al root (opcional, para preview en tiempo real)
    document.documentElement.style.setProperty('--upel-blue', form.primary_color)
  } catch (err) {
    console.error('Fetch settings error:', err)
  } finally {
    loading.value = false
  }
}

const handleLogoChange = (e) => {
  const file = e.target.files[0]
  if (!file) return
  logoFile.value = file
  logoPreview.value = URL.createObjectURL(file)
}

const updateSettings = async () => {
  saving.value = true
  try {
    const formData = new FormData()
    formData.append('system_name', form.system_name)
    formData.append('university_name', form.university_name)
    formData.append('primary_color', form.primary_color)
    formData.append('secondary_color', form.secondary_color)
    
    if (logoFile.value) {
      formData.append('logo', logoFile.value)
    }

    const res = await axios.patch('/api/settings/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    
    // El backend devuelve los datos actualizados
    Object.assign(form, res.data)
    logoPreview.value = null
    logoFile.value = null
    
    // Forzar actualización de colores CSS base
    document.documentElement.style.setProperty('--upel-blue', form.primary_color)
    
    alert('Configuración actualizada con éxito. La identidad visual del sistema ha sido renovada.')
  } catch (err) {
    console.error('Update settings error:', err)
    alert('Error al guardar la configuración institucional.')
  } finally {
    saving.value = false
  }
}

onMounted(fetchSettings)
</script>

<style scoped>
.scale-in {
  animation: scaleIn 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes scaleIn {
  from { opacity: 0; transform: scale(0.9) translateY(10px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}

@keyframes bounce-subtle {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-3px); }
}

.animate-bounce-subtle {
  animation: bounce-subtle 2s infinite ease-in-out;
}
</style>
