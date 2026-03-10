<template>
  <div class="min-h-screen bg-[#F8FAFC] flex text-gray-900">
    <AdminSidebar />
    
    <main class="flex-1 p-8 overflow-y-auto">
      <header class="mb-10 flex flex-col md:flex-row justify-between items-start gap-4">
        <div>
          <h1 class="text-3xl font-black text-gray-900 tracking-tight mb-2">Gestión Académica Regional</h1>
          <p class="text-gray-500 font-medium">Control institucional de especialidades, planes de estudio y despliegue territorial.</p>
        </div>
        <div class="flex gap-3">
          <button @click="openGeneralCreate" class="bg-[var(--upel-blue)] text-white px-6 py-3 rounded-2xl font-bold text-sm shadow-lg shadow-blue-500/20 hover:scale-[1.02] transition-all flex items-center gap-2">
            <PlusIcon class="w-5 h-5 text-blue-200" />
            Nuevo Registro
          </button>
        </div>
      </header>

      <!-- Tab Navigation -->
      <div class="flex gap-1 bg-white p-1.5 rounded-2xl border border-gray-100 mb-8 w-fit shadow-sm overflow-x-auto max-w-full">
        <button 
          v-for="tab in tabs" 
          :key="tab.id"
          @click="activeTab = tab.id"
          class="px-6 py-2.5 rounded-xl text-sm font-bold transition-all whitespace-nowrap"
          :class="activeTab === tab.id ? 'bg-[var(--upel-blue)] text-white shadow-md' : 'text-gray-400 hover:text-gray-600 hover:bg-gray-50'"
        >
          {{ tab.name }}
        </button>
      </div>      <!-- Tab Content: Especialidades (Careers) -->
      <div v-if="activeTab === 'careers'" class="animate-fade-in">
        <div class="mb-6 flex items-center justify-between gap-4">
          <div class="relative group flex-1 max-w-md">
             <input 
               v-model="searchCareers" 
               type="text" 
               placeholder="Buscar especialidad..." 
               class="w-full bg-white border border-gray-100 rounded-2xl px-5 py-3 text-sm font-bold shadow-sm outline-none focus:ring-4 focus:ring-blue-500/5 transition-all font-mono"
             />
             <MagnifyingGlassIcon class="w-4 h-4 absolute right-5 top-3.5 text-gray-300" />
          </div>
        </div>

        <div class="bg-white rounded-[32px] border border-gray-100 shadow-sm overflow-hidden min-h-[500px]">
          <DataTable 
            :value="filteredCareers" 
            :paginator="true" 
            :rows="10" 
            stripedRows
            responsiveLayout="scroll"
            class="p-datatable-sm"
          >
            <template #empty>
              <div class="p-20 text-center opacity-40 font-black uppercase text-xs italic">No se encontraron especialidades</div>
            </template>

            <Column field="name" header="ESPECIALIDAD / PROGRAMA" sortable>
              <template #body="{ data }">
                <div class="flex items-center gap-4 py-1">
                  <div class="h-10 w-10 rounded-xl bg-blue-50 text-[var(--upel-blue)] flex items-center justify-center font-black text-sm border border-blue-100 italic transition-all group-hover:scale-110">
                    {{ data.code?.[0] || 'C' }}
                  </div>
                  <div>
                    <div class="text-sm font-black text-gray-900 group-hover:text-[var(--upel-blue)] transition-colors italic uppercase tracking-tighter">{{ data.name }}</div>
                    <div class="text-[10px] text-gray-400 font-bold uppercase tracking-tight">{{ data.faculty }}</div>
                  </div>
                </div>
              </template>
            </Column>

            <Column field="code" header="CÓDIGO" sortable class="text-center font-mono text-[11px] font-black text-gray-400">
               <template #body="{ data }">
                  <span class="bg-gray-50 px-2 py-0.5 rounded border border-gray-100">{{ data.code }}</span>
               </template>
            </Column>

            <Column header="ESTADO" class="text-center">
              <template #body>
                <div class="flex flex-col items-center">
                  <span class="px-3 py-1 bg-emerald-50 text-emerald-600 text-[9px] font-black uppercase rounded-full border border-emerald-100 leading-none">Activa</span>
                  <span class="text-[8px] text-gray-300 font-bold mt-1">Oferta Vigente</span>
                </div>
              </template>
            </Column>

            <Column header="ACCIONES" class="text-right">
              <template #body="{ data }">
                 <div class="flex justify-end gap-1">
                    <button @click="activeTab = 'plans'; selectedCareerId = data.id; fetchCareerPlan();" class="p-2.5 text-blue-400 hover:bg-blue-50 rounded-xl transition-all active:scale-90" title="Ver Pensum">
                       <AcademicCapIcon class="w-5 h-5" />
                    </button>
                    <button class="p-2.5 text-gray-300 hover:bg-gray-50 rounded-xl transition-all active:scale-90" title="Editar">
                       <PencilIcon class="w-5 h-5" />
                    </button>
                 </div>
              </template>
            </Column>
          </DataTable>
        </div>
      </div>

      <!-- Tab Content: Unidades Curriculares -->
      <div v-if="activeTab === 'units'" class="animate-fade-in">
        <div class="mb-6 flex items-center justify-between gap-4">
          <div class="relative group flex-1 max-w-md">
             <input 
               v-model="searchUnits" 
               type="text" 
               placeholder="Buscar unidad por nombre o código..." 
               class="w-full bg-white border border-gray-100 rounded-2xl px-5 py-3 text-sm font-bold shadow-sm outline-none focus:ring-4 focus:ring-blue-500/5 transition-all font-mono"
             />
             <MagnifyingGlassIcon class="w-4 h-4 absolute right-5 top-3.5 text-gray-300" />
          </div>
        </div>

        <div class="bg-white rounded-[32px] border border-gray-100 shadow-sm overflow-hidden min-h-[500px]">
          <DataTable 
            :value="filteredUnits" 
            :paginator="true" 
            :rows="10" 
            :rowsPerPageOptions="[10, 20, 50]"
            stripedRows
            responsiveLayout="scroll"
            class="p-datatable-sm"
            paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink RowsPerPageDropdown"
          >
            <template #empty>
              <div class="p-20 text-center opacity-40 italic font-black uppercase text-xs">No se encontraron unidades curriculares</div>
            </template>

            <Column field="code" header="CÓDIGO" sortable>
              <template #body="{ data }">
                <span class="font-mono text-[11px] font-black text-[var(--upel-blue)] bg-blue-50 px-2.5 py-1 rounded-lg border border-blue-100">{{ data.code }}</span>
              </template>
            </Column>

            <Column field="name" header="NOMBRE DE LA UNIDAD" sortable>
              <template #body="{ data }">
                <div class="text-sm font-black text-gray-800 italic uppercase tracking-tighter">{{ data.name }}</div>
              </template>
            </Column>

            <Column field="component" header="COMPONENTE" sortable>
              <template #body="{ data }">
                <span :class="getComponentClass(data.component)" class="px-3 py-1 rounded-full text-[9px] font-black uppercase tracking-tight">
                  {{ data.component }}
                </span>
              </template>
            </Column>

            <Column header="HAD / HLE" class="text-center">
              <template #body="{ data }">
                <div class="text-[10px] font-bold text-gray-400 uppercase">
                  <span class="text-blue-600">{{ data.teaching_hours || 4 }}</span> / <span class="text-amber-600">{{ data.student_hours || 8 }}</span>
                </div>
              </template>
            </Column>

            <Column field="credits" header="CRÉDITOS" sortable class="text-center font-black">
              <template #body="{ data }">
                 <span class="text-sm font-black text-gray-700">{{ data.credits }}</span>
              </template>
            </Column>

            <Column header="ACCIONES" class="text-right">
              <template #body>
                <button class="p-2 text-gray-300 hover:text-[var(--upel-blue)] transition-all active:scale-90">
                  <PencilIcon class="w-5 h-5" />
                </button>
              </template>
            </Column>
          </DataTable>
        </div>
      </div>

      <!-- Tab Content: Planes de Estudio (Pensum) -->
      <div v-if="activeTab === 'plans'" class="animate-fade-in">
        <div class="mb-8 flex flex-col md:flex-row gap-4 items-end bg-white p-6 rounded-3xl border border-gray-100 shadow-sm">
          <div class="flex-1 w-full">
            <label class="block text-[11px] font-black uppercase text-gray-400 mb-2">Seleccionar Especialidad</label>
            <select v-model="selectedCareerId" @change="fetchCareerPlan" class="w-full bg-gray-50 border-none rounded-2xl px-5 py-3 text-sm font-bold focus:ring-2 focus:ring-[var(--upel-blue)]">
              <option :value="null" disabled>Seleccione una carrera...</option>
              <option v-for="c in careers" :key="c.id" :value="c.id">{{ c.name }}</option>
            </select>
          </div>
          <button @click="openAddToPlanModal" :disabled="!selectedCareerId" class="mb-0.5 px-6 py-3 bg-[var(--upel-blue)] text-white rounded-2xl font-bold text-sm shadow-lg shadow-blue-500/20 disabled:opacity-50 transition-all hover:scale-[1.02]">
            Asignar Unidad
          </button>
        </div>

        <div v-if="selectedCareerId" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
          <div v-for="sem in 8" :key="sem" class="bg-white rounded-[32px] p-6 border border-gray-100 shadow-sm flex flex-col min-h-[400px]">
            <div class="flex items-center justify-between mb-6">
              <h4 class="text-sm font-black text-gray-900 uppercase tracking-tighter italic">Semestre {{ sem }}</h4>
              <span class="h-6 w-6 rounded-full bg-gray-50 text-gray-400 flex items-center justify-center text-[10px] font-bold">{{ getUnitsBySemester(sem).length }}</span>
            </div>
            <div class="flex-1 overflow-y-auto custom-scrollbar pr-1 h-[300px]">
               <div v-if="getUnitsBySemester(sem).length === 0" class="h-full flex flex-col items-center justify-center opacity-20 grayscale border-2 border-dashed border-gray-100 rounded-[40px] p-10">
                  <ClockIcon class="w-12 h-12 mb-2 text-gray-400" />
                  <span class="text-[9px] font-black uppercase tracking-tighter italic">Vacío</span>
               </div>
               <div v-for="item in getUnitsBySemester(sem)" :key="item.id" class="group/item flex items-center justify-between p-4 mb-3 bg-gray-50/50 rounded-2xl border border-transparent hover:bg-white hover:border-blue-100 hover:shadow-lg transition-all relative overflow-hidden">
                 <div class="flex-1 min-w-0">
                   <div class="flex items-center gap-2 mb-1.5">
                     <span :class="getComponentClass(item.curricular_unit_info?.component)" class="px-2 py-0.5 rounded-lg text-[8px] font-black uppercase tracking-tight shadow-sm">{{ item.curricular_unit_info?.component || 'UC' }}</span>
                     <span class="text-[9px] font-mono text-gray-400 font-bold tracking-tighter italic opacity-60">REF: {{ item.curricular_unit_info?.code }}</span>
                   </div>
                   <div class="text-[11px] font-black text-gray-800 leading-tight italic uppercase tracking-tighter truncate">{{ item.curricular_unit_info?.name }}</div>
                   <div class="flex items-center gap-3 mt-2 text-[9px] font-bold text-gray-400">
                      <div class="flex items-center gap-1"><ClockIcon class="w-3 h-3" /> {{ item.curricular_unit_info?.hours }}H</div>
                      <div class="flex items-center gap-1 font-black text-blue-400">{{ item.curricular_unit_info?.credits }} CRED</div>
                   </div>
                 </div>
                 <button @click="removeFromPlan(item.id)" class="opacity-0 group-hover/item:opacity-100 p-2 text-gray-200 hover:text-red-500 transition-all font-black text-xs shrink-0 bg-white rounded-lg shadow-sm border border-gray-100">
                    <TrashIcon class="w-4 h-4" />
                 </button>
               </div>
            </div>
          </div>
        </div>

        <div v-else class="py-20 text-center bg-white rounded-[40px] border border-dashed border-gray-200 shadow-inner">
          <AcademicCapIcon class="w-16 h-16 text-gray-100 mx-auto mb-4" />
          <p class="text-gray-400 font-bold italic">Seleccione una especialidad para gestionar su malla curricular.</p>
        </div>
      </div>

      <!-- Tab Content: Sedes y Núcleos -->
      <div v-if="activeTab === 'assignments'" class="animate-fade-in">
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <!-- Columna Sedes -->
          <div class="lg:col-span-1 space-y-6">
            <div class="bg-white rounded-3xl p-6 border border-gray-100 shadow-sm relative overflow-hidden">
              <div class="flex justify-between items-center mb-6 px-2">
                <h3 class="text-lg font-black text-gray-900 flex items-center gap-2">
                  <div class="h-8 w-2 bg-blue-500 rounded-full"></div>
                  Sedes
                </h3>
                <button @click="openSedeModal" class="p-2 bg-blue-50 text-[var(--upel-blue)] rounded-xl hover:bg-blue-100 transition-all">
                  <PlusIcon class="w-4 h-4" />
                </button>
              </div>
              
              <div class="space-y-2 max-h-[600px] overflow-y-auto pr-2 custom-scrollbar">
                <button 
                  v-for="sede in sedes" :key="sede.id"
                  @click="selectedSedeId = sede.id; selectedNucleoId = null"
                  class="w-full text-left p-4 rounded-2xl border transition-all flex items-center justify-between group"
                  :class="selectedSedeId === sede.id ? 'bg-blue-50 border-blue-200 shadow-sm' : 'bg-gray-50/50 border-transparent hover:bg-white hover:border-gray-200'"
                >
                  <div class="flex-1">
                    <div class="flex items-center gap-2 mb-0.5">
                      <span class="text-xs font-black text-blue-600 bg-white px-2 py-0.5 rounded-lg shadow-xs border border-blue-100">{{ sede.sigla || 'UPEL' }}</span>
                      <div class="text-[13px] font-black text-gray-800 group-hover:text-[var(--upel-blue)]">{{ sede.name }}</div>
                    </div>
                    <div class="text-[10px] text-gray-400 font-medium px-0.5">{{ sede.city || 'Ubicación no especificada' }}</div>
                  </div>
                  <ChevronRightIcon class="w-4 h-4 text-gray-300 group-hover:text-blue-500" />
                </button>
              </div>
            </div>

            <!-- Autoridades de la Sede -->
            <div v-if="selectedSedeId" class="bg-white rounded-[32px] p-6 border border-gray-100 shadow-sm animate-fade-in">
              <div class="flex justify-between items-center mb-6">
                <h4 class="text-[11px] font-black text-gray-400 uppercase tracking-widest">Autoridades {{ getSelectedSede?.sigla }}</h4>
                <button @click="openAuthorityModal" class="p-2 bg-blue-50 text-[var(--upel-blue)] rounded-xl hover:bg-blue-100 transition-all">
                  <PlusIcon class="w-4 h-4" />
                </button>
              </div>
              
              <DataTable :value="filteredAuthorities" class="p-datatable-sm" stripedRows>
                <template #empty>
                  <div class="py-4 text-center text-[10px] text-gray-300 font-bold italic uppercase">Sin autoridades</div>
                </template>
                <Column header="NOMBRE / CARGO">
                  <template #body="{ data }">
                    <div class="py-1">
                      <div class="text-[10px] font-black text-gray-800 italic leading-none mb-1">{{ data.name }}</div>
                      <div class="text-[8px] text-gray-400 font-bold uppercase tracking-tighter">{{ data.position }}</div>
                    </div>
                  </template>
                </Column>
                <Column class="text-right">
                  <template #body="{ data }">
                    <button @click="removeAuthority(data.id)" class="p-1 px-2 text-gray-200 hover:text-red-400 transition-all">
                       <TrashIcon class="w-3 h-3" />
                    </button>
                  </template>
                </Column>
              </DataTable>
            </div>
          </div>

          <!-- Columna Núcleos y Carreras -->
          <div class="lg:col-span-2 space-y-8">
            <div v-if="selectedSedeId" class="animate-fade-in space-y-8">
              <!-- Núcleos -->
              <div class="bg-white rounded-3xl p-8 border border-gray-100 shadow-sm">
                <div class="flex justify-between items-center mb-8">
                  <h4 class="text-sm font-black text-gray-400 uppercase tracking-widest">Núcleos Académicos</h4>
                  <button @click="openNucleoModal" class="px-5 py-2.5 bg-gray-50 text-[11px] font-black text-gray-600 rounded-xl hover:bg-[var(--upel-blue)] hover:text-white transition-all shadow-sm">
                    Nuevo Núcleo
                  </button>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div 
                    v-for="n in getNucleosBySede" :key="n.id" 
                    @click="selectedNucleoId = n.id"
                    class="p-6 rounded-[32px] border transition-all cursor-pointer group relative overflow-hidden"
                    :class="selectedNucleoId === n.id ? 'bg-indigo-50 border-indigo-200 shadow-lg' : 'bg-gray-50/50 border-transparent hover:bg-white hover:border-blue-100 hover:shadow-xl'"
                  >
                    <div class="absolute -right-4 -bottom-4 opacity-5 group-hover:scale-110 transition-transform">
                      <MapPinIcon class="w-24 h-24" />
                    </div>
                    <div class="flex items-center gap-4 mb-4">
                      <div class="h-10 w-10 bg-white shadow-sm rounded-xl flex items-center justify-center border border-gray-50">
                        <MapPinIcon class="w-5 h-5 text-indigo-500" />
                      </div>
                      <div>
                        <div class="font-black text-gray-900 text-sm italic">{{ n.name }}</div>
                        <div class="text-[10px] text-indigo-400 font-bold uppercase tracking-tight">Núcleo Activo</div>
                      </div>
                    </div>
                    <p class="text-[11px] text-gray-400 font-medium mb-4 line-clamp-1 italic">{{ n.address || 'Sin dirección registrada' }}</p>
                    <div class="flex items-center justify-between mt-6">
                       <span class="text-[9px] font-black text-gray-300 uppercase italic px-1">CÓDIGO: {{ n.id }}</span>
                       <div class="flex gap-1">
                          <button @click.stop="removeNucleo(n.id)" class="p-2 text-gray-300 hover:text-red-500 transition-all">
                             <TrashIcon class="w-4 h-4" />
                          </button>
                       </div>
                    </div>
                  </div>
                  <div v-if="getNucleosBySede.length === 0" class="md:col-span-2 py-10 text-center text-gray-300 font-bold italic uppercase border-2 border-dashed border-gray-50 rounded-[40px]">No hay núcleos registrados en esta sede</div>
                </div>
              </div>

              <!-- Oferta Académica (Sede o Núcleo seleccionado) -->
              <div class="bg-white rounded-3xl p-8 border border-gray-100 shadow-sm relative overflow-hidden">
                <div class="absolute top-0 right-0 p-4">
                  <DocumentIcon class="w-12 h-12 text-blue-50/50" />
                </div>
                
                <div class="flex justify-between items-center mb-8">
                   <div>
                     <h4 class="text-sm font-black text-gray-900 uppercase tracking-tighter italic">
                       {{ selectedNucleoId ? 'Oferta Específica del Núcleo' : 'Oferta Académica de la Sede' }}
                     </h4>
                     <p class="text-[10px] text-gray-400 font-bold mt-1">
                       {{ selectedNucleoId ? 'Carreras habilitadas para este núcleo' : 'Afecta a todos los núcleos de la sede' }}
                     </p>
                   </div>
                   <button @click="openSedeAssignModal" class="px-5 py-2.5 bg-emerald-50 text-emerald-600 border border-emerald-100 rounded-xl text-[10px] font-black hover:bg-emerald-500 hover:text-white transition-all shadow-sm">
                     + Vincular Carrera
                   </button>
                </div>

                <!-- DataTable de Oferta -->
                <div class="bg-gray-50/30 rounded-2xl border border-gray-100 overflow-hidden min-h-[300px]">
                  <DataTable 
                    :value="currentAssignments" 
                    :paginator="true" 
                    :rows="5"
                    stripedRows
                    class="p-datatable-sm overflow-hidden"
                  >
                    <template #empty>
                      <div class="p-12 text-center opacity-40 font-black uppercase text-[10px] italic">Sin oferta vinculada</div>
                    </template>

                    <Column header="ESPECIALIDAD / CARRERA" sortable :sortField="(d) => getCareerInfo(d.career_id).name">
                      <template #body="{ data }">
                        <div class="flex items-center gap-3 py-1">
                          <div class="h-8 w-8 rounded-lg bg-white border border-gray-100 flex items-center justify-center font-black text-[10px] text-[var(--upel-blue)]">
                            {{ getCareerInfo(data.career_id).code?.[0] || 'C' }}
                          </div>
                          <div>
                            <div class="text-[11px] font-black text-gray-800 leading-none mb-1 italic">{{ getCareerInfo(data.career_id).name }}</div>
                            <div class="text-[9px] text-gray-400 font-bold uppercase">{{ getCareerInfo(data.career_id).faculty }}</div>
                          </div>
                        </div>
                      </template>
                    </Column>

                    <Column header="CÓDIGO" class="text-center">
                       <template #body="{ data }">
                         <span class="text-[10px] font-mono font-bold text-gray-400 capitalize bg-white px-2 py-0.5 rounded border border-gray-100">{{ getCareerInfo(data.career_id).code }}</span>
                       </template>
                    </Column>

                    <Column header="ACCIONES" class="text-right">
                      <template #body="{ data }">
                        <button @click="removeAssignment(data)" class="p-2 text-gray-300 hover:text-red-500 transition-all active:scale-90">
                           <TrashIcon class="w-4 h-4" />
                        </button>
                      </template>
                    </Column>
                  </DataTable>
                </div>
              </div>
            </div>

            <div v-else class="h-full flex flex-col items-center justify-center p-20 bg-white rounded-[40px] border border-dashed border-gray-100">
               <MapIcon class="w-20 h-20 text-gray-50 mb-6" />
               <p class="text-gray-400 font-bold italic">Seleccione una sede para gestionar sus núcleos, autoridades y oferta territorial.</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Unified Action Modal -->
      <Teleport to="body">
        <div v-if="modal.show" class="fixed inset-0 bg-gray-900/70 backdrop-blur-md z-[100] flex items-center justify-center p-4">
          <div class="bg-white rounded-[40px] w-full max-w-xl shadow-2xl overflow-hidden animate-fade-in text-gray-900 border border-white/20">
            <div class="p-10 border-b border-gray-50 flex justify-between items-center bg-gray-50/50">
              <div>
                <h2 class="text-2xl font-black text-gray-900 leading-none mb-2">{{ modal.title }}</h2>
                <p class="text-[11px] text-gray-400 font-bold uppercase tracking-widest">{{ modal.subtitle }}</p>
              </div>
              <button @click="modal.show = false" class="h-12 w-12 flex items-center justify-center hover:bg-white rounded-2xl transition-all text-gray-400 font-black text-2xl shadow-sm border border-transparent hover:border-gray-100">&times;</button>
            </div>
            
            <form @submit.prevent="handleModalSubmit" class="p-10 space-y-6">
              <!-- Career/Unit fields -->
              <template v-if="modal.type === 'career' || modal.type === 'unit'">
                <div>
                  <label class="block text-[11px] font-black uppercase text-gray-400 mb-3 px-1">Identificador / Código</label>
                  <input v-model="form.code" type="text" placeholder="Ej: EDU-IPB-01" class="w-full bg-gray-50 border-gray-100 border rounded-2xl px-6 py-4 text-sm font-bold focus:ring-4 focus:ring-blue-500/10 focus:bg-white transition-all outline-none" required>
                </div>
                <div>
                  <label class="block text-[11px] font-black uppercase text-gray-400 mb-3 px-1">Nombre Completo</label>
                  <input v-model="form.name" type="text" placeholder="Ej: Educación Especial" class="w-full bg-gray-50 border-gray-100 border rounded-2xl px-6 py-4 text-sm font-bold focus:ring-4 focus:ring-blue-500/10 focus:bg-white transition-all outline-none" required>
                </div>
                <div v-if="modal.type === 'career'">
                  <label class="block text-[11px] font-black uppercase text-gray-400 mb-3 px-1">Facultad / Departamento</label>
                  <input v-model="form.faculty" type="text" placeholder="Ej: Ciencias Naturales" class="w-full bg-gray-50 border-gray-100 border rounded-2xl px-6 py-4 text-sm font-bold focus:ring-4 focus:ring-blue-500/10 focus:bg-white transition-all outline-none">
                </div>
                <div v-if="modal.type === 'unit'" class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="block text-[11px] font-black uppercase text-gray-400 mb-3 px-1">Componente</label>
                    <select v-model="form.component" class="w-full bg-gray-50 border-gray-100 border rounded-2xl px-6 py-4 text-sm font-bold focus:ring-4 focus:ring-blue-500/10 focus:bg-white transition-all outline-none">
                      <option value="CFPE">CFPE (Específico)</option>
                      <option value="CFD">CFD (Docente)</option>
                      <option value="CFC">CFC (Contextual)</option>
                      <option value="ECU">ECU (Eje)</option>
                    </select>
                  </div>
                  <div>
                    <label class="block text-[11px] font-black uppercase text-gray-400 mb-3 px-1">Créditos (UC)</label>
                    <input v-model="form.credits" type="number" class="w-full bg-gray-50 border-gray-100 border rounded-2xl px-6 py-4 text-sm font-bold focus:ring-4 focus:ring-blue-500/10 focus:bg-white transition-all outline-none" required>
                  </div>
                </div>
              </template>

              <!-- Sede fields -->
              <template v-if="modal.type === 'sede'">
                <div class="grid grid-cols-3 gap-4">
                  <div class="col-span-1">
                    <label class="block text-[11px] font-black uppercase text-gray-400 mb-3 px-1">Sigla</label>
                    <input v-model="form.sigla" type="text" placeholder="Ej: IPB" class="w-full bg-gray-50 border-gray-100 border rounded-2xl px-6 py-4 text-sm font-bold focus:ring-4 focus:ring-blue-500/10 outline-none uppercase" required>
                  </div>
                  <div class="col-span-2">
                    <label class="block text-[11px] font-black uppercase text-gray-400 mb-3 px-1">Nombre de la Sede</label>
                    <input v-model="form.name" type="text" placeholder="Ej: Instituto Pedagógico de Barquisimeto" class="w-full bg-gray-50 border-gray-100 border rounded-2xl px-6 py-4 text-sm font-bold focus:ring-4 focus:ring-blue-500/10 outline-none" required>
                  </div>
                </div>
                <div>
                  <label class="block text-[11px] font-black uppercase text-gray-400 mb-3 px-1">Ciudad</label>
                  <input v-model="form.city" type="text" class="w-full bg-gray-50 border-gray-100 border rounded-2xl px-6 py-4 text-sm font-bold focus:ring-4 focus:ring-blue-500/10 outline-none px-1">
                </div>
              </template>

              <!-- Nucleo fields -->
              <template v-if="modal.type === 'nucleo'">
                <div>
                   <label class="block text-[11px] font-black uppercase text-gray-400 mb-3 px-1">Nombre del Núcleo</label>
                   <input v-model="form.name" type="text" placeholder="Ej: Núcleo Chivacoa" class="w-full bg-gray-50 border-gray-100 border rounded-2xl px-6 py-4 text-sm font-bold outline-none" required>
                </div>
                <div>
                   <label class="block text-[11px] font-black uppercase text-gray-400 mb-3 px-1">Sede de Pertenencia</label>
                   <select v-model="form.sede" class="w-full bg-gray-50 border-gray-100 border rounded-2xl px-6 py-4 text-sm font-bold outline-none" required>
                     <option v-for="s in sedes" :key="s.id" :value="s.id">{{ s.sigla }} - {{ s.name }}</option>
                   </select>
                </div>
              </template>

              <!-- Authority fields -->
              <template v-if="modal.type === 'authority'">
                <div>
                   <label class="block text-[11px] font-black uppercase text-gray-400 mb-3 px-1">Título y Nombre</label>
                   <input v-model="form.name" type="text" placeholder="Ej: Dra. Elena Méndez" class="w-full bg-gray-50 border-gray-100 border rounded-2xl px-6 py-4 text-sm font-bold outline-none" required>
                </div>
                <div>
                   <label class="block text-[11px] font-black uppercase text-gray-400 mb-3 px-1">Cargo Institucional</label>
                   <input v-model="form.position" type="text" placeholder="Ej: Director del IPB" class="w-full bg-gray-50 border-gray-100 border rounded-2xl px-6 py-4 text-sm font-bold outline-none" required>
                </div>
                <div class="grid grid-cols-2 gap-4">
                   <div>
                     <label class="block text-[11px] font-black uppercase text-gray-400 mb-3 px-1">Sede Asignada</label>
                     <select v-model="form.sede" class="w-full bg-gray-50 border-gray-100 border rounded-2xl px-6 py-4 text-sm font-bold outline-none">
                       <option :value="null">Rectorado (Nacional)</option>
                       <option v-for="s in sedes" :key="s.id" :value="s.id">{{ s.sigla }}</option>
                     </select>
                   </div>
                   <div>
                     <label class="block text-[11px] font-black uppercase text-gray-400 mb-3 px-1">Orden de Firma</label>
                     <input v-model="form.order" type="number" class="w-full bg-gray-50 border-gray-100 border rounded-2xl px-6 py-4 text-sm font-bold outline-none">
                   </div>
                </div>
              </template>

              <!-- Assignment fields -->
              <template v-if="modal.type === 'assignment'">
                <div>
                  <label class="block text-[11px] font-black uppercase text-gray-400 mb-3 px-1">Especialidad (Carrera)</label>
                  <select v-model="form.career_id" class="w-full bg-gray-50 border-gray-100 border rounded-2xl px-6 py-4 text-sm font-bold outline-none" required>
                    <option v-for="c in careers" :key="c.id" :value="c.id">{{ c.name }}</option>
                  </select>
                </div>
                <div v-if="selectedNucleoId">
                   <p class="p-4 bg-amber-50 text-amber-600 rounded-2xl text-[10px] font-bold border border-amber-100 italic">
                     La especialidad se vinculará directamente al núcleo: <strong>{{ getSelectedNucleo?.name }}</strong>.
                   </p>
                </div>
              </template>

              <!-- Plan Item fields -->
              <template v-if="modal.type === 'plan_item'">
                <div>
                   <label class="block text-[11px] font-black uppercase text-gray-400 mb-3 px-1">Unidad Curricular</label>
                   <select v-model="form.curricular_unit" class="w-full bg-gray-50 border-gray-100 border rounded-2xl px-6 py-4 text-sm font-bold outline-none" required>
                     <option v-for="u in units" :key="u.id" :value="u.id">{{ u.code }} - {{ u.name }}</option>
                   </select>
                </div>
                <div class="grid grid-cols-2 gap-4">
                   <div>
                     <label class="block text-[11px] font-black uppercase text-gray-400 mb-3 px-1">Semestre</label>
                     <input v-model="form.academic_period" type="number" min="1" max="8" class="w-full bg-gray-50 border-gray-100 border rounded-2xl px-6 py-4 text-sm font-bold outline-none" required>
                   </div>
                   <div>
                     <label class="block text-[11px] font-black uppercase text-gray-400 mb-3 px-1">Posición/Orden</label>
                     <input v-model="form.order" type="number" min="1" class="w-full bg-gray-50 border-gray-100 border rounded-2xl px-6 py-4 text-sm font-bold outline-none" required>
                   </div>
                </div>
              </template>

              <div class="pt-8 flex gap-4">
                <button type="button" @click="modal.show = false" class="flex-1 px-8 py-4 rounded-[20px] font-bold text-sm text-gray-500 hover:bg-gray-100 transition-all border border-transparent hover:border-gray-200">
                  Cerrar
                </button>
                <button type="submit" :disabled="loading" class="flex-[2] bg-[var(--upel-blue)] text-white px-8 py-4 rounded-[24px] font-black text-sm shadow-xl shadow-blue-500/30 hover:shadow-blue-500/50 hover:scale-[1.02] active:scale-95 transition-all disabled:opacity-50 flex items-center justify-center gap-3">
                   <span v-if="loading" class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                   Procesar Solicitud
                </button>
              </div>
            </form>
          </div>
        </div>
      </Teleport>

    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, reactive, watch } from 'vue'
