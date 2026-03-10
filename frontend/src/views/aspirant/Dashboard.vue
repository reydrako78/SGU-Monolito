<template>
  <div class="min-h-screen bg-gray-50 flex flex-col font-sans">
    <!-- Sophisticated Header -->
    <header class="bg-white/80 backdrop-blur-md border-b border-gray-100 px-8 py-5 sticky top-0 z-50 flex justify-between items-center">
      <div class="flex items-center gap-3">
        <div class="h-10 w-10 bg-gradient-to-tr from-[var(--upel-blue)] to-blue-500 rounded-2xl flex items-center justify-center shadow-lg shadow-blue-900/10">
          <span class="text-white font-black text-xl">U</span>
        </div>
        <div>
          <span class="text-xl font-black text-gray-900 tracking-tighter">UPEL <span class="text-blue-600 font-light">Admisiones</span></span>
        </div>
      </div>
      <div class="flex items-center gap-6">
        <div class="hidden md:block text-right">
          <div class="text-sm font-bold text-gray-800">{{ authStore.fullName }}</div>
          <div class="text-[10px] text-gray-400 uppercase font-black tracking-widest">Portal del Aspirante</div>
        </div>
        <button @click="logout" class="p-2 hover:bg-red-50 text-gray-400 hover:text-red-500 rounded-xl transition-all">
          <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" /></svg>
        </button>
      </div>
    </header>

    <main class="flex-1 max-w-5xl mx-auto w-full p-6 lg:p-12">
      <!-- Welcome & Overall Status -->
      <section class="mb-12 flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <h1 class="text-4xl font-black text-gray-900 mb-2">Hola, {{ authStore.firstName }}</h1>
          <p class="text-gray-500 text-lg">Estamos revisando tu solicitud para el período 2026-I.</p>
        </div>
        <button 
          @click="router.push('/aspirant/profile')"
          class="bg-blue-600 text-white px-8 py-4 rounded-2xl font-black text-sm hover:bg-blue-700 shadow-xl shadow-blue-900/10 transition-all flex items-center gap-3"
        >
          <UserIcon class="w-5 h-5" />
          Completar mi Perfil
        </button>
      </section>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-10">
        <!-- Application Progress details -->
        <div class="lg:col-span-2 space-y-8">
          <!-- Admission Decision Box (NEW) -->
          <div v-if="aspirantData?.admission_status === 'approved'" class="p-8 rounded-[32px] border-2 border-indigo-500 bg-white shadow-2xl shadow-indigo-500/10 relative overflow-hidden group">
            <div class="absolute top-0 right-0 p-8 opacity-[0.05] group-hover:scale-110 transition-transform">
               <AcademicCapIcon class="w-32 h-32 text-indigo-900" />
            </div>
            
            <div class="relative z-10">
              <div class="flex items-center gap-3 mb-6">
                 <div class="h-10 w-10 rounded-xl bg-indigo-600 flex items-center justify-center text-white shadow-lg shadow-indigo-600/20">
                    <CheckBadgeIcon class="w-6 h-6" />
                 </div>
                 <h3 class="text-2xl font-black text-gray-900 italic tracking-tight">Resultado de Admisión</h3>
              </div>

              <div class="bg-gray-50 rounded-2xl p-6 border border-gray-100 mb-8">
                 <div class="text-[10px] font-black uppercase text-gray-400 tracking-widest mb-1 italic">Carrera Asignada</div>
                 <div class="text-2xl font-black text-indigo-600 leading-tight">{{ aspirantData.admitted_career_name }}</div>
                 
                 <div v-if="aspirantData.admitted_option === 4" class="mt-4 flex items-start gap-2 text-amber-600 bg-amber-50 p-3 rounded-xl border border-amber-100">
                    <ExclamationCircleIcon class="w-5 h-5 shrink-0 mt-0.5" />
                    <p class="text-[11px] font-bold leading-relaxed">
                      Esta carrera es una **opción alternativa** ofrecida por el comité de admisiones dado que no fue posible asignarte una de tus opciones iniciales.
                    </p>
                 </div>
                 <div v-else class="mt-4 flex items-center gap-2 text-emerald-600 bg-emerald-50 px-3 py-1.5 rounded-full w-fit border border-emerald-100">
                    <span class="text-[9px] font-black uppercase tracking-widest italic">Opción {{ aspirantData.admitted_option }} Asignada</span>
                 </div>
              </div>

              <div class="flex flex-col sm:flex-row gap-4">
                 <button 
                   @click="handleDecision('accept')"
                   class="flex-1 bg-indigo-600 text-white px-8 py-4 rounded-2xl font-black text-xs uppercase tracking-widest hover:bg-indigo-700 shadow-xl shadow-indigo-900/20 transition-all active:scale-95 text-center"
                 >
                   Aceptar y Confirmar Inscripción
                 </button>
                 <button 
                    @click="handleDecision('decline')"
                    class="px-8 py-4 rounded-2xl font-black text-xs uppercase tracking-widest text-gray-400 hover:text-red-500 hover:bg-red-50 transition-all active:scale-95 text-center"
                 >
                   Declinar Cupo
                 </button>
              </div>
            </div>
          </div>

          <!-- Alert Status -->
          <div class="p-8 rounded-[32px] border flex items-center gap-8 shadow-sm transition-all bg-white" :class="statusStyles.container">
             <div class="h-20 w-20 rounded-[24px] flex items-center justify-center shrink-0 shadow-inner" :class="statusStyles.iconBg">
                <component :is="statusStyles.icon" class="w-10 h-10" :class="statusStyles.iconColor" />
             </div>
             <div class="flex-1">
                <div class="text-[10px] font-black uppercase tracking-[0.2em] mb-1" :class="statusStyles.textColor">{{ statusStyles.label }}</div>
                <h3 class="text-2xl font-black text-gray-900 italic tracking-tight">{{ statusStyles.title }}</h3>
                <p class="text-gray-500 mt-2 text-sm leading-relaxed font-medium">{{ statusStyles.description }}</p>
             </div>
          </div>

          <!-- Career Choices (Only show if not already accepted/declined/admitted or show as reference) -->
          <section v-if="!['accepted', 'declined'].includes(aspirantData?.admission_status)">
            <h3 class="text-xl font-black text-gray-900 mb-6 italic tracking-tight">Tus Opciones Seleccionadas</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div v-for="(career, idx) in careerChoices" :key="idx" class="bg-white p-6 rounded-[28px] border border-gray-100 shadow-sm relative overflow-hidden group hover:border-blue-100 transition-all">
                 <div class="relative z-10">
                   <div class="text-[10px] font-black text-gray-300 uppercase tracking-widest mb-1 italic">Prioridad {{ idx + 1 }}</div>
                   <div class="text-lg font-black text-gray-800 leading-tight">{{ career || 'Pendiente' }}</div>
                   <div class="text-[10px] text-blue-400 font-bold mt-2 uppercase tracking-widest">UPEL Principal</div>
                 </div>
                 <div class="absolute -right-4 -bottom-4 opacity-[0.03] group-hover:opacity-[0.07] transition-all group-hover:scale-110">
                   <AcademicCapIcon class="w-24 h-24" />
                 </div>
              </div>
            </div>
          </section>
        </div>

        <!-- Sidebar / Help -->
        <div class="space-y-8">
           <section class="bg-gray-900 rounded-[32px] p-8 text-white shadow-2xl shadow-black/20">
             <h4 class="text-lg font-black mb-4 italic tracking-tight">¿Preguntas?</h4>
             <p class="text-gray-400 text-sm mb-6 leading-relaxed font-medium">Nuestro equipo de admisiones está disponible para orientarte en cada paso.</p>
             <a href="mailto:admisiones@upel.edu.ve" class="flex items-center justify-center gap-3 w-full py-4 bg-white/5 hover:bg-white/10 rounded-2xl text-[10px] font-black uppercase tracking-widest transition-all border border-white/5 active:scale-95">
                <EnvelopeIcon class="w-4 h-4 text-blue-400" />
                Contactar Soporte
             </a>
           </section>

           <section class="bg-white rounded-[32px] p-8 border border-gray-100 shadow-sm">
              <h4 class="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-6 italic">Documentación</h4>
              <ul class="space-y-4">
                <li class="flex items-center gap-3">
                  <div class="w-6 h-6 bg-green-50 text-green-600 rounded-lg flex items-center justify-center border border-green-100">
                    <CheckIcon class="w-4 h-4" />
                  </div>
                  <span class="text-xs font-bold text-gray-700">Cédula de Identidad</span>
                </li>
                <li class="flex items-center gap-3">
                  <div class="w-6 h-6 bg-green-50 text-green-600 rounded-lg flex items-center justify-center border border-green-100">
                    <CheckIcon class="w-4 h-4" />
                  </div>
                  <span class="text-xs font-bold text-gray-700">Título de Bachiller</span>
                </li>
                <li class="flex items-center gap-3">
                  <div class="w-6 h-6 bg-amber-50 text-amber-500 rounded-lg flex items-center justify-center border border-amber-100">
                    <ClockIcon class="w-4 h-4" />
                  </div>
                  <span class="text-xs font-bold text-gray-400 italic">Notas Certificadas</span>
                </li>
          </ul>
           </section>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'

