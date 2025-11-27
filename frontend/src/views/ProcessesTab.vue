<template>
  <div class="flex items-center justify-center py-16">
    <div class="text-center max-w-md">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto mb-4 text-primary opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
      </svg>
      <h3 class="text-xl font-semibold text-white mb-2">Processes Monitoring</h3>
      <p class="text-slate-400">
        Real-time process monitoring and analysis will be available here soon.
        Track running processes, resource usage, and identify analysis targets.
      </p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ProcessesTab',
  props: {
    device: {
      type: Object,
      required: true
    }
  }
}
</script>

