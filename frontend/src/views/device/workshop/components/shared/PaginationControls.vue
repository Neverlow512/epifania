<template>
  <div class="flex items-center justify-between mt-4">
    <span class="text-sm text-slate-400">
      Showing {{ hasItems ? startIndex + 1 : 0 }}-{{ Math.min(endIndex, totalItems) }} of {{ totalItems }}
    </span>
    
    <div class="btn-group">
      <button 
        type="button"
        class="btn btn-sm"
        :disabled="currentPage === 1 || !hasItems"
        @click="$emit('prev-page')"
      >
        Prev
      </button>
      <span class="btn btn-sm btn-ghost">
        {{ currentPage }} / {{ displayPages }}
      </span>
      <button 
        type="button"
        class="btn btn-sm"
        :disabled="currentPage >= displayPages || !hasItems"
        @click="$emit('next-page')"
      >
        Next
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PaginationControls',
  props: {
    currentPage: {
      type: Number,
      required: true
    },
    totalPages: {
      type: Number,
      required: true
    },
    itemsPerPage: {
      type: Number,
      required: true
    },
    totalItems: {
      type: Number,
      required: true
    }
  },
  emits: ['prev-page', 'next-page'],
  computed: {
    startIndex() {
      return (this.currentPage - 1) * this.itemsPerPage
    },
    endIndex() {
      return this.startIndex + this.itemsPerPage
    },
    displayPages() {
      return this.totalPages || 1
    },
    hasItems() {
      return this.totalItems > 0
    }
  }
}
</script>

