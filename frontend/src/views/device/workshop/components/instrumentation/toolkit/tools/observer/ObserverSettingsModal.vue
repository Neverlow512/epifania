<template>
  <div
    v-if="show"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-[3px]"
    @click.self="$emit('close')"
  >
    <div class="bg-neutral-950 border border-primary/20 ring-1 ring-primary/10 rounded-xl shadow-2xl w-full max-w-md p-5 space-y-4">
      <div class="flex items-start justify-between gap-4">
        <div class="min-w-0">
          <div class="flex items-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-primary/90" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            <h3 class="text-base font-semibold text-white truncate">Observer Settings</h3>
          </div>
          <p class="text-xs text-slate-400 mt-1">
            Configure auto-stop and log storage for this session.
          </p>
        </div>

        <button
          type="button"
          class="btn btn-ghost btn-sm btn-circle text-slate-300 hover:text-white"
          @click="$emit('close')"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div class="space-y-3">
        <div class="p-3 rounded-lg bg-neutral-900/40 border border-primary/10">
          <div class="flex items-start justify-between gap-3">
            <div class="min-w-0">
              <div class="text-xs font-semibold tracking-[0.18em] uppercase text-slate-300">Auto-stop</div>
              <div class="text-[11px] text-slate-500 mt-1">Stops the observer automatically after N seconds.</div>
            </div>
            <input
              v-model="autoStopEnabled"
              type="checkbox"
              class="toggle toggle-xs toggle-primary"
              aria-label="Toggle auto-stop"
            />
          </div>

          <div class="mt-3 flex items-center gap-2">
            <div class="join">
              <button
                type="button"
                class="btn btn-sm btn-square join-item h-8 min-h-8 bg-neutral-950/40 border border-primary/20 text-slate-200 hover:bg-neutral-800/40"
                :disabled="!autoStopEnabled"
                @click="decrementTime"
                @mousedown.prevent="startHold(-1)"
                @mouseup="stopHold"
                @mouseleave="stopHold"
                @touchstart.prevent="startHold(-1)"
                @touchend="stopHold"
                @touchcancel="stopHold"
                aria-label="Decrease seconds"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4" />
                </svg>
              </button>
              <input
                v-model.number="localTimeLimit"
                type="number"
                min="1"
                step="1"
                inputmode="numeric"
                class="input input-bordered input-sm join-item w-20 h-8 bg-neutral-950/40 text-white border-primary/20 text-right tabular-nums [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
                :disabled="!autoStopEnabled"
                :class="autoStopEnabled ? '' : 'opacity-60'"
              />
              <button
                type="button"
                class="btn btn-sm btn-square join-item h-8 min-h-8 bg-neutral-950/40 border border-primary/20 text-slate-200 hover:bg-neutral-800/40"
                :disabled="!autoStopEnabled"
                @click="incrementTime"
                @mousedown.prevent="startHold(1)"
                @mouseup="stopHold"
                @mouseleave="stopHold"
                @touchstart.prevent="startHold(1)"
                @touchend="stopHold"
                @touchcancel="stopHold"
                aria-label="Increase seconds"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                </svg>
              </button>
            </div>
            <span class="text-[11px]" :class="autoStopEnabled ? 'text-slate-400' : 'text-slate-600'">
              {{ autoStopEnabled ? 'seconds' : 'disabled' }}
            </span>
          </div>
        </div>

        <div class="p-3 rounded-lg bg-neutral-900/40 border border-primary/10">
          <div class="text-xs font-semibold tracking-[0.18em] uppercase text-slate-300">Log storage</div>
          <div class="text-[11px] text-slate-500 mt-1">Choose where Observer session files are written.</div>

          <div class="mt-3 flex gap-2">
            <input
              v-model="localLogPath"
              type="text"
              class="input input-bordered input-sm flex-1 bg-neutral-950/40 text-white border-primary/20"
            />
            <button
              type="button"
              class="btn btn-sm btn-ghost text-primary"
              @click="useDefaultPath"
              title="Restore default log path"
            >
              Default
            </button>
          </div>
          <div class="text-[10px] text-slate-500 mt-2 font-mono break-all">
            {{ defaultLogPath }}
          </div>
        </div>
      </div>

      <div class="flex gap-3 justify-end pt-1">
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
          @click="handleSave"
        >
          Save
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ObserverSettingsModal',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    timeLimit: {
      type: Number,
      default: null
    },
    logPath: {
      type: String,
      default: ''
    }
  },
  emits: ['close', 'save'],
  data() {
    return {
      defaultLogPath: 'logs/instrumentation/observer/{package}/{date}/{session}/',
      autoStopEnabled: false,
      localTimeLimit: null,
      localLogPath: '',
      holdTimer: null,
      holdStartMs: 0,
      holdDirection: 0
    }
  },
  watch: {
    show: {
      handler(newValue) {
        if (newValue) {
          if (this.timeLimit && this.timeLimit > 0) {
            this.autoStopEnabled = true
            this.localTimeLimit = this.timeLimit
          } else {
            this.autoStopEnabled = false
            this.localTimeLimit = 30
          }
          this.localLogPath = (this.logPath && this.logPath.trim()) ? this.logPath : this.defaultLogPath
        } else {
          this.stopHold()
        }
      },
      immediate: true
    }
  },
  beforeUnmount() {
    this.stopHold()
  },
  methods: {
    startHold(direction) {
      if (!this.autoStopEnabled) return
      if (direction !== 1 && direction !== -1) return
      this.stopHold()
      this.holdDirection = direction
      this.holdStartMs = Date.now()
      
      const tick = () => {
        if (!this.holdTimer) return
        const elapsedMs = Date.now() - this.holdStartMs
        const speedStep = Math.min(10, Math.floor(elapsedMs / 450))
        const nextDelay = Math.max(60, 260 - speedStep * 20)
        
        if (this.holdDirection === 1) this.incrementTime()
        else this.decrementTime()
        
        this.holdTimer = setTimeout(tick, nextDelay)
      }
      
      this.holdTimer = setTimeout(tick, 320)
    },
    stopHold() {
      if (this.holdTimer) {
        clearTimeout(this.holdTimer)
        this.holdTimer = null
      }
      this.holdDirection = 0
      this.holdStartMs = 0
    },
    incrementTime() {
      const current = Number(this.localTimeLimit) || 1
      this.localTimeLimit = Math.max(1, current + 1)
    },
    decrementTime() {
      const current = Number(this.localTimeLimit) || 1
      this.localTimeLimit = Math.max(1, current - 1)
    },
    useDefaultPath() {
      this.localLogPath = this.defaultLogPath
    },
    handleSave() {
      this.$emit('save', {
        timeLimit: this.autoStopEnabled && this.localTimeLimit && this.localTimeLimit > 0 ? this.localTimeLimit : null,
        logPath: (this.localLogPath || '').trim()
      })
      this.$emit('close')
    }
  }
}
</script>
