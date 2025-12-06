<template>
  <Teleport to="body">
    <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div
        class="absolute inset-0 bg-black/70 backdrop-blur-sm"
        @click="$emit('close')"
      ></div>

      <div class="relative bg-neutral-900 border border-primary/30 rounded-xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        <div class="flex items-center justify-between p-4 border-b border-neutral-800">
          <div class="flex items-center gap-3">
            <div
              class="w-12 h-12 rounded-lg flex items-center justify-center text-lg font-bold"
              :class="packageData?.is_system ? 'bg-slate-700 text-slate-300' : 'bg-violet-500/20 text-violet-400'"
            >
              {{ getPackageInitials() }}
            </div>
            <div>
              <h3 class="text-lg font-semibold text-white">
                {{ packageData?.name || packageData?.package_id || 'Loading...' }}
              </h3>
              <p class="text-xs text-slate-500 font-mono">{{ packageData?.package_id }}</p>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <button
              type="button"
              class="btn btn-ghost btn-sm btn-circle"
              @click="showDetailsHelp = true"
              title="Help"
            >
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </button>
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
        </div>

        <div v-if="loading" class="flex-1 flex items-center justify-center py-16">
          <span class="loading loading-spinner loading-lg text-primary"></span>
        </div>

        <div v-else-if="error" class="flex-1 flex items-center justify-center py-16">
          <div class="text-center">
            <svg class="w-12 h-12 mx-auto mb-4 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <p class="text-red-400">{{ error }}</p>
          </div>
        </div>

        <div v-else-if="packageData" class="flex-1 overflow-y-auto p-4 space-y-4">
          <div class="flex flex-wrap gap-2 pb-4 border-b border-neutral-800">
            <button
              v-if="packageData.is_running"
              class="btn btn-sm btn-warning"
              :disabled="actionInProgress"
              @click="$emit('stop', packageData)"
            >
              Force Stop
            </button>
            <button
              v-else
              class="btn btn-sm btn-success"
              :disabled="actionInProgress"
              @click="$emit('launch', packageData)"
            >
              Launch
            </button>
            <button
              v-if="packageData.is_running"
              class="btn btn-sm btn-ghost"
              @click="$emit('navigate-to-process', packageData.pid)"
            >
              View Process ({{ packageData.pid }})
            </button>
            <button
              class="btn btn-sm btn-ghost"
              :disabled="actionInProgress"
              @click="$emit('pull', packageData)"
            >
              Extract APK
            </button>
            <button
              class="btn btn-sm btn-ghost"
              :disabled="actionInProgress"
              @click="$emit('clear-cache', packageData)"
            >
              Clear Cache
            </button>
            <button
              class="btn btn-sm btn-ghost text-amber-400"
              :disabled="actionInProgress"
              @click="$emit('clear-data', packageData)"
            >
              Clear Data
            </button>
            <button
              class="btn btn-sm btn-error btn-outline ml-auto"
              :disabled="actionInProgress"
              @click="$emit('uninstall', packageData)"
            >
              Uninstall
            </button>
          </div>

          <section class="space-y-2">
            <h4 class="text-sm font-medium text-slate-300 flex items-center gap-2">
              <svg class="w-4 h-4 text-violet-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V8a2 2 0 00-2-2h-5m-4 0V5a2 2 0 114 0v1m-4 0a2 2 0 104 0m-5 8a2 2 0 100-4 2 2 0 000 4zm0 0c1.306 0 2.417.835 2.83 2M9 14a3.001 3.001 0 00-2.83 2M15 11h3m-3 4h2" />
              </svg>
              Identity
            </h4>
            <div class="bg-black/40 rounded-lg p-3 border border-neutral-800 grid grid-cols-2 gap-3 text-sm">
              <div>
                <span class="text-slate-500">Version</span>
                <p class="text-white font-mono">{{ packageData.version || '--' }}</p>
              </div>
              <div>
                <span class="text-slate-500">Version Code</span>
                <p class="text-white font-mono">{{ packageData.version_code || '--' }}</p>
              </div>
              <div>
                <span class="text-slate-500">Install Source</span>
                <p class="text-white font-mono text-xs">{{ packageData.install_source || '--' }}</p>
              </div>
              <div>
                <span class="text-slate-500">Main Activity</span>
                <p class="text-white font-mono text-xs truncate" :title="packageData.main_activity">
                  {{ packageData.main_activity || '--' }}
                </p>
              </div>
              <div>
                <span class="text-slate-500">Target SDK</span>
                <p class="text-white">{{ packageData.target_sdk || '--' }}</p>
              </div>
              <div>
                <span class="text-slate-500">Min SDK</span>
                <p class="text-white">{{ packageData.min_sdk || '--' }}</p>
              </div>
            </div>
          </section>

          <section class="space-y-2">
            <h4 class="text-sm font-medium text-slate-300 flex items-center gap-2">
              <svg class="w-4 h-4 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
              </svg>
              Storage
            </h4>
            <div class="bg-black/40 rounded-lg p-3 border border-neutral-800 grid grid-cols-2 gap-3 text-sm">
              <div>
                <span class="text-slate-500">APK Size</span>
                <p class="text-white">{{ formatSize(packageData.size_mb) }}</p>
              </div>
              <div>
                <span class="text-slate-500">Data Size</span>
                <p class="text-white">{{ formatSize(packageData.data_size_mb) }}</p>
              </div>
              <div>
                <span class="text-slate-500">Cache Size</span>
                <p class="text-white">{{ formatSize(packageData.cache_size_mb) }}</p>
              </div>
              <div>
                <span class="text-slate-500">Total</span>
                <p class="text-white font-medium">{{ formatTotalSize() }}</p>
              </div>
              <div class="col-span-2">
                <span class="text-slate-500">APK Path</span>
                <p class="text-white font-mono text-xs break-all">{{ packageData.apk_path || '--' }}</p>
              </div>
            </div>
          </section>

          <section class="space-y-2">
            <h4 class="text-sm font-medium text-slate-300 flex items-center gap-2">
              <svg class="w-4 h-4 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
              Permissions
              <span class="badge badge-sm badge-ghost">{{ packageData.permissions_count || 0 }}</span>
            </h4>
            <div class="bg-black/40 rounded-lg border border-neutral-800">
              <div
                v-if="packageData.permissions && packageData.permissions.length > 0"
                class="max-h-48 overflow-y-auto p-3 space-y-1"
              >
                <div
                  v-for="perm in packageData.permissions"
                  :key="perm"
                  class="text-xs font-mono text-slate-400 py-1 border-b border-neutral-800 last:border-0"
                  :class="{ 'text-amber-400': isDangerousPermission(perm) }"
                >
                  {{ perm }}
                </div>
              </div>
              <div v-else class="p-3 text-sm text-slate-500">
                No permissions declared
              </div>
            </div>
          </section>

          <section v-if="packageData.signing_cert" class="space-y-2">
            <h4 class="text-sm font-medium text-slate-300 flex items-center gap-2">
              <svg class="w-4 h-4 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
              </svg>
              Signing Certificate
            </h4>
            <div class="bg-black/40 rounded-lg p-3 border border-neutral-800">
              <div class="flex items-center gap-2">
                <p class="text-xs font-mono text-slate-400 flex-1">{{ fullCertHash }}</p>
                <button
                  type="button"
                  class="btn btn-xs btn-ghost flex-shrink-0"
                  @click="copyToClipboard(fullCertHash)"
                  title="Copy signature ID"
                >
                  <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                </button>
              </div>
              <p class="text-xs text-slate-500 mt-1">Android signature reference ID</p>
            </div>
          </section>
        </div>
      </div>
    </div>

    <PackageDetailsHelpModal
      :show="showDetailsHelp"
      @close="showDetailsHelp = false"
    />
  </Teleport>
