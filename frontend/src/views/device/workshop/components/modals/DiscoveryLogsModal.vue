<template>
  <div v-if="show" class="modal modal-open">
    <div class="modal-box bg-neutral-900 border border-primary/30 max-w-4xl max-h-[80vh]">
      <h3 class="font-bold text-lg text-white flex items-center justify-between">
        <div class="flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          {{ logMode === 'frida' ? 'Frida Session Logs' : 'Discovery Logs' }}
          <span v-if="isPolling" class="badge badge-sm badge-success gap-1">
            <span class="relative flex h-2 w-2">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
              <span class="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
            </span>
            Live
          </span>
        </div>
        <div class="flex items-center gap-2">
          <div class="tabs tabs-boxed tabs-xs bg-neutral-800">
            <button 
              class="tab"
              :class="{ 'tab-active': logMode === 'discovery' }"
              @click="logMode = 'discovery'"
            >Discovery</button>
            <button 
              class="tab"
              :class="{ 'tab-active': logMode === 'frida' }"
              @click="logMode = 'frida'"
            >Frida</button>
          </div>
          <button 
            class="btn btn-sm btn-ghost btn-square w-8 h-8 min-h-8 bg-neutral-900/40 border border-primary/30 text-slate-200 hover:bg-neutral-800/70 hover:border-primary/60 hover:text-white"
            @click="scrollToBottom"
            title="Scroll to bottom"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3" />
            </svg>
          </button>
          <button 
            class="btn btn-sm btn-ghost btn-square w-8 h-8 min-h-8 bg-neutral-900/40 border border-primary/30 text-slate-200 hover:bg-neutral-800/70 hover:border-primary/60 hover:text-white"
            @click="copyLogs"
            title="Copy logs"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
          </button>
        </div>
      </h3>
      
      <div v-if="logMode === 'discovery' && packageId" class="mt-2 text-sm text-slate-400">
        Package: <code class="text-primary">{{ packageId }}</code>
        <span v-if="timestamp" class="ml-2">| {{ formatTimestamp(timestamp) }}</span>
      </div>
      
      <div 
        ref="logsContainer"
        class="mt-4 bg-neutral-950 rounded-lg p-4 h-96 overflow-y-auto font-mono text-xs"
      >
        <div v-if="loading" class="flex items-center justify-center h-full">
          <span class="loading loading-spinner loading-md text-primary"></span>
        </div>
        
        <div v-else-if="displayLogs.length === 0" class="flex items-center justify-center h-full text-slate-500">
          No logs available
        </div>
        
        <div v-else>
          <div 
            v-for="(log, index) in displayLogs" 
            :key="index"
            class="py-0.5 border-b border-neutral-800 last:border-0"
            :class="getLogClass(log)"
          >
            <template v-if="logMode === 'frida'">
              <span class="text-slate-300" v-html="highlightFridaLog(log)"></span>
            </template>
            <template v-else>
              <span class="text-slate-600">{{ log.timestamp || '' }}</span>
              <span class="mx-2">-</span>
              <span 
                class="font-semibold"
                :class="{
                  'text-green-400': log.level === 'INFO',
                  'text-yellow-400': log.level === 'WARNING',
                  'text-red-400': log.level === 'ERROR',
                  'text-slate-400': log.level === 'DEBUG'
                }"
              >{{ log.level || 'INFO' }}</span>
              <span class="mx-2">-</span>
              <span class="text-slate-300">{{ log.message }}</span>
            </template>
          </div>
        </div>
      </div>
      
      <div v-if="logMode === 'discovery' && stats" class="mt-4 grid grid-cols-4 gap-2 text-center">
        <div class="bg-neutral-800 rounded p-2">
          <div class="text-lg font-bold text-white">{{ stats.java?.classes_included || 0 }}</div>
          <div class="text-xs text-slate-500">Classes</div>
        </div>
        <div class="bg-neutral-800 rounded p-2">
          <div class="text-lg font-bold text-white">{{ stats.java?.total_methods || 0 }}</div>
          <div class="text-xs text-slate-500">Methods</div>
        </div>
        <div class="bg-neutral-800 rounded p-2">
          <div class="text-lg font-bold text-white">{{ stats.native?.modules_included || 0 }}</div>
          <div class="text-xs text-slate-500">Modules</div>
        </div>
        <div class="bg-neutral-800 rounded p-2">
          <div class="text-lg font-bold text-white">{{ stats.native?.total_exports || 0 }}</div>
          <div class="text-xs text-slate-500">Exports</div>
        </div>
      </div>
      
      <div class="modal-action">
        <button 
          v-if="logMode === 'frida'" 
          class="btn btn-ghost btn-sm"
          @click="clearFridaLogs"
        >
          Clear Logs
        </button>
        <button 
          v-if="logMode === 'discovery' && !isLive && logFile" 
          class="btn btn-ghost btn-sm"
          @click="refreshLogs"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Refresh
        </button>
        <button class="btn btn-ghost" @click="$emit('close')">Close</button>
      </div>
    </div>
    <div class="modal-backdrop bg-black/60" @click="$emit('close')"></div>
  </div>
