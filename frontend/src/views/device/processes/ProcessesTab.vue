<template>
  <div class="space-y-4">
    <div class="grid grid-cols-1 lg:grid-cols-5 gap-4">
      <div class="lg:col-span-3">
        <div class="card bg-neutral-900/60 backdrop-blur-sm shadow-xl border border-primary/20 h-full">
          <div class="card-body p-4 space-y-4">
            <ProcessControlBar
              :searchQuery="searchQuery"
              :filterType="filterType"
              :sortBy="sortBy"
              :showKernelThreads="showKernelThreads"
              @update:searchQuery="searchQuery = $event"
              @update:filterType="filterType = $event"
              @update:sortBy="sortBy = $event"
              @update:showKernelThreads="showKernelThreads = $event"
            />

            <div class="-mx-4 -mb-4">
              <ProcessTable
                :paginatedProcesses="paginatedProcesses"
                :startIndex="startIndex"
                :endIndex="endIndex"
                :totalCount="filteredProcesses.length"
                :currentPage="currentPage"
                :loading="loading"
                :focusedPid="expandedPid"
                @toggle-overview="handleToggleOverview"
                @page-change="currentPage = $event"
              />
            </div>
          </div>
        </div>
      </div>

      <div class="lg:col-span-2">
        <div class="sticky top-4 max-h-[calc(100vh-2rem)] overflow-y-auto space-y-4">
          <Transition
            enter-active-class="transition-all duration-300 ease-out"
            enter-from-class="opacity-0 translate-x-4 scale-95"
            enter-to-class="opacity-100 translate-x-0 scale-100"
            leave-active-class="transition-all duration-200 ease-in"
            leave-from-class="opacity-100 translate-x-0 scale-100"
            leave-to-class="opacity-0 translate-x-4 scale-95"
          >
            <ProcessOverviewPanel
              v-if="expandedPid"
              :data="overviewData"
              :loading="overviewLoading"
              :error="overviewError"
              :autoRefresh="overviewAutoRefresh"
              :refreshInterval="overviewRefreshInterval"
              :lastUpdate="overviewLastUpdate"
              :isCached="overviewIsCached"
              :isPrimary="overviewIsPrimary"
              :sessionRegistered="overviewSessionRegistered"
              @inspect-process="handleInspectProcess"
              @kill-process="handleKillProcess"
              @close="handleCloseOverview"
              @refresh="handleRefreshOverview"
              @toggle-auto-refresh="handleToggleOverviewAutoRefresh"
              @update-refresh-interval="handleUpdateOverviewInterval"
            />
          </Transition>

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
          :churnHistory="churnHistory"
          :loadingChurnHistory="loadingHistory"
          :autoRefresh="autoRefresh"
          :refreshInterval="refreshInterval"
          :lastUpdate="lastUpdate"
          :loading="loading"
          :processHistory="processHistory"
          :memoryHistory="memoryHistory"
          :isPrimary="isPrimary"
          @refresh="handleRefresh"
          @toggle-auto-refresh="toggleAutoRefresh"
          @update-refresh-interval="setRefreshInterval"
          @load-network-connections="loadNetworkConnections"
          @load-churn-history="fetchChurnHistory"
        />
        </div>
      </div>
    </div>

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
import { computed, watch } from 'vue'
import ProcessStatsBar from './components/ProcessStatsBar.vue'
import ProcessControlBar from './components/ProcessControlBar.vue'
import ProcessTable from './components/ProcessTable.vue'
import ProcessKillModal from './components/ProcessKillModal.vue'
import ProcessOverviewPanel from './components/ProcessOverviewPanel.vue'
import { useProcesses } from './composables/useProcesses'
import { useProcessFilters } from './composables/useProcessFilters'
import { useProcessActions } from './composables/useProcessActions'
import { useProcessOverview } from './composables/useProcessOverview'
import { useSystemMetrics } from './composables/useSystemMetrics'
import { useProcessChurn } from './composables/useProcessChurn'

