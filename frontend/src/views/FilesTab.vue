<template>
  <div class="flex items-center justify-center py-16">
    <div class="text-center max-w-md">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto mb-4 text-primary opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
      </svg>
      <h3 class="text-xl font-semibold text-white mb-2">File Browser</h3>
      <p class="text-slate-400">
        Device file system browser will be available here soon.
        Navigate directories, download files, and access package data.
      </p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FilesTab',
  props: {
    device: {
      type: Object,
      required: true
    }
  }
}
</script>