import { 
  ClockIcon, 
  CheckCircleIcon, 
  XCircleIcon,
  AcademicCapIcon,
  UserIcon,
  CheckBadgeIcon,
  ExclamationCircleIcon,
  EnvelopeIcon,
  CheckIcon
} from '@heroicons/vue/24/outline'

const router = useRouter()
const authStore = useAuthStore()
const aspirantData = ref(null)

const steps = [
  { name: 'Registro' },
  { name: 'Expediente' },
  { name: 'Entrevista' },
  { name: 'Resultado' }
]

const currentStepIndex = computed(() => {
  const status = aspirantData.value?.admission_status || 'pending'
  if (status === 'approved') return 3
  if (status === 'rejected') return 3
  if (status === 'in_review') return 2
  return 1 // 'pending' or other
})

const careerChoices = computed(() => [
  aspirantData.value?.career_name,
  aspirantData.value?.career_name_2
])

const statusStyles = computed(() => {
  const status = aspirantData.value?.admission_status || 'pending'
  switch (status) {
    case 'accepted':
       return {
        label: 'Proceso de Inscripción',
        title: 'Admisión Aceptada',
        description: 'Has aceptado tu cupo. Pronto recibirás un correo con tu nuevo Carnet Estudiantil y acceso al Portal de Estudiante.',
        container: 'bg-emerald-50/50 border-emerald-100',
        iconBg: 'bg-emerald-100',
        iconColor: 'text-emerald-600',
        textColor: 'text-emerald-700',
        icon: CheckCircleIcon
      }
    case 'declined':
       return {
        label: 'Resultado',
        title: 'Cita Declinada',
        description: 'Has declinado la oferta de admisión para este período académico.',
        container: 'bg-gray-100 border-gray-200',
        iconBg: 'bg-gray-200',
        iconColor: 'text-gray-500',
        textColor: 'text-gray-600',
        icon: XCircleIcon
      }
    case 'approved':
      return {
        label: '¡Felicidades!',
        title: 'Has sido Admitido',
        description: 'Tu proceso de admisión fue exitoso. Por favor revisa la carrera asignada y confirma si deseas formalizar tu inscripción.',
        container: 'bg-indigo-50/50 border-indigo-100',
        iconBg: 'bg-indigo-100',
        iconColor: 'text-indigo-600',
        textColor: 'text-indigo-700',
        icon: AcademicCapIcon
      }
    case 'rejected':
      return {
        label: 'Resultado',
        title: 'No admitido en esta fase',
        description: 'Lamentamos informarte que tu solicitud no ha sido aprobada en este período académico.',
        container: 'bg-red-50/50 border-red-100',
        iconBg: 'bg-red-100',
        iconColor: 'text-red-600',
        textColor: 'text-red-700',
        icon: XCircleIcon
      }
    default: // pending o in_review
      return {
        label: 'En Proceso',
        title: 'Expediente en Revisión',
        description: 'El comité de admisión está validando tus documentos. Te notificaremos por correo cualquier novedad.',
        container: 'bg-amber-50/50 border-amber-100',
        iconBg: 'bg-amber-100',
        iconColor: 'text-amber-600',
        textColor: 'text-amber-700',
        icon: ClockIcon
      }
  }
})

const fetchAspirant = async () => {
  try {
    const res = await axios.get('/api/aspirants/')
    const data = res.data.results ? res.data.results[0] : res.data
    aspirantData.value = data
  } catch (err) {
    console.error('Error fetching aspirant dashboard:', err)
  }
}

const handleDecision = async (decision) => {
  if (!aspirantData.value) return
  
  try {
    const newStatus = decision === 'accept' ? 'accepted' : 'declined'
    await axios.patch(`/api/aspirants/${aspirantData.value.code}/`, {
      admission_status: newStatus
    })
    await fetchAspirant()
  } catch (err) {
    console.error('Error handling admission decision:', err)
  }
}

const logout = () => {
  authStore.logout()
  router.push('/')
}

onMounted(fetchAspirant)
</script>

<style scoped>
/* Transiciones suaves */
.transition-all { transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1); }
</style>
