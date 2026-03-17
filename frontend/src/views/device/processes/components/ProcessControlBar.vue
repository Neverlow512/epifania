<template>
  <div class="flex gap-3 items-center flex-wrap">
    <input
      type="text"
      placeholder="Search by PID, name, or user..."
      class="input input-sm input-bordered bg-neutral-900 border-primary/30 focus:border-primary text-white flex-1 min-w-[200px]"
      :value="searchQuery"
      @input="$emit('update:searchQuery', $event.target.value)"
    />
    
    <select 
      class="select select-sm select-bordered bg-neutral-900 border-primary/30 focus:border-primary text-white"
      :value="filterType"
      @change="$emit('update:filterType', $event.target.value)"
    >
      <option value="all">All Processes</option>
      <option value="user">User Processes</option>
      <option value="system">System Processes</option>
    </select>
    
    <select 
      class="select select-sm select-bordered bg-neutral-900 border-primary/30 focus:border-primary text-white"
      :value="sortBy"
      @change="$emit('update:sortBy', $event.target.value)"
    >
      <option value="pid">Sort by PID</option>
      <option value="name">Sort by Name</option>
      <option value="memory">Sort by Memory</option>
      <option value="user">Sort by User</option>
    </select>

    <label class="cursor-pointer flex items-center gap-1.5 text-xs">
      <input 
        type="checkbox" 
        class="checkbox checkbox-xs checkbox-primary"
        :checked="showKernelThreads"
        @change="$emit('update:showKernelThreads', $event.target.checked)"
      />
      <span class="text-slate-400">Kernel threads</span>
    </label>

    <button
      type="button"
      class="ml-auto text-[10px] text-slate-500 hover:text-primary transition-colors border border-slate-700 hover:border-primary/50 rounded px-2 py-1"
      @click="showDetails = true"
    >
      Details
    </button>

    <Teleport to="body">
      <div
        v-if="showDetails"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
      >
        <div
          class="absolute inset-0 bg-black/70 backdrop-blur-sm"
          @click="showDetails = false"
        ></div>
        <div class="relative bg-neutral-900 border border-primary/30 rounded-xl shadow-2xl max-w-2xl w-full max-h-[85vh] overflow-hidden">
          <div class="flex items-center justify-between p-4 border-b border-neutral-800">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-lg bg-violet-500/20 flex items-center justify-center">
                <svg class="w-5 h-5 text-violet-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
                </svg>
              </div>
              <div>
                <h3 class="text-lg font-semibold text-white">Understanding the Process List</h3>
                <p class="text-xs text-slate-500">How to read and interpret process data</p>
              </div>
            </div>
            <button
              type="button"
              class="btn btn-ghost btn-sm btn-circle"
              @click="showDetails = false"
            >
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div class="p-4 overflow-y-auto max-h-[calc(85vh-80px)] space-y-6 text-sm">
            <section class="space-y-2">
              <h4 class="text-base font-medium text-white flex items-center gap-2">
                <span class="w-6 h-6 rounded bg-violet-500/20 flex items-center justify-center text-xs text-violet-400">1</span>
                What is This List?
              </h4>
              <p class="text-slate-400 leading-relaxed">
                This table shows all processes running on the Android device. Each row represents a <span class="text-white">process</span> - an instance of a running program. The data comes from the Linux <code class="text-violet-400 bg-violet-500/10 px-1 rounded">ps</code> command executed via ADB.
              </p>
            </section>

            <section class="space-y-2">
              <h4 class="text-base font-medium text-white flex items-center gap-2">
                <span class="w-6 h-6 rounded bg-blue-500/20 flex items-center justify-center text-xs text-blue-400">2</span>
                Column Explanations
              </h4>
              <div class="space-y-2">
                <div class="bg-black/40 rounded p-2 border border-neutral-800">
                  <span class="text-primary font-medium">PID (Process ID)</span>
                  <p class="text-slate-500 text-xs mt-1">Unique identifier assigned by the kernel. Lower PIDs are typically system processes started at boot.</p>
                </div>
                <div class="bg-black/40 rounded p-2 border border-neutral-800">
                  <span class="text-white font-medium">Process Name</span>
                  <p class="text-slate-500 text-xs mt-1">The executable name. Names in [brackets] are kernel threads. The smaller text below shows the full command line.</p>
                </div>
                <div class="bg-black/40 rounded p-2 border border-neutral-800">
                  <span class="text-slate-300 font-medium">User</span>
                  <p class="text-slate-500 text-xs mt-1">The Linux user running the process. Common users: root (system), system (Android framework), u0_aXXX (apps).</p>
                </div>
                <div class="bg-black/40 rounded p-2 border border-neutral-800">
                  <span class="text-slate-300 font-medium">Memory (RSS)</span>
                  <p class="text-slate-500 text-xs mt-1">Resident Set Size - memory pages currently in RAM. Includes shared libraries (see note below). Delta indicators show change since last refresh.</p>
                </div>
                <div class="bg-black/40 rounded p-2 border border-neutral-800">
                  <span class="text-blue-400 font-medium">State</span>
                  <p class="text-slate-500 text-xs mt-1">
                    Android process state (foreground, cached, persistent, etc.). 
                    Click the <span class="text-primary">?</span> icon next to the State column header for a full explanation of each state.
                  </p>
                </div>
              </div>
            </section>

            <section class="space-y-2">
              <h4 class="text-base font-medium text-white flex items-center gap-2">
                <span class="w-6 h-6 rounded bg-amber-500/20 flex items-center justify-center text-xs text-amber-400">3</span>
                About Memory (RSS) Values
              </h4>
              <p class="text-slate-400 leading-relaxed">
                The memory column shows <span class="text-amber-400">RSS (Resident Set Size)</span>. Important things to know:
              </p>
              <div class="bg-black/40 rounded-lg p-3 border border-neutral-800 space-y-2 text-xs">
                <div class="flex items-start gap-2">
                  <span class="text-amber-400 mt-0.5">*</span>
                  <span class="text-slate-300">RSS includes shared libraries counted per-process. Summing all RSS will exceed actual RAM usage.</span>
                </div>
                <div class="flex items-start gap-2">
                  <span class="text-amber-400 mt-0.5">*</span>
                  <span class="text-slate-300">Use RSS for <span class="text-white">relative comparison</span> between processes, not absolute values.</span>
                </div>
                <div class="flex items-start gap-2">
                  <span class="text-amber-400 mt-0.5">*</span>
                  <span class="text-slate-300">Kernel threads (names in [brackets]) show 0 MB because they run in kernel space, not user space.</span>
                </div>
                <div class="flex items-start gap-2">
                  <span class="text-amber-400 mt-0.5">*</span>
                  <span class="text-slate-300">For actual system RAM usage, check the Memory widget in Runtime Overview.</span>
                </div>
              </div>
            </section>

            <section class="space-y-2">
              <h4 class="text-base font-medium text-white flex items-center gap-2">
                <span class="w-6 h-6 rounded bg-emerald-500/20 flex items-center justify-center text-xs text-emerald-400">4</span>
                Memory Delta Indicators
              </h4>
              <p class="text-slate-400 leading-relaxed">
                When a process's memory changes between refreshes, you'll see colored indicators:
              </p>
              <div class="bg-black/40 rounded-lg p-3 border border-neutral-800 space-y-2 text-xs">
                <div class="flex items-center gap-3">
                  <span class="text-red-400">+1.2 MB</span>
                  <span class="text-slate-400">Memory increased (potential leak or normal allocation)</span>
                </div>
                <div class="flex items-center gap-3">
                  <span class="text-green-400">-0.5 MB</span>
                  <span class="text-slate-400">Memory decreased (freed or garbage collected)</span>
                </div>
              </div>
            </section>

            <section class="space-y-2">
              <h4 class="text-base font-medium text-white flex items-center gap-2">
                <span class="w-6 h-6 rounded bg-sky-500/20 flex items-center justify-center text-xs text-sky-400">5</span>
                Filters and Sorting
              </h4>
              <div class="bg-black/40 rounded-lg p-3 border border-neutral-800 space-y-2 text-xs">
                <div class="flex items-start gap-2">
                  <span class="text-sky-400 w-28 flex-shrink-0">All Processes</span>
                  <span class="text-slate-400">Shows everything (excluding kernel threads by default)</span>
                </div>
                <div class="flex items-start gap-2">
                  <span class="text-sky-400 w-28 flex-shrink-0">User Processes</span>
                  <span class="text-slate-400">Apps and user-space services (not root/system)</span>
                </div>
                <div class="flex items-start gap-2">
                  <span class="text-sky-400 w-28 flex-shrink-0">System Processes</span>
                  <span class="text-slate-400">Root and system user processes (framework, daemons)</span>
                </div>
                <div class="flex items-start gap-2">
                  <span class="text-sky-400 w-28 flex-shrink-0">Kernel threads</span>
                  <span class="text-slate-400">Toggle to show/hide kernel threads (names in [brackets])</span>
                </div>
                <div class="flex items-start gap-2">
                  <span class="text-sky-400 w-28 flex-shrink-0">Sort by Memory</span>
                  <span class="text-slate-400">Default sort - shows biggest memory consumers first</span>
                </div>
              </div>
            </section>

            <section class="space-y-2">
              <h4 class="text-base font-medium text-white flex items-center gap-2">
                <span class="w-6 h-6 rounded bg-red-500/20 flex items-center justify-center text-xs text-red-400">6</span>
                Process States
              </h4>
              <p class="text-slate-400 text-sm leading-relaxed">
                Process states show Android's view of each process's importance, not the raw kernel state. 
                This helps you understand which processes are actively used vs. which can be safely terminated.
              </p>
              <div class="grid grid-cols-2 gap-2">
                <div class="bg-black/40 rounded p-2 border border-neutral-800">
                  <span class="badge badge-success badge-sm">foreground</span>
                  <p class="text-slate-500 text-xs mt-1">App currently on screen</p>
                </div>
                <div class="bg-black/40 rounded p-2 border border-neutral-800">
                  <span class="badge badge-info badge-sm">visible</span>
                  <p class="text-slate-500 text-xs mt-1">Visible or bound to foreground</p>
                </div>
                <div class="bg-black/40 rounded p-2 border border-neutral-800">
                  <span class="badge badge-ghost badge-sm">cached</span>
                  <p class="text-slate-500 text-xs mt-1">Can be killed to free memory</p>
                </div>
                <div class="bg-black/40 rounded p-2 border border-neutral-800">
                  <span class="badge badge-secondary badge-sm">persistent</span>
                  <p class="text-slate-500 text-xs mt-1">System-critical, always running</p>
                </div>
              </div>
              <div class="bg-violet-500/10 border border-violet-500/30 rounded-lg p-3 mt-2">
                <p class="text-violet-300 text-xs">
                  <span class="font-medium">State Dictionary:</span> 
                  For a complete list of all states with detailed explanations, click the 
                  <span class="inline-flex items-center justify-center w-4 h-4 rounded-full border border-slate-500 text-[10px] text-slate-400 mx-1">?</span> 
                  icon next to the <span class="text-white">State</span> column header in the process table.
                </p>
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
  name: 'ProcessControlBar',
  props: {
    searchQuery: {
      type: String,
      default: ''
    },
    filterType: {
      type: String,
      default: 'all'
    },
    sortBy: {
      type: String,
      default: 'memory'
    },
    showKernelThreads: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:searchQuery', 'update:filterType', 'update:sortBy', 'update:showKernelThreads'],
  data() {
    return {
      showDetails: false
    }
  }
}
</script>

