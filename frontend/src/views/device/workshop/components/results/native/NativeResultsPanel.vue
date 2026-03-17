<template>
  <div class="space-y-4">
    <ResultsToolbar
      :searchQuery="searchQuery"
      :categoryFilter="categoryFilter"
      :sourceFilter="sourceFilter"
      :itemsPerPage="itemsPerPage"
      @update:searchQuery="updateSearch"
      @update:categoryFilter="categoryFilter = $event"
      @update:sourceFilter="sourceFilter = $event"
      @update:itemsPerPage="itemsPerPage = $event"
    />
    
    <div v-if="filteredModules.length === 0">
      <EmptyState
        title="No Modules Found"
        message="No native modules match the current filters. Try adjusting your search or filter criteria."
      />
    </div>
    
    <ModuleExportTable
      v-else
      :modules="paginatedModules"
      :expandedModules="expandedModules"
      @toggle-expand="toggleModuleExpansion"
    />
    
    <PaginationControls
      v-if="filteredModules.length > 0"
      :currentPage="currentPage"
      :totalPages="totalPages"
      :itemsPerPage="itemsPerPage"
      :totalItems="filteredModules.length"
      @prev-page="prevPage"
      @next-page="nextPage"
    />
  </div>
</template>

<script>
import { computed } from 'vue'
import ResultsToolbar from '../ResultsToolbar.vue'
import ModuleExportTable from './ModuleExportTable.vue'
import EmptyState from '../../shared/EmptyState.vue'
import PaginationControls from '../../shared/PaginationControls.vue'
import { useNativeFilters } from '../../../composables/useNativeFilters'

export default {
  name: 'NativeResultsPanel',
  components: {
    ResultsToolbar,
    ModuleExportTable,
    EmptyState,
    PaginationControls
  },
  props: {
    modules: {
      type: Array,
      required: true
    }
  },
  setup(props) {
    const modulesRef = computed(() => props.modules)
    
    const {
      searchQuery,
      categoryFilter,
      sourceFilter,
      expandedModules,
      currentPage,
      itemsPerPage,
      filteredModules,
      paginatedModules,
      totalPages,
      updateSearch,
      toggleModuleExpansion,
      nextPage,
      prevPage
    } = useNativeFilters(modulesRef)
    
    return {
      searchQuery,
      categoryFilter,
      sourceFilter,
      expandedModules,
      currentPage,
      itemsPerPage,
      filteredModules,
      paginatedModules,
      totalPages,
      updateSearch,
      toggleModuleExpansion,
      nextPage,
      prevPage
    }
  }
}
</script>

