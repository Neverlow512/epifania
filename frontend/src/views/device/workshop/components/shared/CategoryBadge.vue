<template>
  <span 
    class="badge badge-sm"
    :class="badgeClass"
  >
    {{ category }}
  </span>
</template>

<script>
export default {
  name: 'CategoryBadge',
  props: {
    category: {
      type: String,
      required: true
    }
  },
  computed: {
    badgeClass() {
      const categoryMap = {
        'Network': 'badge-info',
        'Crypto': 'badge-secondary',
        'Storage': 'badge-success',
        'Security': 'badge-error',
        'UI': 'badge-accent',
        'Reflection': 'badge-warning',
        'Native': 'badge-ghost',
        'Obfuscated': 'bg-yellow-600 text-white',
        'Unknown': 'badge-neutral'
      }
      return categoryMap[this.category] || 'badge-neutral'
    }
  }
}
</script>

