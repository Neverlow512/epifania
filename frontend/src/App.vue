<template>
  <div class="min-h-screen bg-base-200">
    <div class="navbar bg-base-300 shadow-lg">
      <div class="flex-1">
        <a class="btn btn-ghost text-xl">Epifania</a>
      </div>
    </div>

    <div class="container mx-auto p-8">
      <div class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <h2 class="card-title text-2xl mb-4">Device Manager</h2>
          
          <div class="card-actions justify-start mb-4">
            <button 
              class="btn btn-primary" 
              @click="scanDevices"
              :disabled="loading"
            >
              <span v-if="loading" class="loading loading-spinner"></span>
              {{ loading ? 'Scanning...' : 'Scan Devices' }}
            </button>
          </div>

          <div v-if="error" class="alert alert-error mb-4">
            <span>{{ error }}</span>
          </div>

          <div v-if="devices.length > 0" class="overflow-x-auto">
            <table class="table table-zebra">
              <thead>
                <tr>
                  <th>Device ID</th>
                  <th>Name</th>
                  <th>Type</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="device in devices" :key="device.id">
                  <td>{{ device.id }}</td>
                  <td>{{ device.name }}</td>
                  <td>{{ device.type }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div v-else-if="!loading && scanned" class="alert alert-info">
            <span>No devices found. Connect a device and try again.</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import axios from 'axios'

export default {
  name: 'App',
  setup() {
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

    return {
      devices,
      loading,
      error,
      scanned,
      scanDevices
    }
  }
}
</script>

