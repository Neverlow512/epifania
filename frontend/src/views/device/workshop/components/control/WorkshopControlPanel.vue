<template>
  <div class="card bg-neutral-900/60 backdrop-blur-sm shadow-xl border border-primary/20 relative z-200">
    <div class="card-body p-4 space-y-4">
      <div class="flex items-center justify-between">
        <h3 class="card-title text-white text-lg">
          {{ isInstrumentationMode ? 'Instrumentation Control' : 'Analysis Control' }}
        </h3>
        <div class="flex items-center gap-2">
          <button
            type="button"
            class="btn btn-xs mode-toggle-btn"
            :class="[
              isInstrumentationMode ? 'btn-purple active-mode' : 'btn-ghost analysis-mode',
              { 'animate-border': showAnimation }
            ]"
            @click="toggleMode"
            :title="isInstrumentationMode ? 'Switch to Analysis Mode' : 'Switch to Instrumentation Mode'"
          >
            <svg v-if="!isInstrumentationMode" xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            Change
          </button>
          <button
            v-if="!isInstrumentationMode"
            type="button"
            class="btn btn-xs btn-accent"
            @click="showHelpModal = true"
          >
            <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Help
          </button>
          <button
            v-else
            type="button"
            class="btn btn-xs btn-accent"
            @click="showInstrumentationHelpModal = true"
          >
            <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Help
          </button>
        </div>
      </div>
      
      <template v-if="!isInstrumentationMode">
        <ProcessSelector
          :device="device"
          :selectedProcess="selectedProcess"
          :disabled="spawnModeEnabled"
          @update:selectedProcess="$emit('update:selectedProcess', $event)"
        />
        
        <FilterModeSelector
          :filterMode="filterMode"
          @update:filterMode="$emit('update:filterMode', $event)"
          @open-config="$emit('open-app-focused-config')"
        />
        
        <WorkshopSettings
          :device="device"
          :selectedProcess="selectedProcess"
        />
        
        <FridaStatusIndicator
          :fridaServerRunning="fridaServerRunning"
          :fridaServerVersion="fridaServerVersion"
          :fridaConnected="fridaConnected"
          @start-frida="$emit('start-frida')"
          @stop-frida="$emit('stop-frida')"
          @restart-frida="$emit('restart-frida')"
        />
        
        <FridaWorkshopControls
          :attached="fridaAttached"
          :attachedPid="attachedPid"
          :sessionNumber="sessionNumber"
          :statusMessage="fridaStatusMessage"
          :crashed="fridaCrashed"
          :selectedProcess="selectedProcess"
          :fridaServerRunning="fridaServerRunning"
          :hasLock="hasLock"
          :deviceSerial="device.serial"
          :isInstrumentationMode="false"
          @attach="$emit('attach-frida', $event)"
          @detach="$emit('detach-frida')"
          @spawn="$emit('spawn-frida', $event)"
          @update:spawnMode="$emit('update:spawnMode', $event)"
          @update:spawnPackage="$emit('update:spawnPackage', $event)"
          @update:spawnDelay="$emit('update:spawnDelay', $event)"
        />
        
        <DiscoveryActions
          :hasLock="hasLock"
          :selectedProcess="selectedProcess"
          :discoveryState="discoveryState"
          :hasResults="stats.totalClasses > 0 || stats.totalModules > 0"
          :spawnModeEnabled="spawnModeEnabled"
          :selectedSpawnPackage="selectedSpawnPackage"
          @start-discovery="$emit('start-discovery')"
          @cancel-discovery="$emit('cancel-discovery')"
          @save-discovery="$emit('save-discovery')"
          @clear-results="$emit('clear-results')"
          @view-logs="$emit('view-logs')"
        />
        
        <DiscoveryProgress
          v-if="discoveryState === 'running'"
          :progress="discoveryProgress"
          :phase="discoveryPhase"
          :message="discoveryMessage"
          @cancel="$emit('cancel-discovery')"
        />
        
        <DiscoveryStats
          v-if="stats.totalClasses > 0 || stats.totalModules > 0"
          :stats="stats"
        />
      </template>
      
      <template v-else>
        <FridaStatusIndicator
          :fridaServerRunning="fridaServerRunning"
          :fridaServerVersion="fridaServerVersion"
          :fridaConnected="fridaConnected"
          @start-frida="$emit('start-frida')"
          @stop-frida="$emit('stop-frida')"
          @restart-frida="$emit('restart-frida')"
        />
        
        <InstrumentationFridaSession
          :attached="fridaAttached"
          :attachedPid="attachedPid"
          :sessionNumber="sessionNumber"
          :statusMessage="fridaStatusMessage"
          :crashed="fridaCrashed"
          :fridaServerRunning="fridaServerRunning"
          :hasLock="hasLock"
          :deviceSerial="device.serial"
          @attach="$emit('attach-frida', $event)"
          @detach="$emit('detach-frida')"
          @spawn="$emit('spawn-frida', $event)"
          @update:selectedApp="$emit('update:selectedApp', $event)"
        />
        
        <InstrumentationPanel 
          :selectedMethodCount="selectedMethodCount"
          :fridaAttached="fridaAttached"
          :isObserving="isObserving"
          :sessionName="observerSessionName"
          :timeLimit="observerTimeLimit"
          :logPath="observerSessionPath"
          :methodSelectionEnabled="methodSelectionEnabled"
          @observer-start="$emit('observer-start')"
          @observer-stop="$emit('observer-stop')"
          @update:sessionName="$emit('update:observerSessionName', $event)"
          @update:timeLimit="$emit('update:observerTimeLimit', $event)"
          @update:logPath="$emit('update:observerSessionPath', $event)"
          @toggle-method-selection="$emit('toggle-method-selection')"
          @open-dashboard="$emit('open-dashboard')"
        />
      </template>
    </div>

    <WorkshopControlHelpModal
      :show="showHelpModal"
      @close="showHelpModal = false"
    />

    <InstrumentationControlHelpModal
      :show="showInstrumentationHelpModal"
      @close="showInstrumentationHelpModal = false"
    />
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import ProcessSelector from './ProcessSelector.vue'
import FilterModeSelector from './FilterModeSelector.vue'
import WorkshopSettings from './WorkshopSettings.vue'
import FridaStatusIndicator from './FridaStatusIndicator.vue'
import FridaWorkshopControls from './FridaWorkshopControls.vue'
import DiscoveryActions from './DiscoveryActions.vue'
import DiscoveryProgress from './DiscoveryProgress.vue'
import DiscoveryStats from './DiscoveryStats.vue'
import WorkshopControlHelpModal from '../modals/WorkshopControlHelpModal.vue'
import InstrumentationPanel from '../instrumentation/InstrumentationPanel.vue'
import InstrumentationControlHelpModal from '../instrumentation/modals/InstrumentationControlHelpModal.vue'
import InstrumentationFridaSession from '../instrumentation/session/InstrumentationFridaSession.vue'

