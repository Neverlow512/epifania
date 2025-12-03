<template>
  <div class="space-y-2">
    <div class="flex items-center gap-2">
      <div class="w-7 h-7 rounded bg-sky-500/20 flex items-center justify-center flex-shrink-0">
        <svg class="w-4 h-4 text-sky-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.141 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0" />
        </svg>
      </div>
      <span class="text-xs text-slate-400 font-medium">Network</span>
      <button
        v-if="hasConnections"
        type="button"
        class="ml-auto text-[9px] text-slate-500 hover:text-sky-400 transition-colors border border-slate-700 hover:border-sky-500/50 rounded px-1.5 py-0.5"
        @click="showModal = true"
      >
        View all
      </button>
    </div>

    <div v-if="network" class="bg-black/40 rounded-lg border border-slate-700/50 p-3">
      <div class="grid grid-cols-3 gap-3 text-xs">
        <div>
          <div class="text-slate-500">TCP</div>
          <div class="text-white font-mono">{{ network.tcp?.count || 0 }}</div>
          <div v-if="establishedCount" class="text-[10px] text-emerald-400">{{ establishedCount }} established</div>
        </div>
        <div>
          <div class="text-slate-500">UDP</div>
          <div class="text-white font-mono">{{ network.udp?.count || 0 }}</div>
        </div>
        <div>
          <div class="text-slate-500">Unix</div>
          <div class="text-white font-mono">{{ network.unix?.count || 0 }}</div>
        </div>
      </div>
    </div>

    <div v-else class="bg-black/40 rounded-lg border border-slate-700/50 p-3">
      <div class="flex items-center gap-2 text-slate-500 text-xs">
        <svg class="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 5.636a9 9 0 010 12.728m0 0l-2.829-2.829m2.829 2.829L21 21M15.536 8.464a5 5 0 010 7.072m0 0l-2.829-2.829m-4.243 2.829a4.978 4.978 0 01-1.414-2.83m-1.414 5.658a9 9 0 01-2.167-9.238m7.824 2.167a1 1 0 111.414 1.414m-1.414-1.414L3 3m8.293 8.293l1.414 1.414" />
        </svg>
        <div>
          <span class="block">No network connections</span>
          <span class="text-[10px] text-slate-600">Process has no open sockets</span>
        </div>
      </div>
    </div>

    <ProcessOverviewDetailModal
      :show="showModal"
      title="Network Connections"
      :subtitle="connectionSummary"
      icon-bg-class="bg-sky-500/20"
      icon-class="text-sky-400"
      max-width="4xl"
      @close="showModal = false"
    >
      <template #icon>
        <svg class="w-5 h-5 text-sky-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.141 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0" />
        </svg>
      </template>

      <div class="space-y-4">
        <div class="tabs tabs-xs tabs-bordered">
          <button
            type="button"
            class="tab"
            :class="activeTab === 'tcp' ? 'tab-active text-primary' : 'text-slate-400'"
            @click="activeTab = 'tcp'"
          >
            TCP ({{ network?.tcp?.count || 0 }})
          </button>
          <button
            type="button"
            class="tab"
            :class="activeTab === 'udp' ? 'tab-active text-primary' : 'text-slate-400'"
            @click="activeTab = 'udp'"
          >
            UDP ({{ network?.udp?.count || 0 }})
          </button>
          <button
            type="button"
            class="tab"
            :class="activeTab === 'unix' ? 'tab-active text-primary' : 'text-slate-400'"
            @click="activeTab = 'unix'"
          >
            Unix ({{ network?.unix?.count || 0 }})
          </button>
        </div>

        <div v-if="activeTab === 'tcp'" class="overflow-x-auto max-h-[50vh]">
          <div v-if="network?.tcp?.truncated" class="mb-2 text-xs text-amber-400">
            Showing first 50 connections (truncated)
          </div>
          <table class="table table-xs w-full">
            <thead class="sticky top-0 bg-neutral-900 z-10">
              <tr class="text-slate-400 border-neutral-800">
                <th>Local Address</th>
                <th>Local Port</th>
                <th>Remote Address</th>
                <th>Remote Port</th>
                <th>State</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(conn, idx) in network?.tcp?.connections || []"
                :key="'tcp-' + idx"
                class="border-neutral-800 hover:bg-neutral-800/50"
              >
                <td class="font-mono text-slate-300 text-[11px]">{{ conn.local_addr }}</td>
                <td class="font-mono text-primary">{{ conn.local_port }}</td>
                <td class="font-mono text-slate-300 text-[11px]">{{ conn.remote_addr }}</td>
                <td class="font-mono text-sky-400">{{ conn.remote_port }}</td>
                <td><span class="badge badge-xs" :class="getStateBadge(conn.state)">{{ conn.state }}</span></td>
              </tr>
              <tr v-if="!network?.tcp?.connections?.length">
                <td colspan="5" class="text-center text-slate-500 py-4">No TCP connections</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-else-if="activeTab === 'udp'" class="overflow-x-auto max-h-[50vh]">
          <div v-if="network?.udp?.truncated" class="mb-2 text-xs text-amber-400">
            Showing first 50 connections (truncated)
          </div>
          <table class="table table-xs w-full">
            <thead class="sticky top-0 bg-neutral-900 z-10">
              <tr class="text-slate-400 border-neutral-800">
                <th>Local Address</th>
                <th>Local Port</th>
                <th>Remote Address</th>
                <th>Remote Port</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(conn, idx) in network?.udp?.connections || []"
                :key="'udp-' + idx"
                class="border-neutral-800 hover:bg-neutral-800/50"
              >
                <td class="font-mono text-slate-300 text-[11px]">{{ conn.local_addr }}</td>
                <td class="font-mono text-primary">{{ conn.local_port }}</td>
                <td class="font-mono text-slate-300 text-[11px]">{{ conn.remote_addr || '*' }}</td>
                <td class="font-mono text-sky-400">{{ conn.remote_port || '*' }}</td>
              </tr>
              <tr v-if="!network?.udp?.connections?.length">
                <td colspan="4" class="text-center text-slate-500 py-4">No UDP connections</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-else-if="activeTab === 'unix'" class="overflow-x-auto max-h-[50vh]">
          <div v-if="network?.unix?.truncated" class="mb-2 text-xs text-amber-400">
            Showing first 50 sockets (truncated)
          </div>
          <table class="table table-xs w-full">
            <thead class="sticky top-0 bg-neutral-900 z-10">
              <tr class="text-slate-400 border-neutral-800">
                <th>Type</th>
                <th>State</th>
                <th>Path</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(sock, idx) in network?.unix?.sockets || []"
                :key="'unix-' + idx"
                class="border-neutral-800 hover:bg-neutral-800/50"
              >
                <td><span class="badge badge-xs badge-ghost">{{ sock.type }}</span></td>
                <td class="text-slate-300">{{ sock.state || '-' }}</td>
                <td class="font-mono text-slate-300 text-[11px] break-all">{{ sock.path || '(unnamed)' }}</td>
              </tr>
              <tr v-if="!network?.unix?.sockets?.length">
                <td colspan="3" class="text-center text-slate-500 py-4">No Unix sockets</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </ProcessOverviewDetailModal>
  </div>