import AdminSidebar from '@/components/AdminSidebar.vue'
import axios from 'axios'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import { 
  PlusIcon, 
  ClockIcon, 
  IdentificationIcon, 
  PencilIcon,
  AcademicCapIcon,
  BookOpenIcon,
  MapIcon,
  DocumentIcon,
  ChevronRightIcon,
  MapPinIcon,
  Cog6ToothIcon,
  MagnifyingGlassIcon,
  TrashIcon
} from '@heroicons/vue/24/outline'

const activeTab = ref('careers')
const loading = ref(false)
const searchUnits = ref('')
const searchCareers = ref('')

// Computed & Helpers
const filteredCareers = computed(() => {
  if (!searchCareers.value) return careers.value
  const q = searchCareers.value.toLowerCase()
  return careers.value.filter(c => 
    (c.name || '').toLowerCase().includes(q) || 
    (c.code || '').toLowerCase().includes(q)
  )
})

const tabs = [
  { id: 'careers', name: 'Especialidades' },
  { id: 'units', name: 'Unidades Curriculares' },
  { id: 'plans', name: 'Planes de Estudio' },
  { id: 'assignments', name: 'Sedes y Núcleos' },
]

const careers = ref([])
const units = ref([])

const filteredUnits = computed(() => {
  if (!searchUnits.value) return units.value
  const q = searchUnits.value.toLowerCase()
  return units.value.filter(u => 
    (u.name || '').toLowerCase().includes(q) || 
    (u.code || '').toLowerCase().includes(q)
  )
})

