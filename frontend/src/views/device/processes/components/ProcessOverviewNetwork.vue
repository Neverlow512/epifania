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
      <button
        type="button"
        class="text-[9px] text-slate-600 hover:text-sky-400 transition-colors"
        :class="{ 'ml-auto': !hasConnections }"
        title="Learn about network connections"
        @click="showHelpModal = true"
      >
        <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </button>
    </div>

    <div v-if="network" class="bg-black/40 rounded-lg border border-slate-700/50 p-3">
      <div class="grid grid-cols-3 gap-3 text-xs">
        <div>
          <div class="text-slate-500">TCP</div>
          <div class="text-white font-mono">{{ network.tcp_count || 0 }}</div>
          <div v-if="establishedCount" class="text-[10px] text-emerald-400">{{ establishedCount }} established</div>
        </div>
        <div>
          <div class="text-slate-500">UDP</div>
          <div class="text-white font-mono">{{ network.udp_count || 0 }}</div>
        </div>
        <div>
          <div class="text-slate-500">Unix</div>
          <div class="text-white font-mono">{{ network.unix_count || 0 }}</div>
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
        <div class="flex items-center justify-between">
          <div class="tabs tabs-xs tabs-bordered">
            <button
              type="button"
              class="tab"
              :class="activeTab === 'tcp' ? 'tab-active text-primary' : 'text-slate-400'"
              @click="activeTab = 'tcp'"
            >
              TCP ({{ network?.tcp_count || 0 }})
            </button>
            <button
              type="button"
              class="tab"
              :class="activeTab === 'udp' ? 'tab-active text-primary' : 'text-slate-400'"
              @click="activeTab = 'udp'"
            >
              UDP ({{ network?.udp_count || 0 }})
            </button>
            <button
              type="button"
              class="tab"
              :class="activeTab === 'unix' ? 'tab-active text-primary' : 'text-slate-400'"
              @click="activeTab = 'unix'"
            >
              Unix ({{ network?.unix_count || 0 }})
            </button>
          </div>
          <button
            type="button"
            class="btn btn-ghost btn-xs text-slate-500 hover:text-sky-400"
            title="Learn about network connections"
            @click="showHelpModal = true"
          >
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </button>
        </div>

        <div v-if="activeTab === 'tcp'" class="overflow-x-auto max-h-[50vh]">
          <div v-if="network?.truncated" class="mb-2 text-xs text-amber-400">
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
                v-for="(conn, idx) in network?.tcp_connections || []"
                :key="'tcp-' + idx"
                class="border-neutral-800 hover:bg-neutral-800/50"
              >
                <td class="font-mono text-slate-300 text-[11px]">{{ conn.local_address }}</td>
                <td class="font-mono text-primary">{{ conn.local_port }}</td>
                <td class="font-mono text-slate-300 text-[11px]">{{ conn.remote_address }}</td>
                <td class="font-mono text-sky-400">{{ conn.remote_port }}</td>
                <td><span class="badge badge-xs" :class="getStateBadge(conn.state)">{{ conn.state }}</span></td>
              </tr>
              <tr v-if="!network?.tcp_connections?.length">
                <td colspan="5" class="text-center text-slate-500 py-4">No TCP connections</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-else-if="activeTab === 'udp'" class="overflow-x-auto max-h-[50vh]">
          <div v-if="network?.truncated" class="mb-2 text-xs text-amber-400">
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
                v-for="(conn, idx) in network?.udp_connections || []"
                :key="'udp-' + idx"
                class="border-neutral-800 hover:bg-neutral-800/50"
              >
                <td class="font-mono text-slate-300 text-[11px]">{{ conn.local_address }}</td>
                <td class="font-mono text-primary">{{ conn.local_port }}</td>
                <td class="font-mono text-slate-300 text-[11px]">{{ conn.remote_address || '*' }}</td>
                <td class="font-mono text-sky-400">{{ conn.remote_port || '*' }}</td>
              </tr>
              <tr v-if="!network?.udp_connections?.length">
                <td colspan="4" class="text-center text-slate-500 py-4">No UDP connections</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-else-if="activeTab === 'unix'" class="overflow-x-auto max-h-[50vh]">
          <div v-if="network?.truncated" class="mb-2 text-xs text-amber-400">
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
                v-for="(sock, idx) in network?.unix_sockets || []"
                :key="'unix-' + idx"
                class="border-neutral-800 hover:bg-neutral-800/50"
              >
                <td><span class="badge badge-xs badge-ghost">{{ sock.type }}</span></td>
                <td class="text-slate-300">{{ sock.state || '-' }}</td>
                <td class="font-mono text-slate-300 text-[11px] break-all">{{ sock.path || '(unnamed)' }}</td>
              </tr>
              <tr v-if="!network?.unix_sockets?.length">
                <td colspan="3" class="text-center text-slate-500 py-4">No Unix sockets</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </ProcessOverviewDetailModal>

    <Teleport to="body">
      <div
        v-if="showHelpModal"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
      >
        <div
          class="absolute inset-0 bg-black/70 backdrop-blur-sm"
          @click="showHelpModal = false"
        ></div>
        <div class="relative bg-neutral-900 border border-primary/30 rounded-xl shadow-2xl max-w-3xl w-full max-h-[85vh] overflow-hidden">
          <div class="flex items-center justify-between p-4 border-b border-neutral-800">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-lg bg-sky-500/20 flex items-center justify-center">
                <svg class="w-5 h-5 text-sky-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.141 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0" />
                </svg>
              </div>
              <div>
                <h3 class="text-lg font-semibold text-white">Understanding Network Connections</h3>
                <p class="text-xs text-slate-500">TCP, UDP, and Unix socket reference</p>
              </div>
            </div>
            <button
              type="button"
              class="btn btn-ghost btn-sm btn-circle"
              @click="showHelpModal = false"
            >
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div class="p-4 overflow-y-auto max-h-[calc(85vh-80px)] space-y-6 text-sm">
            <section class="space-y-3">
              <h4 class="text-base font-medium text-white flex items-center gap-2">
                <span class="w-6 h-6 rounded bg-sky-500/20 flex items-center justify-center text-xs text-sky-400">1</span>
                Reading Addresses
              </h4>
              <div class="bg-black/40 rounded-lg p-3 border border-neutral-800 space-y-3">
                <div>
                  <div class="text-slate-300 font-medium text-xs mb-1">Local Address / Port</div>
                  <p class="text-slate-500 text-xs">The IP address and port on this device. <code class="text-sky-400 bg-sky-500/10 px-1 rounded">0.0.0.0</code> means listening on all interfaces.</p>
                </div>
                <div>
                  <div class="text-slate-300 font-medium text-xs mb-1">Remote Address / Port</div>
                  <p class="text-slate-500 text-xs">The IP and port of the connected peer. <code class="text-sky-400 bg-sky-500/10 px-1 rounded">0.0.0.0:0</code> means no remote connection (listening sockets).</p>
                </div>
                <div>
                  <div class="text-slate-300 font-medium text-xs mb-1">IPv4-Mapped IPv6</div>
                  <p class="text-slate-500 text-xs">Addresses like <code class="text-sky-400 bg-sky-500/10 px-1 rounded">::ffff:10.0.3.15</code> are IPv4 addresses accessed via IPv6 sockets. They display as regular IPv4.</p>
                </div>
              </div>
            </section>

            <section class="space-y-3">
              <h4 class="text-base font-medium text-white flex items-center gap-2">
                <span class="w-6 h-6 rounded bg-emerald-500/20 flex items-center justify-center text-xs text-emerald-400">2</span>
                TCP Connection States
              </h4>
              <div class="grid grid-cols-2 gap-2">
                <div class="bg-black/40 rounded p-2 border border-neutral-800">
                  <span class="badge badge-xs badge-success">ESTABLISHED</span>
                  <p class="text-slate-500 text-xs mt-1">Active connection, data can flow both ways</p>
                </div>
                <div class="bg-black/40 rounded p-2 border border-neutral-800">
                  <span class="badge badge-xs badge-info">LISTEN</span>
                  <p class="text-slate-500 text-xs mt-1">Server waiting for incoming connections</p>
                </div>
                <div class="bg-black/40 rounded p-2 border border-neutral-800">
                  <span class="badge badge-xs badge-warning">TIME_WAIT</span>
                  <p class="text-slate-500 text-xs mt-1">Connection closed, waiting for stray packets (normal)</p>
                </div>
                <div class="bg-black/40 rounded p-2 border border-neutral-800">
                  <span class="badge badge-xs badge-warning">CLOSE_WAIT</span>
                  <p class="text-slate-500 text-xs mt-1">Remote closed, local app hasn't closed yet</p>
                </div>
                <div class="bg-black/40 rounded p-2 border border-neutral-800">
                  <span class="badge badge-xs badge-accent">SYN_SENT</span>
                  <p class="text-slate-500 text-xs mt-1">Initiating connection (handshake step 1)</p>
                </div>
                <div class="bg-black/40 rounded p-2 border border-neutral-800">
                  <span class="badge badge-xs badge-accent">SYN_RECV</span>
                  <p class="text-slate-500 text-xs mt-1">Received connection request (handshake step 2)</p>
                </div>
                <div class="bg-black/40 rounded p-2 border border-neutral-800">
                  <span class="badge badge-xs badge-secondary">FIN_WAIT1</span>
                  <p class="text-slate-500 text-xs mt-1">Local initiated close, waiting for ACK</p>
                </div>
                <div class="bg-black/40 rounded p-2 border border-neutral-800">
                  <span class="badge badge-xs badge-secondary">FIN_WAIT2</span>
                  <p class="text-slate-500 text-xs mt-1">Local close ACKed, waiting for remote close</p>
                </div>
                <div class="bg-black/40 rounded p-2 border border-neutral-800">
                  <span class="badge badge-xs badge-error">CLOSING</span>
                  <p class="text-slate-500 text-xs mt-1">Both sides closing simultaneously</p>
                </div>
                <div class="bg-black/40 rounded p-2 border border-neutral-800">
                  <span class="badge badge-xs badge-error">LAST_ACK</span>
                  <p class="text-slate-500 text-xs mt-1">Waiting for final ACK before closing</p>
                </div>
              </div>
              <div class="bg-black/40 rounded-lg p-3 border border-neutral-800">
                <p class="text-slate-400 text-xs">
                  <span class="text-amber-400 font-medium">Many CLOSE_WAIT?</span> The app isn't properly closing connections after the remote side disconnects. This can indicate a bug or resource leak.
                </p>
              </div>
            </section>

            <section class="space-y-3">
              <h4 class="text-base font-medium text-white flex items-center gap-2">
                <span class="w-6 h-6 rounded bg-violet-500/20 flex items-center justify-center text-xs text-violet-400">3</span>
                UDP Connections
              </h4>
              <div class="bg-black/40 rounded-lg p-3 border border-neutral-800 space-y-2">
                <p class="text-slate-400 text-xs">UDP is connectionless - there's no handshake or state machine like TCP.</p>
                <p class="text-slate-500 text-xs">UDP sockets show the local address/port they're bound to. Remote address is only shown if the socket is "connected" (restricted to one peer).</p>
                <p class="text-slate-500 text-xs">Common uses: DNS (port 53), streaming, gaming, VoIP.</p>
              </div>
            </section>

            <section class="space-y-3">
              <h4 class="text-base font-medium text-white flex items-center gap-2">
                <span class="w-6 h-6 rounded bg-amber-500/20 flex items-center justify-center text-xs text-amber-400">4</span>
                Unix Sockets
              </h4>
              <div class="bg-black/40 rounded-lg p-3 border border-neutral-800 space-y-3">
                <div>
                  <div class="text-slate-300 font-medium text-xs mb-1">What are Unix sockets?</div>
                  <p class="text-slate-500 text-xs">Inter-process communication (IPC) on the same device. Faster than TCP/IP because they bypass the network stack.</p>
                </div>
                <div>
                  <div class="text-slate-300 font-medium text-xs mb-1">Socket Types</div>
                  <div class="grid grid-cols-3 gap-2 mt-1">
                    <div class="text-center">
                      <span class="badge badge-xs badge-ghost">STREAM</span>
                      <p class="text-slate-600 text-[10px] mt-0.5">Like TCP - ordered, reliable</p>
                    </div>
                    <div class="text-center">
                      <span class="badge badge-xs badge-ghost">DGRAM</span>
                      <p class="text-slate-600 text-[10px] mt-0.5">Like UDP - messages</p>
                    </div>
                    <div class="text-center">
                      <span class="badge badge-xs badge-ghost">SEQPACKET</span>
                      <p class="text-slate-600 text-[10px] mt-0.5">Ordered messages</p>
                    </div>
                  </div>
                </div>
                <div>
                  <div class="text-slate-300 font-medium text-xs mb-1">Path Column</div>
                  <p class="text-slate-500 text-xs">Shows the filesystem path or abstract name. <code class="text-amber-400 bg-amber-500/10 px-1 rounded">@</code> prefix means abstract namespace (not a real file). <code class="text-slate-500">(unnamed)</code> means anonymous socket pair.</p>
                </div>
                <div>
                  <div class="text-slate-300 font-medium text-xs mb-1">States</div>
                  <div class="flex flex-wrap gap-2 mt-1">
                    <span class="text-xs"><span class="text-emerald-400">LISTENING</span> - waiting for connections</span>
                    <span class="text-xs"><span class="text-sky-400">CONNECTED</span> - active connection</span>
                    <span class="text-xs"><span class="text-amber-400">CONNECTING</span> - handshake in progress</span>
                  </div>
                </div>
              </div>
            </section>

            <section class="space-y-3">
              <h4 class="text-base font-medium text-white flex items-center gap-2">
                <span class="w-6 h-6 rounded bg-rose-500/20 flex items-center justify-center text-xs text-rose-400">5</span>
                Common Patterns
              </h4>
              <div class="bg-black/40 rounded-lg p-3 border border-neutral-800 space-y-2 text-xs">
                <div class="flex items-start gap-2">
                  <span class="text-slate-500 w-32 flex-shrink-0">Port 443 remote:</span>
                  <span class="text-slate-400">HTTPS connection to a server</span>
                </div>
                <div class="flex items-start gap-2">
                  <span class="text-slate-500 w-32 flex-shrink-0">Port 53 remote:</span>
                  <span class="text-slate-400">DNS query</span>
                </div>
                <div class="flex items-start gap-2">
                  <span class="text-slate-500 w-32 flex-shrink-0">0.0.0.0:* local:</span>
                  <span class="text-slate-400">Listening on all interfaces</span>
                </div>
                <div class="flex items-start gap-2">
                  <span class="text-slate-500 w-32 flex-shrink-0">127.0.0.1 local:</span>
                  <span class="text-slate-400">Localhost only (not accessible from network)</span>
                </div>
              </div>
            </section>
          </div>
        </div>
      </div>
    </Teleport>
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
      showHelpModal: false,
      activeTab: 'tcp'
    }
  },
  computed: {
    hasConnections() {
      if (!this.network) return false
      return (this.network.tcp_count || 0) + 
             (this.network.udp_count || 0) + 
             (this.network.unix_count || 0) > 0
    },
    establishedCount() {
      if (!this.network?.tcp_connections) return 0
      return this.network.tcp_connections.filter(c => c.state === 'ESTABLISHED').length
    },
    connectionSummary() {
      const tcp = this.network?.tcp_count || 0
      const udp = this.network?.udp_count || 0
      const unix = this.network?.unix_count || 0
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
