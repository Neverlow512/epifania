<template>
  <div class="flex gap-3 items-center flex-wrap">
    <input
      type="text"
      placeholder="Search by name or package ID..."
      class="input input-sm input-bordered bg-neutral-900 border-primary/30 focus:border-primary text-white flex-1 min-w-[200px]"
      :value="searchQuery"
      @input="$emit('update:searchQuery', $event.target.value)"
    />

    <select
      class="select select-sm select-bordered bg-neutral-900 border-primary/30 focus:border-primary text-white"
      :value="activeFilter"
      @change="$emit('update:activeFilter', $event.target.value)"
    >
      <option value="user">User Packages</option>
      <option value="system">System Packages</option>
      <option value="all">All Packages</option>
    </select>

    <select
      class="select select-sm select-bordered bg-neutral-900 border-primary/30 focus:border-primary text-white"
      :value="sortBy"
      @change="$emit('update:sortBy', $event.target.value)"
    >
      <option value="name">Sort by Name</option>
      <option value="package_id">Sort by Package ID</option>
      <option value="status">Sort by Status</option>
    </select>

    <label class="cursor-pointer flex items-center gap-1.5 text-xs">
      <input
        type="checkbox"
        class="checkbox checkbox-xs checkbox-primary"
        :checked="showRunningOnly"
        @change="$emit('update:showRunningOnly', $event.target.checked)"
      />
      <span class="text-slate-400">Running only</span>
    </label>

    <div class="flex gap-2 ml-auto">
      <button
        type="button"
        class="btn btn-sm btn-ghost text-slate-400 hover:text-white"
        :disabled="loading"
        @click="$emit('refresh')"
      >
        <svg
          class="w-4 h-4"
          :class="{ 'animate-spin': loading }"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
          />
        </svg>
        Refresh
      </button>

      <button
        type="button"
        class="btn btn-sm btn-accent"
        @click="$emit('show-help')"
      >
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        Help
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PackageControlBar',
  props: {
    searchQuery: {
      type: String,
      default: ''
    },
    sortBy: {
      type: String,
      default: 'name'
    },
    showRunningOnly: {
      type: Boolean,
      default: false
    },
    activeFilter: {
      type: String,
      default: 'user'
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: [
    'update:searchQuery',
    'update:sortBy',
    'update:showRunningOnly',
    'update:activeFilter',
    'refresh',
    'show-help'
  ]
}
</script>

