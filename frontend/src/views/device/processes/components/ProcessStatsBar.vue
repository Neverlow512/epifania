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
            @click="$emit('refresh')"
          >
            Refresh
          </button>
        </div>
      </div>

      <div class="grid grid-cols-2 gap-2">
        <!-- Processes -->
        <div class="bg-black/40 rounded-lg border border-slate-700/50 p-3 flex flex-col">
          <div class="flex items-center gap-2 mb-2">
            <div class="w-7 h-7 rounded bg-violet-500/20 flex items-center justify-center flex-shrink-0">
              <svg class="w-4 h-4 text-violet-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
              </svg>
            </div>
            <span class="text-xs text-slate-400 font-medium">Processes</span>
          </div>
          <div class="text-2xl font-semibold text-white font-mono mb-1">{{ stats.total || 0 }}</div>
          <div class="text-[11px] text-slate-500 mt-auto">
            <span class="text-cyan-400">{{ stats.user || 0 }}</span> user
            <span class="mx-1 text-slate-600">|</span>
            <span class="text-amber-400">{{ stats.system || 0 }}</span> system
          </div>
        </div>

        <!-- CPU -->
        <div class="bg-black/40 rounded-lg border border-slate-700/50 p-3 flex flex-col">
          <div class="flex items-center gap-2 mb-2">
            <div class="w-7 h-7 rounded bg-blue-500/20 flex items-center justify-center flex-shrink-0">
              <svg class="w-4 h-4 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
              </svg>
            </div>
            <span class="text-xs text-slate-400 font-medium">CPU</span>
            <button
              type="button"
              class="ml-auto text-[9px] text-slate-500 hover:text-blue-400 transition-colors border border-slate-700 hover:border-blue-500/50 rounded px-1.5 py-0.5"
              @click="showCpuDetails = true"
            >
              Details
            </button>
            <span class="text-[10px] px-1.5 py-0.5 rounded" :class="cpuBadgeClass">{{ cpuLoadLabel }}</span>
          </div>
          <div class="flex items-baseline gap-2 mb-2">
            <span class="text-2xl font-semibold text-white font-mono">{{ (cpu.overall_percent || 0).toFixed(1) }}</span>
            <span class="text-sm text-slate-500">%</span>
          </div>
          <div class="w-full h-1.5 bg-neutral-800 rounded-full overflow-hidden mb-2">
            <div class="h-full rounded-full transition-all duration-300" :class="cpuUsageClass" :style="{ width: cpuUsage + '%' }"></div>
          </div>
          <div class="text-[11px] text-slate-500 truncate mt-auto">
            <template v-if="cpu.top_consumers && cpu.top_consumers.length">
              <span class="text-slate-400">Top:</span> {{ cpu.top_consumers[0].name }}
            </template>
            <template v-else>Idle</template>
          </div>
        </div>

        <!-- RAM -->
        <div class="bg-black/40 rounded-lg border border-slate-700/50 p-3 flex flex-col">
          <div class="flex items-center gap-2 mb-2">
            <div class="w-7 h-7 rounded bg-emerald-500/20 flex items-center justify-center flex-shrink-0">
              <svg class="w-4 h-4 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
            </div>
            <span class="text-xs text-slate-400 font-medium">Memory</span>
            <span class="ml-auto text-[10px] text-slate-500">{{ memoryUsedPercent }}%</span>
          </div>
          <div class="flex items-baseline gap-1 mb-1">
            <span class="text-lg font-semibold text-white font-mono">{{ formatMemoryCompact(memoryActualUsed) }}</span>
            <span class="text-xs text-slate-600">/</span>
            <span class="text-sm text-slate-400 font-mono">{{ formatMemoryCompact(memory.total_mb) }}</span>
          </div>
          <div class="w-full h-1.5 bg-neutral-800 rounded-full overflow-hidden mb-2">
            <div class="h-full bg-emerald-500 rounded-full" :style="{ width: memoryUsedPercent + '%' }"></div>
          </div>
          <div class="text-[11px] text-slate-500 mt-auto">
            <span class="text-emerald-400">{{ formatMemoryCompact(memory.available_mb || memory.free_mb) }}</span> available
          </div>
        </div>

        <!-- Storage -->
        <div class="bg-black/40 rounded-lg border border-slate-700/50 p-3 flex flex-col">
          <div class="flex items-center gap-2 mb-2">
            <div class="w-7 h-7 rounded bg-indigo-500/20 flex items-center justify-center flex-shrink-0">
              <svg class="w-4 h-4 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
              </svg>
            </div>
            <span class="text-xs text-slate-400 font-medium">Storage</span>
            <span class="ml-auto text-[10px] text-slate-500">{{ (storage.percent_used || 0).toFixed(0) }}%</span>
          </div>
          <div class="flex items-baseline gap-1 mb-1">
            <span class="text-lg font-semibold text-white font-mono">{{ formatGb(storage.used_gb) }}</span>
            <span class="text-xs text-slate-600">/</span>
            <span class="text-sm text-slate-400 font-mono">{{ formatGb(storage.total_gb) }}</span>
          </div>
          <div class="w-full h-1.5 bg-neutral-800 rounded-full overflow-hidden mb-2">
            <div class="h-full bg-indigo-500 rounded-full" :style="{ width: (storage.percent_used || 0) + '%' }"></div>
          </div>
          <div class="text-[11px] text-slate-500 mt-auto">
            <span class="text-indigo-400">{{ formatGb(storage.free_gb) }}</span> free
          </div>
        </div>

        <!-- Network -->
        <div class="bg-black/40 rounded-lg border border-slate-700/50 p-3 flex flex-col">
          <div class="flex items-center gap-2 mb-2">
            <div class="w-7 h-7 rounded bg-sky-500/20 flex items-center justify-center flex-shrink-0">
              <svg class="w-4 h-4 text-sky-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.141 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0" />
              </svg>
            </div>
            <span class="text-xs text-slate-400 font-medium">Network</span>
          </div>
          <div class="flex items-center gap-3 mb-2">
            <div class="flex items-center gap-1">
              <span class="text-green-400 text-xs">&#9650;</span>
              <span class="text-sm font-mono text-white">{{ formatBytesPerSecCompact(network.throughput?.bytes_sent_per_sec) }}</span>
            </div>
            <div class="flex items-center gap-1">
              <span class="text-blue-400 text-xs">&#9660;</span>
              <span class="text-sm font-mono text-white">{{ formatBytesPerSecCompact(network.throughput?.bytes_recv_per_sec) }}</span>
            </div>
          </div>
          <div class="text-[11px] text-slate-500 mt-auto">
            {{ (network.recent_endpoints || []).length }} endpoints
          </div>
        </div>

        <!-- Churn -->
        <div class="bg-black/40 rounded-lg border border-slate-700/50 p-3 flex flex-col">
          <div class="flex items-center gap-2 mb-2">
            <div class="w-7 h-7 rounded bg-orange-500/20 flex items-center justify-center flex-shrink-0">
              <svg class="w-4 h-4 text-orange-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </div>
            <span class="text-xs text-slate-400 font-medium">Churn</span>
            <span class="ml-auto text-[10px] text-slate-600">{{ churn.window_seconds || 60 }}s</span>
          </div>
          <div class="flex items-center gap-3 mb-2">
            <div class="text-center">
              <div class="text-lg font-semibold text-green-400 font-mono">{{ churn.spawned_count || 0 }}</div>
              <div class="text-[10px] text-slate-600">spawned</div>
            </div>
            <div class="text-center">
              <div class="text-lg font-semibold text-red-400 font-mono">{{ churn.killed_count || 0 }}</div>
              <div class="text-[10px] text-slate-600">killed</div>
            </div>
          </div>
          <div class="text-[11px] text-slate-500 mt-auto">
            Net: <span :class="churnNetClass">{{ churn.net_change > 0 ? '+' : '' }}{{ churn.net_change || 0 }}</span>
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
            <div class="flex items-center gap-3">
              <span class="text-slate-500">
                Overall: {{ (cpu.overall_percent || 0).toFixed(1) }}%
              </span>
              <button
                type="button"
                class="text-[10px] text-slate-500 hover:text-blue-400 transition-colors border border-slate-700 hover:border-blue-500/50 rounded px-1.5 py-0.5"
                @click="showCpuDetails = true"
              >
                Details
              </button>
            </div>
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

    <!-- CPU Details Modal -->
    <Teleport to="body">
      <div
        v-if="showCpuDetails"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
      >
        <div
          class="absolute inset-0 bg-black/70 backdrop-blur-sm"
          @click="showCpuDetails = false"
        ></div>
        <div class="relative bg-neutral-900 border border-primary/30 rounded-xl shadow-2xl max-w-2xl w-full max-h-[85vh] overflow-hidden">
          <div class="flex items-center justify-between p-4 border-b border-neutral-800">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center">
                <svg class="w-5 h-5 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
                </svg>
              </div>
              <div>
                <h3 class="text-lg font-semibold text-white">Understanding CPU Metrics</h3>
                <p class="text-xs text-slate-500">How CPU usage is measured on Android devices</p>
              </div>
            </div>
            <button
              type="button"
              class="btn btn-ghost btn-sm btn-circle"
              @click="showCpuDetails = false"
            >
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div class="p-4 overflow-y-auto max-h-[calc(85vh-80px)] space-y-6 text-sm">
            <section class="space-y-2">
              <h4 class="text-base font-medium text-white flex items-center gap-2">
                <span class="w-6 h-6 rounded bg-blue-500/20 flex items-center justify-center text-xs text-blue-400">1</span>
                Why do most processes show 0% CPU?
              </h4>
              <p class="text-slate-400 leading-relaxed">
                CPU measurements are taken as <span class="text-white">instant snapshots</span>. At any given microsecond, most processes are sleeping (waiting for I/O, timers, or user input) rather than actively executing code.
              </p>
              <p class="text-slate-400 leading-relaxed">
                A process showing 0% means it wasn't running on any CPU core at that exact moment. Even busy processes spend most of their time sleeping between handling events.
              </p>
            </section>

            <section class="space-y-2">
              <h4 class="text-base font-medium text-white flex items-center gap-2">
                <span class="w-6 h-6 rounded bg-emerald-500/20 flex items-center justify-center text-xs text-emerald-400">2</span>
                How can a process use 100% but overall be ~30%?
              </h4>
              <p class="text-slate-400 leading-relaxed">
                This is due to <span class="text-white">multi-core CPUs</span>. Your device has multiple CPU cores, and percentages are calculated differently:
              </p>
              <div class="bg-black/40 rounded-lg p-3 border border-neutral-800 space-y-2">
                <div class="flex items-start gap-2">
                  <span class="text-blue-400 font-mono text-xs mt-0.5">Per-process:</span>
                  <span class="text-slate-300 text-xs">Relative to one core (0-100% per core)</span>
                </div>
                <div class="flex items-start gap-2">
                  <span class="text-emerald-400 font-mono text-xs mt-0.5">Overall:</span>
                  <span class="text-slate-300 text-xs">Relative to all cores combined</span>
                </div>
              </div>
              <p class="text-slate-400 leading-relaxed">
                On a 4-core system, one process at 100% uses 1 full core, which equals <span class="text-white">25% of total CPU capacity</span>. The overall ~30% you see is that process (25%) plus other system overhead (~5%).
              </p>
            </section>

            <section class="space-y-2">
              <h4 class="text-base font-medium text-white flex items-center gap-2">
                <span class="w-6 h-6 rounded bg-amber-500/20 flex items-center justify-center text-xs text-amber-400">3</span>
                Visual Example
              </h4>
              <div class="bg-black/40 rounded-lg p-4 border border-neutral-800 font-mono text-xs">
                <div class="text-slate-500 mb-2">4-Core CPU Total Capacity: 400%</div>
                <div class="grid grid-cols-4 gap-1 mb-3">
                  <div class="bg-red-500/30 border border-red-500/50 rounded p-2 text-center">
                    <div class="text-red-400">Core 0</div>
                    <div class="text-white text-sm">100%</div>
                    <div class="text-red-300 text-[10px]">(busy)</div>
                  </div>
                  <div class="bg-neutral-800 border border-neutral-700 rounded p-2 text-center">
                    <div class="text-slate-500">Core 1</div>
                    <div class="text-slate-400 text-sm">0%</div>
                    <div class="text-slate-600 text-[10px]">(idle)</div>
                  </div>
                  <div class="bg-neutral-800 border border-neutral-700 rounded p-2 text-center">
                    <div class="text-slate-500">Core 2</div>
                    <div class="text-slate-400 text-sm">0%</div>
                    <div class="text-slate-600 text-[10px]">(idle)</div>
                  </div>
                  <div class="bg-neutral-800 border border-neutral-700 rounded p-2 text-center">
                    <div class="text-slate-500">Core 3</div>
                    <div class="text-slate-400 text-sm">0%</div>
                    <div class="text-slate-600 text-[10px]">(idle)</div>
                  </div>
                </div>
                <div class="space-y-1 text-slate-400">
                  <div>Process "sh": <span class="text-white">100%</span> (of 1 core)</div>
                  <div>Overall CPU: 100/400 = <span class="text-emerald-400">25%</span> (+ overhead = ~30%)</div>
                </div>
              </div>
            </section>

            <section class="space-y-2">
              <h4 class="text-base font-medium text-white flex items-center gap-2">
                <span class="w-6 h-6 rounded bg-violet-500/20 flex items-center justify-center text-xs text-violet-400">4</span>
                Process States
              </h4>
              <div class="grid grid-cols-2 gap-2">
                <div class="bg-black/40 rounded p-2 border border-neutral-800">
                  <span class="text-emerald-400 font-medium">Running (R)</span>
                  <p class="text-slate-500 text-xs mt-1">Actively executing on a CPU core</p>
                </div>
                <div class="bg-black/40 rounded p-2 border border-neutral-800">
                  <span class="text-blue-400 font-medium">Sleeping (S)</span>
                  <p class="text-slate-500 text-xs mt-1">Waiting for an event (most common)</p>
                </div>
                <div class="bg-black/40 rounded p-2 border border-neutral-800">
                  <span class="text-amber-400 font-medium">Disk Sleep (D)</span>
                  <p class="text-slate-500 text-xs mt-1">Waiting for I/O operation</p>
                </div>
                <div class="bg-black/40 rounded p-2 border border-neutral-800">
                  <span class="text-red-400 font-medium">Zombie (Z)</span>
                  <p class="text-slate-500 text-xs mt-1">Terminated but not yet cleaned up</p>
                </div>
              </div>
            </section>

            <section class="space-y-2">
              <h4 class="text-base font-medium text-white flex items-center gap-2">
                <span class="w-6 h-6 rounded bg-sky-500/20 flex items-center justify-center text-xs text-sky-400">5</span>
                Data Sources
              </h4>
              <div class="bg-black/40 rounded-lg p-3 border border-neutral-800 space-y-2 text-xs">
                <div class="flex items-start gap-2">
                  <span class="text-slate-500 w-24 flex-shrink-0">Overall CPU:</span>
                  <span class="text-slate-400">Calculated from <code class="text-blue-400 bg-blue-500/10 px-1 rounded">/proc/stat</code> delta between samples</span>
                </div>
                <div class="flex items-start gap-2">
                  <span class="text-slate-500 w-24 flex-shrink-0">Per-process:</span>
                  <span class="text-slate-400">Instant snapshot from <code class="text-blue-400 bg-blue-500/10 px-1 rounded">top</code> command</span>
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
      tabs: ['Overview', 'CPU', 'Network', 'Activity'],
      showCpuDetails: false
    }
  },
  computed: {
    intervalOptions() {
      return [1000, 2000, 5000, 10000]
    },
    cpuUsage() {
      const value = this.cpu && this.cpu.overall_percent ? this.cpu.overall_percent : 0
      if (value < 0) return 0
      if (value > 100) return 100
      return Number(value.toFixed(1))
    },
    cpuUsageClass() {
      const v = this.cpuUsage
      if (v < 40) return 'bg-emerald-500'
      if (v < 75) return 'bg-amber-400'
      return 'bg-red-500'
    },
    cpuLoadLabel() {
      const v = this.cpu && this.cpu.overall_percent ? this.cpu.overall_percent : 0
      if (v < 40) return 'Low'
      if (v < 75) return 'Moderate'
      return 'High'
    },
    cpuBadgeClass() {
      const v = this.cpuUsage
      if (v < 40) return 'bg-emerald-500/20 text-emerald-400'
      if (v < 75) return 'bg-amber-500/20 text-amber-400'
      return 'bg-red-500/20 text-red-400'
    },
    churnNetClass() {
      const net = this.churn.net_change || 0
      if (net > 0) return 'text-emerald-400'
      if (net < 0) return 'text-red-400'
      return 'text-slate-400'
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
    },
    memoryActualUsed() {
      const total = this.memory.total_mb || 0
      const available = this.memory.available_mb || this.memory.free_mb || 0
      return Math.max(0, total - available)
    },
    memoryUsedPercent() {
      const total = this.memory.total_mb || 0
      if (!total || total <= 0) return 0
      const used = this.memoryActualUsed
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
    formatMemoryCompact(mb) {
      if (!mb) return '0'
      if (mb >= 1024) {
        const gb = mb / 1024
        return `${gb.toFixed(2)} GB`
      }
      return `${Math.round(mb)} MB`
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
    },
    formatBytesPerSecCompact(value) {
      const v = value || 0
      if (v < 1024) return `${v} B/s`
      if (v < 1024 * 1024) return `${(v / 1024).toFixed(0)} KB/s`
      return `${(v / (1024 * 1024)).toFixed(1)} MB/s`
    }
  }
}
</script>