const sedes = ref([])
const nucleos = ref([])
const authorities = ref([])
const currentCareerPlan = ref([])
const sedeAssignments = ref([])
const nucleoAssignments = ref([])

// Selection States
const selectedCareerId = ref(null)
const selectedSedeId = ref(null)
const selectedNucleoId = ref(null)

// Modal State
const modal = reactive({
  show: false,
  type: 'career',
  title: '',
  subtitle: ''
})

const form = reactive({})

// Data Fetching
const fetchData = async () => {
  loading.value = true
  try {
    const [careersRes, unitsRes, sedesRes, nucleosRes, authRes] = await Promise.all([
      axios.get('/api/students/careers/'),
      axios.get('/api/curriculum/curricular-units/'),
      axios.get('/api/sedes/'),
      axios.get('/api/nucleos/'),
      axios.get('/api/authorities/')
    ])
    careers.value = careersRes.data.results || careersRes.data
    units.value = unitsRes.data.results || unitsRes.data
    sedes.value = sedesRes.data.results || sedesRes.data
    nucleos.value = nucleosRes.data.results || nucleosRes.data
    authorities.value = authRes.data.results || authRes.data
    
    if (sedes.value.length > 0 && !selectedSedeId.value) {
      selectedSedeId.value = sedes.value[0].id
    }
  } catch (err) {
    console.error('Error fetching global curriculum data:', err)
  } finally {
    loading.value = false
  }
}

