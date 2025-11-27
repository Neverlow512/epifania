<template>
  <div class="card bg-neutral-900/60 backdrop-blur-sm shadow-xl border border-primary/20">
    <div class="card-body p-4">
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
      </div>
    </div>
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
      default: 'pid'
    }
  },
  emits: ['update:searchQuery', 'update:filterType', 'update:sortBy']
}
</script>

