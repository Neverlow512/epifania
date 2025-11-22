<template>
  <div class="container mx-auto p-6 max-w-7xl">
    <!-- Control Panel -->
    <div class="card bg-neutral-900/60 backdrop-blur-sm shadow-2xl border border-primary/20 mb-6">
      <div class="card-body">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="card-title text-2xl text-white mb-2">Device Manager</h2>
            <p class="text-slate-400 text-sm">Manage connected Android devices and emulators</p>
          </div>
          <button 
            class="btn btn-primary border-0 gap-2 transition active:scale-95 disabled:opacity-60 disabled:pointer-events-none focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#7100d0]"
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
      <DeviceCard 
        v-for="device in devices" 
        :key="device.id"
        :device="device"
        @connect="handleConnect"
        @open="handleOpen"
      />
    </div>

    <!-- Empty State -->
    <div v-else-if="!loading && scanned" class="card bg-neutral-900/40 backdrop-blur-sm shadow-xl border border-neutral-700/50">
      <div class="card-body items-center text-center py-16">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-24 w-24 text-slate-600 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
        </svg>
        <h3 class="text-xl font-bold text-slate-300 mb-2">No Devices Found</h3>
        <p class="text-slate-500 max-w-md">
          Connect an Android device via USB or start an emulator, then scan again.
        </p>
        <button 
          class="btn btn-primary border-0 mt-6 transition active:scale-95"
          @click="scanDevices"
        >
          Scan Again
        </button>
      </div>
    </div>

    <!-- Initial State -->
    <div v-else-if="!scanned && !loading" class="card bg-neutral-900/40 backdrop-blur-sm shadow-xl border border-neutral-700/50">
      <div class="card-body items-center text-center py-16">
        <div class="w-24 h-24 bg-gradient-to-br from-[#7100d0]/20 to-black/20 rounded-full flex items-center justify-center mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-[#7100d0]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
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
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import DeviceCard from '../components/DeviceCard.vue'

export default {
  name: 'Dashboard',
  components: {
    DeviceCard
  },
  setup() {
    const router = useRouter()
    const devices = ref([])
    const loading = ref(false)
    const error = ref(null)
    const scanned = ref(false)

    const scanDevices = async () => {
      loading.value = true
      error.value = null
      
      try {
        const response = await axios.get('http://localhost:8000/api/devices')
        devices.value = response.data.devices
        scanned.value = true
      } catch (err) {
        error.value = err.response?.data?.detail || 'Failed to connect to backend'
        devices.value = []
      } finally {
        loading.value = false
      }
    }

    const handleConnect = async (device) => {
      try {
        const response = await axios.post(`http://localhost:8000/api/devices/${device.serial}/connect`)
        if (response.data.connected) {
          console.log('Device connected:', device.serial)
        }
      } catch (err) {
        console.error('Failed to connect:', err)
      }
    }

    const handleOpen = (device) => {
      router.push({ name: 'DeviceDetails', params: { id: device.serial } })
    }

    return {
      devices,
      loading,
      error,
      scanned,
      scanDevices,
      handleConnect,
      handleOpen
    }
  }
}
</script>

