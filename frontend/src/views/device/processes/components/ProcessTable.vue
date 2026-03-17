<template>
  <div>
    <div class="overflow-x-auto">
    <table class="table table-sm">
      <thead>
        <tr class="border-b border-primary/20">
          <th class="text-slate-400">PID</th>
          <th class="text-slate-400">Process Name</th>
          <th class="text-slate-400">User</th>
          <th class="text-slate-400">Memory</th>
          <th class="text-slate-400">
            <span class="flex items-center gap-1">
              State
              <button 
                class="btn btn-xs btn-ghost btn-circle text-slate-500 hover:text-primary"
                @click.stop="showStateHelp = true"
                title="State Dictionary"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </button>
            </span>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-if="loading && paginatedProcesses.length === 0">
          <td colspan="5" class="text-center py-8">
            <span class="loading loading-spinner loading-lg text-primary"></span>
          </td>
        </tr>
        <tr v-else-if="paginatedProcesses.length === 0">
          <td colspan="5" class="text-center py-8 text-slate-400">
            No processes found
          </td>
        </tr>
        <tr 
          v-else
          v-for="process in paginatedProcesses" 
          :key="process.pid"
          class="hover:bg-primary/5 border-b border-neutral-800 cursor-pointer transition-colors"
          :class="process.pid === focusedPid ? 'bg-primary/10 border-primary/40' : ''"
          @click="$emit('toggle-overview', process)"
        >
          <td class="font-mono text-primary">
            <div class="flex items-center gap-2">
              <svg 
                class="w-3 h-3 text-slate-500 transition-transform"
                :class="process.pid === focusedPid ? 'rotate-90' : ''"
                fill="none" viewBox="0 0 24 24" stroke="currentColor"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
              {{ process.pid }}
            </div>
          </td>
          <td class="text-white">
            <div class="flex items-center gap-2">
              <span class="font-medium">{{ process.name }}</span>
            </div>
            <div class="text-xs text-slate-500 font-mono truncate max-w-xs" :title="process.command">
              {{ process.command }}
            </div>
          </td>
          <td class="text-slate-300 font-mono text-xs">{{ process.user }}</td>
          <td class="text-slate-300">
            <span>{{ formatMemory(process.memory_mb) }}</span>
            <span 
              v-if="process.memory_delta_mb > 0.1" 
              class="text-red-400 text-xs ml-1"
            >+{{ formatDelta(process.memory_delta_mb) }}</span>
            <span 
              v-else-if="process.memory_delta_mb < -0.1" 
              class="text-green-400 text-xs ml-1"
            >{{ formatDelta(process.memory_delta_mb) }}</span>
          </td>
          <td>
            <span 
              class="badge badge-xs"
              :class="getStateBadgeClass(process.state)"
            >
              {{ process.state || 'unknown' }}
            </span>
          </td>
        </tr>
      </tbody>
    </table>

    <div class="flex justify-between items-center py-3 border-t border-primary/20 mt-2">
      <div class="text-sm text-slate-400">
        Showing {{ startIndex + 1 }}-{{ endIndex }} of {{ totalCount }} processes
      </div>
      <div class="flex gap-2">
        <button 
          class="btn btn-sm btn-ghost"
          @click="$emit('page-change', currentPage - 1)"
          :disabled="currentPage === 0"
        >
          Previous
        </button>
        <button 
          class="btn btn-sm btn-ghost"
          @click="$emit('page-change', currentPage + 1)"
          :disabled="endIndex >= totalCount"
        >
          Next
        </button>
      </div>
    </div>
    </div>

    <Teleport to="body">
      <div v-if="showStateHelp" class="modal modal-open">
        <div class="modal-box bg-neutral-900 border border-primary/30 max-w-2xl max-h-[85vh]">
          <h3 class="font-bold text-lg text-white mb-2">Process State Dictionary</h3>
          <p class="text-slate-400 text-sm mb-4">
            Process states are derived from Android's ActivityManager via <code class="text-violet-400 bg-violet-500/10 px-1 rounded text-xs">dumpsys activity processes</code>. 
            Non-Android processes fall back to kernel-level classification.
          </p>
          
          <div class="space-y-3 overflow-y-auto max-h-[calc(85vh-180px)] pr-2">
            <div class="text-sm font-medium text-slate-300 border-b border-primary/20 pb-2">Android-Managed Processes</div>
            
            <div v-for="state in androidStates" :key="state.name" class="flex items-start gap-3 py-2">
              <span class="badge badge-sm shrink-0 w-24" :class="getStateBadgeClass(state.name)">
                {{ state.name }}
              </span>
              <span class="text-slate-300 text-sm">{{ state.description }}</span>
            </div>
            
            <div class="text-sm font-medium text-slate-300 border-b border-primary/20 pb-2 pt-4">System Processes (Fallback States)</div>
            <p class="text-slate-500 text-xs mb-2">
              These states are assigned to processes not managed by Android's ActivityManager.
            </p>
            
            <div v-for="state in systemStates" :key="state.name" class="flex items-start gap-3 py-2">
              <span class="badge badge-sm shrink-0 w-24" :class="getStateBadgeClass(state.name)">
                {{ state.name }}
              </span>
              <span class="text-slate-300 text-sm">{{ state.description }}</span>
            </div>

            <div class="text-sm font-medium text-slate-300 border-b border-primary/20 pb-2 pt-4">How States Are Determined</div>
            
            <div class="bg-black/40 rounded-lg p-3 border border-neutral-800 space-y-3 text-xs">
              <div>
                <span class="text-violet-400 font-medium">1. Android Apps</span>
                <p class="text-slate-400 mt-1">
                  For processes in <code class="text-violet-400 bg-violet-500/10 px-1 rounded">dumpsys activity processes</code>, 
                  we read the <code class="text-violet-400 bg-violet-500/10 px-1 rounded">curProcState</code> value (0-20) 
                  and map it to a user-friendly label. This reflects Android's own view of process importance.
                </p>
              </div>
              
              <div>
                <span class="text-violet-400 font-medium">2. Kernel Threads</span>
                <p class="text-slate-400 mt-1">
                  Processes with names in <code class="text-violet-400 bg-violet-500/10 px-1 rounded">[brackets]</code> 
                  (e.g., [kworker/0:1]) are kernel threads. They run in kernel space and aren't Android apps.
                </p>
              </div>
              
              <div>
                <span class="text-violet-400 font-medium">3. Native Daemons</span>
                <p class="text-slate-400 mt-1">
                  Processes not in dumpsys and not kernel threads are classified as <span class="text-slate-300">native</span>. 
                  These are typically system daemons (init, adbd, logd, surfaceflinger) that run outside the Android runtime.
                </p>
              </div>
              
              <div>
                <span class="text-violet-400 font-medium">4. Zombie Detection</span>
                <p class="text-slate-400 mt-1">
                  If the kernel reports a process as <span class="text-red-400">zombie</span> (state 'Z' in ps), 
                  we preserve this regardless of other classifications. Zombies indicate a parent process 
                  that hasn't collected its child's exit status.
                </p>
              </div>
            </div>

            <div class="text-sm font-medium text-slate-300 border-b border-primary/20 pb-2 pt-4">Interpreting the States</div>
            
            <div class="bg-black/40 rounded-lg p-3 border border-neutral-800 space-y-2 text-xs">
              <div class="flex items-start gap-2">
                <span class="text-emerald-400 mt-0.5">Tip:</span>
                <span class="text-slate-300">
                  <span class="text-emerald-400">foreground</span> and <span class="text-blue-400">visible</span> 
                  processes are actively used. Killing them will be noticed by the user.
                </span>
              </div>
              <div class="flex items-start gap-2">
                <span class="text-emerald-400 mt-0.5">Tip:</span>
                <span class="text-slate-300">
                  <span class="text-slate-400">cached</span> processes can be safely killed to free memory. 
                  Android will restart them when needed.
                </span>
              </div>
              <div class="flex items-start gap-2">
                <span class="text-amber-400 mt-0.5">Warning:</span>
                <span class="text-slate-300">
                  <span class="text-secondary">persistent</span> processes are critical. Killing them may 
                  cause system instability or require a reboot.
                </span>
              </div>
              <div class="flex items-start gap-2">
                <span class="text-amber-400 mt-0.5">Warning:</span>
                <span class="text-slate-300">
                  Many <span class="text-slate-400">zombie</span> processes may indicate a buggy app 
                  that isn't properly managing child processes.
                </span>
              </div>
            </div>
          </div>
          
          <div class="modal-action">
            <button class="btn btn-sm" @click="showStateHelp = false">Close</button>
          </div>
        </div>
        <div class="modal-backdrop bg-black/50" @click="showStateHelp = false"></div>
      </div>
    </Teleport>
  </div>
