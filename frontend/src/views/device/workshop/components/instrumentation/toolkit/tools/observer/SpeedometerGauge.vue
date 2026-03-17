<template>
  <div class="tach" :style="{ width: size + 'px', height: size + 'px' }">
    <svg :width="size" :height="size" :viewBox="`0 0 ${size} ${size}`">
      <!-- Tick bars -->
      <g class="tach-ticks">
        <line
          v-for="t in ticks"
          :key="t.i"
          :x1="t.x1"
          :y1="t.y1"
          :x2="t.x2"
          :y2="t.y2"
          class="tach-tick"
          :class="{ 'tach-tick--major': t.isMajor }"
          :stroke="t.active ? tickColor(t.pct) : 'rgba(148, 163, 184, 0.22)'"
          :opacity="t.active ? 0.95 : 0.45"
          :stroke-width="t.w"
        />
      </g>
    </svg>

    <div class="tach-center">
      <div class="tach-value tabular-nums" :style="{ fontSize: valueFontSize + 'px' }">{{ displayValue }}</div>
      <div class="tach-label" :style="{ fontSize: labelFontSize + 'px' }">calls/s</div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SpeedometerGauge',
  props: {
    value: {
      type: Number,
      default: 0
    },
    maxValue: {
      type: Number,
      default: 10
    },
    size: {
      type: Number,
      default: 100
    }
  },
  data() {
    return {
      animatedFill: 0,
      _raf: null
    }
  },
  computed: {
    centerX() {
      return this.size / 2
    },
    centerY() {
      return this.size / 2
    },
    arcStroke() {
      return Math.max(6, Math.round(this.size * 0.07))
    },
    radius() {
      return (this.size - this.arcStroke) / 2
    },
    startAngle() {
      // degrees (down-left). We render a 270° arc across the TOP,
      // leaving the missing 90° gap at the bottom.
      return 225
    },
    arcSpan() {
      return 270
    },
    rawPercentage() {
      if (this.maxValue === 0) return 0
      return Math.min((this.value / this.maxValue) * 100, 100)
    },
    fillPercentage() {
      // Keep it honest: never "hits max" unless rawPercentage is 100.
      // Add only a tiny minimum so low rates are still visible.
      if (this.rawPercentage <= 0) return 0
      return Math.min(Math.max(this.rawPercentage, 2), 100)
    },
    displayValue() {
      if (this.value >= 100) {
        return Math.round(this.value)
      } else if (this.value >= 10) {
        return this.value.toFixed(1)
      } else {
        return this.value.toFixed(2)
      }
    },
    valueFontSize() {
      // Keep value readable but always inside the ring (adaptive by text length)
      const s = String(this.displayValue)
      let scale = 0.19
      if (s.length >= 5) scale = 0.17
      if (s.length >= 6) scale = 0.16
      return Math.max(11, Math.round(this.size * scale))
    },
    labelFontSize() {
      return Math.max(7, Math.round(this.size * 0.07))
    },
    tickCount() {
      return 45
    },
    ticks() {
      const out = []
      for (let i = 0; i <= this.tickCount; i++) {
        const pct = i / this.tickCount
        const angle = (this.startAngle + this.arcSpan * pct) % 360

        // small -> big bar ramp
        // Keep ticks mostly OUTSIDE the center so the value/label fits nicely.
        const len = 4 + Math.round(10 * Math.pow(pct, 1.25))
        const rOuter = this.radius + Math.round(this.arcStroke * 0.1)
        const rInner = rOuter - len

        const p1 = this.polarToCartesian(this.centerX, this.centerY, rInner, angle)
        const p2 = this.polarToCartesian(this.centerX, this.centerY, rOuter, angle)

        const active = pct * 100 <= this.animatedFill + 0.25
        const isMajor = i % 5 === 0
        const w = 1.4 + 2.2 * Math.pow(pct, 1.55)
        out.push({ i, pct, x1: p1.x, y1: p1.y, x2: p2.x, y2: p2.y, active, isMajor, w })
      }
      return out
    },
    gaugeColor() {
      // kept for compatibility; per-tick colors are used in the template
      if (this.rawPercentage <= 30) return '#22d3ee'
      if (this.rawPercentage <= 60) return '#10b981'
      if (this.rawPercentage <= 85) return '#fbbf24'
      return '#ef4444'
    }
  },
  watch: {
    fillPercentage: {
      immediate: true,
      handler(next) {
        this.animateTo(next)
      }
    }
  },
  methods: {
    polarToCartesian(cx, cy, r, angleDeg) {
      const rad = ((angleDeg - 90) * Math.PI) / 180.0
      return {
        x: cx + r * Math.cos(rad),
        y: cy + r * Math.sin(rad)
      }
    },
    tickColor(pct) {
      // Color by how far around the arc the tick is (cool -> hot)
      if (pct <= 0.4) return '#22d3ee' // cyan
      if (pct <= 0.7) return '#10b981' // green
      if (pct <= 0.9) return '#fbbf24' // yellow
      return '#ef4444' // red
    },
    animateTo(target) {
      if (this._raf) cancelAnimationFrame(this._raf)
      const start = this.animatedFill || 0
      const end = Math.max(0, Math.min(100, target || 0))
      const diff = Math.abs(end - start)

      // Slower for larger jumps; never "snaps".
      const duration = Math.max(180, Math.min(900, 220 + diff * 10))
      const t0 = performance.now()

      const step = (t) => {
        const p = Math.min((t - t0) / duration, 1)
        // easeOutCubic
        const e = 1 - Math.pow(1 - p, 3)
        this.animatedFill = start + (end - start) * e
        if (p < 1) this._raf = requestAnimationFrame(step)
      }

      this._raf = requestAnimationFrame(step)
    }
  }
}
</script>

<style scoped>
.tach {
  position: relative;
  display: inline-block;
}

.tach-plate {
  fill: rgba(0, 0, 0, 0.28);
  stroke: rgba(255, 255, 255, 0.04);
  stroke-width: 1;
}

.tach-tick {
  stroke-width: 2;
  stroke-linecap: round;
  transition: stroke 0.25s ease, opacity 0.25s ease;
}

.tach-tick--major {
  stroke-width: 2.6;
}

.tach-center {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  pointer-events: none;
}

.tach-value {
  font-weight: 700;
  color: white;
  line-height: 1;
}

.tach-label {
  color: #94a3b8;
  margin-top: 0.125rem;
  letter-spacing: 0.02em;
  line-height: 1.1;
  opacity: 0.95;
}
</style>
