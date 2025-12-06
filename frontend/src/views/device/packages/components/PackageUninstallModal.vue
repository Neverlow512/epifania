<template>
  <Teleport to="body">
    <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div
        class="absolute inset-0 bg-black/70 backdrop-blur-sm"
        @click="$emit('close')"
      ></div>

      <div class="relative bg-neutral-900 border border-red-500/30 rounded-xl shadow-2xl max-w-md w-full">
        <div class="flex items-center justify-between p-4 border-b border-neutral-800">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-lg bg-red-500/20 flex items-center justify-center">
              <svg class="w-5 h-5 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </div>
            <div>
              <h3 class="text-lg font-semibold text-white">Uninstall Package</h3>
              <p class="text-xs text-slate-500">This action cannot be undone</p>
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
          <p class="text-slate-300">
            Are you sure you want to uninstall
            <span class="font-medium text-white">{{ packageName }}</span>?
          </p>

          <p class="text-sm text-slate-400">
            This will remove the application from the device.
          </p>

          <label class="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              class="checkbox checkbox-sm checkbox-warning"
              v-model="keepData"
            />
            <span class="text-sm text-slate-300">Keep app data</span>
          </label>
          <p v-if="keepData" class="text-xs text-amber-400 ml-6">
            App data will be preserved and restored if the app is reinstalled.
          </p>
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
            class="btn btn-sm btn-error"
            :disabled="uninstalling"
            @click="handleConfirm"
          >
            <span v-if="uninstalling" class="loading loading-spinner loading-xs"></span>
            {{ uninstalling ? 'Uninstalling...' : 'Uninstall' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script>
import { ref, computed, watch } from 'vue'

export default {
  name: 'PackageUninstallModal',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    package: {
      type: Object,
      default: null
    },
    uninstalling: {
      type: Boolean,
      default: false
    }
  },
  emits: ['close', 'confirm'],
  setup(props, { emit }) {
    const keepData = ref(false)

    watch(() => props.show, (newVal) => {
      if (newVal) {
        keepData.value = false
      }
    })

    const packageName = computed(() => {
      if (!props.package) return ''
      return props.package.name || props.package.package_id
    })

    const handleConfirm = () => {
      if (!props.package) return
      emit('confirm', props.package.package_id, keepData.value)
    }

    return {
      keepData,
      packageName,
      handleConfirm
    }
  }
}
</script>

