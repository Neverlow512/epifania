<template>
  <div
    class="hook-card hud-tile border border-primary/15 p-2 transition-colors duration-150"
    :class="[{ 'hook-card--pulse': pulse }, cardToneClass]"
    :style="{ '--hook-accent': accentColor }"
    :title="`${hook.class_name}.${hook.method_name}`"
  >
    <div class="mb-2">
      <div class="flex items-center justify-between gap-2">
        <div class="text-[0.65rem] uppercase tracking-wider text-slate-400/80">Class</div>
        <button
          v-if="isClassExpandable"
          type="button"
          class="btn btn-ghost btn-xs h-6 min-h-6 px-2 text-slate-300/70 hover:text-white"
          :aria-label="classExpanded ? 'Collapse class' : 'Expand class'"
          @click="toggleClassExpanded"
        >
          <span class="text-xs">{{ classExpanded ? '▴' : '▾' }}</span>
        </button>
      </div>
      <div class="text-[0.78rem] text-slate-200 leading-tight relative">
        <button
          v-if="!classExpanded"
          type="button"
          class="w-full text-left truncate underline decoration-dotted decoration-slate-500/60 hover:decoration-slate-300 cursor-pointer"
          @click="copyClassName"
        >
          {{ hook.class_name || '' }}
        </button>
        <button
          v-else
          type="button"
          class="w-full text-left underline decoration-dotted decoration-slate-500/60 hover:decoration-slate-300 cursor-pointer"
          @click="copyClassName"
        >
          <div class="wrap-break-word">{{ classLine1 }}</div>
          <div v-if="classLine2" class="wrap-break-word text-slate-300/90">{{ classLine2 }}</div>
        </button>
        <transition name="fade">
          <div
            v-if="showCopied"
            class="absolute -top-1 right-0 text-[0.65rem] font-semibold text-success bg-black/90 px-2 py-0.5 rounded border border-success/30 pointer-events-none"
          >
            Copied!
          </div>
        </transition>
      </div>
      <div class="mt-1 text-[0.65rem] uppercase tracking-wider text-slate-400/80">Method</div>
      <div class="text-[0.85rem] text-white font-semibold truncate leading-tight">
        {{ hook.method_name || '' }}
      </div>
    </div>

    <div class="gauge-wrap">
      <SpeedometerGauge
        :value="hook.call_rate || 0"
        :maxValue="maxCallRate"
        :size="86"
      />
    </div>

    <div class="mt-2 flex items-center justify-between text-[0.68rem] text-slate-300/85">
      <span class="tabular-nums">
        <span class="text-slate-400/90">Calls</span>
        <span class="text-slate-200 font-semibold">{{ hook.call_count || 0 }}</span>
      </span>
      <span class="text-slate-500/60">·</span>
      <span class="tabular-nums">
        <span class="text-slate-400/90">Errors</span>
        <span :class="(hook.error_count || 0) > 0 ? 'text-error font-semibold' : 'text-slate-200 font-semibold'">{{ hook.error_count || 0 }}</span>
      </span>
      <span class="text-slate-500/60">·</span>
      <span class="tabular-nums">
        <span class="text-slate-400/90">Rate</span>
        <span class="text-slate-200 font-semibold">{{ displayRate }}</span>/s
      </span>
    </div>
  </div>
</template>

<script>
import SpeedometerGauge from './SpeedometerGauge.vue'

