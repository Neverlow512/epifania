<template>
  <div class="card bg-black/30 border border-primary/20">
    <div class="card-body p-3">
      <h4 class="text-sm font-semibold text-white mb-2">Frida Session</h4>
      
      <div class="space-y-2 mb-3">
        <div class="flex items-center justify-between text-sm">
          <span class="text-slate-400">Status:</span>
          <div class="flex items-center gap-2">
            <div 
              class="w-2 h-2 rounded-full" 
              :class="statusIndicatorClass"
            ></div>
            <span :class="statusTextClass">{{ statusText }}</span>
          </div>
        </div>
        
        <div v-if="attached && attachedPid" class="flex items-center justify-between text-sm">
          <span class="text-slate-400">PID:</span>
          <span class="text-white font-mono">{{ attachedPid }}</span>
        </div>
        
        <div v-if="attached && sessionNumber" class="flex items-center justify-between text-sm">
          <span class="text-slate-400">Session:</span>
          <span class="text-purple-400 font-mono">#{{ sessionNumber }}</span>
        </div>
        
        <div v-if="statusMessage" class="text-xs mt-1" :class="crashed ? 'text-red-400' : 'text-slate-500'">
          {{ statusMessage }}
        </div>
        
        <div v-if="!spawnModeEnabled && !selectedProcess" class="text-xs text-yellow-400/70 mt-1">
          Select a process first
        </div>
        
        <div v-else-if="!fridaServerRunning" class="text-xs text-yellow-400/70 mt-1">
          Start Frida server first
        </div>
      </div>
      
      <div class="flex gap-2 mb-3">
        <button 
          type="button"
          class="btn btn-xs btn-success flex-1"
          :disabled="!canAttach"
          @click="handleAttach"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
          </svg>
          Attach
        </button>
        <button 
          type="button"
          class="btn btn-xs btn-error flex-1"
          :disabled="!canDetach"
          @click="handleDetach"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
          </svg>
          Detach
        </button>
        <button 
          type="button"
          class="btn btn-xs btn-primary flex-1"
          :disabled="!canSpawn"
          @click="handleSpawn"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Start App
        </button>
      </div>
      
      <div class="border-t border-primary/10 pt-3 space-y-2">
        <label class="label cursor-pointer justify-start gap-2 py-1">
          <input 
            type="checkbox" 
            class="checkbox checkbox-xs checkbox-primary" 
            v-model="spawnModeEnabled"
          />
          <span class="label-text text-xs text-white">{{ isInstrumentationMode ? 'Spawn app' : 'Spawn app on next discovery' }}</span>
        </label>
        
        <div v-if="spawnModeEnabled" class="space-y-2">
          <div class="flex gap-2">
            <select 
              v-model="selectedSpawnPackage"
              class="select select-bordered select-xs w-full bg-black border-primary/30 focus:border-primary text-white"
              :disabled="packagesLoading"
            >
              <option value="" disabled>{{ packagesLoading ? 'Loading packages...' : 'Select app to spawn' }}</option>
              <option 
                v-for="pkg in spawnPackages" 
                :key="pkg.package_id"
                :value="pkg.package_id"
              >
                {{ pkg.package_id }}
              </option>
            </select>
            <button 
              type="button"
              class="btn btn-xs btn-ghost btn-square bg-neutral-900/40 border border-primary/35 text-primary/80 hover:bg-primary/10"
              @click="handleRefreshPackages"
              :disabled="packagesLoading"
              title="Refresh package list"
            >
              <svg v-if="!packagesLoading" xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              <span v-else class="loading loading-spinner loading-xs text-primary"></span>
            </button>
          </div>
          
          <div v-if="!selectedSpawnPackage" class="text-xs text-yellow-400/70">
            Select a package to spawn
          </div>
          
          <div class="border-t border-primary/10 pt-2 space-y-1.5">
            <label class="text-xs text-gray-400">Package filter</label>
            <div class="flex flex-col gap-1">
              <label class="label cursor-pointer justify-start gap-2 py-0.5">
                <input 
                  type="radio" 
                  name="packageFilter" 
                  class="radio radio-xs radio-primary" 
                  :value="false"
                  v-model="includeSystemPackages"
                />
                <span class="label-text text-xs text-white">User apps only</span>
              </label>
              <label class="label cursor-pointer justify-start gap-2 py-0.5">
                <input 
                  type="radio" 
                  name="packageFilter" 
                  class="radio radio-xs radio-primary" 
                  :value="true"
                  v-model="includeSystemPackages"
                />
                <span class="label-text text-xs text-white">All packages (including system)</span>
              </label>
            </div>
            <div v-if="includeSystemPackages" class="text-xs text-yellow-400/70 flex items-start gap-1">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 mt-0.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <span>System packages may be numerous and some cannot be spawned</span>
            </div>
          </div>
          
          <div class="space-y-1.5">
            <label class="text-xs text-gray-400">Wait after spawn (seconds)</label>
            <input 
              type="number"
              v-model.number="spawnDelay"
              min="0"
              max="600"
              class="input input-bordered input-xs w-full bg-black border-primary/30 focus:border-primary text-white"
            />
            <div class="text-xs text-gray-500">
              Time to wait for app to load classes (0-600s, default: 30s)
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted } from 'vue'
import { useSpawnPackages } from '../../composables/useSpawnPackages'

