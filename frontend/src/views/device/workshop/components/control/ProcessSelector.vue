<template>
  <div class="form-control" :class="{ 'opacity-50': disabled }">
    <label class="label flex items-center justify-between gap-2 py-1">
      <span class="label-text text-white font-semibold">Select Process</span>
      <button 
        type="button"
        class="btn btn-sm btn-ghost btn-square w-8 h-8 min-h-8 bg-neutral-900/40 border border-primary/35 text-primary/80 hover:bg-primary/10 hover:border-primary/70 hover:text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/40"
        @click="handleRefresh"
        :disabled="loading || disabled"
        title="Refresh process list"
        aria-label="Refresh process list"
      >
        <svg v-if="!loading" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        <span v-else class="loading loading-spinner loading-xs text-primary"></span>
      </button>
    </label>
    
    <div v-if="disabled" class="mb-2 p-2 bg-amber-500/10 border border-amber-500/30 rounded text-xs text-amber-400">
      Process selector disabled - Using spawn mode
    </div>
    
    <div class="flex gap-2 mb-2" :class="{ 'pointer-events-none': disabled }">
      <label class="label cursor-pointer gap-1 flex-1 justify-start">
        <input 
          type="radio" 
          name="process-filter" 
          class="radio radio-xs radio-primary" 
          value="all"
          :checked="processFilter === 'all'"
          @change="processFilter = 'all'"
          :disabled="disabled"
        />
        <span class="label-text text-xs text-white">All</span>
      </label>
      <label class="label cursor-pointer gap-1 flex-1 justify-start">
        <input 
          type="radio" 
          name="process-filter" 
          class="radio radio-xs radio-primary" 
          value="apps"
          :checked="processFilter === 'apps'"
          @change="processFilter = 'apps'"
          :disabled="disabled"
        />
        <span class="label-text text-xs text-white">Apps</span>
      </label>
      <label class="label cursor-pointer gap-1 flex-1 justify-start">
        <input 
          type="radio" 
          name="process-filter" 
          class="radio radio-xs radio-primary" 
          value="system"
          :checked="processFilter === 'system'"
          @change="processFilter = 'system'"
          :disabled="disabled"
        />
        <span class="label-text text-xs text-white">System</span>
      </label>
    </div>
    
    <select 
      :value="selectedProcess?.pid || ''"
      @change="handleProcessChange"
      class="select select-bordered w-full bg-black border-primary/30 focus:border-primary text-white"
      :disabled="loading || disabled"
    >
      <option value="" disabled>{{ loading ? 'Loading processes...' : disabled ? 'Using spawn mode' : 'Choose a process' }}</option>
      <option 
        v-for="process in filteredProcesses" 
        :key="process.pid"
        :value="process.pid"
      >
        {{ formatProcessLabel(process) }}
      </option>
    </select>
    <label v-if="selectedProcess && !disabled" class="label">
      <span
        class="label-text-alt text-slate-400 break-words max-w-full"
        :title="selectedProcess.package_id || selectedProcess.name"
      >{{ selectedProcess.package_id || selectedProcess.name }}</span>
    </label>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRunningProcesses } from '../../composables/useRunningProcesses'

export default {
  name: 'ProcessSelector',
  props: {
    device: {
      type: Object,
      required: true
    },
    selectedProcess: {
      type: Object,
      default: null
    },
    disabled: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:selectedProcess'],
  setup(props, { emit }) {
    const { processes, loading, fetchProcesses } = useRunningProcesses(props.device.serial)
    const processFilter = ref('all')
    
    const filteredProcesses = computed(() => {
      if (processFilter.value === 'apps') {
        return processes.value.filter(p => p.processType === 'app')
      } else if (processFilter.value === 'system') {
        return processes.value.filter(p => p.processType === 'system')
      }
      return processes.value
    })
    
    const formatProcessLabel = (process) => {
      const prefix = process.processType === 'app' ? '[App]' : '[System]'
      const name = process.package_id || process.name
      return `${prefix} ${name} (PID: ${process.pid})`
    }
    
    const handleProcessChange = (event) => {
      const pid = Number(event.target.value)
      const process = processes.value.find(p => p.pid === pid)
      emit('update:selectedProcess', process || null)
    }
    
    const handleRefresh = async () => {
      await fetchProcesses()
    }
    
    onMounted(() => {
      fetchProcesses()
    })
    
    return {
      processes,
      loading,
      processFilter,
      filteredProcesses,
      formatProcessLabel,
      handleProcessChange,
      handleRefresh
    }
  }
}
</script>

