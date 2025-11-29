<template>
  <div class="card bg-neutral-900/60 backdrop-blur-sm shadow-xl border border-primary/20">
    <div class="card-body p-4 space-y-4">
      <div class="flex items-center justify-between">
        <div>
          <h3 class="text-sm font-semibold text-white">Runtime Overview</h3>
          <p class="text-xs text-slate-500">
            Last updated: <span class="text-slate-300">{{ lastUpdate }}</span>
          </p>
        </div>
        <div class="flex items-center gap-2">
          <div class="flex items-center gap-2 text-xs">
            <label class="cursor-pointer flex items-center gap-1">
              <input
                type="checkbox"
                class="toggle toggle-xs toggle-primary"
                :checked="autoRefresh"
                @change="$emit('toggle-auto-refresh')"
              />
              <span :class="autoRefresh ? 'text-green-400' : 'text-slate-500'">
                {{ autoRefresh ? 'Auto' : 'Manual' }}
              </span>
            </label>
            <span class="text-slate-500">
              {{ refreshInterval / 1000 }}s
            </span>
          </div>
          <button
            type="button"
            class="btn btn-ghost btn-xs text-xs px-2 h-6 min-h-0"
            :disabled="loading"
            @click="$emit('refresh')"
          >
            Refresh
          </button>
        </div>
      </div>

      <div class="grid grid-cols-2 md:grid-cols-3 gap-3 text-xs">
        <div class="bg-black/30 rounded border border-primary/20 p-3 space-y-1">
          <div class="flex items-center justify-between">
            <span class="text-slate-400">Processes</span>
            <span class="text-[10px] text-slate-500">total/user/system</span>
          </div>
          <div class="text-white text-lg leading-tight">
            {{ stats.total || 0 }}
          </div>
          <div class="text-slate-500">
            User: {{ stats.user || 0 }} • System: {{ stats.system || 0 }}
          </div>
        </div>

        <div class="bg-black/30 rounded border border-primary/20 p-3 space-y-1">
          <div class="flex items-center justify-between">
            <span class="text-slate-400">CPU</span>
            <span class="text-[10px] text-slate-500">overall</span>
          </div>
          <div class="text-white text-lg leading-tight">
            {{ (cpu.overall_percent || 0).toFixed(1) }}%
          </div>
          <div class="text-slate-500 truncate">
            <span v-if="cpu.top_consumers && cpu.top_consumers.length">
              Top: {{ cpu.top_consumers[0].name }} ({{ cpu.top_consumers[0].cpu_percent }}%)
            </span>
            <span v-else>
              No active consumers
            </span>
          </div>
        </div>

        <div class="bg-black/30 rounded border border-primary/20 p-3 space-y-1">
          <div class="flex items-center justify-between">
            <span class="text-slate-400">RAM</span>
            <span class="text-[10px] text-slate-500">used / total</span>
          </div>
          <div class="text-white text-lg leading-tight">
            {{ formatMemory(memory.used_mb) }} / {{ formatMemory(memory.total_mb) }}
          </div>
          <div class="w-full h-1.5 bg-neutral-800 rounded overflow-hidden">
            <div
              class="h-full bg-emerald-500"
              :style="{ width: memoryFillPercent + '%' }"
            ></div>
          </div>
          <div class="text-slate-500">
            Free: {{ formatMemory(memory.free_mb) }} • Cache: {{ formatMemory(memory.cached_mb) }}
          </div>
        </div>

        <div class="bg-black/30 rounded border border-primary/20 p-3 space-y-1">
          <div class="flex items-center justify-between">
            <span class="text-slate-400">Storage (/data)</span>
            <span class="text-[10px] text-slate-500">used / total</span>
          </div>
          <div class="text-white text-lg leading-tight">
            {{ formatGb(storage.used_gb) }} / {{ formatGb(storage.total_gb) }}
          </div>
          <div class="w-full h-1.5 bg-neutral-800 rounded overflow-hidden">
            <div
              class="h-full bg-indigo-500"
              :style="{ width: (storage.percent_used || 0) + '%' }"
            ></div>
          </div>
          <div class="text-slate-500">
            Free: {{ formatGb(storage.free_gb) }} • {{ (storage.percent_used || 0).toFixed(1) }}%
          </div>
        </div>

        <div class="bg-black/30 rounded border border-primary/20 p-3 space-y-1">
          <div class="flex items-center justify-between">
            <span class="text-slate-400">Network</span>
            <span class="text-[10px] text-slate-500">throughput</span>
          </div>
          <div class="text-white text-lg leading-tight">
            ↑ {{ formatBytesPerSec(network.throughput?.bytes_sent_per_sec) }}
            · ↓ {{ formatBytesPerSec(network.throughput?.bytes_recv_per_sec) }}
          </div>
          <div class="text-slate-500 truncate">
            Recent endpoints: {{ (network.recent_endpoints || []).length }}
          </div>
        </div>

        <div class="bg-black/30 rounded border border-primary/20 p-3 space-y-1">
          <div class="flex items-center justify-between">
            <span class="text-slate-400">Churn ({{ churn.window_seconds || 60 }}s)</span>
            <span class="text-[10px] text-slate-500">spawned / killed</span>
          </div>
          <div class="text-white text-lg leading-tight">
            {{ churn.spawned_count || 0 }} / {{ churn.killed_count || 0 }}
          </div>
          <div class="text-slate-500">
            Net:
            <span
              :class="{
                'text-emerald-400': churn.net_change > 0,
                'text-red-400': churn.net_change < 0,
                'text-slate-400': !churn.net_change
              }"
            >
              {{ churn.net_change || 0 }}
            </span>
          </div>
        </div>
      </div>

      <div class="border-t border-primary/20 pt-3 space-y-3">
        <div class="flex items-center justify-between text-xs">
          <div class="tabs tabs-xs tabs-bordered">
            <button
              v-for="tab in tabs"
              :key="tab"
              type="button"
              class="tab"
              :class="tab === activeTab ? 'tab-active text-primary' : 'text-slate-400'"
              @click="activeTab = tab"
            >
              {{ tab }}
            </button>
          </div>
          <div class="join join-xs">
            <button
              v-for="option in intervalOptions"
              :key="option"
              type="button"
              class="btn btn-xs join-item px-2"
              :class="option === refreshInterval ? 'btn-primary' : 'btn-ghost text-slate-400'"
              @click="$emit('update-refresh-interval', option)"
            >
              {{ option / 1000 }}s
            </button>
          </div>
        </div>

        <div v-if="activeTab === 'Overview'" class="space-y-3">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div class="space-y-2">
              <div class="flex items-center justify-between text-xs text-slate-400">
                <span>Processes over time</span>
                <span v-if="processHistory && processHistory.length" class="text-slate-500">
                  {{ processHistory[processHistory.length - 1].total }} now
                </span>
              </div>
              <div class="h-10 bg-black/40 rounded overflow-hidden">
                <svg
                  v-if="processHistory && processHistory.length > 1"
                  class="w-full h-full"
                  viewBox="0 0 100 40"
                  preserveAspectRatio="none"
                >
                  <polyline
                    :points="buildLinePoints(processHistory.map(p => p.total))"
                    fill="none"
                    stroke="#7100d0"
                    stroke-width="1.5"
                  />
                </svg>
              </div>
            </div>

            <div class="space-y-2">
              <div class="flex items-center justify-between text-xs text-slate-400">
                <span>Memory over time</span>
                <span v-if="memoryHistory && memoryHistory.length" class="text-slate-500">
                  {{ formatMemory(memoryHistory[memoryHistory.length - 1].memoryMb) }} now
                </span>
              </div>
              <div class="h-10 bg-black/40 rounded overflow-hidden">
                <svg
                  v-if="memoryHistory && memoryHistory.length > 1"
                  class="w-full h-full"
                  viewBox="0 0 100 40"
                  preserveAspectRatio="none"
                >
                  <polyline
                    :points="buildLinePoints(memoryHistory.map(p => p.memoryMb))"
                    fill="none"
                    stroke="#10b981"
                    stroke-width="1.5"
                  />
                </svg>
              </div>
            </div>
          </div>

          <div v-if="storagePartitions && storagePartitions.length" class="space-y-1 text-xs">
            <div class="flex items-center justify-between">
              <span class="text-slate-400">Storage partitions</span>
              <span class="text-slate-500">
                {{ storagePartitions.length }} mounts
              </span>
            </div>
            <div class="max-h-32 overflow-y-auto border border-neutral-800 rounded">
              <table class="table table-xs">
                <thead>
                  <tr class="text-slate-400">
                    <th>Mount</th>
                    <th class="text-right">Used</th>
                    <th class="text-right">Total</th>
                    <th class="text-right">% Used</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="part in storagePartitions"
                    :key="part.partition"
                    class="border-neutral-800"
                  >
                    <td class="text-slate-200">{{ part.partition }}</td>
                    <td class="text-right text-slate-300">
                      {{ formatGb(part.used_gb) }}
                    </td>
                    <td class="text-right text-slate-300">
                      {{ formatGb(part.total_gb) }}
                    </td>
                    <td class="text-right text-slate-300">
                      {{ (part.percent_used || 0).toFixed(1) }}%
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div v-else-if="activeTab === 'CPU'" class="space-y-2 text-xs">
          <div class="flex items-center justify-between text-slate-400">
            <span>Top CPU consumers</span>
            <span class="text-slate-500">
              Overall: {{ (cpu.overall_percent || 0).toFixed(1) }}%
            </span>
          </div>
          <div class="max-h-40 overflow-y-auto border border-neutral-800 rounded">
            <table class="table table-xs">
              <thead>
                <tr class="text-slate-400">
                  <th>PID</th>
                  <th>Name</th>
                  <th class="text-right">CPU %</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="item in cpu.top_consumers || []"
                  :key="item.pid"
                  class="border-neutral-800"
                >
                  <td class="font-mono text-primary">{{ item.pid }}</td>
                  <td class="text-slate-200 truncate">{{ item.name }}</td>
                  <td class="text-right text-slate-300">
                    {{ item.cpu_percent.toFixed(1) }}
                  </td>
                </tr>
                <tr v-if="!cpu.top_consumers || !cpu.top_consumers.length">
                  <td colspan="3" class="text-center text-slate-500 py-3">
                    No CPU consumer data
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div v-else-if="activeTab === 'Network'" class="space-y-3 text-xs">
          <div class="space-y-1">
            <div class="flex items-center justify-between text-slate-400">
              <span>Recent endpoints (5 min)</span>
              <span class="text-slate-500">
                {{ (network.recent_endpoints || []).length }} tracked
              </span>
            </div>
            <div class="max-h-32 overflow-y-auto border border-neutral-800 rounded">
              <table class="table table-xs">
                <thead>
                  <tr class="text-slate-400">
                    <th>IP</th>
                    <th class="text-right">Port</th>
                    <th class="text-right">Hits</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="endpoint in network.recent_endpoints || []"
                    :key="endpoint.ip + ':' + endpoint.port"
                    class="border-neutral-800"
                  >
                    <td class="text-slate-200">{{ endpoint.ip }}</td>
                    <td class="text-right text-slate-300">{{ endpoint.port }}</td>
                    <td class="text-right text-slate-300">{{ endpoint.count }}</td>
                  </tr>
                  <tr v-if="!network.recent_endpoints || !network.recent_endpoints.length">
                    <td colspan="3" class="text-center text-slate-500 py-3">
                      No recent endpoints
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div class="space-y-2">
            <div class="flex items-center justify-between">
              <span class="text-slate-400">All TCP connections</span>
              <button
                type="button"
                class="btn btn-ghost btn-xs"
                @click="$emit('load-network-connections')"
              >
                Load connections ({{ networkConnectionsCount }})
              </button>
            </div>
            <div class="max-h-32 overflow-y-auto border border-neutral-800 rounded">
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
                    v-for="conn in networkConnections"
                    :key="conn.local + '-' + conn.remote + '-' + conn.state"
                    class="border-neutral-800"
                  >
                    <td class="text-slate-200 truncate">{{ conn.local }}</td>
                    <td class="text-slate-200 truncate">{{ conn.remote }}</td>
                    <td class="text-right text-slate-300">{{ conn.state }}</td>
                  </tr>
                  <tr v-if="!networkConnections || !networkConnections.length">
                    <td colspan="3" class="text-center text-slate-500 py-3">
                      No connection data loaded
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div v-else-if="activeTab === 'Activity'" class="space-y-3 text-xs">
          <div class="flex items-center justify-between text-slate-400">
            <span>Process churn ({{ churn.window_seconds || 60 }}s)</span>
            <span class="text-slate-500">
              Spawned: {{ churn.spawned_count || 0 }} • Killed: {{ churn.killed_count || 0 }}
            </span>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div class="space-y-1">
              <div class="text-slate-400">Recent spawned</div>
              <div class="max-h-32 overflow-y-auto border border-neutral-800 rounded">
                <table class="table table-xs">
                  <thead>
                    <tr class="text-slate-400">
                      <th>PID</th>
                      <th>Name</th>
                      <th class="text-right">Seconds ago</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="item in churn.recent_spawned || []"
                      :key="'spawn-' + item.pid + '-' + item.seconds_ago"
                      class="border-neutral-800"
                    >
                      <td class="font-mono text-primary">{{ item.pid }}</td>
                      <td class="text-slate-200 truncate">{{ item.name }}</td>
                      <td class="text-right text-slate-300">{{ item.seconds_ago }}</td>
                    </tr>
                    <tr v-if="!churn.recent_spawned || !churn.recent_spawned.length">
                      <td colspan="3" class="text-center text-slate-500 py-3">
                        No spawn events in window
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <div class="space-y-1">
              <div class="text-slate-400">Recent killed</div>
              <div class="max-h-32 overflow-y-auto border border-neutral-800 rounded">
                <table class="table table-xs">
                  <thead>
                    <tr class="text-slate-400">
                      <th>PID</th>
                      <th>Name</th>
                      <th class="text-right">Seconds ago</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="item in churn.recent_killed || []"
                      :key="'killed-' + item.pid + '-' + item.seconds_ago"
                      class="border-neutral-800"
                    >
                      <td class="font-mono text-primary">{{ item.pid }}</td>
                      <td class="text-slate-200 truncate">{{ item.name }}</td>
                      <td class="text-right text-slate-300">{{ item.seconds_ago }}</td>
                    </tr>
                    <tr v-if="!churn.recent_killed || !churn.recent_killed.length">
                      <td colspan="3" class="text-center text-slate-500 py-3">
                        No kill events in window
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ProcessStatsBar',
  props: {
    stats: {
      type: Object,
      default: () => ({})
    },
    cpu: {
      type: Object,
      default: () => ({})
    },
    memoryMetrics: {
      type: Object,
      default: () => ({})
    },
    storageMetrics: {
      type: Object,
      default: () => ({})
    },
    storagePartitions: {
      type: Array,
      default: () => []
    },
    networkMetrics: {
      type: Object,
      default: () => ({})
    },
    networkConnections: {
      type: Array,
      default: () => []
    },
    networkConnectionsCount: {
      type: Number,
      default: 0
    },
    churn: {
      type: Object,
      default: () => ({})
    },
    churnWindowSeconds: {
      type: Number,
      default: 60
    },
    autoRefresh: {
      type: Boolean,
      default: true
    },
    refreshInterval: {
      type: Number,
      default: 2000
    },
    lastUpdate: {
      type: String,
      default: 'Never'
    },
    loading: {
      type: Boolean,
      default: false
    },
    processHistory: {
      type: Array,
      default: () => []
    },
    memoryHistory: {
      type: Array,
      default: () => []
    }
  },
  emits: ['refresh', 'toggle-auto-refresh', 'update-refresh-interval', 'load-network-connections'],
  data() {
    return {
      activeTab: 'Overview',
      tabs: ['Overview', 'CPU', 'Network', 'Activity']
    }
  },
  computed: {
    intervalOptions() {
      return [1000, 2000, 5000, 10000]
    },
    memory() {
      return this.memoryMetrics || {}
    },
    storage() {
      return this.storageMetrics || {}
    },
    network() {
      return this.networkMetrics || {}
    },
    memoryFillPercent() {
      const used = this.memory.used_mb || 0
      const total = this.memory.total_mb || 0
      if (!total || total <= 0) {
        return 0
      }
      const percent = (used / total) * 100
      if (percent < 0) return 0
      if (percent > 100) return 100
      return percent.toFixed(1)
    }
  },
  methods: {
    buildLinePoints(values) {
      if (!values || values.length < 2) return ''

      const max = Math.max(...values)
      const min = Math.min(...values)
      const span = max - min || 1
      const step = values.length > 1 ? 100 / (values.length - 1) : 100

      return values
        .map((v, index) => {
          const x = step * index
          const normalized = (v - min) / span
          const y = 40 - normalized * 30 - 5
          return `${x},${y}`
        })
        .join(' ')
    },
    formatMemory(mb) {
      if (!mb) return '0 MB'
      if (mb < 1) return `${(mb * 1024).toFixed(0)} KB`
      return `${mb.toFixed(1)} MB`
    },
    formatGb(gb) {
      if (!gb) return '0 GB'
      return `${gb.toFixed(2)} GB`
    },
    formatBytesPerSec(value) {
      const v = value || 0
      if (v < 1024) return `${v} B/s`
      if (v < 1024 * 1024) return `${(v / 1024).toFixed(1)} KB/s`
      return `${(v / (1024 * 1024)).toFixed(1)} MB/s`
    }
  }
}
</script>