</template>

<script>
export default {
  name: 'ProcessTable',
  props: {
    paginatedProcesses: {
      type: Array,
      default: () => []
    },
    startIndex: {
      type: Number,
      default: 0
    },
    endIndex: {
      type: Number,
      default: 0
    },
    totalCount: {
      type: Number,
      default: 0
    },
    currentPage: {
      type: Number,
      default: 0
    },
    loading: {
      type: Boolean,
      default: false
    },
    focusedPid: {
      type: Number,
      default: null
    }
  },
  emits: ['toggle-overview', 'page-change'],
  data() {
    return {
      showStateHelp: false,
      androidStates: [
        { name: 'foreground', description: 'Currently on screen. The user is actively interacting with this app.' },
        { name: 'visible', description: 'Visible to the user or bound to a foreground service (e.g., launcher, picture-in-picture).' },
        { name: 'service', description: 'Running a foreground service (e.g., music playback, active downloads, GPS tracking).' },
        { name: 'bound', description: 'Bound to the currently active app (e.g., keyboard, accessibility service).' },
        { name: 'background', description: 'Running in the background but not visible. May be doing work or waiting.' },
        { name: 'cached', description: 'Kept in memory for fast switching but can be killed anytime to free resources.' },
        { name: 'persistent', description: 'System-critical process that Android keeps running at all times.' },
        { name: 'receiver', description: 'Currently receiving a broadcast message from the system or another app.' }
      ],
      systemStates: [
        { name: 'kernel', description: 'Kernel thread running inside the Linux kernel (e.g., kworker, ksoftirqd). Not an Android app.' },
        { name: 'native', description: 'Native system daemon running outside Android runtime (e.g., init, adbd, logd).' },
        { name: 'zombie', description: 'Process has terminated but its parent hasn\'t collected its exit status. May indicate a bug.' }
      ]
    }
  },
  methods: {
    formatMemory(mb) {
      if (!mb) return '0 MB'
      if (mb < 1) return `${(mb * 1024).toFixed(0)} KB`
      return `${mb.toFixed(1)} MB`
    },
    formatDelta(mb) {
      if (!mb) return ''
      const abs = Math.abs(mb)
      if (abs < 1) return `${(mb * 1024).toFixed(0)} KB`
      return `${mb.toFixed(1)} MB`
    },
    getStateBadgeClass(state) {
      if (!state) return 'badge-ghost'
      const stateMap = {
        'foreground': 'badge-success',
        'visible': 'badge-info',
        'service': 'badge-accent',
        'bound': 'badge-info badge-outline',
        'background': 'badge-neutral',
        'cached': 'badge-ghost',
        'persistent': 'badge-secondary',
        'receiver': 'badge-warning',
        'kernel': 'badge-ghost text-slate-500',
        'native': 'badge-ghost text-slate-500',
        'zombie': 'badge-error'
      }
      return stateMap[state] || 'badge-ghost'
    }
  }
}
</script>