</template>

<script>
import ProcessOverviewDetailModal from './ProcessOverviewDetailModal.vue'

export default {
  name: 'ProcessOverviewNetwork',
  components: {
    ProcessOverviewDetailModal
  },
  props: {
    network: {
      type: Object,
      default: null
    }
  },
  data() {
    return {
      showModal: false,
      activeTab: 'tcp'
    }
  },
  computed: {
    hasConnections() {
      if (!this.network) return false
      return (this.network.tcp?.count || 0) + 
             (this.network.udp?.count || 0) + 
             (this.network.unix?.count || 0) > 0
    },
    establishedCount() {
      if (!this.network?.tcp?.connections) return 0
      return this.network.tcp.connections.filter(c => c.state === 'ESTABLISHED').length
    },
    connectionSummary() {
      const tcp = this.network?.tcp?.count || 0
      const udp = this.network?.udp?.count || 0
      const unix = this.network?.unix?.count || 0
      return `${tcp} TCP, ${udp} UDP, ${unix} Unix`
    }
  },
  methods: {
    getStateBadge(state) {
      const map = {
        'ESTABLISHED': 'badge-success',
        'LISTEN': 'badge-info',
        'TIME_WAIT': 'badge-warning',
        'CLOSE_WAIT': 'badge-warning',
        'SYN_SENT': 'badge-accent',
        'SYN_RECV': 'badge-accent',
        'FIN_WAIT1': 'badge-secondary',
        'FIN_WAIT2': 'badge-secondary',
        'CLOSING': 'badge-error',
        'LAST_ACK': 'badge-error'
      }
      return map[state] || 'badge-ghost'
    }
  }
}
</script>

