<template>
  <div class="device-card card bg-neutral-900/60 backdrop-blur-sm shadow-xl border border-primary/20 hover:border-primary/40">
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
        <div class="flex items-center justify-between text-sm">
          <span class="text-slate-400">Root Access</span>
          <div class="flex items-center gap-1">
            <svg v-if="device.has_root" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span :class="device.has_root ? 'text-green-400' : 'text-red-400'" class="text-xs">
              {{ device.has_root ? 'Available' : 'Not Available' }}
            </span>
          </div>
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
      <div class="card-actions justify-end mt-4 gap-2">
        <button 
          class="btn btn-sm btn-outline btn-primary transition active:scale-95"
          @click="$emit('connect', device)"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          Connect
        </button>
        <button 
          class="btn btn-sm btn-primary transition active:scale-95"
          @click="$emit('open', device)"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
          </svg>
          Open
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DeviceCard',
  props: {
    device: {
      type: Object,
      required: true
    }
  },
  emits: ['connect', 'open'],
  setup() {
    const getDeviceColor = (type) => {
      if (type === 'emulator') return 'bg-gradient-to-br from-[#7100d0] to-purple-700'
      if (type === 'physical') return 'bg-gradient-to-br from-[#7100d0] to-black'
      return 'bg-gradient-to-br from-slate-500 to-slate-600'
    }

    const getStatusBadge = (state) => {
      if (state === 'online') return 'badge-success'
      if (state === 'error') return 'badge-error'
      return 'badge-warning'
    }

    return {
      getDeviceColor,
      getStatusBadge
    }
  }
}
</script>

