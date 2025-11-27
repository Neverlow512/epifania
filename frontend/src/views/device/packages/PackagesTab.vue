<template>
  <div class="flex items-center justify-center py-16">
    <div class="text-center max-w-md">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto mb-4 text-primary opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
      </svg>
      <h3 class="text-xl font-semibold text-white mb-2">Package Management</h3>
      <p class="text-slate-400">
        Comprehensive package catalog and management will be available here soon.
        Browse installed packages, manage lifecycle, and analyze package details.
      </p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PackagesTab',
  props: {
    device: {
      type: Object,
      required: true
    }
  }
}
</script>

