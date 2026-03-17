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
        
        <div v-if="!selectedAppPackage" class="text-xs text-yellow-400/70 mt-1">
          Select an app first
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
        <label class="text-xs text-gray-400 mb-1 block">Choose App</label>
        
        <div class="flex gap-2">
          <select 
            v-model="selectedAppPackage"
            class="select select-bordered select-xs w-full bg-black border-primary/30 focus:border-primary text-white"
            :disabled="packagesLoading"
          >
            <option value="" disabled>{{ packagesLoading ? 'Loading packages...' : 'Select an app' }}</option>
            <option 
              v-for="pkg in packages" 
              :key="pkg.package_id"
              :value="pkg.package_id"
            >
              {{ pkg.package_id }}{{ pkg.is_running ? ' (Running)' : '' }}
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
          <div ref="settingsMenuRef" class="relative">
            <button 
              type="button"
              class="btn btn-xs btn-ghost btn-square bg-neutral-900/40 border border-primary/35 text-primary/80 hover:bg-primary/10"
              @click.stop="showSettings = !showSettings"
              title="Instrumentation settings"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </button>

            <div
              v-if="showSettings"
              class="absolute right-0 mt-1 w-56 rounded-md border border-primary/30 bg-neutral-950/95 shadow-lg z-50 overflow-hidden"
            >
              <div class="px-3 py-2 text-xs text-slate-400 border-b border-primary/10">
                Attach mode
              </div>
              <button
                type="button"
                class="w-full text-left px-3 py-2 text-xs hover:bg-primary/10 flex items-center justify-between"
                :class="attachTargetMode === 'pid' ? 'text-primary' : 'text-white'"
                @click="setAttachTargetMode('pid')"
              >
                <span>Use PID</span>
                <span v-if="attachTargetMode === 'pid'" class="text-primary">✓</span>
              </button>
              <button
                type="button"
                class="w-full text-left px-3 py-2 text-xs hover:bg-primary/10 flex items-center justify-between"
                :class="attachTargetMode === 'package' ? 'text-primary' : 'text-white'"
                @click="setAttachTargetMode('package')"
              >
                <span>Use Package Name</span>
                <span v-if="attachTargetMode === 'package'" class="text-primary">✓</span>
              </button>
            </div>
          </div>
        </div>

        <div v-if="selectedAppPackage && fridaServerRunning" class="text-[11px] text-slate-500 mt-1">
          Attach mode: <span class="text-slate-300">{{ attachTargetModeLabel }}</span>
        </div>
        
        <div v-if="selectedAppPackage && !isAppRunning && fridaServerRunning" class="text-xs text-blue-400/70 flex items-start gap-1">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 mt-0.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>
            App is not running.
            <span v-if="attachTargetMode === 'package'">Use "Attach" to spawn and attach, or "Start App" to spawn only.</span>
            <span v-else>Use "Start App" to spawn it.</span>
          </span>
        </div>
        
        <div v-if="selectedAppPackage && isAppRunning && fridaServerRunning" class="text-xs text-green-400/70 flex items-start gap-1">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 mt-0.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>App is running (PID: {{ runningPid }}). Use "Attach" to connect.</span>
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
            <span>System packages may be numerous and some cannot be instrumented</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useSpawnPackages } from '../../../composables/useSpawnPackages'
import axios from 'axios'