</template>

<script>
import { ref, computed } from 'vue'
import { useToast } from '../../../../composables/useToast'
import PackageDetailsHelpModal from './PackageDetailsHelpModal.vue'

export default {
  name: 'PackageDetailsModal',
  components: {
    PackageDetailsHelpModal
  },
  props: {
    show: {
      type: Boolean,
      default: false
    },
    packageData: {
      type: Object,
      default: null
    },
    loading: {
      type: Boolean,
      default: false
    },
    error: {
      type: String,
      default: null
    },
    actionInProgress: {
      type: Boolean,
      default: false
    }
  },
  emits: [
    'close',
    'launch',
    'stop',
    'uninstall',
    'pull',
    'clear-cache',
    'clear-data',
    'navigate-to-process'
  ],
  setup(props) {
    const toast = useToast()
    const showDetailsHelp = ref(false)

    const fullCertHash = computed(() => {
      if (!props.packageData?.signing_cert) return ''
      return props.packageData.signing_cert
    })

    return { toast, showDetailsHelp, fullCertHash }
  },
  methods: {
    getPackageInitials() {
      if (!this.packageData) return '??'
      const name = this.packageData.name || this.packageData.package_id
      const parts = name.split(/[.\s]/)
      if (parts.length >= 2) {
        return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
      }
      return name.substring(0, 2).toUpperCase()
    },
    formatSize(mb) {
      if (mb === null || mb === undefined) return '--'
      if (mb < 1) return `${(mb * 1024).toFixed(0)} KB`
      return `${mb.toFixed(1)} MB`
    },
    formatTotalSize() {
      if (!this.packageData) return '--'
      const total = (this.packageData.size_mb || 0) +
                    (this.packageData.data_size_mb || 0) +
                    (this.packageData.cache_size_mb || 0)
      if (total === 0) return '--'
      return this.formatSize(total)
    },
    isDangerousPermission(perm) {
      const dangerous = [
        'CAMERA', 'RECORD_AUDIO', 'READ_CONTACTS', 'WRITE_CONTACTS',
        'READ_CALL_LOG', 'WRITE_CALL_LOG', 'READ_CALENDAR', 'WRITE_CALENDAR',
        'READ_SMS', 'SEND_SMS', 'RECEIVE_SMS', 'READ_PHONE_STATE',
        'CALL_PHONE', 'READ_EXTERNAL_STORAGE', 'WRITE_EXTERNAL_STORAGE',
        'ACCESS_FINE_LOCATION', 'ACCESS_COARSE_LOCATION', 'ACCESS_BACKGROUND_LOCATION',
        'BODY_SENSORS', 'ACTIVITY_RECOGNITION'
      ]
      return dangerous.some(d => perm.includes(d))
    },
    async copyToClipboard(text) {
      try {
        await navigator.clipboard.writeText(text)
        this.toast.success('Copied to clipboard')
      } catch (err) {
        console.error('Failed to copy:', err)
        this.toast.error('Failed to copy to clipboard')
      }
    }
  }
}
</script>

