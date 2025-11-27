<template>
  <div class="space-y-4">
    <ProcessStatsBar
      :stats="stats"
      :autoRefresh="autoRefresh"
      :refreshInterval="refreshInterval"
      :lastUpdate="lastUpdate"
      :loading="loading"
      @refresh="fetchProcesses"
      @toggle-auto-refresh="toggleAutoRefresh"
    />

    <ProcessControlBar
      :searchQuery="searchQuery"
      :filterType="filterType"
      :sortBy="sortBy"
      @update:searchQuery="searchQuery = $event"
      @update:filterType="filterType = $event"
      @update:sortBy="sortBy = $event"
    />

    <ProcessTable
      :paginatedProcesses="paginatedProcesses"
      :startIndex="startIndex"
      :endIndex="endIndex"
      :totalCount="filteredProcesses.length"
      :currentPage="currentPage"
      :loading="loading"
      @inspect="showProcessDetails"
      @kill="confirmKill"
      @page-change="currentPage = $event"
    />

    <ProcessDetailsModal
      :show="showDetailsModal"
      :process="selectedProcess"
      :details="processDetails"
      :loading="loadingDetails"
      @close="closeDetailsModal"
    />

    <ProcessKillModal
      :show="showKillModal"
      :process="processToKill"
      :killing="killing"
      @close="closeKillModal"
      @confirm="killProcess"
    />
  </div>
</template>

<script>
import ProcessStatsBar from './components/ProcessStatsBar.vue'
import ProcessControlBar from './components/ProcessControlBar.vue'
import ProcessTable from './components/ProcessTable.vue'
import ProcessDetailsModal from './components/ProcessDetailsModal.vue'
import ProcessKillModal from './components/ProcessKillModal.vue'
import { useProcesses } from './composables/useProcesses'
import { useProcessFilters } from './composables/useProcessFilters'
import { useProcessActions } from './composables/useProcessActions'

export default {
  name: 'ProcessesTab',
  components: {
    ProcessStatsBar,
    ProcessControlBar,
    ProcessTable,
    ProcessDetailsModal,
    ProcessKillModal
  },
  props: {
    device: {
      type: Object,
      required: true
    }
  },
  setup(props) {
    const {
      processes,
      stats,
      loading,
      lastUpdate,
      autoRefresh,
      refreshInterval,
      fetchProcesses,
      toggleAutoRefresh
    } = useProcesses(props.device.serial)

    const {
      searchQuery,
      filterType,
      sortBy,
      currentPage,
      pageSize,
      filteredProcesses,
      paginatedProcesses,
      startIndex,
      endIndex
    } = useProcessFilters(processes)

    const {
      selectedProcess,
      showDetailsModal,
      loadingDetails,
      processDetails,
      processToKill,
      showKillModal,
      killing,
      showProcessDetails,
      closeDetailsModal,
      confirmKill,
      closeKillModal,
      killProcess
    } = useProcessActions(props.device.serial, fetchProcesses)

    return {
      stats,
      loading,
      lastUpdate,
      autoRefresh,
      refreshInterval,
      fetchProcesses,
      toggleAutoRefresh,
      searchQuery,
      filterType,
      sortBy,
      currentPage,
      pageSize,
      filteredProcesses,
      paginatedProcesses,
      startIndex,
      endIndex,
      selectedProcess,
      showDetailsModal,
      loadingDetails,
      processDetails,
      processToKill,
      showKillModal,
      killing,
      showProcessDetails,
      closeDetailsModal,
      confirmKill,
      closeKillModal,
      killProcess
    }
  }
}
</script>

