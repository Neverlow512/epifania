<template>
  <div v-if="show && process" class="modal modal-open">
    <div class="modal-box bg-neutral-900 border border-primary/30 max-w-4xl">
      <h3 class="font-bold text-lg text-white mb-4">
        Process Details - {{ process.name }} (PID: {{ process.pid }})
      </h3>
      
      <div v-if="loading" class="flex justify-center py-8">
        <span class="loading loading-spinner loading-lg text-primary"></span>
      </div>
      
      <div v-else-if="details" class="space-y-4">
        <div>
          <div class="text-sm text-slate-400 mb-1">Command Line</div>
          <div class="bg-black/30 p-3 rounded border border-primary/20">
            <code class="text-sm text-white break-all">{{ details.cmdline || 'N/A' }}</code>
          </div>
        </div>
        
        <div>
          <div class="text-sm text-slate-400 mb-1">Status Information</div>
          <div class="bg-black/30 p-3 rounded border border-primary/20 max-h-60 overflow-y-auto">
            <div v-for="(value, key) in details.status" :key="key" class="text-xs mb-1">
              <span class="text-slate-500">{{ key }}:</span>
              <span class="text-white ml-2">{{ value }}</span>
            </div>
          </div>
        </div>
        
        <div>
          <div class="text-sm text-slate-400 mb-1">Threads ({{ details.threads?.length || 0 }})</div>
          <div class="bg-black/30 p-3 rounded border border-primary/20">
            <div class="text-xs text-slate-300">
              {{ details.threads?.map(t => t.tid).join(', ') || 'None' }}
            </div>
          </div>
        </div>
        
        <div>
          <div class="text-sm text-slate-400 mb-1">Open Files ({{ details.open_files?.length || 0 }})</div>
          <div class="bg-black/30 p-3 rounded border border-primary/20 max-h-40 overflow-y-auto">
            <div v-for="file in details.open_files" :key="file.fd" class="text-xs mb-1">
              <span class="text-primary">{{ file.fd }}:</span>
              <span class="text-white ml-2">{{ file.path }}</span>
            </div>
          </div>
        </div>

        <div v-if="memoryDetails" class="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div class="text-sm text-slate-400 col-span-2 md:col-span-4">Memory Breakdown</div>
          <div class="bg-black/30 p-3 rounded border border-primary/20 text-xs space-y-1">
            <div class="text-slate-400">RSS</div>
            <div class="text-white">{{ memoryDetails.rss_mb }} MB</div>
          </div>
          <div class="bg-black/30 p-3 rounded border border-primary/20 text-xs space-y-1">
            <div class="text-slate-400">VSZ</div>
            <div class="text-white">{{ memoryDetails.vsz_mb }} MB</div>
          </div>
          <div class="bg-black/30 p-3 rounded border border-primary/20 text-xs space-y-1">
            <div class="text-slate-400">Peak</div>
            <div class="text-white">{{ memoryDetails.peak_mb }} MB</div>
          </div>
          <div class="bg-black/30 p-3 rounded border border-primary/20 text-xs space-y-1">
            <div class="text-slate-400">High-water</div>
            <div class="text-white">{{ memoryDetails.hwm_mb }} MB</div>
          </div>
        </div>

        <div v-if="networkDetails && networkDetails.connections && networkDetails.connections.length" class="space-y-2">
          <div class="text-sm text-slate-400">Network Connections ({{ networkDetails.connections.length }})</div>
          <div class="bg-black/30 p-3 rounded border border-primary/20 max-h-48 overflow-y-auto">
            <table class="table table-xs">
              <thead>
                <tr class="text-slate-400">
                  <th>Local</th>
                  <th>Remote</th>
                  <th class="text-right">State</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="conn in networkDetails.connections"
                  :key="conn.local + '-' + conn.remote + '-' + conn.state"
                  class="border-neutral-800"
                >
                  <td class="text-slate-200 truncate">{{ conn.local }}</td>
                  <td class="text-slate-200 truncate">{{ conn.remote }}</td>
                  <td class="text-right text-slate-300">{{ conn.state }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
      
      <div class="modal-action">
        <button class="btn btn-ghost" @click="$emit('close')">Close</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ProcessDetailsModal',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    process: {
      type: Object,
      default: null
    },
    details: {
      type: Object,
      default: null
    },
    loading: {
      type: Boolean,
      default: false
    },
    memoryDetails: {
      type: Object,
      default: null
    },
    networkDetails: {
      type: Object,
      default: null
    }
  },
  emits: ['close']
}
</script>

