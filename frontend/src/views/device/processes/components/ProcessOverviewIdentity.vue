<template>
  <div class="space-y-2">
    <div class="flex items-center gap-2">
      <div class="w-7 h-7 rounded bg-violet-500/20 flex items-center justify-center flex-shrink-0">
        <svg class="w-4 h-4 text-violet-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
        </svg>
      </div>
      <span class="text-xs text-slate-400 font-medium">Identity</span>
    </div>

    <div class="bg-black/40 rounded-lg border border-slate-700/50 p-3 space-y-2">
      <div class="flex items-start gap-2 flex-wrap">
        <span class="text-white font-medium break-all">{{ identity.cmdline || identity.name }}</span>
        <div class="flex items-center gap-1.5 flex-shrink-0">
          <span 
            v-if="identity.android_state"
            class="badge badge-xs"
            :class="androidStateBadgeClass"
            :title="'Android: ' + identity.android_state"
          >{{ identity.android_state }}</span>
          <span 
            class="badge badge-xs"
            :class="kernelStateBadgeClass"
            :title="'Kernel: ' + identity.kernel_state"
          >
            <span v-if="identity.android_state" class="text-[9px] opacity-70">kernel:</span>
            {{ identity.kernel_state }}
          </span>
          <span 
            v-if="identity.is_kernel_thread"
            class="badge badge-xs badge-ghost text-slate-500"
            title="Kernel thread"
          >kthread</span>
          <button
            type="button"
            class="btn btn-xs btn-ghost btn-circle text-slate-500 hover:text-violet-400 -mr-1"
            title="About process states"
            @click.stop="showStateHelp = true"
          >
            <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </button>
        </div>
      </div>

      <div class="grid grid-cols-2 gap-x-4 gap-y-1 text-xs">
        <div>
          <span class="text-slate-500">PID:</span>
          <span class="text-primary font-mono ml-1">{{ identity.pid }}</span>
        </div>
        <div>
          <span class="text-slate-500">PPID:</span>
          <span class="text-slate-300 font-mono ml-1">{{ identity.ppid }}</span>
        </div>
        <div>
          <span class="text-slate-500">UID:</span>
          <span class="text-slate-300 font-mono ml-1">{{ identity.uid }}</span>
        </div>
        <div>
          <span class="text-slate-500">GID:</span>
          <span class="text-slate-300 font-mono ml-1">{{ identity.gid }}</span>
        </div>
      </div>

      <div class="grid grid-cols-2 gap-x-4 gap-y-1 text-xs">
        <div>
          <span class="text-slate-500">Threads:</span>
          <span class="text-slate-300 ml-1">{{ identity.thread_count }}</span>
        </div>
        <div>
          <span class="text-slate-500">Priority:</span>
          <span class="text-slate-300 ml-1">{{ identity.priority }}</span>
        </div>
        <div>
          <span class="text-slate-500">Nice:</span>
          <span class="text-slate-300 ml-1">{{ identity.nice }}</span>
        </div>
        <div>
          <span class="text-slate-500">Running:</span>
          <span class="text-slate-300 ml-1">{{ formatDuration(identity.running_seconds) }}</span>
        </div>
      </div>

      <div v-if="identity.cmdline && identity.cmdline !== identity.name" class="text-xs border-t border-neutral-800 pt-2 mt-2">
        <span class="text-slate-500">Command:</span>
        <code class="text-slate-300 ml-1 break-all text-[11px]">{{ identity.cmdline }}</code>
      </div>
    </div>

    <Teleport to="body">
      <div v-if="showStateHelp" class="modal modal-open">
        <div class="modal-box bg-neutral-900 border border-primary/30 max-w-xl">
          <h3 class="font-bold text-lg text-white mb-3">Understanding Process States</h3>
          
          <div class="space-y-4 text-sm">
            <div class="bg-black/40 rounded-lg border border-neutral-800 p-3">
              <div class="font-medium text-violet-400 mb-2">Why Two States?</div>
              <p class="text-slate-300 text-xs leading-relaxed">
                Android processes have two different state classifications that measure different things. 
                Both are valid and provide complementary information.
              </p>
            </div>

            <div class="space-y-3">
              <div>
                <div class="flex items-center gap-2 mb-1">
                  <span class="badge badge-xs badge-success">foreground</span>
                  <span class="text-slate-400 text-xs">Android State</span>
                </div>
                <p class="text-slate-300 text-xs leading-relaxed pl-2 border-l-2 border-emerald-500/30">
                  Reflects <span class="text-emerald-400">app lifecycle importance</span> from Android's perspective. 
                  States like "cached", "foreground", "service" indicate how Android prioritizes this process 
                  and whether it can be killed to free memory.
                </p>
              </div>

              <div>
                <div class="flex items-center gap-2 mb-1">
                  <span class="badge badge-xs badge-info">sleeping</span>
                  <span class="text-slate-400 text-xs">Kernel State</span>
                </div>
                <p class="text-slate-300 text-xs leading-relaxed pl-2 border-l-2 border-sky-500/30">
                  Reflects <span class="text-sky-400">CPU scheduling status</span> from the Linux kernel. 
                  States like "sleeping", "running", "disk_sleep" indicate what the process is currently 
                  doing at the CPU level.
                </p>
              </div>
            </div>

            <div class="bg-black/40 rounded-lg border border-neutral-800 p-3">
              <div class="font-medium text-amber-400 mb-2">Which Should I Trust?</div>
              <ul class="text-slate-300 text-xs space-y-1.5">
                <li class="flex items-start gap-2">
                  <span class="text-emerald-400 mt-0.5">-</span>
                  <span>For <span class="text-white">killing processes</span>: Trust the Android state. "cached" processes are safe to kill.</span>
                </li>
                <li class="flex items-start gap-2">
                  <span class="text-emerald-400 mt-0.5">-</span>
                  <span>For <span class="text-white">performance analysis</span>: Trust the kernel state. "running" means actively using CPU.</span>
                </li>
                <li class="flex items-start gap-2">
                  <span class="text-emerald-400 mt-0.5">-</span>
                  <span>For <span class="text-white">debugging hangs</span>: "disk_sleep" indicates I/O wait issues.</span>
                </li>
              </ul>
            </div>

            <div class="text-[10px] text-slate-500">
              A process can be Android-"cached" (low priority, can be killed) while simultaneously 
              kernel-"sleeping" (waiting for I/O). These are orthogonal concepts.
            </div>
          </div>
          
          <div class="modal-action">
            <button class="btn btn-sm" @click="showStateHelp = false">Got it</button>
          </div>
        </div>
        <div class="modal-backdrop bg-black/50" @click="showStateHelp = false"></div>
      </div>
    </Teleport>
  </div>