export default {
  name: 'ProcessesTab',
  components: {
    ProcessStatsBar,
    ProcessControlBar,
    ProcessTable,
    ProcessKillModal,
    ProcessOverviewPanel
  },
  props: {
    device: {
      type: Object,
      required: true
    }
  },
  emits: ['update:isPrimary', 'update:sessionActive'],
  setup(props, { emit }) {
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
      churnHistory,
      loadingHistory,
      fetchProcessChurn,
      fetchChurnHistory
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
      setRefreshInterval,
      updateMemoryHistory,
      isPrimary,
      sessionRegistered
    } = useProcesses(props.device.serial, {
      extraFetchers: [
        async () => {
          await fetchSystemMetrics()
          const totalMb = memory.value.total_mb || 0
          const availableMb = memory.value.available_mb || memory.value.free_mb || 0
          const usedMb = Math.max(0, totalMb - availableMb)
          updateMemoryHistory(usedMb)
        },
        fetchProcessChurn
      ]
    })

    const {
      searchQuery,
      filterType,
      sortBy,
      showKernelThreads,
      currentPage,
      pageSize,
      filteredProcesses,
      paginatedProcesses,
      startIndex,
      endIndex
    } = useProcessFilters(processes)

    const {
      processToKill,
      showKillModal,
      killing,
      confirmKill,
      closeKillModal,
      killProcess
    } = useProcessActions(props.device.serial, fetchProcesses)

    const {
      expandedPid,
      overviewData,
      loading: overviewLoading,
      error: overviewError,
      lastUpdate: overviewLastUpdate,
      isCached: overviewIsCached,
      autoRefresh: overviewAutoRefresh,
      refreshInterval: overviewRefreshInterval,
      isPrimary: overviewIsPrimary,
      sessionRegistered: overviewSessionRegistered,
      toggleOverview,
      inspectProcess,
      closeOverview,
      forceRefreshOverview,
      toggleAutoRefresh: toggleOverviewAutoRefresh,
      setRefreshInterval: setOverviewRefreshInterval
    } = useProcessOverview(props.device.serial)

    const handleRefresh = async () => {
      await refreshAll()
    }

    const loadNetworkConnections = async () => {
      await fetchNetworkConnections()
    }

    const handleToggleOverview = (process) => {
      toggleOverview(process.pid)
    }

    const handleInspectProcess = (pid) => {
      inspectProcess(pid)
    }

    const handleKillProcess = (pid) => {
      const process = processes.value.find(p => p.pid === pid)
      if (process) {
        confirmKill(process)
      }
    }

    const handleCloseOverview = () => {
      closeOverview()
    }

    const handleRefreshOverview = () => {
      forceRefreshOverview()
    }

    const handleToggleOverviewAutoRefresh = () => {
      toggleOverviewAutoRefresh()
    }

    const handleUpdateOverviewInterval = (intervalMs) => {
      setOverviewRefreshInterval(intervalMs)
    }

    // Computed properties for combined primary status
    const isProcessesPrimary = computed(() => isPrimary.value)
    const isOverviewPrimary = computed(() => overviewIsPrimary.value)
    const isAnyPrimary = computed(() => isProcessesPrimary.value || isOverviewPrimary.value)
    const isAnySessionActive = computed(() => sessionRegistered.value || overviewSessionRegistered.value)

    // Emit primary status changes to parent
    watch(isAnyPrimary, (value) => {
      emit('update:isPrimary', value)
    }, { immediate: true })

    // Emit session active status to parent
    watch(isAnySessionActive, (value) => {
      emit('update:sessionActive', value)
    }, { immediate: true })

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
      isPrimary,
      sessionRegistered,
      cpu,
      memory,
      storage,
      partitions,
      network,
      networkConnections,
      networkConnectionsCount,
      churn,
      churnWindowSeconds,
      churnHistory,
      loadingHistory,
      fetchChurnHistory,
      searchQuery,
      filterType,
      sortBy,
      showKernelThreads,
      currentPage,
      pageSize,
      filteredProcesses,
      paginatedProcesses,
      startIndex,
      endIndex,
      processToKill,
      showKillModal,
      killing,
      closeKillModal,
      killProcess,
      expandedPid,
      overviewData,
      overviewLoading,
      overviewError,
      overviewLastUpdate,
      overviewIsCached,
      overviewAutoRefresh,
      overviewRefreshInterval,
      overviewIsPrimary,
      overviewSessionRegistered,
      handleRefresh,
      loadNetworkConnections,
      handleToggleOverview,
      handleInspectProcess,
      handleKillProcess,
      handleCloseOverview,
      handleRefreshOverview,
      handleToggleOverviewAutoRefresh,
      handleUpdateOverviewInterval
    }
  }
}
</script>
