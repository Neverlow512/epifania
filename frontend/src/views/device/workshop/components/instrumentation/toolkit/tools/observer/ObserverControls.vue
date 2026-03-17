<template>
  <div class="mt-1 ml-1 mr-1">
    <div v-if="isObserving" class="px-2 pb-1 text-[10px] text-primary/90">
      Active: {{ sessionName }}
    </div>

    <div class="p-1 rounded-md bg-neutral-900/20">
      <div class="space-y-1">
        <button
          type="button"
          class="w-full flex items-center justify-between px-2 py-2 rounded-md text-left transition-colors duration-75 hover:bg-neutral-800/40 active:bg-neutral-800/60 active:translate-y-px focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-primary/40 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
          :class="methodSelectionEnabled ? 'bg-primary/10' : ''"
          @click="handleToggleMethodSelection"
          :disabled="isObserving"
        >
          <span class="flex items-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            <span class="text-sm font-medium text-white">Select methods</span>
            <span
              v-if="selectedMethodCount > 0"
              class="badge badge-xs bg-primary text-primary-content font-semibold border border-primary/40"
              :title="`${selectedMethodCount} methods selected`"
            >
              {{ selectedMethodCount }} Methods
            </span>
          </span>
          <span class="flex items-center gap-2">
            <span
              class="badge badge-xs font-semibold tracking-[0.18em] uppercase"
              :class="methodSelectionEnabled ? 'badge-primary' : 'badge-ghost text-slate-400'"
            >
              {{ methodSelectionEnabled ? 'On' : 'Off' }}
            </span>
            <input
              type="checkbox"
              class="toggle toggle-xs toggle-primary"
              :checked="methodSelectionEnabled"
              :disabled="isObserving"
              @click.stop="handleToggleMethodSelection"
              aria-label="Toggle method selection"
            />
          </span>
        </button>

        <button
          type="button"
          class="w-full flex items-center justify-between px-2 py-2 rounded-md text-left transition-colors duration-75 hover:bg-neutral-800/40 active:bg-neutral-800/60 active:translate-y-px focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-primary/40 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
          :disabled="!canStart || isObserving"
          @click="handleStart"
        >
          <span class="flex items-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-primary/90" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span class="text-sm font-medium text-white">Start</span>
          </span>
          <span class="text-[10px] font-semibold tracking-[0.18em] uppercase text-slate-400">
            {{ canStart ? 'Ready' : (fridaAttached ? 'Select' : 'No Frida') }}
          </span>
        </button>

        <button
          type="button"
          class="w-full flex items-center justify-between px-2 py-2 rounded-md text-left transition-colors duration-75 hover:bg-neutral-800/40 active:bg-neutral-800/60 active:translate-y-px focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-primary/40 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
          @click="handleStop"
          :disabled="!isObserving"
        >
          <span class="flex items-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-red-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z" />
            </svg>
            <span class="text-sm font-medium text-white">Stop</span>
          </span>
          <span class="text-[10px] font-semibold tracking-[0.18em] uppercase text-slate-400">
            {{ isObserving ? 'Running' : 'Idle' }}
          </span>
        </button>

        <button
          type="button"
          class="w-full flex items-center justify-between px-2 py-2 rounded-md text-left transition-colors duration-75 hover:bg-neutral-800/40 active:bg-neutral-800/60 active:translate-y-px focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-primary/40 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
          :disabled="isObserving"
          @click="showSettingsModal = true"
          title="Configure time limit and log path"
        >
          <span class="flex items-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            <span class="text-sm font-medium text-white">Settings</span>
          </span>
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </button>

        <button
          type="button"
          class="w-full flex items-center justify-between px-2 py-2 rounded-md text-left transition-colors duration-75 hover:bg-neutral-800/40 active:bg-neutral-800/60 active:translate-y-px focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-primary/40 cursor-pointer"
          @click="handleOpenDashboard"
          title="Open toolkit dashboard"
        >
          <span class="flex items-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-primary/90" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <span class="text-sm font-medium text-white">Dashboard</span>
          </span>
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>
    </div>

    <ObserverSettingsModal
      :show="showSettingsModal"
      :timeLimit="timeLimit"
      :logPath="logPath"
      @close="showSettingsModal = false"
      @save="handleSettingsSave"
    />
  </div>
</template>

<script>
import ObserverSettingsModal from './ObserverSettingsModal.vue'

export default {
  name: 'ObserverControls',
  components: {
    ObserverSettingsModal
  },
  props: {
    selectedMethodCount: {
      type: Number,
      default: 0
    },
    fridaAttached: {
      type: Boolean,
      default: false
    },
    isObserving: {
      type: Boolean,
      default: false
    },
    sessionName: {
      type: String,
      default: ''
    },
    timeLimit: {
      type: Number,
      default: null
    },
    logPath: {
      type: String,
      default: ''
    },
    methodSelectionEnabled: {
      type: Boolean,
      default: false
    }
  },
  emits: ['start', 'stop', 'update:timeLimit', 'update:logPath', 'toggle-method-selection', 'open-dashboard'],
  data() {
    return {
      showSettingsModal: false
    }
  },
  computed: {
    canStart() {
      return this.methodSelectionEnabled && this.selectedMethodCount > 0 && this.fridaAttached && !this.isObserving
    }
  },
  methods: {
    handleToggleMethodSelection() {
      this.$emit('toggle-method-selection')
    },
    handleStart() {
      this.$emit('start')
    },
    handleStop() {
      this.$emit('stop')
    },
    handleSettingsSave(settings) {
      this.$emit('update:timeLimit', settings.timeLimit)
      this.$emit('update:logPath', settings.logPath)
    },
    handleOpenDashboard() {
      this.$emit('open-dashboard')
    }
  }
}
</script>
