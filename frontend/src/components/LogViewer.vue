<template>
  <div class="card bg-neutral-900/60 backdrop-blur-sm shadow-xl border border-primary/20">
    <div class="card-body">
      <h3 class="card-title text-white mb-4">Device Logs</h3>
      
      <div class="space-y-2">
        <!-- Logcat -->
        <div class="collapse collapse-arrow bg-black/30 border border-primary/20">
          <input type="checkbox" v-model="expandedLogs.logcat" @change="handleToggle('logcat')" />
          <div class="collapse-title flex items-center justify-between">
            <div class="flex items-center gap-3">
              <button 
                type="button"
                class="btn btn-sm btn-circle z-10 relative hover:scale-110 transition-transform"
                :class="streamingLogs.logcat ? 'btn-error hover:btn-error' : 'btn-success hover:btn-success'"
                @click.prevent.stop="toggleStream('logcat')"
                :title="streamingLogs.logcat ? 'Stop streaming' : 'Start streaming'"
              >
                <svg v-if="!streamingLogs.logcat" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z" />
                </svg>
              </button>
              <span class="text-white font-semibold">ADB Logcat</span>
              <div class="badge badge-sm" :class="streamingLogs.logcat ? 'badge-success' : 'badge-ghost'">
                {{ streamingLogs.logcat ? 'Streaming' : 'Stopped' }}
              </div>
            </div>
            <span class="text-xs text-slate-400">{{ logs.logcat.length }} lines</span>
          </div>
          <div class="collapse-content">
            <div class="log-container bg-[#0a0a0a] rounded-lg p-4 h-64 overflow-y-auto font-mono text-xs" ref="logcatContainer">
              <div v-if="logs.logcat.length === 0" class="text-slate-500 text-center py-8">
                No logs yet. Click the play button to start streaming.
              </div>
              <div v-for="(log, index) in logs.logcat" :key="index" class="log-line" :class="getLogClass(log.level)">
                <span class="text-slate-500">[{{ formatTimestamp(log.timestamp) }}]</span>
                <span class="ml-2">{{ log.message }}</span>
              </div>
            </div>
            <div class="flex gap-2 mt-2">
              <button type="button" class="btn btn-xs btn-ghost" @click.prevent.stop="clearLogs('logcat')">Clear</button>
              <button type="button" class="btn btn-xs btn-ghost" @click.prevent.stop="scrollToBottom('logcat')">Scroll to Bottom</button>
            </div>
          </div>
        </div>

        <!-- Frida Installation -->
        <div class="collapse collapse-arrow bg-black/30 border border-primary/20">
          <input type="checkbox" v-model="expandedLogs.frida_install" @change="handleToggle('frida_install')" />
          <div class="collapse-title flex items-center justify-between">
            <div class="flex items-center gap-3">
              <button 
                type="button"
                class="btn btn-sm btn-circle z-10 relative hover:scale-110 transition-transform"
                :class="streamingLogs.frida_install ? 'btn-error hover:btn-error' : 'btn-success hover:btn-success'"
                @click.prevent.stop="toggleStream('frida_install')"
                :title="streamingLogs.frida_install ? 'Stop streaming' : 'Start streaming'"
              >
                <svg v-if="!streamingLogs.frida_install" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z" />
                </svg>
              </button>
              <span class="text-white font-semibold">Frida Installation</span>
              <div class="badge badge-sm" :class="streamingLogs.frida_install ? 'badge-success' : 'badge-ghost'">
                {{ streamingLogs.frida_install ? 'Streaming' : 'Stopped' }}
              </div>
            </div>
            <span class="text-xs text-slate-400">{{ logs.frida_install.length }} lines</span>
          </div>
          <div class="collapse-content">
            <div class="log-container bg-[#0a0a0a] rounded-lg p-4 h-64 overflow-y-auto font-mono text-xs" ref="fridaInstallContainer">
              <div v-if="logs.frida_install.length === 0" class="text-slate-500 text-center py-8">
                No installation logs yet.
              </div>
              <div v-for="(log, index) in logs.frida_install" :key="index" class="log-line" :class="getLogClass(log.level)">
                <span class="text-slate-500">[{{ formatTimestamp(log.timestamp) }}]</span>
                <span class="ml-2">{{ log.message }}</span>
              </div>
            </div>
            <div class="flex gap-2 mt-2">
              <button type="button" class="btn btn-xs btn-ghost" @click.prevent.stop="clearLogs('frida_install')">Clear</button>
              <button type="button" class="btn btn-xs btn-ghost" @click.prevent.stop="scrollToBottom('frida_install')">Scroll to Bottom</button>
            </div>
          </div>
        </div>

        <!-- Frida Server -->
        <div class="collapse collapse-arrow bg-black/30 border border-primary/20">
          <input type="checkbox" v-model="expandedLogs.frida_server" @change="handleToggle('frida_server')" />
          <div class="collapse-title flex items-center justify-between">
            <div class="flex items-center gap-3">
              <button 
                type="button"
                class="btn btn-sm btn-circle z-10 relative hover:scale-110 transition-transform"
                :class="streamingLogs.frida_server ? 'btn-error hover:btn-error' : 'btn-success hover:btn-success'"
                @click.prevent.stop="toggleStream('frida_server')"
                :title="streamingLogs.frida_server ? 'Stop streaming' : 'Start streaming'"
              >
                <svg v-if="!streamingLogs.frida_server" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z" />
                </svg>
              </button>
              <span class="text-white font-semibold">Frida Server</span>
              <div class="badge badge-sm" :class="streamingLogs.frida_server ? 'badge-success' : 'badge-ghost'">
                {{ streamingLogs.frida_server ? 'Streaming' : 'Stopped' }}
              </div>
            </div>
            <span class="text-xs text-slate-400">{{ logs.frida_server.length }} lines</span>
          </div>
          <div class="collapse-content">
            <div class="log-container bg-[#0a0a0a] rounded-lg p-4 h-64 overflow-y-auto font-mono text-xs" ref="fridaServerContainer">
              <div v-if="logs.frida_server.length === 0" class="text-slate-500 text-center py-8">
                No server logs yet.
              </div>
              <div v-for="(log, index) in logs.frida_server" :key="index" class="log-line" :class="getLogClass(log.level)">
                <span class="text-slate-500">[{{ formatTimestamp(log.timestamp) }}]</span>
                <span class="ml-2">{{ log.message }}</span>
              </div>
            </div>
            <div class="flex gap-2 mt-2">
              <button type="button" class="btn btn-xs btn-ghost" @click.prevent.stop="clearLogs('frida_server')">Clear</button>
              <button type="button" class="btn btn-xs btn-ghost" @click.prevent.stop="scrollToBottom('frida_server')">Scroll to Bottom</button>
            </div>
          </div>
        </div>

        <!-- ADB Operations -->
        <div class="collapse collapse-arrow bg-black/30 border border-primary/20">
          <input type="checkbox" v-model="expandedLogs.adb_operations" @change="handleToggle('adb_operations')" />
          <div class="collapse-title flex items-center justify-between">
            <div class="flex items-center gap-3">
              <button 
                type="button"
                class="btn btn-sm btn-circle z-10 relative hover:scale-110 transition-transform"
                :class="streamingLogs.adb_operations ? 'btn-error hover:btn-error' : 'btn-success hover:btn-success'"
                @click.prevent.stop="toggleStream('adb_operations')"
                :title="streamingLogs.adb_operations ? 'Stop streaming' : 'Start streaming'"
              >
                <svg v-if="!streamingLogs.adb_operations" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z" />
                </svg>
              </button>
              <span class="text-white font-semibold">ADB Operations</span>
              <div class="badge badge-sm" :class="streamingLogs.adb_operations ? 'badge-success' : 'badge-ghost'">
                {{ streamingLogs.adb_operations ? 'Streaming' : 'Stopped' }}
              </div>
            </div>
            <span class="text-xs text-slate-400">{{ logs.adb_operations.length }} lines</span>
          </div>
          <div class="collapse-content">
            <div class="log-container bg-[#0a0a0a] rounded-lg p-4 h-64 overflow-y-auto font-mono text-xs" ref="adbOperationsContainer">
              <div v-if="logs.adb_operations.length === 0" class="text-slate-500 text-center py-8">
                No ADB operation logs yet.
              </div>
              <div v-for="(log, index) in logs.adb_operations" :key="index" class="log-line" :class="getLogClass(log.level)">
                <span class="text-slate-500">[{{ formatTimestamp(log.timestamp) }}]</span>
                <span class="ml-2">{{ log.message }}</span>
              </div>
            </div>
            <div class="flex gap-2 mt-2">
              <button type="button" class="btn btn-xs btn-ghost" @click.prevent.stop="clearLogs('adb_operations')">Clear</button>
              <button type="button" class="btn btn-xs btn-ghost" @click.prevent.stop="scrollToBottom('adb_operations')">Scroll to Bottom</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'

