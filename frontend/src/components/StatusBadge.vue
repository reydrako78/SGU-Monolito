<template>
  <span 
    class="px-3 py-1 rounded-full text-xs font-semibold"
    :class="statusClass"
  >
    {{ label || statusText }}
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: {
    type: String,
    required: true
  },
  label: {
    type: String,
    default: ''
  },
  type: {
    type: String,
    default: 'student' // 'student', 'enrollment', 'constancia'
  }
})

const statusText = computed(() => {
  const maps = {
    student: {
      active: 'Activo',
      inactive: 'Inactivo',
      graduated: 'Egresado',
      suspended: 'Suspendido'
    },
    enrollment: {
      enrolled: 'Inscrito',
      withdrawn: 'Retirado',
      completed: 'Completado'
    },
    constancia: {
      pending: 'Pendiente',
      in_review: 'En Revisión',
      approved: 'Admitido',
      rejected: 'Rechazado',
      delivered: 'Entregado',
      accepted: 'Asignado (Confirmado)',
      declined: 'Cupo Declinado'
    }
  }
  return maps[props.type]?.[props.status] || props.status
})

const statusClass = computed(() => {
  const classes = {
    // Verdes / Emerald
    active: 'bg-emerald-50 text-emerald-700 border border-emerald-100',
    enrolled: 'bg-emerald-50 text-emerald-700 border border-emerald-100',
    approved: 'bg-emerald-50 text-emerald-700 border border-emerald-100',
    accepted: 'bg-emerald-600 text-white shadow-sm shadow-emerald-500/20',
    delivered: 'bg-blue-50 text-blue-700 border border-blue-100',
    
    // Grises / Slate / Neutros
    inactive: 'bg-slate-50 text-slate-600 border border-slate-100',
    pending: 'bg-amber-50 text-amber-700 border border-amber-100',
    in_review: 'bg-sky-50 text-sky-700 border border-sky-100',
    declined: 'bg-slate-100 text-slate-500 border border-slate-200 line-through decoration-slate-300',
    
    // Azules / Indigo
    graduated: 'bg-indigo-50 text-indigo-700 border border-indigo-100',
    completed: 'bg-indigo-600 text-white',
    
    // Rojos / Rose
    suspended: 'bg-rose-50 text-rose-600 border border-rose-100',
    withdrawn: 'bg-rose-50 text-rose-600 border border-rose-100',
    rejected: 'bg-rose-50 text-rose-700 border border-rose-100',
  }
  return classes[props.status] || 'bg-gray-50 text-gray-500 border border-gray-100'
})
</script>