const fetchCareerPlan = async () => {
  if (!selectedCareerId.value) return
  try {
    const res = await axios.get(`/api/curriculum/career-plan/?career_id=${selectedCareerId.value}`)
    currentCareerPlan.value = res.data.results || res.data
  } catch (err) {
    console.error('Error fetching plan:', err)
  }
}

const fetchTerritorialAssignments = async () => {
  if (!selectedSedeId.value) return
  try {
    const endpoints = [
       axios.get(`/api/curriculum/career-sede/?sede_id=${selectedSedeId.value}`)
    ]
    if (selectedNucleoId.value) {
       endpoints.push(axios.get(`/api/curriculum/career-nucleo/?nucleo_id=${selectedNucleoId.value}`))
    }
    
    const [sedeRes, nucleoRes] = await Promise.all(endpoints)
    sedeAssignments.value = sedeRes.data.results || sedeRes.data
    if (nucleoRes) nucleoAssignments.value = nucleoRes.data.results || nucleoRes.data
    else nucleoAssignments.value = []
  } catch (err) {
    console.error('Error fetching territorial info:', err)
  }
}

// Modal Handlers
const openGeneralCreate = () => {
  if (activeTab.value === 'careers') openCareerModal()
  else if (activeTab.value === 'units') openUnitModal()
  else if (activeTab.value === 'plans') openAddToPlanModal()
  else if (activeTab.value === 'assignments') openSedeModal()
}

