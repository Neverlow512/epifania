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
            <div class="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center">
              <svg class="w-5 h-5 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
            </div>
            <div>
              <h3 class="text-lg font-semibold text-white">Extract APK</h3>
              <p class="text-xs text-slate-500">Save APK to local filesystem</p>
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
          <div>
            <label class="text-sm text-slate-400 mb-1 block">Package</label>
            <p class="text-white font-medium">{{ packageName }}</p>
            <p class="text-xs text-slate-500 font-mono">{{ packageId }}</p>
          </div>

          <div>
            <label class="text-sm text-slate-400 mb-1 block">Destination Path</label>
            <input
              type="text"
              class="input input-sm input-bordered bg-neutral-800 border-neutral-700 text-white w-full font-mono text-xs"
              v-model="destinationPath"
              placeholder="tmp/extracted_apks/com.example.apk"
            />
            <p class="text-xs text-slate-500 mt-1">
              Path relative to project root or absolute path
            </p>
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

          <div class="flex flex-wrap gap-2">
            <button
              type="button"
              class="btn btn-xs btn-ghost"
              @click="destinationPath = defaultPath"
            >
              Use Default
            </button>
            <button
              type="button"
              class="btn btn-xs btn-ghost"
              @click="destinationPath = 'tmp/extracted_apks/'"
            >
              tmp/extracted_apks/
            </button>
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
            :disabled="!canExtract || pulling"
            @click="handleConfirm"
          >
            <span v-if="pulling" class="loading loading-spinner loading-xs"></span>
            {{ pulling ? 'Extracting...' : 'Extract' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script>
import { ref, computed, watch } from 'vue'

export default {
  name: 'PackagePullModal',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    package: {
      type: Object,
      default: null
    },
    pulling: {
      type: Boolean,
      default: false
    },
    defaultPath: {
      type: String,
      default: ''
    },
    recentPaths: {
      type: Array,
      default: () => []
    }
  },
  emits: ['close', 'confirm'],
  setup(props, { emit }) {
    const destinationPath = ref('')

    watch(() => props.show, (newVal) => {
      if (newVal && props.defaultPath) {
        destinationPath.value = props.defaultPath
      }
    })

    watch(() => props.defaultPath, (newVal) => {
      if (props.show && newVal) {
        destinationPath.value = newVal
      }
    })

    const packageName = computed(() => {
      if (!props.package) return ''
      return props.package.name || props.package.package_id
    })

    const packageId = computed(() => {
      return props.package?.package_id || ''
    })

    const canExtract = computed(() => {
      return destinationPath.value.trim().length > 0
    })

    const selectRecentPath = (path) => {
      if (path) {
        destinationPath.value = path
      }
    }

    const handleConfirm = () => {
      if (!props.package || !canExtract.value) return
      emit('confirm', props.package.package_id, destinationPath.value.trim())
    }

    return {
      destinationPath,
      packageName,
      packageId,
      canExtract,
      selectRecentPath,
      handleConfirm
    }
  }
}
</script>

