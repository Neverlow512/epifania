<template>
  <div class="min-h-screen bg-black">
    <!-- Header -->
    <div class="navbar bg-black/80 backdrop-blur-md shadow-xl border-b border-primary/20">
      <div class="flex-1">
        <div class="flex items-center px-4">
          <div class="leading-tight">
            <h1 class="brand-title text-2xl md:text-3xl font-extrabold tracking-[0.12em] text-[#7100d0] uppercase cursor-pointer" @click="$router.push('/')">
              Epifania
            </h1>
            <p class="mt-1 text-xs md:text-sm text-slate-400 tracking-[0.18em] uppercase">
              Dynamic Instrumentation Platform
            </p>
          </div>
        </div>
      </div>
      <div class="flex-none px-4 gap-4">
        <!-- Frida Version Selector -->
        <div class="flex items-center gap-2">
          <label class="text-sm text-slate-400">Frida Version:</label>
          <select 
            v-model="selectedFridaVersion" 
            class="select select-sm select-bordered bg-neutral-900 border-primary/30 focus:border-primary text-white"
            @focus="loadFridaVersions"
          >
            <option value="" disabled>Select version</option>
            <option v-for="version in fridaVersions" :key="version.version" :value="version.version">
              {{ version.version }}
            </option>
          </select>
        </div>
        
        <!-- ADB Status -->
        <div class="flex items-center gap-2">
          <div class="badge badge-sm" :class="adbConnected ? 'badge-success' : 'badge-error'">
            {{ adbConnected ? 'ADB Connected' : 'ADB Offline' }}
          </div>
        </div>
      </div>
    </div>

    <!-- Warning Banner -->
    <div class="alert alert-warning shadow-lg border-0 rounded-none bg-yellow-900/20 border-b border-yellow-700/30">
      <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-5 w-5" fill="none" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
      </svg>
      <span class="text-yellow-200 text-sm">
        For best results, use emulators for Frida server installation. Physical devices may require manual setup or root access.
      </span>
    </div>

    <!-- Main Content -->
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" :selected-frida-version="selectedFridaVersion" />
      </transition>
    </router-view>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import axios from 'axios'

export default {
  name: 'App',
  setup() {
    const adbConnected = ref(false)
    const fridaVersions = ref([])
    const selectedFridaVersion = ref('')

    const checkHealth = async () => {
      try {
        const response = await axios.get('http://localhost:8000/health')
        adbConnected.value = response.data.adb_connected
      } catch (err) {
        adbConnected.value = false
      }
    }

    const loadFridaVersions = async () => {
      if (fridaVersions.value.length > 0) return
      
      try {
        const response = await axios.get('http://localhost:8000/api/frida/versions')
        fridaVersions.value = response.data.versions
        
        if (fridaVersions.value.length > 0 && !selectedFridaVersion.value) {
          selectedFridaVersion.value = fridaVersions.value[0].version
        }
      } catch (err) {
        console.error('Failed to load Frida versions:', err)
      }
    }

    onMounted(() => {
      checkHealth()
      loadFridaVersions()
      
      setInterval(checkHealth, 10000)
    })

    return {
      adbConnected,
      fridaVersions,
      selectedFridaVersion,
      loadFridaVersions
    }
  }
}
</script>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