const openCareerModal = () => {
  Object.assign(form, { code: '', name: '', faculty: '' })
  modal.type = 'career'; modal.title = 'Nueva Especialidad'; modal.subtitle = 'Catálogo de Carreras UPEL'; modal.show = true
}

const openUnitModal = () => {
  Object.assign(form, { code: '', name: '', component: 'CFPE', credits: 4 })
  modal.type = 'unit'; modal.title = 'Unidad Curricular'; modal.subtitle = 'Definición de materia global'; modal.show = true
}

const openSedeModal = () => {
  Object.assign(form, { name: '', sigla: '', city: '' })
  modal.type = 'sede'; modal.title = 'Registrar Sede'; modal.subtitle = 'Expansión territorial institucional'; modal.show = true
}

const openNucleoModal = () => {
  Object.assign(form, { name: '', sede: selectedSedeId.value, address: '' })
  modal.type = 'nucleo'; modal.title = 'Nuevo Núcleo'; modal.subtitle = `Dependencia de ${getSelectedSede.value?.sigla}`; modal.show = true
}

const openAuthorityModal = () => {
  Object.assign(form, { name: '', position: '', sede: selectedSedeId.value, order: 0 })
  modal.type = 'authority'; modal.title = 'Asignar Autoridad'; modal.subtitle = 'Nombramiento de cargo oficial'; modal.show = true
}

