<template>
  <div class="space-y-4">
    <div class="grid grid-cols-1 lg:grid-cols-5 gap-4">
      <!-- Left: processes widget (filters + table) -->
      <div class="lg:col-span-3">
        <div class="card bg-neutral-900/60 backdrop-blur-sm shadow-xl border border-primary/20 h-full">
          <div class="card-body p-4 space-y-4">
            <ProcessControlBar
              :searchQuery="searchQuery"
              :filterType="filterType"
              :sortBy="sortBy"
              @update:searchQuery="searchQuery = $event"
              @update:filterType="filterType = $event"
              @update:sortBy="sortBy = $event"
            />

            <div class="-mx-4 -mb-4">
              <ProcessTable
                :paginatedProcesses="paginatedProcesses"
                :startIndex="startIndex"
                :endIndex="endIndex"
                :totalCount="filteredProcesses.length"
                :currentPage="currentPage"
                :loading="loading"
                :focusedPid="selectedProcess ? selectedProcess.pid : null"
                @inspect="showProcessDetails"
                @kill="confirmKill"
                @page-change="currentPage = $event"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Right: compact stats / overview widget -->
      <div class="lg:col-span-2">
        <ProcessStatsBar
          :stats="stats"
          :cpu="cpu"
          :memoryMetrics="memory"
          :storageMetrics="storage"
          :storagePartitions="partitions"
          :networkMetrics="network"
          :networkConnections="networkConnections"
          :networkConnectionsCount="networkConnectionsCount"
          :churn="churn"
          :churnWindowSeconds="churnWindowSeconds"
          :autoRefresh="autoRefresh"
          :refreshInterval="refreshInterval"
          :lastUpdate="lastUpdate"
          :loading="loading"
          :processHistory="processHistory"
          :memoryHistory="memoryHistory"
          @refresh="handleRefresh"
          @toggle-auto-refresh="toggleAutoRefresh"
          @update-refresh-interval="setRefreshInterval"
          @load-network-connections="loadNetworkConnections"
        />
      </div>
    </div>

    <ProcessDetailsModal
      :show="showDetailsModal"
      :process="selectedProcess"
      :details="processDetails"
      :memoryDetails="processMemoryDetails"
      :networkDetails="processNetworkDetails"
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
import { useSystemMetrics } from './composables/useSystemMetrics'
import { useProcessChurn } from './composables/useProcessChurn'

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
      cpu,
      memory,
      storage,
      partitions,
      network,
      networkConnections,
      networkConnectionsCount,
      fetchSystemMetrics,
      fetchNetworkConnections
    } = useSystemMetrics(props.device.serial)

    const {
      churn,
      churnWindowSeconds,
      fetchProcessChurn
    } = useProcessChurn(props.device.serial)

    const {
      processes,
      stats,
      loading,
      lastUpdate,
      autoRefresh,
      refreshInterval,
      fetchProcesses,
      refreshAll,
      toggleAutoRefresh,
      processHistory,
      memoryHistory,
      setRefreshInterval
    } = useProcesses(props.device.serial, {
      extraFetchers: [fetchSystemMetrics, fetchProcessChurn]
    })

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
      processMemoryDetails,
      processNetworkDetails,
      processToKill,
      showKillModal,
      killing,
      showProcessDetails,
      closeDetailsModal,
      confirmKill,
      closeKillModal,
      killProcess
    } = useProcessActions(props.device.serial, fetchProcesses)

    const handleRefresh = async () => {
      await refreshAll()
    }

    const loadNetworkConnections = async () => {
      await fetchNetworkConnections()
    }

    return {
      stats,
      loading,
      lastUpdate,
      autoRefresh,
      refreshInterval,
      fetchProcesses,
      toggleAutoRefresh,
      processHistory,
      memoryHistory,
      setRefreshInterval,
      cpu,
      memory,
      storage,
      partitions,
      network,
      networkConnections,
      networkConnectionsCount,
      churn,
      churnWindowSeconds,
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
      processMemoryDetails,
      processNetworkDetails,
      processToKill,
      showKillModal,
      killing,
      showProcessDetails,
      closeDetailsModal,
      confirmKill,
      closeKillModal,
      killProcess,
      handleRefresh,
      loadNetworkConnections
    }
  }
}
</script>

