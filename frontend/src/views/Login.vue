<template>
  <div class="min-h-screen bg-[var(--upel-gray)] flex items-center justify-center p-4">
    <!-- Glowing background effect -->
    <div class="absolute inset-0 z-0 overflow-hidden pointer-events-none">
      <div class="absolute -top-[20%] -left-[10%] w-[50%] h-[50%] rounded-full bg-[var(--upel-blue)]/10 blur-[100px]"></div>
      <div class="absolute bottom-[10%] right-[0%] w-[40%] h-[40%] rounded-full bg-[var(--upel-red)]/10 blur-[100px]"></div>
    </div>

    <div class="relative z-10 w-full max-w-4xl bg-white/80 backdrop-blur-xl rounded-2xl shadow-2xl overflow-hidden border border-white/40 flex flex-col md:flex-row">
      <!-- Left side (branding) -->
      <div class="md:w-5/12 bg-gradient-to-br from-[var(--upel-blue)] to-[#06245c] p-10 flex flex-col justify-between text-white relative overflow-hidden">
        <div class="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-10 mix-blend-overlay"></div>
        <div class="relative z-10">
          <div class="flex items-center space-x-3 mb-8">
            <div class="h-10 w-10 bg-white rounded-lg flex items-center justify-center font-bold text-[var(--upel-blue)] text-xl shadow-lg">U</div>
            <h1 class="text-2xl font-bold tracking-tight">UPEL</h1>
          </div>
          <h2 class="text-3xl font-semibold mb-4 leading-tight">Sistema<br/>Universitario</h2>
          <p class="text-blue-100/80 text-sm">Plataforma integral de gestión académica y administrativa. Accede al portal de autogestión moderno.</p>
        </div>
        
        <div class="relative z-10 text-xs text-blue-200 mt-12 md:mt-0">
          &copy; 2026 Universidad Pedagógica Experimental Libertador
        </div>
      </div>

      <!-- Right side (form) -->
      <div class="md:w-7/12 p-10 lg:p-14">
        <div class="flex flex-col xl:flex-row justify-between xl:items-center mb-8">
          <h3 class="text-2xl font-semibold text-[var(--upel-dark-text)] mb-3 xl:mb-0">Bienvenido</h3>
          <!-- Role selector simple UI -->
          <div class="relative min-w-[180px]">
            <select
              v-model="activeRole"
              class="appearance-none bg-gray-50 border border-gray-200 text-gray-700 text-sm rounded-lg focus:ring-[var(--upel-blue)] focus:border-[var(--upel-blue)] w-full p-2.5 pr-8 transition-all shadow-sm outline-none font-medium cursor-pointer"
            >
              <option value="estudiante">Estudiante</option>
              <option value="aspirante">Aspirante</option>
              <option value="docente">Docente</option>
              <option value="administrativo">Administrativo</option>
              <option value="egresado">Egresado</option>
            </select>
            <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-500">
              <svg class="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><path d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"/></svg>
            </div>
          </div>
        </div>

        <!-- Form error -->
        <div v-if="error" class="mb-6 bg-red-50 border-l-4 border-red-500 p-4 rounded-md flex items-start animate-fade-in">
          <svg class="h-5 w-5 text-red-500 mr-2 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
          </svg>
          <span class="text-sm text-red-700">{{ error }}</span>
        </div>

        <form v-if="!isRegistering" @submit.prevent="login" class="space-y-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1" for="username">Usuario / Cédula</label>
            <div class="relative">
              <input 
                id="username" 
                v-model="username" 
                type="text" 
                class="w-full pl-4 pr-10 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[var(--upel-blue)]/20 focus:border-[var(--upel-blue)] outline-none transition-all"
                placeholder="Ingresa tu usuario"
                required
              />
            </div>
          </div>

          <div>
            <div class="flex items-center justify-between mb-1">
              <label class="block text-sm font-medium text-gray-700" for="password">Contraseña</label>
              <a href="#" class="text-xs text-[var(--upel-blue)] hover:underline font-medium">¿Olvidaste tu clave?</a>
            </div>
            <div class="relative">
              <input 
                id="password" 
                v-model="password" 
                type="password" 
                class="w-full pl-4 pr-10 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[var(--upel-blue)]/20 focus:border-[var(--upel-blue)] outline-none transition-all"
                placeholder="••••••••"
                required
              />
            </div>
          </div>

          <button 
            type="submit" 
            :disabled="loading"
            class="w-full bg-[var(--upel-blue)] hover:bg-[#082f70] text-white font-medium py-3 px-4 rounded-xl transition-all duration-300 transform active:scale-[0.98] flex items-center justify-center mt-2 disabled:opacity-70"
          >
            <svg v-if="loading" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ loading ? 'Ingresando...' : 'Iniciar Sesión' }}
          </button>
          
          <div v-if="activeRole === 'aspirante'" class="mt-4 text-center text-sm">
            ¿Deseas registrarte como Aspirante? 
            <a href="#" @click.prevent="toggleRegister(true)" class="text-[var(--upel-blue)] hover:underline font-semibold transition-colors">
              Crea tu cuenta aquí
            </a>
          </div>
        </form>

        <form v-else @submit.prevent="registerAspirant" class="space-y-4 animate-fade-in">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-medium text-gray-700 mb-1">Nombre</label>
              <input v-model="regForm.first_name" type="text" class="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-[var(--upel-blue)]/20 outline-none" required />
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-700 mb-1">Apellido</label>
              <input v-model="regForm.last_name" type="text" class="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-[var(--upel-blue)]/20 outline-none" required />
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-medium text-gray-700 mb-1">Cédula</label>
              <input v-model="regForm.national_id" type="text" class="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-[var(--upel-blue)]/20 outline-none" required />
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-700 mb-1">Correo Electrónico</label>
              <input v-model="regForm.email" type="email" class="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-[var(--upel-blue)]/20 outline-none" required />
            </div>
          </div>

          <div>
            <label class="block text-xs font-medium text-gray-700 mb-1">Usuario</label>
            <input v-model="regForm.username" type="text" class="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-[var(--upel-blue)]/20 outline-none" required />
          </div>

          <div>
            <label class="block text-xs font-medium text-gray-700 mb-1">Contraseña</label>
            <input v-model="regForm.password" type="password" class="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-[var(--upel-blue)]/20 outline-none" required />
          </div>

          <button 
            type="submit" 
            :disabled="loading"
            class="w-full bg-[#06245c] hover:bg-[#083488] text-white font-medium py-3 px-4 rounded-xl transition-all duration-300 mt-4 disabled:opacity-70"
          >
            {{ loading ? 'Registrando...' : 'Registrar Aspirante' }}
          </button>
          
          <div class="mt-4 text-center text-sm">
            ¿Ya tienes cuenta? 
            <a href="#" @click.prevent="toggleRegister(false)" class="text-gray-600 hover:text-[var(--upel-blue)] hover:underline transition-colors">
              Volver al inicio de sesión
            </a>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth' // <--- Importamos Pinia Store