</template>

<script>
import { ref, computed, watch, nextTick, onUnmounted } from 'vue'
import axios from 'axios'

export default {
  name: 'DiscoveryLogsModal',
  props: {
    show: {
      type: Boolean,
      required: true
    },
    deviceSerial: {
      type: String,
      required: true
    },
    packageId: {
      type: String,
      default: ''
    },
    timestamp: {
      type: String,
      default: ''
    },
    clientId: {
      type: String,
      default: ''
    },
    isLive: {
      type: Boolean,
      default: false
    },
    stats: {
      type: Object,
      default: null
    },
    defaultMode: {
      type: String,
      default: 'discovery'
    }
  },
  emits: ['close'],
  setup(props) {
    const logMode = ref(props.defaultMode)
    const discoveryLogs = ref([])
    const fridaLogs = ref([])
    const loading = ref(false)
    const logsContainer = ref(null)
    const logFile = ref('')
    let discoveryPollInterval = null
    let fridaPollInterval = null
    
    const displayLogs = computed(() => {
      return logMode.value === 'frida' ? fridaLogs.value : discoveryLogs.value
    })
    
    const isPolling = computed(() => {
      return (logMode.value === 'frida' && fridaPollInterval !== null) ||
             (logMode.value === 'discovery' && props.isLive && discoveryPollInterval !== null)
    })
    
    const fetchDiscoveryLogs = async () => {
      if (!props.packageId) return
      
      try {
        loading.value = true
        
        const params = new URLSearchParams()
        params.append('package_id', props.packageId)
        if (props.timestamp) {
          params.append('timestamp', props.timestamp)
        }
        
        const response = await axios.get(
          `http://localhost:8000/api/devices/${props.deviceSerial}/workshop/discovery/logs?${params.toString()}`
        )
        
        discoveryLogs.value = response.data.logs || []
        logFile.value = response.data.log_file || ''
        
        await nextTick()
        scrollToBottom()
      } catch (err) {
        console.error('Failed to fetch discovery logs:', err)
        discoveryLogs.value = [{ level: 'ERROR', message: 'Failed to load logs: ' + (err.response?.data?.detail || err.message) }]
      } finally {
        loading.value = false
      }
    }
    
    const fetchFridaLogs = async () => {
      try {
        const response = await axios.get(
          `http://localhost:8000/api/devices/${props.deviceSerial}/workshop/frida/logs/live`
        )
        
        const newLogs = response.data.logs || []
        const previousLength = fridaLogs.value.length
        fridaLogs.value = newLogs
        
        if (newLogs.length > previousLength) {
          await nextTick()
          scrollToBottom()
        }
      } catch (err) {
        console.error('Failed to fetch Frida logs:', err)
      }
    }
    
    const clearFridaLogs = async () => {
      try {
        await axios.post(
          `http://localhost:8000/api/devices/${props.deviceSerial}/workshop/frida/logs/clear`,
          { client_id: props.clientId }
        )
        fridaLogs.value = []
      } catch (err) {
        console.error('Failed to clear Frida logs:', err)
      }
    }
    
    const startDiscoveryPolling = () => {
      if (discoveryPollInterval) return
      
      discoveryPollInterval = setInterval(() => {
        if (props.isLive && logMode.value === 'discovery') {
          fetchDiscoveryLogs()
        }
      }, 1000)
    }
    
    const stopDiscoveryPolling = () => {
      if (discoveryPollInterval) {
        clearInterval(discoveryPollInterval)
        discoveryPollInterval = null
      }
    }
    
    const startFridaPolling = () => {
      if (fridaPollInterval) return
      
      fridaPollInterval = setInterval(() => {
        if (logMode.value === 'frida') {
          fetchFridaLogs()
        }
      }, 2000)
    }
    
    const stopFridaPolling = () => {
      if (fridaPollInterval) {
        clearInterval(fridaPollInterval)
        fridaPollInterval = null
      }
    }
    
    const scrollToBottom = () => {
      if (logsContainer.value) {
        logsContainer.value.scrollTop = logsContainer.value.scrollHeight
      }
    }
    
    const copyLogs = () => {
      const text = displayLogs.value.map(l => {
        if (logMode.value === 'frida') {
          return l
        }
        return `${l.timestamp || ''} - ${l.level || 'INFO'} - ${l.message}`
      }).join('\n')
      navigator.clipboard.writeText(text)
    }
    
    const formatTimestamp = (ts) => {
      if (!ts) return ''
      const match = ts.match(/(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})/)
      if (match) {
        return `${match[1]}-${match[2]}-${match[3]} ${match[4]}:${match[5]}:${match[6]}`
      }
      return ts
    }
    
    const getLogClass = (log) => {
      if (logMode.value === 'frida') {
        if (log.includes('[SESSION_LOST]') || log.includes('ERROR')) return 'bg-red-900/20'
        if (log.includes('WARNING') || log.includes('[DETACHED]')) return 'bg-yellow-900/20'
        if (log.includes('[SESSION_START]')) return 'bg-green-900/20'
        return ''
      }
      if (log.level === 'ERROR') return 'bg-red-900/20'
      if (log.level === 'WARNING') return 'bg-yellow-900/20'
      return ''
    }
    
    const highlightFridaLog = (log) => {
      let result = log
        .replace(/\[SESSION_START\]/g, '<span class="text-green-400 font-bold">[SESSION_START]</span>')
        .replace(/\[SESSION_LOST\]/g, '<span class="text-red-400 font-bold">[SESSION_LOST]</span>')
        .replace(/\[DETACHED\]/g, '<span class="text-orange-400 font-bold">[DETACHED]</span>')
        .replace(/\[OPERATION_START\]/g, '<span class="text-blue-400">[OPERATION_START]</span>')
        .replace(/\[OPERATION_COMPLETE\]/g, '<span class="text-cyan-400">[OPERATION_COMPLETE]</span>')
        .replace(/ERROR/g, '<span class="text-red-400 font-bold">ERROR</span>')
        .replace(/WARNING/g, '<span class="text-yellow-400">WARNING</span>')
        .replace(/\[S(\d+)\]/g, '<span class="text-purple-400">[S$1]</span>')
      return result
    }
    
    const refreshLogs = () => {
      if (logMode.value === 'frida') {
        fetchFridaLogs()
      } else {
        fetchDiscoveryLogs()
      }
    }
    
    watch(() => props.show, (newVal) => {
      if (newVal) {
        if (logMode.value === 'frida') {
          fetchFridaLogs()
          startFridaPolling()
        } else {
          fetchDiscoveryLogs()
          if (props.isLive) {
            startDiscoveryPolling()
          }
        }
      } else {
        stopDiscoveryPolling()
        stopFridaPolling()
      }
    })
    
    watch(() => logMode.value, (newMode) => {
      if (!props.show) return
      
      if (newMode === 'frida') {
        stopDiscoveryPolling()
        fetchFridaLogs()
        startFridaPolling()
      } else {
        stopFridaPolling()
        fetchDiscoveryLogs()
        if (props.isLive) {
          startDiscoveryPolling()
        }
      }
    })
    
    watch(() => props.isLive, (newVal) => {
      if (newVal && props.show && logMode.value === 'discovery') {
        startDiscoveryPolling()
      } else {
        stopDiscoveryPolling()
      }
    })
    
    watch(() => props.defaultMode, (newMode) => {
      logMode.value = newMode
    })
    
    onUnmounted(() => {
      stopDiscoveryPolling()
      stopFridaPolling()
    })
    
    return {
      logMode,
      displayLogs,
      isPolling,
      loading,
      logsContainer,
      logFile,
      scrollToBottom,
      copyLogs,
      formatTimestamp,
      getLogClass,
      highlightFridaLog,
      refreshLogs,
      clearFridaLogs
    }
  }
}
</script>
