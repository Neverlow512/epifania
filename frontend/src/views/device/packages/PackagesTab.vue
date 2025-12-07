<template>
  <div class="space-y-4">
    <div class="grid grid-cols-1 lg:grid-cols-5 gap-4">
      <div class="lg:col-span-3">
        <div class="card bg-neutral-900/60 backdrop-blur-sm shadow-xl border border-primary/20 h-full">
          <div class="card-body p-4 space-y-4">
            <PackageControlBar
              :searchQuery="searchQuery"
              :sortBy="sortBy"
              :showRunningOnly="showRunningOnly"
              :activeFilter="activeFilter"
              :loading="loading"
              @update:searchQuery="setSearch"
              @update:sortBy="setSort"
              @update:showRunningOnly="toggleRunningOnly"
              @update:activeFilter="setFilter"
              @refresh="refreshPackages"
              @show-help="showHelpModal = true"
            />

            <div class="-mx-4 -mb-4">
              <PackageTable
                :packages="paginatedPackages"
                :startIndex="startIndex"
                :endIndex="endIndex"
                :totalCount="filteredPackages.length"
                :currentPage="currentPage"
                :loading="loading"
                :actionInProgress="actionInProgress"
                @page-change="currentPage = $event"
                @view-details="handleViewDetails"
                @launch="handleLaunch"
                @stop="handleStop"
                @uninstall="handleUninstallRequest"
                @pull="handlePullRequest"
                @clear-cache="handleClearCache"
                @clear-data="handleClearDataRequest"
                @navigate-to-process="navigateToProcess"
              />
            </div>
          </div>
        </div>
      </div>

      <div class="lg:col-span-2">
        <div class="sticky top-4 max-h-[calc(100vh-2rem)] overflow-y-auto space-y-4">
          <PackageStatsBar
            :stats="stats"
            :lastUpdate="lastUpdate"
            :loading="loading"
            :activeFilter="activeFilter"
            :hasActiveFilters="hasActiveFilters"
            @refresh="refreshPackages"
            @clear-filters="clearFilters"
            @install="showInstallModal = true"
          />
        </div>
      </div>
    </div>

    <PackageDetailsModal
      :show="showDetailsModal"
      :packageData="currentPackage"
      :loading="detailsLoading"
      :error="detailsError"
      :actionInProgress="actionInProgress"
      @close="closeDetailsModal"
      @launch="handleLaunch"
      @stop="handleStop"
      @uninstall="handleUninstallRequest"
      @pull="handlePullRequest"
      @clear-cache="handleClearCache"
      @clear-data="handleClearDataRequest"
      @navigate-to-process="navigateToProcess"
    />

    <PackageInstallModal
      :show="showInstallModal"
      :installing="actionInProgress && actionType === 'install'"
      :deviceTempPath="deviceTempPath"
      :recentPaths="recentInstallPaths"
      :deviceSerial="device.serial"
      @close="showInstallModal = false"
      @install="handleInstall"
    />

    <PackageUninstallModal
      :show="showUninstallModal"
      :package="packageToUninstall"
      :uninstalling="actionInProgress && actionType === 'uninstall'"
      @close="closeUninstallModal"
      @confirm="handleUninstall"
    />

    <PackagePullModal
      :show="showPullModal"
      :package="packageToPull"
      :pulling="actionInProgress && actionType === 'pull'"
      :defaultPath="pullDefaultPath"
      :recentPaths="recentExtractPaths"
      @close="closePullModal"
      @confirm="handlePull"
    />

    <PackageClearDataModal
      :show="showClearDataModal"
      :package="packageToClearData"
      :clearing="actionInProgress && actionType === 'clear-data'"
      @close="closeClearDataModal"
      @confirm="handleClearData"
    />

    <PackageHelpModal
      :show="showHelpModal"
      @close="showHelpModal = false"
    />
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import PackageControlBar from './components/PackageControlBar.vue'
import PackageTable from './components/PackageTable.vue'
import PackageStatsBar from './components/PackageStatsBar.vue'
import PackageDetailsModal from './components/PackageDetailsModal.vue'
import PackageInstallModal from './components/PackageInstallModal.vue'
import PackageUninstallModal from './components/PackageUninstallModal.vue'
import PackagePullModal from './components/PackagePullModal.vue'
import PackageClearDataModal from './components/PackageClearDataModal.vue'
import PackageHelpModal from './components/PackageHelpModal.vue'
import { usePackages } from './composables/usePackages'
import { usePackageFilters } from './composables/usePackageFilters'
import { usePackageDetails } from './composables/usePackageDetails'
import { usePackageActions } from './composables/usePackageActions'
import { usePackagePaths } from './composables/usePackagePaths'
import { usePackagePollingSession } from './composables/usePackagePollingSession'

