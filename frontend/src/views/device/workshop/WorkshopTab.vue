<template>
  <div class="space-y-4" :class="{ 'pb-[360px]': isObserving }">
    <div class="grid grid-cols-1 lg:grid-cols-4 gap-4">
      <!-- Left: Control Panel (1 col) -->
      <div class="lg:col-span-1">
        <WorkshopControlPanel
          :device="device"
          :hasLock="hasLock"
          :sessionMessage="sessionMessage"
          :fridaServerRunning="device.frida_server_running"
          :fridaServerVersion="device.frida_server_version"
          :fridaConnected="fridaConnected"
          :fridaAttached="fridaAttached"
          :attachedPid="attachedPid"
          :sessionNumber="fridaSessionNumber"
          :fridaStatusMessage="fridaStatusMessage"
          :fridaCrashed="fridaCrashed"
          :selectedProcess="selectedProcess"
          :filterMode="filterMode"
          :discoveryState="discoveryState"
          :discoveryProgress="discoveryProgress"
          :discoveryPhase="discoveryPhase"
          :discoveryMessage="discoveryMessage"
          :stats="stats"
          :spawnModeEnabled="spawnModeEnabled"
          :selectedSpawnPackage="selectedSpawnPackage"
          :spawnDelay="spawnDelay"
          :selectedMethodCount="selectedMethodCount"
          :isObserving="isObserving"
          :observerSessionName="observerSessionName"
          :observerTimeLimit="observerTimeLimit"
          :observerSessionPath="observerSessionPath"
          :methodSelectionEnabled="methodSelectionEnabled"
          @update:selectedProcess="selectedProcess = $event"
          @update:filterMode="filterMode = $event"
          @start-discovery="startDiscovery"
          @cancel-discovery="cancelDiscovery"
          @save-discovery="showSaveModal = true"
          @clear-results="clearResults"
          @view-logs="showLogsModal = true"
          @start-frida="$emit('start-frida')"
          @stop-frida="$emit('stop-frida')"
          @restart-frida="$emit('restart-frida')"
          @attach-frida="handleAttachFrida"
          @detach-frida="handleDetachFrida"
          @spawn-frida="handleSpawnFrida"
          @update:spawnMode="spawnModeEnabled = $event"
          @update:spawnPackage="selectedSpawnPackage = $event"
          @update:spawnDelay="spawnDelay = $event"
          @update:mode="workshopMode = $event"
          @open-app-focused-config="showAppFocusedConfigModal = true"
          @observer-start="handleObserverStart"
          @observer-stop="handleObserverStop"
          @toggle-method-selection="handleToggleMethodSelection"
          @update:observerSessionName="observerSessionName = $event"
          @update:observerTimeLimit="observerTimeLimit = $event"
          @update:observerSessionPath="observerSessionPath = $event"
          @open-dashboard="showToolkitDashboard = true"
        />
      </div>
      
      <!-- Right: Results (3 cols) -->
      <div class="lg:col-span-3">
        <ResultsPanel
          :activeTab="resultsTab"
          :discoveryData="discoveryData"
          :loading="discoveryState === 'running'"
          :deviceSerial="device.serial"
          :selectedClasses="selectedClasses"
          :classStates="classStates"
          :filterMode="filterMode"
          :workshopMode="workshopMode"
          :showSelection="hasDiscoveryData"
          :appFocusedPatterns="appFocusedPatterns"
          :packageId="selectedProcess?.package_id || discoveryData?.metadata?.package_id || ''"
          :selectedScanTypes="selectedScanTypes"
          :stats="stats"
          :selectedMethods="selectedMethods"
          :methodSelectionEnabled="methodSelectionEnabled"
          @update:activeTab="resultsTab = $event"
          @discovery-loaded="handleDiscoveryLoaded"
          @toggle-select="toggleClass"
          @select-page="selectClasses"
          @select-all="selectClasses"
          @deselect-all="deselectAll"
          @scan-classloader="handleScanClassLoader"
          @open-scan-modal="handleOpenScanModal"
          @remove-scan-type="handleRemoveScanType"
          @clear-scan-types="handleClearScanTypes"
          @scan-modifiers="handleScanModifiers"
          @extract-methods="handleExtractMethods"
          @toggle-select-method="handleToggleSelectMethod"
        />
      </div>
    </div>

    <!-- Session Locked Modal -->
    <SessionLockedModal
      :show="showLockedModal"
      :lockOwner="lockOwner"
      :expiresIn="expiresIn"
      @close="showLockedModal = false"
      @retry="retryAcquireLock"
    />

    <!-- Save Discovery Modal -->
    <SaveDiscoveryModal
      :show="showSaveModal"
      :metadata="discoveryData?.metadata"
      :saving="saving"
      @close="showSaveModal = false"
      @save="handleSaveDiscovery"
    />

    <!-- Clear Discovery Warning Modal -->
    <ClearDiscoveryModal
      :show="showClearModal"
      :packageId="discoveryData?.metadata?.package_id"
      :stats="stats"
      @cancel="showClearModal = false"
      @confirm="confirmClearResults"
    />

    <!-- Discovery Logs Modal -->
    <DiscoveryLogsModal
      :show="showLogsModal"
      :deviceSerial="device.serial"
      :packageId="currentPackageId"
      :timestamp="currentTimestamp"
      :clientId="clientId"
      :isLive="discoveryState === 'running'"
      :stats="discoveryData?.metadata?.stats"
      :defaultMode="logsDefaultMode"
      @close="showLogsModal = false"
    />

    <!-- TODO: TEMPORARY FALLBACK - Remove once backend temp persistence is implemented -->
    <FallbackSaveModal
      :show="showFallbackSaveModal"
      :packageId="discoveryData?.metadata?.package_id"
      :stats="stats"
      :saving="saving"
      @cancel="cancelFallbackSave"
      @confirm="handleFallbackSave"
    />

    <!-- App Focused Configuration Modal -->
    <AppFocusedConfigModal
      :show="showAppFocusedConfigModal"
      :packageId="selectedProcess?.package_id || ''"
      @close="showAppFocusedConfigModal = false"
      @saved="handleAppFocusedConfigSaved"
    />

    <!-- Operation Progress Modal -->
    <OperationProgressModal
      :show="showProgressModal"
      :title="progressTitle"
      :current="operationProgressTracker?.current.value || 0"
      :total="operationProgressTracker?.total.value || 0"
      :currentItem="operationProgressTracker?.currentItem.value || ''"
      :cancelled="operationProgressTracker?.cancelled.value || false"
      @cancel="handleCancelOperation"
    />

    <!-- Recovery Modal (Phase 3) -->
    <RecoveryModal
      v-if="showRecoveryModal"
      :recoveryInfo="recoveryInfo"
      @recover="handleRecoverState"
      @discard="handleDiscardRecovery"
      @cancel="showRecoveryModal = false"
    />

    <!-- Conflict Modal (Phase 3) -->
    <ConflictModal
      v-if="showConflictModal"
      :unsavedStats="getUnsavedStats()"
      @save="handleConflictSave"
      @discard="handleConflictDiscard"
      @cancel="handleConflictCancel"
    />
    
    <!-- Scan Selection Modal -->
    <ScanSelectionModal
      :show="showScanSelectionModal"
      :selectedTypes="selectedScanTypes.map(t => t.id)"
      @close="showScanSelectionModal = false"
      @confirm="handleScanSelectionConfirm"
    />
    
    <!-- Session Lost Modal -->
    <SessionLostModal
      :show="showSessionLostModal"
      :data="sessionLostModalData"
      @close="handleSessionLostClose"
      @view-logs="handleSessionLostViewLogs"
    />
    
    <!-- Exit Warning Modal -->
    <ExitWarningModal
      :show="showExitWarningModal"
      :pid="attachedPid"
      :unsavedCount="unsavedClassCount"
      @confirm="handleExitConfirm"
      @cancel="handleExitCancel"
    />
    
    <!-- Observer Stats Panel -->
    <ObserverStatsPanel
      :deviceSerial="device.serial"
      :isObserving="isObserving"
      :clientId="clientId"
      :showDashboard="showToolkitDashboard"
      @close="showToolkitDashboard = false"
    />
  </div>