const openAddToPlanModal = () => {
  Object.assign(form, { curricular_unit: null, academic_period: 1, order: 1 })
  modal.type = 'plan_item'; modal.title = 'Añadir al Plan'; modal.subtitle = `Modificando: ${getCareerInfo(selectedCareerId.value)?.name}`; modal.show = true
}

const openSedeAssignModal = () => {
  Object.assign(form, { career_id: null })
  modal.type = 'assignment'; modal.title = 'Vincular Especialidad'; modal.subtitle = 'Asignación de oferta territorial'; modal.show = true
}

// Submission Logic
const handleModalSubmit = async () => {
  loading.value = true
  try {
    let endpoint = ''
    let data = { ...form }

    switch (modal.type) {
      case 'career': endpoint = '/api/students/careers/'; break
      case 'unit': endpoint = '/api/curriculum/curricular-units/'; break
      case 'sede': endpoint = '/api/sedes/'; break
      case 'nucleo': endpoint = '/api/nucleos/'; break
      case 'authority': endpoint = '/api/authorities/'; break
      case 'plan_item': 
        endpoint = '/api/curriculum/career-plan/'
        data.career_id = selectedCareerId.value
        break
      case 'assignment':
        if (selectedNucleoId.value) {
           endpoint = '/api/curriculum/career-nucleo/'
           data.nucleo_id = selectedNucleoId.value
        } else {
           endpoint = '/api/curriculum/career-sede/'
           data.sede_id = selectedSedeId.value
        }
        break
    }

    await axios.post(endpoint, data)
    modal.show = false
    await fetchData()
    if (activeTab.value === 'plans') await fetchCareerPlan()
    if (activeTab.value === 'assignments') await fetchTerritorialAssignments()
  } catch (err) {
    console.error('Submit error:', err)
    alert(err.response?.data?.non_field_errors?.[0] || 'Error al procesar la solicitud.')
  } finally {
    loading.value = false
  }
}