export default {
  name: 'PackagesTab',
  components: {
    PackageControlBar,
    PackageTable,
    PackageStatsBar,
    PackageDetailsModal,
    PackageInstallModal,
    PackageUninstallModal,
    PackagePullModal,
    PackageClearDataModal,
    PackageHelpModal
  },
  props: {
    device: {
      type: Object,
      required: true
    }
  },
  emits: ['update:packagesPrimary'],
  setup(props, { emit }) {
    const router = useRouter()

    const { isPrimary, sessionRegistered } = usePackagePollingSession(props.device.serial)

    watch(isPrimary, (value) => {
      emit('update:packagesPrimary', value)
    }, { immediate: true })

    const {
      packages,
      stats,
      loading,
      lastUpdate,
      activeFilter,
      fetchPackages,
      refreshPackages,
      setFilter
    } = usePackages(props.device.serial)

    const {
      searchQuery,
      sortBy,
      showRunningOnly,
      currentPage,
      filteredPackages,
      paginatedPackages,
      startIndex,
      endIndex,
      hasActiveFilters,
      setSearch,
      setSort,
      toggleRunningOnly,
      clearFilters
    } = usePackageFilters(packages)

    const {
      loading: detailsLoading,
      currentPackage,
      error: detailsError,
      fetchDetails,
      clearDetails,
      closeDetails
    } = usePackageDetails(props.device.serial)

    const {
      actionInProgress,
      actionType,
      launchPackage,
      stopPackage,
      installPackage,
      uninstallPackage,
      pullPackage,
      clearCache,
      clearData
    } = usePackageActions(props.device.serial, refreshPackages, clearDetails, isPrimary)

    const {
      deviceTempPath,
      recentInstallPaths,
      recentExtractPaths,
      getExtractPath,
      addRecentInstallPath,
      addRecentExtractPath,
      confirmUninstall,
      confirmClearData
    } = usePackagePaths()

    const showDetailsModal = ref(false)
    const showInstallModal = ref(false)
    const showUninstallModal = ref(false)
    const showPullModal = ref(false)
    const showClearDataModal = ref(false)
    const showHelpModal = ref(false)

    const packageToUninstall = ref(null)
    const packageToPull = ref(null)
    const packageToClearData = ref(null)

    const pullDefaultPath = computed(() => {
      if (packageToPull.value) {
        return getExtractPath(packageToPull.value.package_id)
      }
      return ''
    })

    const handleViewDetails = async (pkg) => {
      showDetailsModal.value = true
      await fetchDetails(pkg.package_id)
    }

    const closeDetailsModal = () => {
      showDetailsModal.value = false
      closeDetails()
    }

    const handleLaunch = async (pkg) => {
      await launchPackage(pkg.package_id)
    }

    const handleStop = async (pkg) => {
      await stopPackage(pkg.package_id)
    }

    const handleUninstallRequest = (pkg) => {
      if (confirmUninstall.value) {
        packageToUninstall.value = pkg
        showUninstallModal.value = true
      } else {
        handleUninstall(pkg.package_id, false)
      }
    }

    const closeUninstallModal = () => {
      showUninstallModal.value = false
      packageToUninstall.value = null
    }

    const handleUninstall = async (packageId, keepData) => {
      const result = await uninstallPackage(packageId, keepData)
      if (result.success) {
        closeUninstallModal()
        if (showDetailsModal.value && currentPackage.value?.package_id === packageId) {
          closeDetailsModal()
        }
      }
    }

    const handlePullRequest = (pkg) => {
      packageToPull.value = pkg
      showPullModal.value = true
    }

    const closePullModal = () => {
      showPullModal.value = false
      packageToPull.value = null
    }

    const handlePull = async (packageId, destinationPath) => {
      const result = await pullPackage(packageId, destinationPath)
      if (result.success) {
        addRecentExtractPath(destinationPath)
        closePullModal()
      }
    }

    const handleClearCache = async (pkg) => {
      await clearCache(pkg.package_id)
    }

    const handleClearDataRequest = (pkg) => {
      if (confirmClearData.value) {
        packageToClearData.value = pkg
        showClearDataModal.value = true
      } else {
        handleClearData(pkg.package_id)
      }
    }

    const closeClearDataModal = () => {
      showClearDataModal.value = false
      packageToClearData.value = null
    }

    const handleClearData = async (packageId) => {
      const result = await clearData(packageId)
      if (result.success) {
        closeClearDataModal()
      }
    }

    const handleInstall = async (apkSource, isLocalFile, tempPath) => {
      const result = await installPackage(apkSource, isLocalFile, tempPath)
      if (result.success) {
        if (isLocalFile) {
          addRecentInstallPath(apkSource)
        }
        showInstallModal.value = false
      }
    }

    const navigateToProcess = (pid) => {
      router.push({
        path: `/device/${props.device.serial}`,
        query: { tab: 'processes', highlight: pid }
      })
    }

    onMounted(() => {
      fetchPackages('user')
    })

    return {
      isPrimary,
      packages,
      stats,
      loading,
      lastUpdate,
      activeFilter,
      refreshPackages,
      setFilter,
      searchQuery,
      sortBy,
      showRunningOnly,
      currentPage,
      filteredPackages,
      paginatedPackages,
      startIndex,
      endIndex,
      hasActiveFilters,
      setSearch,
      setSort,
      toggleRunningOnly,
      clearFilters,
      detailsLoading,
      currentPackage,
      detailsError,
      actionInProgress,
      actionType,
      deviceTempPath,
      recentInstallPaths,
      recentExtractPaths,
      showDetailsModal,
      showInstallModal,
      showUninstallModal,
      showPullModal,
      showClearDataModal,
      showHelpModal,
      packageToUninstall,
      packageToPull,
      packageToClearData,
      pullDefaultPath,
      handleViewDetails,
      closeDetailsModal,
      handleLaunch,
      handleStop,
      handleUninstallRequest,
      closeUninstallModal,
      handleUninstall,
      handlePullRequest,
      closePullModal,
      handlePull,
      handleClearCache,
      handleClearDataRequest,
      closeClearDataModal,
      handleClearData,
      handleInstall,
      navigateToProcess
    }
  }
}
</script>