export default {
  name: 'WorkshopControlPanel',
  components: {
    ProcessSelector,
    FilterModeSelector,
    WorkshopSettings,
    FridaStatusIndicator,
    FridaWorkshopControls,
    DiscoveryActions,
    DiscoveryProgress,
    DiscoveryStats,
    WorkshopControlHelpModal,
    InstrumentationPanel,
    InstrumentationControlHelpModal,
    InstrumentationFridaSession
  },
  setup(props, { emit }) {
    const showHelpModal = ref(false)
    const showInstrumentationHelpModal = ref(false)
    const isInstrumentationMode = ref(false)
    const showAnimation = ref(false)
    
    const toggleMode = () => {
      isInstrumentationMode.value = !isInstrumentationMode.value
      emit('update:mode', isInstrumentationMode.value ? 'instrumentation' : 'analysis')
    }
    
    onMounted(() => {
      showAnimation.value = true
      setTimeout(() => {
        showAnimation.value = false
      }, 3000)
    })
    
    return {
      showHelpModal,
      showInstrumentationHelpModal,
      isInstrumentationMode,
      showAnimation,
      toggleMode
    }
  },
  props: {
    device: Object,
    hasLock: Boolean,
    sessionMessage: String,
    fridaServerRunning: Boolean,
    fridaServerVersion: String,
    fridaConnected: Boolean,
    fridaAttached: Boolean,
    attachedPid: [Number, String],
    sessionNumber: [Number, String],
    fridaStatusMessage: String,
    fridaCrashed: Boolean,
    selectedProcess: Object,
    filterMode: String,
    discoveryState: String,
    discoveryProgress: Number,
    discoveryPhase: String,
    discoveryMessage: String,
    stats: Object,
    spawnModeEnabled: Boolean,
    selectedSpawnPackage: String,
    selectedMethodCount: Number,
    isObserving: Boolean,
    observerSessionName: String,
    observerTimeLimit: Number,
    observerSessionPath: String,
    methodSelectionEnabled: Boolean
  },
  emits: [
    'update:selectedProcess',
    'update:filterMode',
    'update:mode',
    'start-discovery',
    'cancel-discovery',
    'save-discovery',
    'clear-results',
    'view-logs',
    'start-frida',
    'stop-frida',
    'restart-frida',
    'attach-frida',
    'detach-frida',
    'spawn-frida',
    'update:spawnMode',
    'update:spawnPackage',
    'update:spawnDelay',
    'open-app-focused-config',
    'observer-start',
    'observer-stop',
    'update:observerSessionName',
    'update:observerTimeLimit',
    'update:observerSessionPath',
    'toggle-method-selection'
  ]
}
</script>

<style scoped>
.mode-toggle-btn {
  position: relative;
  overflow: visible;
  transition: box-shadow 0.3s ease, border-color 0.3s ease, background-color 0.3s ease;
}

.mode-toggle-btn.btn-purple {
  background-color: #7100d0;
  border-color: #7100d0;
  color: white;
}

.mode-toggle-btn.btn-purple:hover {
  background-color: #5f00b3;
  border-color: #5f00b3;
}

.mode-toggle-btn.analysis-mode {
  border: 2px solid rgba(113, 0, 208, 0.5) !important;
  box-shadow: 0 0 8px 1px rgba(113, 0, 208, 0.3);
}

.mode-toggle-btn.active-mode {
  border: none !important;
  box-shadow: none !important;
}

.mode-toggle-btn.animate-border {
  animation: subtle-border-pulse 3s ease-in-out;
}

@keyframes subtle-border-pulse {
  0% {
    border-color: rgba(113, 0, 208, 0.5);
    box-shadow: 0 0 8px 1px rgba(113, 0, 208, 0.3);
  }
  25% {
    border-color: rgba(113, 0, 208, 0.7);
    box-shadow: 0 0 16px 3px rgba(113, 0, 208, 0.6);
  }
  50% {
    border-color: rgba(113, 0, 208, 0.9);
    box-shadow: 0 0 20px 5px rgba(113, 0, 208, 0.8);
  }
  75% {
    border-color: rgba(113, 0, 208, 0.7);
    box-shadow: 0 0 16px 3px rgba(113, 0, 208, 0.6);
  }
  100% {
    border-color: rgba(113, 0, 208, 0.5);
    box-shadow: 0 0 8px 1px rgba(113, 0, 208, 0.3);
  }
}
</style>