const removeAssignment = async (assign) => {
  if (!confirm('¿Desea eliminar este vínculo territorial?')) return
  try {
    const isNucleo = !!assign.nucleo_id
    await axios.delete(`/api/curriculum/career-${isNucleo ? 'nucleo' : 'sede'}/${assign.id}/`)
    await fetchTerritorialAssignments()
  } catch (err) {
    console.error('Delete assignment error:', err)
  }
}

const removeFromPlan = async (id) => {
  if (!confirm('¿Desea eliminar esta unidad de la malla curricular?')) return
  try {
    await axios.delete(`/api/curriculum/career-plan/${id}/`)
    await fetchCareerPlan()
  } catch (err) {
    console.error('Delete plan item error:', err)
  }
}

const removeAuthority = async (id) => {
  if (!confirm('¿Desea eliminar este nombramiento oficial?')) return
  try {
    await axios.delete(`/api/authorities/${id}/`)
    await fetchData()
  } catch (err) {
    console.error('Delete authority error:', err)
  }
}

const removeNucleo = async (id) => {
  if (!confirm('¿Desea desactivar este núcleo?')) return
  try {
    await axios.delete(`/api/nucleos/${id}/`)
    await fetchData()
    if (selectedNucleoId.value === id) selectedNucleoId.value = null
  } catch (err) {
    console.error('Delete nucleo error:', err)
  }
}