export default {
  name: 'HookCard',
  components: {
    SpeedometerGauge
  },
  props: {
    hook: {
      type: Object,
      required: true
    },
    maxCallRate: {
      type: Number,
      default: 10
    }
  },
  data() {
    return {
      classExpanded: false,
      pulse: false,
      showCopied: false,
      _pulseTimer: null,
      _prevCalls: 0,
      _copiedTimer: null
    }
  },
  watch: {
    'hook.call_count': {
      immediate: true,
      handler(next) {
        const n = Number(next || 0)
        if (this._prevCalls && n > this._prevCalls) {
          this.pulse = true
          if (this._pulseTimer) clearTimeout(this._pulseTimer)
          this._pulseTimer = setTimeout(() => {
            this.pulse = false
          }, 320)
        }
        this._prevCalls = n
      }
    }
  },
  computed: {
    truncatedClassName() {
      const className = this.hook.class_name || ''
      const parts = className.split('.')
      if (parts.length > 2) {
        return `...${parts.slice(-2).join('.')}`
      }
      return className
    },
    truncatedMethodName() {
      const methodName = this.hook.method_name || ''
      if (methodName.length > 20) {
        return methodName.substring(0, 17) + '...'
      }
      return methodName
    },
    errorClass() {
      const errorCount = this.hook.error_count || 0
      return errorCount > 0 ? 'text-red-400' : 'text-slate-300'
    },
    displayRate() {
      const v = this.hook.call_rate || 0
      if (v >= 100) return Math.round(v)
      if (v >= 10) return v.toFixed(1)
      return v.toFixed(2)
    },
    classLine1() {
      const full = this.hook.class_name || ''
      const parts = full.split('.').filter(Boolean)
      if (parts.length <= 3) return full
      const splitIdx = Math.ceil(parts.length / 2)
      return parts.slice(0, splitIdx).join('.')
    },
    classLine2() {
      const full = this.hook.class_name || ''
      const parts = full.split('.').filter(Boolean)
      if (parts.length <= 3) return ''
      const splitIdx = Math.ceil(parts.length / 2)
      return parts.slice(splitIdx).join('.')
    },
    isClassExpandable() {
      const s = this.hook.class_name || ''
      return s.length > 26
    },
    accentColor() {
      const errors = this.hook.error_count || 0
      const rate = this.hook.call_rate || 0
      if (errors > 0) return 'rgba(239, 68, 68, 0.95)'
      if (rate > 0.01) return 'rgba(34, 211, 238, 0.9)'
      return 'rgba(148, 163, 184, 0.55)'
    },
    cardToneClass() {
      const errors = this.hook.error_count || 0
      const rate = this.hook.call_rate || 0
      if (errors > 0) return 'hook-card--error'
      if (rate > 0.01) return 'hook-card--active'
      return 'hook-card--idle'
    }
  },
  methods: {
    toggleClassExpanded() {
      if (!this.isClassExpandable) return
      this.classExpanded = !this.classExpanded
    },
    async copyClassName() {
      const className = this.hook.class_name || ''
      if (!className) return
      
      try {
        await navigator.clipboard.writeText(className)
        this.showCopied = true
        if (this._copiedTimer) clearTimeout(this._copiedTimer)
        this._copiedTimer = setTimeout(() => {
          this.showCopied = false
        }, 1500)
      } catch (_) {
        // clipboard not available
      }
    }
  }
}
</script>

<style scoped>
.hook-card {
  min-height: 132px;
  display: flex;
  flex-direction: column;
}

.hud-tile {
  clip-path: polygon(
    10px 0,
    calc(100% - 10px) 0,
    100% 10px,
    100% calc(100% - 10px),
    calc(100% - 10px) 100%,
    10px 100%,
    0 calc(100% - 10px),
    0 10px
  );
}

.hook-card {
  background:
    radial-gradient(120px 90px at 50% 50%, rgba(255, 255, 255, 0.035), transparent 60%),
    linear-gradient(180deg, rgba(0, 0, 0, 0.78), rgba(0, 0, 0, 0.62));
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.04),
    inset 0 -1px 0 rgba(0, 0, 0, 0.7);
}

.hook-card::after {
  content: '';
  position: absolute;
  left: 10px;
  right: 10px;
  bottom: 6px;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--hook-accent), transparent);
  opacity: 0.85;
  pointer-events: none;
}

.hook-card {
  position: relative;
}

.hook-card--idle {
  border-color: rgba(113, 0, 208, 0.12);
}

.hook-card--active {
  border-color: rgba(34, 211, 238, 0.16);
}

.hook-card--error {
  border-color: rgba(239, 68, 68, 0.22);
}

.hook-card--pulse::after {
  animation: accentPulse 0.35s ease-out;
}

@keyframes accentPulse {
  0% {
    opacity: 0.45;
    transform: scaleX(0.92);
  }
  60% {
    opacity: 1;
    transform: scaleX(1);
  }
  100% {
    opacity: 0.85;
    transform: scaleX(1);
  }
}

.gauge-wrap {
  height: 86px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 2px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