</template>

<script>
export default {
  name: 'ProcessOverviewIdentity',
  props: {
    identity: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      showStateHelp: false
    }
  },
  computed: {
    androidStateBadgeClass() {
      const stateMap = {
        'foreground': 'badge-success',
        'visible': 'badge-info',
        'service': 'badge-accent',
        'bound': 'badge-info badge-outline',
        'background': 'badge-neutral',
        'cached': 'badge-ghost',
        'persistent': 'badge-secondary',
        'receiver': 'badge-warning'
      }
      return stateMap[this.identity.android_state] || 'badge-ghost'
    },
    kernelStateBadgeClass() {
      const stateMap = {
        'running': 'badge-success',
        'sleeping': 'badge-info',
        'disk_sleep': 'badge-warning',
        'zombie': 'badge-error',
        'traced': 'badge-secondary',
        'dead': 'badge-error'
      }
      return stateMap[this.identity.kernel_state || this.identity.state] || 'badge-ghost'
    }
  },
  methods: {
    formatDuration(seconds) {
      if (!seconds || seconds < 0) return 'N/A'
      
      const days = Math.floor(seconds / 86400)
      const hours = Math.floor((seconds % 86400) / 3600)
      const minutes = Math.floor((seconds % 3600) / 60)
      const secs = seconds % 60
      
      if (days > 0) return `${days}d ${hours}h`
      if (hours > 0) return `${hours}h ${minutes}m`
      if (minutes > 0) return `${minutes}m ${secs}s`
      return `${secs}s`
    }
  }
}
</script>