// Computed & Helpers
const getUnitsBySemester = (sem) => {
  return currentCareerPlan.value.filter(item => item.academic_period === sem)
}

const getCareerInfo = (id) => {
  return careers.value.find(c => c.id === id) || { name: 'Desconocido' }
}

const getSelectedSede = computed(() => {
  return sedes.value.find(s => s.id === selectedSedeId.value)
})

const getSelectedNucleo = computed(() => {
  return nucleos.value.find(n => n.id === selectedNucleoId.value)
})

const getNucleosBySede = computed(() => {
  return nucleos.value.filter(n => n.sede_id === selectedSedeId.value)
})

const filteredAuthorities = computed(() => {
  return authorities.value.filter(a => a.sede === selectedSedeId.value || (selectedSedeId.value === null && a.sede === null))
})

const currentAssignments = computed(() => {
  return selectedNucleoId.value ? nucleoAssignments.value : sedeAssignments.value
})

const getComponentClass = (comp) => {
  const map = {
    'CFPE': 'bg-blue-50 text-blue-600 border border-blue-100',
    'CFD':  'bg-amber-50 text-amber-600 border border-amber-100',
    'CFC':  'bg-emerald-50 text-emerald-600 border border-emerald-100',
    'ECU':  'bg-purple-50 text-purple-600 border border-purple-100',
  }
  return map[comp] || 'bg-gray-50 text-gray-600 border border-gray-100'
}

watch([selectedSedeId, selectedNucleoId], fetchTerritorialAssignments)

onMounted(fetchData)
</script>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #E2E8F0;
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #CBD5E1;
}

:root {
  --upel-blue: #004A99;
}
</style>