export default {
  name: 'InstrumentationFridaSession',
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
    }
  },
  emits: ['attach', 'detach', 'spawn', 'update:selectedApp'],
  setup(props, { emit }) {
    const selectedAppPackage = ref('')
    const includeSystemPackages = ref(false)
    const showSettings = ref(false)
    const settingsMenuRef = ref(null)
    const attachTargetMode = ref('pid')
    const runningProcesses = ref([])
    const foregroundPackageId = ref(null)
    
    const { packages: rawPackages, loading: packagesLoading, fetchPackages } = useSpawnPackages(props.deviceSerial)
    
    const toPackageId = (process) => {
      const rawName = (process?.name || '').trim()
      if (!rawName || rawName.startsWith('[')) return null
      const base = rawName.split(':')[0]
      if (!base.includes('.')) return null
      return base
    }

    // Enrich packages with running status
    const packages = computed(() => {
      return rawPackages.value.map(pkg => ({
        ...pkg,
        is_running: !!foregroundPackageId.value && pkg.package_id === foregroundPackageId.value
      }))
    })
    
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
    
    const isAppRunning = computed(() => {
      if (!selectedAppPackage.value) return false
      return runningProcesses.value.some(p => p.package_id === selectedAppPackage.value)
    })
    
    const runningPid = computed(() => {
      if (!selectedAppPackage.value) return null
      const process = runningProcesses.value.find(p => p.package_id === selectedAppPackage.value)
      return process?.pid || null
    })
    
    const canAttach = computed(() => {
      if (!props.hasLock || !props.fridaServerRunning || !selectedAppPackage.value || props.attached) return false
      if (attachTargetMode.value === 'package') return true
      return isAppRunning.value
    })
    
    const canDetach = computed(() => {
      return props.attached
    })
    
    const canSpawn = computed(() => {
      return props.hasLock &&
             props.fridaServerRunning &&
             selectedAppPackage.value &&
             !isAppRunning.value &&
             !props.attached
    })
    
    const fetchRunningProcesses = async () => {
      if (!props.deviceSerial) return
      
      try {
        const response = await axios.get(`http://localhost:8000/api/devices/${props.deviceSerial}/processes`)
        const raw = response.data.processes || []
        foregroundPackageId.value = response.data.foreground_package_id || null
        runningProcesses.value = raw
          .map(p => ({ ...p, package_id: toPackageId(p) }))
          .filter(p => !!p.package_id)
      } catch (err) {
        console.error('[InstrumentationFridaSession] Failed to fetch running processes:', err)
      }
    }
    
    const handleAttach = () => {
      if (!canAttach.value) return
      if (attachTargetMode.value === 'package') {
        emit('attach', { package_id: selectedAppPackage.value, spawn_if_needed: true })
        return
      }
      if (runningPid.value) emit('attach', { pid: runningPid.value })
    }
    
    const handleDetach = () => {
      if (canDetach.value) {
        emit('detach')
      }
    }
    
    const handleSpawn = () => {
      if (canSpawn.value) {
        emit('spawn', selectedAppPackage.value)
      }
    }
    
    const handleRefreshPackages = async () => {
      await fetchPackages(includeSystemPackages.value)
      await fetchRunningProcesses()
    }

    const setAttachTargetMode = (mode) => {
      attachTargetMode.value = mode
      showSettings.value = false
    }

    const attachTargetModeLabel = computed(() => {
      return attachTargetMode.value === 'package' ? 'Package Name' : 'PID'
    })

    const handleDocumentClick = (e) => {
      if (!showSettings.value) return
      const el = settingsMenuRef.value
      if (el && !el.contains(e.target)) showSettings.value = false
    }
    
    watch(selectedAppPackage, (packageId) => {
      emit('update:selectedApp', packageId)
    })
    
    watch(includeSystemPackages, async (includeSystem) => {
      selectedAppPackage.value = ''
      await fetchPackages(includeSystem)
      await fetchRunningProcesses()
    })
    
    let pollTimer = null

    onMounted(async () => {
      await fetchPackages(includeSystemPackages.value)
      await fetchRunningProcesses()
      
      // Poll for running processes every 3 seconds
      pollTimer = setInterval(fetchRunningProcesses, 3000)
      document.addEventListener('click', handleDocumentClick)
    })

    onUnmounted(() => {
      if (pollTimer) {
        clearInterval(pollTimer)
        pollTimer = null
      }
      document.removeEventListener('click', handleDocumentClick)
    })
    
    return {
      selectedAppPackage,
      includeSystemPackages,
      showSettings,
      settingsMenuRef,
      attachTargetMode,
      attachTargetModeLabel,
      packages,
      packagesLoading,
      statusText,
      statusIndicatorClass,
      statusTextClass,
      isAppRunning,
      runningPid,
      canAttach,
      canDetach,
      canSpawn,
      setAttachTargetMode,
      handleAttach,
      handleDetach,
      handleSpawn,
      handleRefreshPackages
    }
  }
}
</script>
