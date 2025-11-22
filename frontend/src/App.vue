<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
    <!-- Header -->
    <div class="navbar bg-slate-900/80 backdrop-blur-md shadow-xl border-b border-purple-500/20">
      <div class="flex-1">
        <div class="flex items-center gap-3 px-4">
          <div class="w-10 h-10 bg-gradient-to-br from-purple-500 to-cyan-500 rounded-lg flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </div>
          <div>
            <h1 class="text-2xl font-bold bg-gradient-to-r from-purple-400 to-cyan-400 bg-clip-text text-transparent">
              Epifania
            </h1>
            <p class="text-xs text-slate-400">Dynamic Instrumentation Platform</p>
          </div>
        </div>
      </div>
      <div class="flex-none px-4">
        <div class="flex items-center gap-2">
          <div class="badge badge-sm" :class="adbConnected ? 'badge-success' : 'badge-error'">
            {{ adbConnected ? 'ADB Connected' : 'ADB Offline' }}
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="container mx-auto p-6 max-w-7xl">
      <!-- Control Panel -->
      <div class="card bg-slate-900/50 backdrop-blur-sm shadow-2xl border border-purple-500/20 mb-6">
        <div class="card-body">
          <div class="flex items-center justify-between">
            <div>
              <h2 class="card-title text-2xl text-white mb-2">Device Manager</h2>
              <p class="text-slate-400 text-sm">Manage connected Android devices and emulators</p>
            </div>
            <button 
              class="btn btn-primary bg-gradient-to-r from-purple-600 to-cyan-600 hover:from-purple-700 hover:to-cyan-700 border-0 gap-2"
              @click="scanDevices"
              :disabled="loading"
            >
              <svg v-if="!loading" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <span v-if="loading" class="loading loading-spinner loading-sm"></span>
              {{ loading ? 'Scanning...' : 'Scan Devices' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Error Alert -->
      <div v-if="error" class="alert alert-error mb-6 shadow-lg border border-red-500/50">
        <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>{{ error }}</span>
      </div>

      <!-- Devices Grid -->
      <div v-if="devices.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div 
          v-for="device in devices" 
          :key="device.id"
          class="device-card card bg-slate-900/50 backdrop-blur-sm shadow-xl border border-purple-500/20 hover:border-purple-500/50"
        >
          <div class="card-body">
            <!-- Device Header -->
            <div class="flex items-start justify-between mb-4">
              <div class="flex items-center gap-3">
                <div class="avatar placeholder">
                  <div class="w-12 h-12 rounded-lg" :class="getDeviceColor(device.type)">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
                    </svg>
                  </div>
                </div>
                <div>
                  <h3 class="font-bold text-white text-lg">{{ device.name }}</h3>
                  <p class="text-xs text-slate-400">{{ device.brand }} {{ device.model }}</p>
                </div>
              </div>
              <div class="badge badge-sm" :class="getStatusBadge(device.state)">
                {{ device.state }}
              </div>
            </div>

            <!-- Device Info -->
            <div class="space-y-2">
              <div class="flex items-center justify-between text-sm">
                <span class="text-slate-400">Serial</span>
                <span class="text-white font-mono text-xs">{{ device.serial }}</span>
              </div>
              <div class="flex items-center justify-between text-sm">
                <span class="text-slate-400">Android</span>
                <span class="text-white">{{ device.android_version }} (SDK {{ device.sdk_version }})</span>
              </div>
              <div class="flex items-center justify-between text-sm">
                <span class="text-slate-400">Architecture</span>
                <span class="text-white font-mono">{{ device.architecture }}</span>
              </div>
              <div class="flex items-center justify-between text-sm">
                <span class="text-slate-400">Type</span>
                <span class="badge badge-sm badge-outline">{{ device.type }}</span>
              </div>
            </div>

            <!-- Frida Status -->
            <div class="divider my-2"></div>
            <div class="flex items-center justify-between">
              <span class="text-sm text-slate-400">Frida Status</span>
              <div class="flex items-center gap-2">
                <div 
                  class="w-2 h-2 rounded-full status-indicator" 
                  :class="device.frida_available ? 'bg-green-500' : 'bg-red-500'"
                ></div>
                <span class="text-xs" :class="device.frida_available ? 'text-green-400' : 'text-red-400'">
                  {{ device.frida_available ? 'Available' : 'Not Available' }}
                </span>
              </div>
            </div>

            <!-- Actions -->
            <div class="card-actions justify-end mt-4">
              <button class="btn btn-sm btn-outline btn-primary">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                Connect
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else-if="!loading && scanned" class="card bg-slate-900/30 backdrop-blur-sm shadow-xl border border-slate-700/50">
        <div class="card-body items-center text-center py-16">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-24 w-24 text-slate-600 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
          </svg>
          <h3 class="text-xl font-bold text-slate-300 mb-2">No Devices Found</h3>
          <p class="text-slate-500 max-w-md">
            Connect an Android device via USB or start an emulator, then scan again.
          </p>
          <button 
            class="btn btn-primary bg-gradient-to-r from-purple-600 to-cyan-600 hover:from-purple-700 hover:to-cyan-700 border-0 mt-6"
            @click="scanDevices"
          >
            Scan Again
          </button>
        </div>
      </div>

      <!-- Initial State -->
      <div v-else-if="!scanned && !loading" class="card bg-slate-900/30 backdrop-blur-sm shadow-xl border border-slate-700/50">
        <div class="card-body items-center text-center py-16">
          <div class="w-24 h-24 bg-gradient-to-br from-purple-500/20 to-cyan-500/20 rounded-full flex items-center justify-center mb-4">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <h3 class="text-xl font-bold text-slate-300 mb-2">Ready to Scan</h3>
          <p class="text-slate-500 max-w-md">
            Click the "Scan Devices" button to discover connected Android devices and emulators.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import axios from 'axios'

export default {
  name: 'App',
  setup() {
    const devices = ref([])
    const loading = ref(false)
    const error = ref(null)
    const scanned = ref(false)
    const adbConnected = ref(false)

    const checkHealth = async () => {
      try {
        const response = await axios.get('http://localhost:8000/health')
        adbConnected.value = response.data.adb_connected
      } catch (err) {
        adbConnected.value = false
      }
    }

    const scanDevices = async () => {
      loading.value = true
      error.value = null
      
      try {
        const response = await axios.get('http://localhost:8000/api/devices')
        devices.value = response.data.devices
        scanned.value = true
        await checkHealth()
      } catch (err) {
        error.value = err.response?.data?.detail || 'Failed to connect to backend'
        devices.value = []
      } finally {
        loading.value = false
      }
    }

    const getDeviceColor = (type) => {
      if (type === 'emulator') return 'bg-gradient-to-br from-cyan-500 to-blue-500'
      if (type === 'physical') return 'bg-gradient-to-br from-purple-500 to-pink-500'
      return 'bg-gradient-to-br from-slate-500 to-slate-600'
    }

    const getStatusBadge = (state) => {
      if (state === 'online') return 'badge-success'
      if (state === 'error') return 'badge-error'
      return 'badge-warning'
    }

    onMounted(() => {
      checkHealth()
    })

    return {
      devices,
      loading,
      error,
      scanned,
      adbConnected,
      scanDevices,
      getDeviceColor,
      getStatusBadge
    }
  }
}
</script>
