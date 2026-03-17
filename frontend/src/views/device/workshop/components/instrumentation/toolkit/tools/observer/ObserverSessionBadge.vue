<template>
  <span 
    v-if="observationHistory && observationHistory.length > 0"
    class="badge badge-xs bg-indigo-600 text-white"
    :title="tooltipText"
  >
    Observed in {{ latestSession.session_name }}
  </span>
</template>

<script>
export default {
  name: 'ObserverSessionBadge',
  props: {
    observationHistory: {
      type: Array,
      default: () => []
    }
  },
  computed: {
    latestSession() {
      if (!this.observationHistory || this.observationHistory.length === 0) {
        return null
      }
      return this.observationHistory[this.observationHistory.length - 1]
    },
    tooltipText() {
      if (!this.latestSession) return ''
      
      const timestamp = new Date(this.latestSession.timestamp).toLocaleString()
      return `Session: ${this.latestSession.session_name}\nTime: ${timestamp}\nTotal observations: ${this.observationHistory.length}`
    }
  }
}
</script>
