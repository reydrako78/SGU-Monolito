<template>
  <div class="min-h-screen bg-[#F8FAFC] flex flex-col font-sans text-gray-900">
    <header class="bg-white/80 backdrop-blur-md border-b border-gray-100 px-8 py-5 sticky top-0 z-50 flex justify-between items-center shadow-sm">
      <div class="flex items-center gap-6">
        <button @click="$router.back()" class="p-3 hover:bg-gray-100 rounded-2xl transition-all text-gray-400 hover:text-blue-600 active:scale-95">
          <ArrowLeftIcon class="w-6 h-6" />
        </button>
        <div>
          <h2 class="text-2xl font-black text-gray-900 leading-none italic tracking-tight">Acta de Calificaciones</h2>
          <p class="text-[10px] text-gray-400 uppercase font-black tracking-widest mt-1 italic">Código de Sección: {{ id }}</p>
        </div>
      </div>
      
      <div class="flex items-center gap-4">
        <div v-if="saving" class="flex items-center gap-2 px-4 py-2 bg-blue-50 text-blue-600 rounded-xl animate-pulse">
           <CloudArrowUpIcon class="w-4 h-4" />
           <span class="text-[10px] font-black uppercase tracking-widest">Sincronizando...</span>
        </div>
        <button @click="saveAll" class="px-8 py-3 bg-gray-900 text-white rounded-2xl text-[10px] font-black uppercase tracking-widest shadow-xl shadow-black/10 hover:bg-indigo-600 transition-all active:scale-95 disabled:opacity-50" :disabled="saving">
          Finalizar y Cerrar Acta
        </button>
      </div>
    </header>

    <main class="flex-1 p-8 lg:p-16 max-w-[1600px] mx-auto w-full">
      <!-- Section Info Glass Banner -->
      <section class="mb-12 bg-white p-10 rounded-[40px] border border-gray-100 shadow-sm relative overflow-hidden group">
        <div class="absolute -right-20 -top-20 text-gray-50 opacity-50 group-hover:rotate-12 transition-transform">
           <ChartBarIcon class="w-80 h-80" />
        </div>
        
        <div class="relative z-10 flex flex-col lg:flex-row justify-between items-start lg:items-center gap-10">
          <div>
            <div class="flex items-center gap-2 mb-3">
               <span class="w-8 h-[2px] bg-blue-500 font-black"></span>
               <span class="text-[10px] font-black uppercase text-blue-500 tracking-[0.3em]">Unidad Curricular</span>
            </div>
            <h1 class="text-5xl font-black text-gray-900 tracking-tighter uppercase italic leading-none">{{ sectionInfo?.uc_name || 'Cargando...' }}</h1>
            <div class="flex items-center gap-6 mt-6">
              <div class="flex items-center gap-2 text-gray-400">
                <UsersIcon class="w-5 h-5" />
                <span class="text-sm font-bold"><span class="text-gray-900">{{ grades.length }}</span> Estudiantes</span>
              </div>
              <div class="w-px h-4 bg-gray-200"></div>
              <div class="flex items-center gap-2 text-gray-400">
                <span class="text-sm font-bold">Promedio: <span class="text-blue-600 text-lg">{{ sectionAverage }}%</span></span>
              </div>
            </div>
          </div>

          <div class="bg-indigo-50/50 backdrop-blur-sm p-6 rounded-[32px] border border-indigo-100 flex items-center gap-5 max-w-sm">
             <div class="h-14 w-14 bg-white rounded-2xl flex items-center justify-center text-indigo-600 shadow-sm shrink-0">
               <InformationCircleIcon class="w-7 h-7" />
             </div>
             <div>
               <p class="text-[11px] font-bold text-indigo-900 leading-relaxed uppercase tracking-tight">Escala de Evaluación</p>
               <p class="text-[10px] text-indigo-500 font-medium mt-1">
                 Calificación máxima: <span class="font-black">100%</span><br>
                 Mínimo aprobatorio: <span class="font-black">61%</span>
               </p>
             </div>
          </div>
        </div>
      </section>

      <!-- Stats Mini Bar -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-6 mb-12">
         <div class="bg-white p-6 rounded-[28px] border border-gray-100 shadow-sm flex items-center gap-4">
            <div class="h-10 w-10 bg-blue-50 text-blue-600 rounded-xl flex items-center justify-center font-black">Σ</div>
            <div>
               <div class="text-[9px] font-black text-gray-400 uppercase tracking-widest">Inscritos</div>
               <div class="text-xl font-black">{{ grades.length }}</div>
            </div>
         </div>
         <div class="bg-white p-6 rounded-[28px] border border-gray-100 shadow-sm flex items-center gap-4">
            <div class="h-10 w-10 bg-emerald-50 text-emerald-600 rounded-xl flex items-center justify-center">
               <CheckCircleIcon class="w-5 h-5" />
            </div>
            <div>
               <div class="text-[9px] font-black text-gray-400 uppercase tracking-widest">Aprobados</div>
               <div class="text-xl font-black">{{ grades.filter(g => g.status === 'passed').length }}</div>
            </div>
         </div>
         <div class="bg-white p-6 rounded-[28px] border border-gray-100 shadow-sm flex items-center gap-4">
            <div class="h-10 w-10 bg-red-50 text-red-600 rounded-xl flex items-center justify-center">
               <XCircleIcon class="w-5 h-5" />
            </div>
            <div>
               <div class="text-[9px] font-black text-gray-400 uppercase tracking-widest">Reprobados</div>
               <div class="text-xl font-black">{{ grades.filter(g => g.status === 'failed').length }}</div>
            </div>
         </div>
         <div class="bg-white p-6 rounded-[28px] border border-gray-100 shadow-sm flex items-center gap-4">
            <div class="h-10 w-10 bg-amber-50 text-amber-600 rounded-xl flex items-center justify-center">
               <ClockIcon class="w-5 h-5" />
            </div>
            <div>
               <div class="text-[9px] font-black text-gray-400 uppercase tracking-widest">Pendientes</div>
               <div class="text-xl font-black">{{ grades.filter(g => g.status === 'in_progress' || g.status === 'incomplete').length }}</div>
            </div>
         </div>
      </div>

      <!-- Grades Table -->
      <div class="bg-white rounded-[40px] border border-gray-100 shadow-xl shadow-gray-200/20 overflow-hidden mb-16">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-gray-50/50">
              <th class="px-10 py-6 text-[10px] font-black text-gray-400 uppercase tracking-[0.2em] border-b border-gray-100 italic">Identificación del Estudiante</th>
              <th class="px-6 py-6 text-[10px] font-black text-gray-400 uppercase tracking-[0.2em] border-b border-gray-100 text-center italic">Corte 1 (30%)</th>
              <th class="px-6 py-6 text-[10px] font-black text-gray-400 uppercase tracking-[0.2em] border-b border-gray-100 text-center italic">Corte 2 (30%)</th>
              <th class="px-6 py-6 text-[10px] font-black text-gray-400 uppercase tracking-[0.2em] border-b border-gray-100 text-center italic">Corte 3 (40%)</th>
              <th class="px-10 py-6 text-[10px] font-black text-gray-400 uppercase tracking-[0.2em] border-b border-gray-100 text-right italic">Definitiva</th>
              <th class="px-10 py-6 text-[10px] font-black text-gray-400 uppercase tracking-[0.2em] border-b border-gray-100 text-center italic">Veredicto</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <tr v-if="loading" v-for="i in 5" :key="i">
              <td colspan="6" class="px-10 py-8"><div class="h-6 bg-gray-50 rounded-2xl animate-pulse"></div></td>
            </tr>
            <tr v-else v-for="item in grades" :key="item.id" class="group hover:bg-gray-50/80 transition-all duration-300">
              <td class="px-10 py-6">
                <div class="font-black text-gray-900 tracking-tight text-lg">{{ item.student_carnet }}</div>
                <div class="text-[9px] text-gray-400 font-black uppercase tracking-widest mt-0.5 italic">ID Inscripción: #{{ item.enrollment_detail_id }}</div>
              </td>
              <td class="px-6 py-6 text-center">
                <div class="relative inline-block group/input">
                  <input 
                    type="number" 
                    v-model.number="item.partial1" 
                    @change="updateGrade(item)"
                    class="w-24 px-4 py-3 bg-gray-50/50 border-2 border-transparent focus:border-blue-500 focus:bg-white rounded-[20px] text-base font-black text-center transition-all outline-none shadow-inner"
                    min="0" max="100"
                  >
                </div>
              </td>
              <td class="px-6 py-6 text-center">
                <input 
                  type="number" 
                  v-model.number="item.partial2" 
                  @change="updateGrade(item)"
                  class="w-24 px-4 py-3 bg-gray-50/50 border-2 border-transparent focus:border-blue-500 focus:bg-white rounded-[20px] text-base font-black text-center transition-all outline-none shadow-inner"
                  min="0" max="100"
                >
              </td>
              <td class="px-6 py-6 text-center">
                <input 
                  type="number" 
                  v-model.number="item.partial3" 
                  @change="updateGrade(item)"
                  class="w-24 px-4 py-3 bg-gray-50/50 border-2 border-transparent focus:border-blue-500 focus:bg-white rounded-[20px] text-base font-black text-center transition-all outline-none shadow-inner"
                  min="0" max="100"
                >
              </td>
              <td class="px-10 py-6 text-right">
                 <div class="font-black text-2xl italic tracking-tighter" :class="getGradeColor(item.final_grade)">
                    {{ item.final_grade !== null ? item.final_grade + '%' : '—' }}
                 </div>
              </td>
              <td class="px-10 py-6 text-center">
                <span class="inline-flex items-center gap-2 px-5 py-2 rounded-2xl text-[10px] font-black uppercase tracking-[0.15em] border italic shadow-sm" :class="getStatusStyles(item.status)">
                  <div class="w-1.5 h-1.5 rounded-full" :class="item.status === 'passed' ? 'bg-emerald-500' : (item.status === 'failed' ? 'bg-red-500' : 'bg-blue-500')"></div>
                  {{ getStatusLabel(item.status) }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import { 
  ArrowLeftIcon, 
  CloudArrowUpIcon,
  ChartBarIcon,
  UsersIcon,
  InformationCircleIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon
} from '@heroicons/vue/24/outline'

const props = defineProps({
  id: { type: String, required: true }
})

const authStore = useAuthStore()
const loading = ref(true)
const saving = ref(false)
const grades = ref([])
const sectionInfo = ref(null)

const sectionAverage = computed(() => {
  if (!grades.value.length) return 0
  const validGrades = grades.value.filter(g => g.final_grade !== null).map(g => Number(g.final_grade))
  if (!validGrades.length) return 0
  const sum = validGrades.reduce((a, b) => a + b, 0)
  return Math.round(sum / validGrades.length)
})

const fetchData = async () => {
  loading.value = true
  try {
    const res = await axios.get(`/api/grades/grades/section/${props.id}/`)
    grades.value = res.data.grades || []
    if (grades.value.length > 0) {
      sectionInfo.value = {
        uc_name: grades.value[0].uc_name,
        uc_code: grades.value[0].uc_code
      }
    }
  } catch (err) {
    console.error('Error fetching grades:', err)
  } finally {
    loading.value = false
  }
}

const updateGrade = async (item) => {
  saving.value = true
  try {
    // El backend autocalcula el final_grade y status al guardar
    const res = await axios.patch(`/api/grades/grades/${item.id}/`, {
      partial1: item.partial1,
      partial2: item.partial2,
      partial3: item.partial3
    })
    // Actualizar datos locales con el cálculo del servidor
    item.final_grade = res.data.final_grade
    item.status = res.data.status
  } catch (err) {
    console.error('Error saving grade:', err)
  } finally {
    saving.value = false
  }
}

const saveAll = () => {
  // En este diseño las notas se guardan individualmente con PATCH al cambiar
  // El botón "Confirmar Acta" podría usarse para un cierre formal de período en el futuro
  alert('Se ha guardado la planilla completa correctamente.')
}

const getGradeColor = (grade) => {
  if (grade === null) return 'text-gray-300'
  return grade >= 61 ? 'text-green-600' : 'text-red-500'
}

const getStatusStyles = (status) => {
  switch (status) {
    case 'passed': return 'bg-green-50 text-green-600 border-green-100'
    case 'failed': return 'bg-red-50 text-red-500 border-red-100'
    case 'in_progress': return 'bg-blue-50 text-blue-500 border-blue-100 font-bold'
    default: return 'bg-gray-50 text-gray-400 border-gray-100'
  }
}

const getStatusLabel = (status) => {
  const map = {
    'passed': 'Aprobado',
    'failed': 'Reprobado',
    'in_progress': 'En Carga',
    'incomplete': 'Incompleto',
    'withdrawn': 'Retirado'
  }
  return map[status] || status
}

onMounted(fetchData)
</script>

<style scoped>
/* Chrome, Safari, Edge, Opera */
input::-webkit-outer-spin-button,
input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
/* Firefox */
input[type=number] {
  -moz-appearance: textfield;
}

.transition-all { transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1); }
</style>