import axios from 'axios'

const router = useRouter()
const authStore = useAuthStore() // <--- Instanciamos Store

const activeRole = ref('estudiante')
const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

const isRegistering = ref(false)
const regForm = ref({
  first_name: '',
  last_name: '',
  national_id: '',
  email: '',
  username: '',
  password: ''
})

const toggleRegister = (val) => {
  isRegistering.value = val
  error.value = ''
}

const login = async () => {
  loading.value = true
  error.value = ''
  
  try {
    // 1. Obtener Token JWT desde Django
    const resAuth = await axios.post('/api/token/', {
      username: username.value,
      password: password.value
    })
    
    const token = resAuth.data.access

    // 2. Validar información y ROL del usuario
    const resValidate = await axios.get('/api/validate/', {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    const userData = resValidate.data

    // Guardamos sesión completa en el store de Pinia
    authStore.login(token, userData)

    const realRole = userData.role

    // Redirigir según el rol real
    if (realRole === 'student' || realRole === 'estudiante') {
      router.push('/student/dashboard')
    } else if (realRole === 'aspirant') {
      router.push('/aspirant/dashboard')
    } else {
      // Docente, Administrativo, Coordinador, Admin, etc.
      router.push('/panel')
    }
  } catch (err) {
    console.error(err)
    error.value = 'Credenciales inválidas o error de conexión con el backend.'
  } finally {
    loading.value = false
  }
}

const registerAspirant = async () => {
  loading.value = true
  error.value = ''
  
  try {
    await axios.post('/api/aspirants/register/', regForm.value)
    // Tras registrar con éxito, hacemos login automático
    username.value = regForm.value.username
    password.value = regForm.value.password
    await login()
  } catch (err) {
    console.error(err)
    error.value = err.response?.data?.detail || err.response?.data?.username?.[0] || 'Ocurrió un error al registrarse. Verifica tus datos e inténtalo de nuevo.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.3s ease-in-out;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-4px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