export default {
  name: 'FridaWorkshopControls',
  props: {
    attached: {
      type: Boolean,
      default: false
    },
    attachedPid: {
      type: [Number, String],
      default: null
    },
    sessionNumber: {
      type: [Number, String],
      default: null
    },
    statusMessage: {
      type: String,
      default: ''
    },
    crashed: {
      type: Boolean,
      default: false
    },
    selectedProcess: {
      type: Object,
      default: null
    },
    fridaServerRunning: {
      type: Boolean,
      default: false
    },
    hasLock: {
      type: Boolean,
      default: false
    },
    deviceSerial: {
      type: String,
      required: true
    },
    isInstrumentationMode: {
      type: Boolean,
      default: false
    }
  },
  emits: ['attach', 'detach', 'spawn', 'update:spawnMode', 'update:spawnPackage', 'update:spawnDelay'],
  setup(props, { emit }) {
    const spawnModeEnabled = ref(false)
    const selectedSpawnPackage = ref('')
    const spawnDelay = ref(30)
    const includeSystemPackages = ref(false)
    
    const { packages: spawnPackages, loading: packagesLoading, fetchPackages } = useSpawnPackages(props.deviceSerial)
    
    const statusText = computed(() => {
      if (props.attached) return 'Attached'
      if (props.crashed) return 'Crashed'
      return 'Detached'
    })
    
    const statusIndicatorClass = computed(() => {
      if (props.attached) return 'bg-green-500 status-indicator'
      if (props.crashed) return 'bg-red-500'
      return 'bg-orange-500'
    })
    
    const statusTextClass = computed(() => {
      if (props.attached) return 'text-green-400'
      if (props.crashed) return 'text-red-400'
      return 'text-orange-400'
    })
    
    const canAttach = computed(() => {
      return props.hasLock && 
             props.fridaServerRunning && 
             props.selectedProcess?.pid && 
             !props.attached &&
             !spawnModeEnabled.value
    })
    
    const canDetach = computed(() => {
      return props.attached
    })
    
    const canSpawn = computed(() => {
      return props.hasLock &&
             props.fridaServerRunning &&
             selectedSpawnPackage.value &&
             !props.attached
    })
    
    const handleAttach = () => {
      if (canAttach.value) {
        emit('attach', props.selectedProcess.pid)
      }
    }
    
    const handleDetach = () => {
      if (canDetach.value) {
        emit('detach')
      }
    }
    
    const handleSpawn = () => {
      if (canSpawn.value) {
        emit('spawn', selectedSpawnPackage.value)
      }
    }
    
    const handleRefreshPackages = async () => {
      await fetchPackages(includeSystemPackages.value)
    }
    
    watch(spawnModeEnabled, (enabled) => {
      emit('update:spawnMode', enabled)
      if (enabled && spawnPackages.value.length === 0) {
        fetchPackages(includeSystemPackages.value)
      }
      if (!enabled) {
        selectedSpawnPackage.value = ''
      }
    })
    
    watch(selectedSpawnPackage, (packageId) => {
      emit('update:spawnPackage', packageId)
    })
    
    watch(spawnDelay, (delay) => {
      emit('update:spawnDelay', delay)
    })
    
    watch(includeSystemPackages, (includeSystem) => {
      if (spawnModeEnabled.value) {
        selectedSpawnPackage.value = ''
        fetchPackages(includeSystem)
      }
    })
    
    onMounted(() => {
      if (spawnModeEnabled.value) {
        fetchPackages(includeSystemPackages.value)
      }
    })
    
    return {
      spawnModeEnabled,
      selectedSpawnPackage,
      spawnDelay,
      includeSystemPackages,
      spawnPackages,
      packagesLoading,
      statusText,
      statusIndicatorClass,
      statusTextClass,
      canAttach,
      canDetach,
      canSpawn,
      handleAttach,
      handleDetach,
      handleSpawn,
      handleRefreshPackages
    }
  }
}
</script>
