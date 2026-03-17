<template>
  <Teleport to="body">
    <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div
        class="absolute inset-0 bg-black/70 backdrop-blur-sm"
        @click="$emit('close')"
      ></div>

      <div class="relative bg-neutral-900 border border-primary/30 rounded-xl shadow-2xl max-w-lg w-full">
        <div class="flex items-center justify-between p-4 border-b border-neutral-800">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-lg bg-violet-500/20 flex items-center justify-center">
              <svg class="w-5 h-5 text-violet-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
              </svg>
            </div>
            <div>
              <h3 class="text-lg font-semibold text-white">Install APK</h3>
              <p class="text-xs text-slate-500">Install an application package</p>
            </div>
          </div>
          <button
            type="button"
            class="btn btn-ghost btn-sm btn-circle"
            @click="$emit('close')"
          >
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="p-4 space-y-4">
          <div class="flex gap-4">
            <label class="flex items-center gap-2 cursor-pointer">
              <input
                type="radio"
                name="source-type"
                class="radio radio-primary radio-sm"
                :checked="isLocalFile"
                @change="isLocalFile = true"
              />
              <span class="text-sm text-slate-300">From my computer</span>
            </label>
            <label class="flex items-center gap-2 cursor-pointer">
              <input
                type="radio"
                name="source-type"
                class="radio radio-primary radio-sm"
                :checked="!isLocalFile"
                @change="isLocalFile = false"
              />
              <span class="text-sm text-slate-300">From device</span>
            </label>
          </div>

          <div v-if="isLocalFile" class="space-y-3">
            <div>
              <label class="text-sm text-slate-400 mb-1 block">APK File or Folder</label>
              <div class="flex gap-2">
                <input
                  type="text"
                  class="input input-sm input-bordered bg-neutral-800 border-neutral-700 text-white flex-1"
                  :value="localPath"
                  placeholder="/path/to/app.apk or /path/to/split_apks_folder"
                  @input="localPath = $event.target.value"
                />
              </div>
              <p class="text-xs text-slate-500 mt-1">
                Enter path to APK file or folder containing split APKs
              </p>
              <div class="alert alert-info bg-blue-500/10 border-blue-500/30 mt-2 p-2">
                <svg class="w-4 h-4 text-blue-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span class="text-xs text-blue-200">
                  For split APKs, provide the folder path containing all APK files
                </span>
              </div>
            </div>

            <div v-if="availableApks.length > 0">
              <label class="text-sm text-slate-400 mb-2 block">Available APKs</label>
              <div class="max-h-48 overflow-y-auto space-y-2 border border-neutral-800 rounded-lg p-2 bg-neutral-800/50">
                <div
                  v-for="apk in availableApks"
                  :key="apk.path"
                  class="flex items-center gap-2 p-2 rounded hover:bg-neutral-700/50 cursor-pointer transition-colors"
                  @click="selectAvailableApk(apk.path)"
                >
                  <div class="flex-shrink-0">
                    <div
                      v-if="apk.type === 'single'"
                      class="w-8 h-8 rounded bg-violet-500/20 flex items-center justify-center"
                    >
                      <svg class="w-4 h-4 text-violet-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                      </svg>
                    </div>
                    <div
                      v-else
                      class="w-8 h-8 rounded bg-blue-500/20 flex items-center justify-center"
                    >
                      <svg class="w-4 h-4 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                      </svg>
                    </div>
                  </div>
                  <div class="flex-1 min-w-0">
                    <p class="text-sm text-white font-medium truncate">{{ apk.name }}</p>
                    <p class="text-xs text-slate-500">
                      <span v-if="apk.type === 'single'">Single APK</span>
                      <span v-else>Split APK ({{ apk.file_count }} files)</span>
                      · {{ apk.size_mb }} MB
                    </p>
                  </div>
                  <div class="flex-shrink-0">
                    <svg class="w-4 h-4 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                </div>
              </div>
            </div>

            <div v-else-if="loadingApks" class="text-center py-4">
              <span class="loading loading-spinner loading-sm text-primary"></span>
              <p class="text-xs text-slate-500 mt-2">Loading available APKs...</p>
            </div>

            <div v-if="recentPaths.length > 0">
              <label class="text-sm text-slate-400 mb-1 block">Recent Paths</label>
              <select
                class="select select-sm select-bordered bg-neutral-800 border-neutral-700 text-white w-full"
                @change="selectRecentPath($event.target.value)"
              >
                <option value="">Select a recent path...</option>
                <option v-for="path in recentPaths" :key="path" :value="path">
                  {{ path }}
                </option>
              </select>
            </div>

            <div>
              <label class="text-sm text-slate-400 mb-1 block">Device Staging Path</label>
              <input
                type="text"
                class="input input-sm input-bordered bg-neutral-800 border-neutral-700 text-white w-full font-mono text-xs"
                v-model="tempPath"
              />
              <p class="text-xs text-slate-500 mt-1">Temporary location on device for installation</p>
            </div>
          </div>

          <div v-else class="space-y-3">
            <div>
              <label class="text-sm text-slate-400 mb-1 block">APK Path on Device</label>
              <input
                type="text"
                class="input input-sm input-bordered bg-neutral-800 border-neutral-700 text-white w-full font-mono"
                v-model="devicePath"
                placeholder="/sdcard/Download/app.apk"
              />
            </div>

            <div class="flex flex-wrap gap-2">
              <button
                type="button"
                class="btn btn-xs btn-ghost"
                @click="devicePath = '/sdcard/Download/'"
              >
                /sdcard/Download/
              </button>
              <button
                type="button"
                class="btn btn-xs btn-ghost"
                @click="devicePath = '/data/local/tmp/'"
              >
                /data/local/tmp/
              </button>
            </div>
          </div>
        </div>

        <div class="flex justify-end gap-2 p-4 border-t border-neutral-800">
          <button
            type="button"
            class="btn btn-sm btn-ghost"
            @click="$emit('close')"
          >
            Cancel
          </button>
          <button
            type="button"
            class="btn btn-sm btn-primary"
            :disabled="!canInstall || installing"
            @click="handleInstall"
          >
            <span v-if="installing" class="loading loading-spinner loading-xs"></span>
            {{ installing ? 'Installing...' : 'Install' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script>
import { ref, computed, watch } from 'vue'
import axios from 'axios'

export default {
  name: 'PackageInstallModal',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    installing: {
      type: Boolean,
      default: false
    },
    deviceTempPath: {
      type: String,
      default: '/data/local/tmp/epifania_install.apk'
    },
    recentPaths: {
      type: Array,
      default: () => []
    },
    deviceSerial: {
      type: String,
      required: true
    }
  },
  emits: ['close', 'install'],
  setup(props, { emit }) {
    const isLocalFile = ref(true)
    const localPath = ref('')
    const devicePath = ref('')
    const tempPath = ref(props.deviceTempPath)
    const availableApks = ref([])
    const loadingApks = ref(false)

    const fetchAvailableApks = async () => {
      if (!props.deviceSerial) return
      
      loadingApks.value = true
      try {
        const response = await axios.get(
          `http://localhost:8000/api/devices/${props.deviceSerial}/packages/available-apks`
        )
        availableApks.value = response.data.apks || []
      } catch (err) {
        console.error('Failed to fetch available APKs:', err)
        availableApks.value = []
      } finally {
        loadingApks.value = false
      }
    }

    watch(() => props.show, (newVal) => {
      if (newVal) {
        localPath.value = ''
        devicePath.value = ''
        tempPath.value = props.deviceTempPath
        isLocalFile.value = true
        fetchAvailableApks()
      }
    })

    const canInstall = computed(() => {
      if (isLocalFile.value) {
        return localPath.value.trim().length > 0
      }
      return devicePath.value.trim().length > 0
    })

    const selectRecentPath = (path) => {
      if (path) {
        localPath.value = path
      }
    }

    const selectAvailableApk = (path) => {
      localPath.value = path
    }

    const handleInstall = () => {
      if (!canInstall.value) return

      const source = isLocalFile.value ? localPath.value.trim() : devicePath.value.trim()
      emit('install', source, isLocalFile.value, tempPath.value)
    }

    return {
      isLocalFile,
      localPath,
      devicePath,
      tempPath,
      availableApks,
      loadingApks,
      canInstall,
      selectRecentPath,
      selectAvailableApk,
      handleInstall
    }
  }
}
</script>