</template>

<script>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { onBeforeRouteLeave } from 'vue-router'
import axios from 'axios'
import WorkshopControlPanel from './components/control/WorkshopControlPanel.vue'
import ResultsPanel from './components/results/ResultsPanel.vue'
import SessionLockedModal from './components/modals/SessionLockedModal.vue'
import SaveDiscoveryModal from './components/modals/SaveDiscoveryModal.vue'
import ClearDiscoveryModal, { shouldShowClearWarning } from './components/modals/ClearDiscoveryModal.vue'
import DiscoveryLogsModal from './components/modals/DiscoveryLogsModal.vue'
import FallbackSaveModal from './components/modals/FallbackSaveModal.vue'
import AppFocusedConfigModal from './components/modals/AppFocusedConfigModal.vue'
import OperationProgressModal from './components/modals/OperationProgressModal.vue'
import RecoveryModal from './components/modals/RecoveryModal.vue'
import ConflictModal from './components/modals/ConflictModal.vue'
import ScanSelectionModal from './components/modals/ScanSelectionModal.vue'
import SessionLostModal from './components/modals/SessionLostModal.vue'
import ExitWarningModal from './components/modals/ExitWarningModal.vue'
import ObserverStatsPanel from './components/instrumentation/toolkit/tools/observer/ObserverStatsPanel.vue'
import { useWorkshopSession } from './composables/useWorkshopSession'
import { useWorkshopDiscovery } from './composables/useWorkshopDiscovery'
import { useDiscoveryResults } from './composables/useDiscoveryResults'
import { useSavedDiscoveries } from './composables/useSavedDiscoveries'
import { useInstallMarkers } from './composables/useInstallMarkers'
import { useClassSelection } from './composables/useClassSelection'
import { useClassOperations } from './composables/useClassOperations'
import { useModifierOperations } from './composables/useModifierOperations'
import { useOperationProgress } from './composables/useOperationProgress'
import { useAppFocusedConfig } from './composables/useAppFocusedConfig'
import { useTempState } from './composables/useTempState'
import { useMethodSelection } from './composables/useMethodSelection'
import { useObserver } from './composables/useObserver'
import { useToast } from '../../../composables/useToast'