export default {
  name: 'LogViewer',
  props: {
    deviceId: {
      type: String,
      required: true
    }
  },
  setup(props) {
    const logs = reactive({
      logcat: [],
      frida_install: [],
      frida_server: [],
      adb_operations: []
    })

    const expandedLogs = reactive({
      logcat: false,
      frida_install: false,
      frida_server: false,
      adb_operations: false
    })

    const streamingLogs = reactive({
      logcat: false,
      frida_install: false,
      frida_server: false,
      adb_operations: false
    })
    
    // Track if user manually stopped a stream
    const manuallyStoppedLogs = reactive({
      logcat: false,
      frida_install: false,
      frida_server: false,
      adb_operations: false
    })

    const logcatContainer = ref(null)
    const fridaInstallContainer = ref(null)
    const fridaServerContainer = ref(null)
    const adbOperationsContainer = ref(null)

    let ws = null
    let reconnectTimeout = null
    let wsReadyResolvers = []

    const connectWebSocket = () => {
      if (ws && ws.readyState === WebSocket.OPEN) {
        return
      }

      ws = new WebSocket(`ws://localhost:8000/ws/devices/${props.deviceId}/logs`)

      ws.onopen = () => {
        console.log('WebSocket connected')
        wsReadyResolvers.forEach((resolve) => resolve())
        wsReadyResolvers = []
      }

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data)
        const logType = data.type
        
        if (logs[logType]) {
          // Auto-start streaming for non-logcat logs when first message arrives
          // Only if user hasn't manually stopped it
          if (logType !== 'logcat' && 
              !streamingLogs[logType] && 
              !manuallyStoppedLogs[logType] &&
              logs[logType].length === 0) {
            ensureWebSocketReady().then(() => {
              try {
                ws.send(JSON.stringify({ action: 'start', log_type: logType }))
                streamingLogs[logType] = true
              } catch {}
            })
          }
          
          logs[logType].push({
            timestamp: data.timestamp,
            level: data.level,
            message: data.message
          })

          // Auto-scroll if expanded
          if (expandedLogs[logType]) {
            nextTick(() => {
              scrollToBottom(logType)
            })
          }
        }
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
      }

      ws.onclose = () => {
        console.log('WebSocket disconnected')
        reconnectTimeout = setTimeout(() => {
          connectWebSocket()
        }, 3000)
      }
    }

    const ensureWebSocketReady = (timeout = 2000) => {
      return new Promise((resolve) => {
        if (ws && ws.readyState === WebSocket.OPEN) {
          resolve()
        } else {
          connectWebSocket()
          wsReadyResolvers.push(resolve)
          setTimeout(resolve, timeout)
        }
      })
    }

    const toggleStream = (logType) => {
      if (!ws || ws.readyState !== WebSocket.OPEN) {
        connectWebSocket()
        setTimeout(() => toggleStream(logType), 500)
        return
      }

      if (streamingLogs[logType]) {
        // User is stopping the stream
        ws.send(JSON.stringify({ action: 'stop', log_type: logType }))
        streamingLogs[logType] = false
        manuallyStoppedLogs[logType] = true
      } else {
        // User is starting the stream
        ws.send(JSON.stringify({ action: 'start', log_type: logType }))
        streamingLogs[logType] = true
        manuallyStoppedLogs[logType] = false
        expandedLogs[logType] = true
      }
    }

    const handleToggle = (logType) => {
      if (expandedLogs[logType]) {
        // Auto start subscription for non-logcat logs on expand
        // Only if user hasn't manually stopped it
        if (logType !== 'logcat' && !streamingLogs[logType] && !manuallyStoppedLogs[logType]) {
          ensureWebSocketReady().then(() => {
            try {
              ws.send(JSON.stringify({ action: 'start', log_type: logType }))
              streamingLogs[logType] = true
            } catch {}
          })
        }
        nextTick(() => {
          scrollToBottom(logType)
        })
      } else {
        // Stop subscription on collapse only for non-logcat
        if (logType !== 'logcat' && streamingLogs[logType] && ws && ws.readyState === WebSocket.OPEN) {
          try {
            ws.send(JSON.stringify({ action: 'stop', log_type: logType }))
          } catch {}
          streamingLogs[logType] = false
        }
      }
    }

    const clearLogs = (logType) => {
      logs[logType] = []
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ action: 'clear', log_type: logType }))
      }
    }

    const scrollToBottom = (logType) => {
      const containerMap = {
        logcat: logcatContainer,
        frida_install: fridaInstallContainer,
        frida_server: fridaServerContainer,
        adb_operations: adbOperationsContainer
      }

      const container = containerMap[logType]?.value
      if (container) {
        container.scrollTop = container.scrollHeight
      }
    }

    const getLogClass = (level) => {
      switch (level) {
        case 'error':
          return 'text-red-400'
        case 'warning':
          return 'text-yellow-400'
        case 'debug':
          return 'text-slate-500'
        default:
          return 'text-white'
      }
    }

    const formatTimestamp = (timestamp) => {
      if (!timestamp) return ''
      
      try {
        const date = new Date(timestamp)
        return date.toLocaleTimeString()
      } catch {
        return timestamp
      }
    }

    onMounted(() => {
      connectWebSocket()
    })

    onUnmounted(() => {
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout)
      }
      
      if (ws) {
        ws.close()
      }
    })

    return {
      logs,
      expandedLogs,
      streamingLogs,
      logcatContainer,
      fridaInstallContainer,
      fridaServerContainer,
      adbOperationsContainer,
      toggleStream,
      handleToggle,
      clearLogs,
      scrollToBottom,
      getLogClass,
      formatTimestamp
    }
  }
}
</script>

<style scoped>
.log-container {
  scrollbar-width: thin;
  scrollbar-color: #7100d0 #0a0a0a;
}

.log-container::-webkit-scrollbar {
  width: 8px;
}

.log-container::-webkit-scrollbar-track {
  background: #0a0a0a;
}

.log-container::-webkit-scrollbar-thumb {
  background: #7100d0;
  border-radius: 4px;
}

.log-container::-webkit-scrollbar-thumb:hover {
  background: #8a1aff;
}

.log-line {
  padding: 2px 0;
  word-wrap: break-word;
  white-space: pre-wrap;
}

.collapse-title {
  padding-right: 3rem;
}
</style>

