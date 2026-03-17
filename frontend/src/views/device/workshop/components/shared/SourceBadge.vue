<template>
  <span 
    class="badge badge-xs"
    :class="badgeClass"
  >
    {{ sourceLabel }}
  </span>
</template>

<script>
export default {
  name: 'SourceBadge',
  props: {
    source: {
      type: String,
      required: true
    }
  },
  computed: {
    sourceLabel() {
      const labelMap = {
        'app': 'App',
        'bundled': 'Bundled',
        'system': 'System'
      }
      return labelMap[this.source] || this.source
    },
    badgeClass() {
      const classMap = {
        'app': 'badge-success',
        'bundled': 'badge-info',
        'system': 'badge-ghost'
      }
      return classMap[this.source] || 'badge-ghost'
    }
  }
}
</script>