export default {
  name: 'WorkshopTab',
  components: {
    WorkshopControlPanel,
    ResultsPanel,
    SessionLockedModal,
    SaveDiscoveryModal,
    ClearDiscoveryModal,
    DiscoveryLogsModal,
    FallbackSaveModal,
    AppFocusedConfigModal,
    OperationProgressModal,
    RecoveryModal,
    ConflictModal,
    ScanSelectionModal,
    SessionLostModal,
    ExitWarningModal,
    ObserverStatsPanel
  },
  props: {
    device: {
      type: Object,
      required: true
    },
    fridaConnected: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:workshopSessionActive', 'start-frida', 'stop-frida', 'restart-frida'],
  setup(props, { emit }) {
    const toast = useToast()
    
    const {
      clientId,
      hasLock,
      lockOwner,
      expiresIn,
      sessionMessage,
      acquireLock
    } = useWorkshopSession(props.device.serial)
    
    const {
      discoveryState,
      discoveryProgress,
      discoveryPhase,
      discoveryMessage,
      discoveryId,
      startDiscovery: startDiscoveryFn,
      cancelDiscovery: cancelDiscoveryFn,
      clearDiscovery: clearDiscoveryFn,
      discoveryResult
    } = useWorkshopDiscovery(props.device.serial, clientId)
    
    const {
      discoveryData,
      stats,
      classStates,
      loadDiscoveryData,
      clearDiscoveryData,
      updateClassState,
      updateClassStatesFromScan,
      updateClassStatesFromExtract
    } = useDiscoveryResults()
    
    const {
      saveDiscovery,
      saveDiscoveryFromFrontend,
      checkBackendHasResult,
      saving
    } = useSavedDiscoveries(props.device.serial, clientId)
    
    const {
      fetchInstallMarkers
    } = useInstallMarkers(props.device.serial)
    
    const {
      selectedClasses,
      selectedCount,
      toggleClass,
      selectClasses,
      deselectAll,
      getSelectedArray
    } = useClassSelection()
    
    const {
      scanClassLoader,
      extractMethods,
      cancelOperation,
      sessionLost: classSessionLost,
      sessionLostData: classSessionLostData,
      clearSessionLost: clearClassSessionLost
    } = useClassOperations(props.device.serial, clientId)
    
    const {
      scanModifiers,
      sessionLost: modifierSessionLost,
      sessionLostData: modifierSessionLostData,
      clearSessionLost: clearModifierSessionLost
    } = useModifierOperations(props.device.serial, clientId)
    
    const {
      patterns: appFocusedPatterns,
      loadConfig: loadAppFocusedConfig
    } = useAppFocusedConfig()
    
    const {
      selectedMethods,
      selectedCount: selectedMethodCount,
      hasSelection: hasMethodSelection,
      toggleMethod,
      isMethodSelected,
      deselectAll: deselectAllMethods,
      getSelectedHooks
    } = useMethodSelection()
    
    const {
      observerState,
      sessionName: observerSessionName,
      sessionPath: observerSessionPath,
      timeLimit: observerTimeLimit,
      isObserving,
      currentSessionNumber: observerSessionNumber,
      observedMethods,
      startObservation,
      stopObservation,
      resetState: resetObserverState,
      getMethodObservationHistory
    } = useObserver(props.device.serial, clientId)
    
    const methodSelectionEnabled = ref(false)

    // Phase 3: Temp state auto-save and recovery
    const {
      startAutoSave,
      stopAutoSave,
      triggerManualSync,
      checkRecovery,
      recoverTempState,
      clearTempState
    } = useTempState(props.device.serial, clientId, computed(() => selectedProcess.value?.package_id))
    
    const selectedProcess = ref(null)
    const filterMode = ref('focused')
    const workshopMode = ref('analysis')
    const resultsTab = ref('java')
    const showLockedModal = ref(false)
    const showSaveModal = ref(false)
    const showClearModal = ref(false)
    const showLogsModal = ref(false)
    const showFallbackSaveModal = ref(false)
    const showAppFocusedConfigModal = ref(false)
    const showProgressModal = ref(false)
    const showRecoveryModal = ref(false)
    const showConflictModal = ref(false)
    const showScanSelectionModal = ref(false)
    const showSessionLostModal = ref(false)
    const sessionLostModalData = ref(null)
    const showExitWarningModal = ref(false)
    const pendingNavigation = ref(null)
    const recoveryInfo = ref(null)
    const showToolkitDashboard = ref(false)
    
    const fridaAttached = ref(false)
    const fridaSessionNumber = ref(null)
    const fridaStatusMessage = ref('')
    const fridaCrashed = ref(false)
    const logsDefaultMode = ref('frida')
    const pendingLoadData = ref(null)
    const pendingSaveOptions = ref(null)
    const isSaved = ref(false)
    
    const spawnModeEnabled = ref(false)
    const selectedSpawnPackage = ref('')
    const spawnDelay = ref(30)
    
    const selectedScanTypes = ref([])
    const SCAN_TYPE_MAP = [
      { id: 'is_public', label: 'Public', color: '#10b981' },
      { id: 'is_private', label: 'Private', color: '#ef4444' },
      { id: 'is_protected', label: 'Protected', color: '#eab308' },
      { id: 'is_static', label: 'Static', color: '#a855f7' },
      { id: 'is_final', label: 'Final', color: '#f97316' },
      { id: 'is_interface', label: 'Interface', color: '#06b6d4' },
      { id: 'is_abstract', label: 'Abstract', color: '#ec4899' }
    ]
    
    // Operation progress tracking
    const operationType = ref('')
    let operationProgressTracker = null
    
    const hasDiscoveryData = computed(() => !!discoveryData.value)
    
    const progressTitle = computed(() => {
      if (operationType.value === 'scan_classloader') {
        return 'Scanning ClassLoader...'
      }
      if (operationType.value === 'scan_modifiers') {
        return 'Scanning Modifiers...'
      }
      if (operationType.value === 'extract_methods') {
        return 'Extracting Methods...'
      }
      return 'Processing...'
    })
    
    const currentPackageId = computed(() => {
      return selectedProcess.value?.package_id || discoveryData.value?.metadata?.package_id || ''
    })
    
    const currentTimestamp = computed(() => {
      if (discoveryId.value) {
        const parts = discoveryId.value.split('_')
        if (parts.length >= 2) {
          return parts.slice(-2).join('_')
        }
      }
      return ''
    })
    
    watch(hasLock, (newValue) => {
      emit('update:workshopSessionActive', newValue)
      if (!newValue && lockOwner.value) {
        showLockedModal.value = true
      }
    })
    
    // Load app focused config when process changes
    watch(() => selectedProcess.value?.package_id, async (packageId) => {
      if (packageId) {
        await loadAppFocusedConfig(packageId)
      }
    }, { immediate: true })
    
    watch(discoveryResult, (newResult) => {
      if (newResult) {
        loadDiscoveryData(newResult)
        isSaved.value = false
        deselectAll()
        
        startAutoSave(classStates)
      }
    })
    
    watch(workshopMode, (newMode, oldMode) => {
      if (newMode === 'instrumentation' && oldMode === 'analysis') {
        toast.guidance('Check Help and Instructions buttons for instrumentation guides', 'Instrumentation Mode')
      }
    })
    
    const retryAcquireLock = async () => {
      showLockedModal.value = false
      await acquireLock()
    }
    
    const startDiscovery = async () => {
      if (!hasLock.value) {
        toast.error('Workshop session not acquired', 'Discovery')
        return
      }
      
      let packageId, packageName
      
      if (spawnModeEnabled.value) {
        if (!selectedSpawnPackage.value) {
          toast.error('Please select a package to spawn', 'Discovery')
          return
        }
        packageId = selectedSpawnPackage.value
        packageName = packageId
      } else {
        if (!selectedProcess.value) {
          toast.error('Please select a process first', 'Discovery')
          return
        }
        packageId = selectedProcess.value.package_id
        packageName = selectedProcess.value.name
      }
      
      const installMarkers = await fetchInstallMarkers(packageId)
      
      const discoveryParams = {
        package_id: packageId,
        filter_mode: filterMode.value,
        package_info: {
          name: packageName,
          device_model: props.device.model,
          android_version: props.device.android_version,
          install_markers: installMarkers
        }
      }
      
      if (spawnModeEnabled.value) {
        discoveryParams.spawn_if_needed = true
        discoveryParams.spawn_delay = spawnDelay.value
      } else {
        discoveryParams.pid = selectedProcess.value.pid
      }
      
      await startDiscoveryFn(discoveryParams)
    }
    
    const cancelDiscovery = async () => {
      await cancelDiscoveryFn()
    }
    
    const clearResults = () => {
      if (discoveryData.value && !isSaved.value && shouldShowClearWarning()) {
        showClearModal.value = true
        return
      }
      confirmClearResults()
    }
    
    const confirmClearResults = async () => {
      showClearModal.value = false
      clearDiscoveryData()
      deselectAll()
      await clearDiscoveryFn()
      isSaved.value = false
      toast.info('Results cleared', 'Workshop')
    }
    
    const handleScanClassLoader = async () => {
      const classNames = getSelectedArray()
      if (classNames.length === 0) {
        toast.warning('No classes selected', 'Scan')
        return
      }
      
      const packageId = selectedProcess.value?.package_id || discoveryData.value?.metadata?.package_id
      if (!packageId) {
        toast.error('Package ID not found', 'Scan')
        return
      }
      
      operationType.value = 'scan_classloader'
      showProgressModal.value = true
      
      operationProgressTracker = useOperationProgress(
        props.device.serial,
        'scan_classloader',
        clientId
      )
      operationProgressTracker.startTracking()
      
      try {
        const response = await scanClassLoader(classNames, packageId)
        
        if (response.sessionLost) {
          handleSessionLost(response.results, response.sessionLostData)
        } else {
          updateClassStatesFromScan(response.results)
          deselectAll()
          triggerManualSync(classStates)
        }
      } catch (err) {
        console.error('[WorkshopTab] Scan ClassLoader failed:', err)
      } finally {
        operationProgressTracker?.stopTracking()
        showProgressModal.value = false
      }
    }
    
    const handleExtractMethods = async () => {
      const classNames = getSelectedArray()
      if (classNames.length === 0) {
        toast.warning('No classes selected', 'Extract')
        return
      }
      
      const packageId = selectedProcess.value?.package_id || discoveryData.value?.metadata?.package_id
      if (!packageId) {
        toast.error('Package ID not found', 'Extract')
        return
      }
      
      operationType.value = 'extract_methods'
      showProgressModal.value = true
      
      operationProgressTracker = useOperationProgress(
        props.device.serial,
        'extract_methods',
        clientId
      )
      operationProgressTracker.startTracking()
      
      try {
        const response = await extractMethods(classNames, packageId)
        
        if (response.sessionLost) {
          handleSessionLost(response.results, response.sessionLostData, true)
        } else {
          updateClassStatesFromExtract(response.results)
          deselectAll()
          triggerManualSync(classStates)
        }
      } catch (err) {
        console.error('[WorkshopTab] Extract methods failed:', err)
      } finally {
        operationProgressTracker?.stopTracking()
        showProgressModal.value = false
      }
    }
    
    const handleOpenScanModal = () => {
      if (getSelectedArray().length === 0) {
        toast.warning('No classes selected', 'Scan')
        return
      }
      showScanSelectionModal.value = true
    }
    
    const handleScanSelectionConfirm = (scanTypes) => {
      const typeObjects = scanTypes.map(id => 
        SCAN_TYPE_MAP.find(t => t.id === id)
      ).filter(Boolean)
      selectedScanTypes.value = typeObjects
    }
    
    const handleRemoveScanType = (typeId) => {
      selectedScanTypes.value = selectedScanTypes.value.filter(t => t.id !== typeId)
    }
    
    const handleClearScanTypes = () => {
      selectedScanTypes.value = []
    }
    
    const handleScanModifiers = async () => {
      const classNames = getSelectedArray()
      if (classNames.length === 0) {
        toast.warning('No classes selected', 'Scan')
        return
      }
      
      if (selectedScanTypes.value.length === 0) {
        toast.warning('No scan types selected. Click "Scan Modifiers" to select.', 'Scan')
        return
      }
      
      const packageId = selectedProcess.value?.package_id || discoveryData.value?.metadata?.package_id
      if (!packageId) {
        toast.error('Package ID not found', 'Scan')
        return
      }
      
      operationType.value = 'scan_modifiers'
      showProgressModal.value = true
      
      operationProgressTracker = useOperationProgress(
        props.device.serial,
        'scan_modifiers',
        clientId
      )
      operationProgressTracker.startTracking()
      
      try {
        const scanTypeIds = selectedScanTypes.value.map(t => t.id)
        const response = await scanModifiers(classNames, scanTypeIds, packageId)
        
        if (response.sessionLost) {
          handleSessionLost(response.results, response.sessionLostData)
        } else {
          updateClassStatesFromScan(response.results)
          deselectAll()
          triggerManualSync(classStates)
        }
      } catch (err) {
        console.error('[WorkshopTab] Scan modifiers failed:', err)
      } finally {
        operationProgressTracker?.stopTracking()
        showProgressModal.value = false
      }
    }
    
    const handleCancelOperation = async () => {
      if (operationProgressTracker) {
        operationProgressTracker.cancelled.value = true
      }
      await cancelOperation(operationType.value)
    }
    
    const handleSessionLost = (results, lostData, isExtract = false) => {
      fridaAttached.value = false
      fridaCrashed.value = true
      fridaStatusMessage.value = 'Session lost during operation'
      
      if (results && Array.isArray(results)) {
        results.forEach(result => {
          if (result.attempted) {
            updateClassState(result.name, { attempted: true, extracted: false })
          } else if (result.success) {
            if (isExtract) {
              updateClassState(result.name, { 
                extracted: true, 
                methods: result.methods || [],
                method_count: result.method_count || 0 
              })
            } else {
              updateClassState(result.name, {
                scanned: true,
                is_from_apk: result.is_from_apk,
                loader_type: result.loader_type
              })
            }
          }
        })
      }
      
      sessionLostModalData.value = { ...lostData, results }
      showSessionLostModal.value = true
      deselectAll()
      triggerManualSync(classStates)
    }
    
    const handleSessionLostClose = () => {
      showSessionLostModal.value = false
      sessionLostModalData.value = null
      clearClassSessionLost()
      clearModifierSessionLost()
    }
    
    const handleSessionLostViewLogs = () => {
      showSessionLostModal.value = false
      logsDefaultMode.value = 'frida'
      showLogsModal.value = true
    }
    
    const handleSaveDiscovery = async (saveOptions) => {
      if (!discoveryData.value || !selectedProcess.value) {
        toast.error('No discovery data to save', 'Save')
        return
      }
      
      const backendHasResult = await checkBackendHasResult()
      
      if (backendHasResult) {
        const success = await saveDiscovery(
          selectedProcess.value.package_id,
          saveOptions.version || discoveryData.value.metadata?.package_version || '1.0.0',
          saveOptions.customName,
          saveOptions.savePath
        )
        
        if (success) {
          showSaveModal.value = false
          isSaved.value = true
          toast.success('Discovery saved successfully', 'Save')
        }
      } else {
        pendingSaveOptions.value = saveOptions
        showSaveModal.value = false
        showFallbackSaveModal.value = true
      }
    }
    
    const handleFallbackSave = async () => {
      if (!discoveryData.value || !selectedProcess.value || !pendingSaveOptions.value) {
        toast.error('No discovery data to save', 'Save')
        return
      }
      
      const saveOptions = pendingSaveOptions.value
      
      const success = await saveDiscoveryFromFrontend(
        selectedProcess.value.package_id,
        saveOptions.version || discoveryData.value.metadata?.package_version || '1.0.0',
        discoveryData.value,
        saveOptions.customName,
        saveOptions.savePath
      )
      
      if (success) {
        showFallbackSaveModal.value = false
        pendingSaveOptions.value = null
        isSaved.value = true
      }
    }
    
    const cancelFallbackSave = () => {
      showFallbackSaveModal.value = false
      pendingSaveOptions.value = null
    }
    
    const handleDiscoveryLoaded = async (data) => {
      // Phase 3: Check if temp state exists (unsaved work)
      const packageId = selectedProcess.value?.package_id || data?.metadata?.package_id
      
      if (packageId && classStates.value.size > 0) {
        try {
          const recovery = await checkRecovery()
          
          if (recovery && recovery.recoverable) {
            // Show conflict modal
            pendingLoadData.value = data
            showConflictModal.value = true
            return
          }
        } catch (err) {
          console.error('[Load] Conflict check failed:', err)
        }
      }
      
      // No conflict, proceed with load
      loadDiscoveryData(data)
      isSaved.value = true
      deselectAll()
      resultsTab.value = 'java'
      
      // Stop auto-save when loading saved discovery
      stopAutoSave()
    }
    
    const getUnsavedStats = () => {
      let scanned_count = 0
      let extracted_count = 0
      
      classStates.value.forEach(state => {
        if (state.scanned) scanned_count++
        if (state.extracted) extracted_count++
      })
      
      return { scanned_count, extracted_count }
    }
    
    const handleAppFocusedConfigSaved = async () => {
      toast.success('App Focused configuration saved', 'Config')
      // Reload config to update patterns for real-time filtering
      if (selectedProcess.value?.package_id) {
        await loadAppFocusedConfig(selectedProcess.value.package_id)
      }
    }
    
    onMounted(async () => {
      emit('update:workshopSessionActive', hasLock.value)
      
      // Phase 3: Check for recoverable temp state
      if (selectedProcess.value?.package_id) {
        await checkForRecovery()
      }
    })
    
    // Phase 3: Recovery check
    const checkForRecovery = async () => {
      const packageId = selectedProcess.value?.package_id
      if (!packageId) return
      
      try {
        const recovery = await checkRecovery()
        
        if (recovery && recovery.recoverable) {
          recoveryInfo.value = recovery
          showRecoveryModal.value = true
        }
      } catch (err) {
        console.error('[Recovery] Check failed:', err)
      }
    }
    
    // Phase 3: Handle recovery actions
    const handleRecoverState = async () => {
      showRecoveryModal.value = false
      
      try {
        const recovered = await recoverTempState()
        
        if (!recovered) {
          toast.error('Failed to recover state')
          return
        }
        
        // Load recovered data
        loadDiscoveryData(recovered)
        
        // Restore class states
        const classStatesObj = recovered.class_states || {}
        Object.entries(classStatesObj).forEach(([className, state]) => {
          classStates.value.set(className, state)
        })
        
        // Start auto-save
        startAutoSave(classStates)
        
        toast.success('Work recovered successfully')
        console.log('[Recovery] State recovered:', recovered)
      } catch (err) {
        console.error('[Recovery] Failed:', err)
        toast.error('Failed to recover state')
      }
    }
    
    const handleDiscardRecovery = async () => {
      showRecoveryModal.value = false
      
      try {
        const success = await clearTempState()
        
        if (success) {
          toast.success('Started fresh - previous work discarded')
        } else {
          toast.warning('No temp state to clear')
        }
      } catch (err) {
        console.error('[Recovery] Clear failed:', err)
      }
    }
    
    // Phase 3: Handle load conflict
    const handleConflictSave = async () => {
      showConflictModal.value = false
      showSaveModal.value = true
      // After save completes, proceed with load
      pendingSaveOptions.value = { thenLoad: true }
    }
    
    const handleConflictDiscard = async () => {
      showConflictModal.value = false
      
      try {
        // Clear temp state using composable
        await clearTempState()
        
        // Proceed with load
        if (pendingLoadData.value) {
          loadDiscoveryData(pendingLoadData.value)
          pendingLoadData.value = null
        }
      } catch (err) {
        console.error('[Conflict] Discard failed:', err)
        toast.error('Failed to discard work')
      }
    }
    
    const handleConflictCancel = () => {
      showConflictModal.value = false
      pendingLoadData.value = null
    }
    
    const hasActiveWork = computed(() => {
      return props.fridaConnected || classStates.value.size > 0
    })
    
    const unsavedClassCount = computed(() => {
      let count = 0
      classStates.value.forEach(state => {
        if (state.extracted || state.scanned || state.attempted) count++
      })
      return count
    })
    
    const fridaAttachedPid = ref(null)
    
    const attachedPid = computed(() => {
      return fridaAttachedPid.value || selectedProcess.value?.pid || ''
    })
    
    const handleExitConfirm = () => {
      showExitWarningModal.value = false
      if (pendingNavigation.value) {
        pendingNavigation.value()
        pendingNavigation.value = null
      }
    }
    
    const handleExitCancel = () => {
      showExitWarningModal.value = false
      pendingNavigation.value = null
    }
    
    const handleAttachFrida = async (payload) => {
      try {
        const attachRequest =
          typeof payload === 'number'
            ? { pid: payload }
            : (payload && typeof payload === 'object' ? payload : null)
        
        if (!attachRequest || (!attachRequest.pid && !attachRequest.package_id)) {
          throw new Error('Invalid attach payload')
        }
        
        const response = await axios.post(
          `http://localhost:8000/api/devices/${props.device.serial}/workshop/frida/attach`,
          { ...attachRequest, client_id: clientId.value }
        )
        
        if (response.data.success) {
          fridaAttached.value = true
          fridaSessionNumber.value = response.data.session_number || null
          fridaStatusMessage.value = 'Attached successfully'
          fridaCrashed.value = false
          fridaAttachedPid.value = response.data.pid || attachRequest.pid || null
          
          if (attachRequest.package_id) {
            toast.success(`Attached to ${attachRequest.package_id}`, 'Frida')
          } else {
            toast.success(`Attached to PID ${attachRequest.pid}`, 'Frida')
          }
        }
      } catch (err) {
        console.error('[WorkshopTab] Attach failed:', err)
        toast.error(err.response?.data?.detail || 'Failed to attach', 'Frida')
      }
    }
    
    const handleDetachFrida = async () => {
      try {
        await axios.post(
          `http://localhost:8000/api/devices/${props.device.serial}/workshop/frida/detach`,
          { client_id: clientId.value }
        )
        
        fridaAttached.value = false
        fridaAttachedPid.value = null
        fridaSessionNumber.value = null
        fridaStatusMessage.value = ''
        toast.info('Detached from process', 'Frida')
      } catch (err) {
        console.error('[WorkshopTab] Detach failed:', err)
        toast.error(err.response?.data?.detail || 'Failed to detach', 'Frida')
      }
    }
    
    const handleSpawnFrida = async (packageId) => {
      try {
        const response = await axios.post(
          `http://localhost:8000/api/devices/${props.device.serial}/workshop/frida/spawn`,
          { package_id: packageId, client_id: clientId.value }
        )
        
        if (response.data.success) {
          fridaAttached.value = true
          fridaSessionNumber.value = response.data.session_number || null
          fridaStatusMessage.value = `Spawned ${packageId}`
          fridaCrashed.value = false
          fridaAttachedPid.value = response.data.pid || null
          toast.success(`Spawned and attached to ${packageId}`, 'Frida')
        }
      } catch (err) {
        console.error('[WorkshopTab] Spawn failed:', err)
        toast.error(err.response?.data?.detail || 'Failed to spawn app', 'Frida')
      }
    }
    
    let fridaStatusInterval = null
    
    const pollFridaStatus = async () => {
      try {
        const response = await axios.get(
          `http://localhost:8000/api/devices/${props.device.serial}/workshop/frida/status`
        )
        
        const wasAttached = fridaAttached.value
        fridaAttached.value = response.data.attached || false
        fridaSessionNumber.value = response.data.session_number || null
        
        if (response.data.attached) {
          fridaAttachedPid.value = response.data.pid || fridaAttachedPid.value || null
          fridaStatusMessage.value = `PID ${response.data.pid || selectedProcess.value?.pid}`
          fridaCrashed.value = false
        } else if (wasAttached && !response.data.attached) {
          fridaCrashed.value = true
          fridaStatusMessage.value = 'Session lost'
          fridaAttachedPid.value = null
        } else {
          fridaStatusMessage.value = ''
          fridaAttachedPid.value = null
        }
      } catch (err) {
        console.error('[WorkshopTab] Frida status poll failed:', err)
      }
    }
    
    const startFridaStatusPolling = () => {
      if (fridaStatusInterval) return
      pollFridaStatus()
      fridaStatusInterval = setInterval(pollFridaStatus, 2000)
    }
    
    const stopFridaStatusPolling = () => {
      if (fridaStatusInterval) {
        clearInterval(fridaStatusInterval)
        fridaStatusInterval = null
      }
    }
    
    const handleBeforeUnload = (e) => {
      if (fridaAttached.value) {
        e.preventDefault()
        e.returnValue = ''
        return ''
      }
    }
    
    const handleToggleSelectMethod = (payload) => {
      if (!methodSelectionEnabled.value) return
      const { className, method } = payload
      toggleMethod(className, method)
    }
    
    const handleToggleMethodSelection = () => {
      if (isObserving.value) return
      methodSelectionEnabled.value = !methodSelectionEnabled.value
      if (!methodSelectionEnabled.value) {
        deselectAllMethods()
      }
    }

    const handleObserverStart = async () => {
      const hooks = getSelectedHooks()
      const packageId = selectedProcess.value?.package_id || discoveryData.value?.metadata?.package_id
      
      if (!packageId) {
        toast.error('No package selected', 'Observer')
        return
      }
      
      const result = await startObservation(hooks, packageId)
      
      if (result.success && result.observedMethods) {
        result.observedMethods.forEach((history, methodKey) => {
          const [className, methodName] = methodKey.split('::')
          
          const classState = classStates.value.get(className)
          if (classState && classState.methods) {
            const methods = classState.methods.map(m => {
              const mKey = `${className}::${m.name}::${m.signature || ''}`
              if (mKey === methodKey) {
                return {
                  ...m,
                  observation_history: history
                }
              }
              return m
            })
            
            classStates.value.set(className, {
              ...classState,
              methods
            })
          }
        })
        
        deselectAllMethods()
        methodSelectionEnabled.value = false
        showToolkitDashboard.value = true
      }
    }
    
    const handleObserverStop = async () => {
      await stopObservation()
    }
    
    onBeforeRouteLeave((to, from, next) => {
      if (fridaAttached.value) {
        pendingNavigation.value = next
        showExitWarningModal.value = true
        return
      }
      next()
    })
    
    onMounted(() => {
      window.addEventListener('beforeunload', handleBeforeUnload)
      startFridaStatusPolling()
    })
    
    onUnmounted(() => {
      window.removeEventListener('beforeunload', handleBeforeUnload)
      stopFridaStatusPolling()
    })
    
    return {
      clientId,
      hasLock,
      lockOwner,
      expiresIn,
      sessionMessage,
      selectedProcess,
      filterMode,
      workshopMode,
      discoveryState,
      discoveryProgress,
      discoveryPhase,
      discoveryMessage,
      discoveryId,
      stats,
      discoveryData,
      classStates,
      resultsTab,
      showLockedModal,
      showSaveModal,
      showClearModal,
      showLogsModal,
      showFallbackSaveModal,
      showAppFocusedConfigModal,
      showProgressModal,
      showRecoveryModal,
      showConflictModal,
      showScanSelectionModal,
      showSessionLostModal,
      sessionLostModalData,
      showExitWarningModal,
      showToolkitDashboard,
      attachedPid,
      unsavedClassCount,
      fridaAttached,
      fridaSessionNumber,
      fridaStatusMessage,
      fridaCrashed,
      logsDefaultMode,
      recoveryInfo,
      saving,
      currentPackageId,
      currentTimestamp,
      hasDiscoveryData,
      selectedClasses,
      selectedCount,
      selectedScanTypes,
      appFocusedPatterns,
      spawnModeEnabled,
      selectedSpawnPackage,
      spawnDelay,
      selectedMethods,
      selectedMethodCount,
      isObserving,
      observerSessionName,
      observerTimeLimit,
      observerSessionPath,
      methodSelectionEnabled,
      toggleClass,
      selectClasses,
      deselectAll,
      getUnsavedStats,
      progressTitle,
      operationProgressTracker,
      retryAcquireLock,
      startDiscovery,
      cancelDiscovery,
      clearResults,
      confirmClearResults,
      handleSaveDiscovery,
      handleFallbackSave,
      cancelFallbackSave,
      handleDiscoveryLoaded,
      handleAppFocusedConfigSaved,
      handleScanClassLoader,
      handleOpenScanModal,
      handleScanSelectionConfirm,
      handleRemoveScanType,
      handleClearScanTypes,
      handleScanModifiers,
      handleExtractMethods,
      handleCancelOperation,
      handleRecoverState,
      handleDiscardRecovery,
      handleConflictSave,
      handleConflictDiscard,
      handleConflictCancel,
      handleSessionLostClose,
      handleSessionLostViewLogs,
      handleExitConfirm,
      handleExitCancel,
      handleAttachFrida,
      handleDetachFrida,
      handleSpawnFrida,
      handleToggleSelectMethod,
      handleToggleMethodSelection,
      handleObserverStart,
      handleObserverStop
    }
  }
}
</script>
