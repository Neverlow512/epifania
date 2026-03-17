<template>
  <div class="space-y-4">
    <ResultsToolbar
      :searchQuery="searchQuery"
      :categoryFilter="categoryFilter"
      :sourceFilter="sourceFilter"
      :itemsPerPage="itemsPerPage"
      :selectedCount="selectedCount"
      :filterMode="filterMode"
      :workshopMode="workshopMode"
      :hasSelection="hasSelection"
      :selectedScanTypes="selectedScanTypes"
      @update:searchQuery="updateSearch"
      @update:categoryFilter="categoryFilter = $event"
      @update:sourceFilter="sourceFilter = $event"
      @update:itemsPerPage="itemsPerPage = $event"
      @select-page="handleSelectPage"
      @select-all="handleSelectAll"
      @deselect-all="handleDeselectAll"
      @scan-classloader="$emit('scan-classloader')"
      @open-scan-modal="$emit('open-scan-modal')"
      @remove-scan-type="$emit('remove-scan-type', $event)"
      @clear-scan-types="$emit('clear-scan-types')"
      @scan-modifiers="$emit('scan-modifiers')"
      @extract-methods="$emit('extract-methods')"
    />
    
    <div v-if="filteredClasses.length === 0">
      <EmptyState
        :title="emptyTitle"
        :message="emptyMessage"
      />
    </div>
    
    <ClassMethodTable
      v-else
      :classes="paginatedClasses"
      :expandedClasses="expandedClasses"
      :selectedClasses="selectedClasses"
      :showSelection="showSelection"
      :workshopMode="workshopMode"
      :showScanButton="filterMode !== 'package'"
      :classStates="classStates"
      :selectedMethods="selectedMethods"
      :methodSelectionEnabled="methodSelectionEnabled"
      @toggle-expand="toggleClassExpansion"
      @toggle-select="handleToggleSelect"
      @method-click="handleMethodClick"
      @scan-class="handleScanClass"
      @extract-class="handleExtractClass"
      @toggle-select-method="$emit('toggle-select-method', $event)"
    />
    
    <PaginationControls
      v-if="filteredClasses.length > 0"
      :currentPage="currentPage"
      :totalPages="totalPages"
      :itemsPerPage="itemsPerPage"
      :totalItems="filteredClasses.length"
      @prev-page="prevPage"
      @next-page="nextPage"
    />
    
    <MethodDetailModal
      :show="showMethodModal"
      :method="selectedMethod"
      :className="selectedClassName"
      @close="showMethodModal = false"
    />
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import ResultsToolbar from '../ResultsToolbar.vue'
import ClassMethodTable from './ClassMethodTable.vue'
import EmptyState from '../../shared/EmptyState.vue'
import PaginationControls from '../../shared/PaginationControls.vue'
import MethodDetailModal from '../../modals/MethodDetailModal.vue'
import { useJavaFilters } from '../../../composables/useJavaFilters'

export default {
  name: 'JavaResultsPanel',
  components: {
    ResultsToolbar,
    ClassMethodTable,
    EmptyState,
    PaginationControls,
    MethodDetailModal
  },
  props: {
    classes: {
      type: Array,
      required: true
    },
    selectedClasses: {
      type: Set,
      default: () => new Set()
    },
    classStates: {
      type: Map,
      default: () => new Map()
    },
    filterMode: {
      type: String,
      default: 'focused'
    },
    workshopMode: {
      type: String,
      default: 'analysis'
    },
    showSelection: {
      type: Boolean,
      default: true
    },
    selectedScanTypes: {
      type: Array,
      default: () => []
    },
    classModifierFilters: {
      type: Array,
      default: () => []
    },
    methodModifierFilters: {
      type: Array,
      default: () => []
    },
    selectedMethods: {
      type: Map,
      default: () => new Map()
    },
    methodSelectionEnabled: {
      type: Boolean,
      default: false
    }
  },
  emits: [
    'toggle-select',
    'select-page',
    'select-all',
    'deselect-all',
    'scan-classloader',
    'open-scan-modal',
    'remove-scan-type',
    'clear-scan-types',
    'scan-modifiers',
    'extract-methods',
    'scan-class',
    'extract-class',
    'toggle-select-method'
  ],
  setup(props, { emit }) {
    const classesRef = computed(() => props.classes)
    const classModifierFiltersRef = computed(() => props.classModifierFilters)
    const methodModifierFiltersRef = computed(() => props.methodModifierFilters)
    const classStatesRef = computed(() => props.classStates)
    
    const {
      searchQuery,
      categoryFilter,
      sourceFilter,
      expandedClasses,
      currentPage,
      itemsPerPage,
      filteredClasses,
      paginatedClasses,
      totalPages,
      updateSearch,
      toggleClassExpansion,
      nextPage,
      prevPage
    } = useJavaFilters(classesRef, classModifierFiltersRef, methodModifierFiltersRef, classStatesRef)
    
    const showMethodModal = ref(false)
    const selectedMethod = ref({})
    const selectedClassName = ref('')
    
    const selectedCount = computed(() => props.selectedClasses.size)
    const hasSelection = computed(() => props.selectedClasses.size > 0)
    
    const emptyTitle = computed(() => {
      if (props.filterMode === 'package' && props.classes.length === 0) {
        return 'No APK Classes Scanned'
      }
      return 'No Classes Found'
    })
    
    const emptyMessage = computed(() => {
      if (props.filterMode === 'package' && props.classes.length === 0) {
        return 'No classes have been scanned yet. Switch to Focused or All mode to scan ClassLoader for classes.'
      }
      return 'No Java classes match the current filters. Try adjusting your search or filter criteria.'
    })
    
    const handleMethodClick = ({ method, className }) => {
      selectedMethod.value = method
      selectedClassName.value = className
      showMethodModal.value = true
    }
    
    const handleToggleSelect = (className) => {
      emit('toggle-select', className)
    }
    
    const handleSelectPage = () => {
      const pageClassNames = paginatedClasses.value.map(c => c.name)
      emit('select-page', pageClassNames)
    }
    
    const handleSelectAll = () => {
      const allClassNames = filteredClasses.value.map(c => c.name)
      emit('select-all', allClassNames)
    }
    
    const handleDeselectAll = () => {
      emit('deselect-all')
    }
    
    const handleScanClass = (className) => {
      emit('scan-class', className)
    }
    
    const handleExtractClass = (className) => {
      emit('extract-class', className)
    }
    
    return {
      searchQuery,
      categoryFilter,
      sourceFilter,
      expandedClasses,
      currentPage,
      itemsPerPage,
      filteredClasses,
      paginatedClasses,
      totalPages,
      updateSearch,
      toggleClassExpansion,
      nextPage,
      prevPage,
      showMethodModal,
      selectedMethod,
      selectedClassName,
      handleMethodClick,
      selectedCount,
      hasSelection,
      emptyTitle,
      emptyMessage,
      handleToggleSelect,
      handleSelectPage,
      handleSelectAll,
      handleDeselectAll,
      handleScanClass,
      handleExtractClass
    }
  }
}
</script>
