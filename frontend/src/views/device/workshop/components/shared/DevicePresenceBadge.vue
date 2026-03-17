<template>
  <div 
    v-if="packageId" 
    class="alert py-2 px-3 text-xs min-w-0 break-words"
    :class="alertClass"
  >
    <span v-if="checking" class="loading loading-spinner loading-xs"></span>
    <svg 
      v-else
      xmlns="http://www.w3.org/2000/svg" 
      class="h-4 w-4 flex-shrink-0" 
      fill="none" 
      viewBox="0 0 24 24" 
      stroke="currentColor"
    >
      <path 
        v-if="isInstalled" 
        stroke-linecap="round" 
        stroke-linejoin="round" 
        stroke-width="2" 
        d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" 
      />
      <path 
        v-else
        stroke-linecap="round" 
        stroke-linejoin="round" 
        stroke-width="2" 
        d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" 
      />
    </svg>
    <span v-if="isInstalled && isRunning">
      Package <strong class="font-semibold break-all">{{ packageId }}</strong> is running on this device
    </span>
    <span v-else-if="isInstalled">
      Package <strong class="font-semibold break-all">{{ packageId }}</strong> is installed on this device
    </span>
    <span v-else>
      Package <strong class="font-semibold break-all">{{ packageId }}</strong> not installed on this device
    </span>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted } from 'vue'
import axios from 'axios'

export default {
  name: 'DevicePresenceBadge',
  props: {
    packageId: {
      type: String,
      default: null
    },
    deviceSerial: {
      type: String,
      required: true
    }
  },
  setup(props) {
    const isInstalled = ref(false)
    const isRunning = ref(false)
    const checking = ref(false)
    
    const alertClass = computed(() => {
      if (isInstalled.value && isRunning.value) return 'alert-success'
      if (isInstalled.value) return 'alert-info'
      return 'alert-warning'
    })
    
    const checkPresence = async () => {
      if (!props.packageId || !props.deviceSerial) {
        isInstalled.value = false
        isRunning.value = false
        return
      }
      
      checking.value = true
      
      try {
        const markersResponse = await axios.get(
          `http://localhost:8000/api/devices/${props.deviceSerial}/workshop/install-markers/${props.packageId}`
        )
        isInstalled.value = !!markersResponse.data
      } catch (err) {
        if (err.response?.status === 404) {
          isInstalled.value = false
        } else {
          console.error('Failed to check package installation:', err)
          isInstalled.value = false
        }
      }
      
      try {
        const processResponse = await axios.get(
          `http://localhost:8000/api/devices/${props.deviceSerial}/processes`
        )
        const processes = processResponse.data.processes || []
        isRunning.value = processes.some(p => 
          p.name === props.packageId || 
          (p.name && p.name.includes('.') && p.name === props.packageId)
        )
      } catch (err) {
        console.error('Failed to check if package is running:', err)
        isRunning.value = false
      }
      
      checking.value = false
    }
    
    watch(() => props.packageId, () => {
      checkPresence()
    }, { immediate: true })
    
    onMounted(() => {
      checkPresence()
    })
    
    return {
      isInstalled,
      isRunning,
      checking,
      alertClass
    }
  }
}
</script>

