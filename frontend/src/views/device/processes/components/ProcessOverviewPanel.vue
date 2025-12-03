<template>
  <div class="card bg-neutral-900/60 backdrop-blur-sm shadow-xl border border-primary/20">
    <div class="card-body p-4 space-y-4">
      <div class="flex items-center justify-between gap-2">
        <div class="min-w-0 flex-1">
          <div class="flex items-center gap-2">
            <h3 class="text-sm font-semibold text-white">Process Overview</h3>
            <span 
              v-if="!isPrimary && sessionRegistered" 
              class="badge badge-xs badge-ghost text-slate-500"
              title="This tab is synced with the primary tab's refresh interval"
            >
              secondary
            </span>
          </div>
          <p v-if="data?.identity" class="text-xs text-slate-500 truncate">
            PID <span class="text-primary">{{ data.identity.pid }}</span> - {{ data.identity.name }}
          </p>
        </div>
        <div class="flex items-center gap-1 flex-shrink-0">
          <button
            type="button"
            class="btn btn-ghost btn-xs btn-circle"
            :class="loading ? 'animate-spin' : ''"
            :disabled="loading"
            title="Refresh"
            @click="$emit('refresh')"
          >
            <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
          <button
            type="button"
            class="btn btn-ghost btn-xs btn-circle"
            @click="$emit('close')"
            title="Close"
          >
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <div class="flex items-center justify-between gap-2 py-1.5 px-2 bg-black/30 rounded-lg border border-neutral-800">
        <div class="flex items-center gap-2">
          <button
            type="button"
            class="btn btn-xs"
            :class="autoRefresh ? 'btn-primary' : 'btn-ghost'"
            @click="$emit('toggle-auto-refresh')"
          >
            <svg class="w-3 h-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path v-if="autoRefresh" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
            </svg>
            {{ autoRefresh ? 'Pause' : 'Auto' }}
          </button>
          <div class="relative">
            <select
              class="select select-xs select-bordered bg-neutral-900 border-neutral-700 text-slate-300 w-20"
              :class="{ 'opacity-60 cursor-not-allowed': !isPrimary && sessionRegistered }"
              :value="refreshInterval"
              :disabled="!isPrimary && sessionRegistered"
              :title="!isPrimary && sessionRegistered ? 'Only the primary tab can change the interval' : 'Refresh interval'"
              @change="$emit('update-refresh-interval', Number($event.target.value))"
            >
              <option :value="2000">2s</option>
              <option :value="5000">5s</option>
              <option :value="10000">10s</option>
              <option :value="30000">30s</option>
            </select>
          </div>
        </div>
        <div class="flex items-center gap-2 text-[10px] text-slate-500">
          <span v-if="!isPrimary && sessionRegistered && autoRefresh" class="flex items-center gap-1 text-sky-400">
            <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
            </svg>
            synced
          </span>
          <span v-else-if="isCached" class="flex items-center gap-1 text-amber-400">
            <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            cached
          </span>
          <span v-if="lastUpdate">{{ formatTime(lastUpdate) }}</span>
        </div>
      </div>

      <div v-if="loading && !data" class="py-8 flex justify-center">
        <span class="loading loading-spinner loading-lg text-primary"></span>
      </div>

      <div v-else-if="error" class="py-4">
        <div class="flex items-center gap-3 text-red-400">
          <svg class="w-5 h-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span class="text-sm">{{ error }}</span>
        </div>
        <button
          type="button"
          class="btn btn-sm btn-ghost mt-3"
          @click="$emit('refresh')"
        >
          Try again
        </button>
      </div>

      <template v-else-if="data">
        <ProcessOverviewIdentity :identity="data.identity" />

        <div class="grid grid-cols-1 gap-4">
          <ProcessOverviewMemory :memory="data.memory" />
          <ProcessOverviewThreads :threads="data.threads" />
        </div>

        <div class="grid grid-cols-1 gap-4">
          <ProcessOverviewFiles :files="data.files" />
          <ProcessOverviewNetwork :network="data.network" />
        </div>

        <div class="grid grid-cols-1 gap-4">
          <ProcessOverviewIO 
            :io="data.io" 
            :available="data.permissions?.io_stats_available" 
          />
          <ProcessOverviewRelationships 
            :relationships="data.relationships"
            @inspect-process="$emit('inspect-process', $event)"
          />
        </div>

        <div class="border-t border-neutral-800 pt-3 flex items-center justify-between flex-wrap gap-2">
          <div class="flex items-center gap-3 text-xs text-slate-500">
            <div v-if="data.permissions?.has_root" class="flex items-center gap-1 text-emerald-400">
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
              Root access
            </div>
            <div v-else class="flex items-center gap-1 text-amber-400">
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
              No root
            </div>
            <div 
              v-if="isPrimary && autoRefresh" 
              class="flex items-center gap-1 text-emerald-400"
              title="This tab controls the refresh interval for all tabs"
            >
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
              </svg>
              primary
            </div>
            <div 
              v-else-if="!isPrimary && autoRefresh && sessionRegistered" 
              class="flex items-center gap-1 text-sky-400"
              title="Synced with primary tab - reading from cache"
            >
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
              </svg>
              synced
            </div>
          </div>

          <button
            type="button"
            class="btn btn-sm btn-error btn-outline"
            @click="$emit('kill-process', data.pid)"
          >
            <svg class="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
            Kill
          </button>
        </div>
      </template>
    </div>
  </div>
</template>

<script>
import ProcessOverviewIdentity from './ProcessOverviewIdentity.vue'
import ProcessOverviewMemory from './ProcessOverviewMemory.vue'
import ProcessOverviewThreads from './ProcessOverviewThreads.vue'
import ProcessOverviewFiles from './ProcessOverviewFiles.vue'
import ProcessOverviewNetwork from './ProcessOverviewNetwork.vue'
import ProcessOverviewIO from './ProcessOverviewIO.vue'
import ProcessOverviewRelationships from './ProcessOverviewRelationships.vue'

export default {
  name: 'ProcessOverviewPanel',
  components: {
    ProcessOverviewIdentity,
    ProcessOverviewMemory,
    ProcessOverviewThreads,
    ProcessOverviewFiles,
    ProcessOverviewNetwork,
    ProcessOverviewIO,
    ProcessOverviewRelationships
  },
  props: {
    data: {
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
    autoRefresh: {
      type: Boolean,
      default: false
    },
    refreshInterval: {
      type: Number,
      default: 5000
    },
    lastUpdate: {
      type: Date,
      default: null
    },
    isCached: {
      type: Boolean,
      default: false
    },
    isPrimary: {
      type: Boolean,
      default: true
    },
    sessionRegistered: {
      type: Boolean,
      default: false
    }
  },
  emits: [
    'inspect-process', 
    'kill-process', 
    'close', 
    'refresh', 
    'toggle-auto-refresh', 
    'update-refresh-interval'
  ],
  methods: {
    formatTime(date) {
      if (!date) return ''
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
    }
  }
}
</script>
