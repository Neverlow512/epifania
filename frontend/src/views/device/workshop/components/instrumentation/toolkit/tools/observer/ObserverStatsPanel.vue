<template>
  <div
    v-if="showDashboard"
    class="observer-stats-panel fixed bottom-4 transition-all duration-300"
    :class="isCollapsed ? 'w-auto right-4' : 'left-[calc(25%+1rem)] right-4'"
    :style="{ zIndex: 9999, maxWidth: isCollapsed ? 'none' : 'calc(75% - 2rem)' }"
  >
    <div class="hud-frame hud-dock overflow-hidden border border-primary/20 bg-neutral-900 shadow-2xl">
      <button
        type="button"
        class="w-full flex items-center justify-between px-4 py-2.5 bg-neutral-900 hover:bg-neutral-800 transition-colors border-b border-primary/20"
        @click="toggleCollapse"
      >
        <div class="flex items-center gap-3 min-w-0">
          <div class="flex items-center gap-2 min-w-0">
            <div class="w-2 h-2 rounded-full" :class="isConnected ? 'bg-success pulse-dot' : 'bg-warning'"></div>
            <span v-if="isCollapsed" class="text-sm font-semibold text-white">
              Toolkit Dashboard
            </span>
            <span v-else class="text-sm font-semibold text-white truncate">
              {{ sessionStatus?.session_name || 'Toolkit Dashboard' }}
            </span>
          </div>
          <div v-if="sessionStatus && !isCollapsed" class="hidden sm:flex items-center gap-3 text-xs text-slate-300/80">
            <span class="tabular-nums">Time <span class="text-white font-medium">{{ formattedElapsed }}</span></span>
          </div>
        </div>

        <div class="flex items-center gap-2">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-4 w-4 text-slate-300/70 transition-transform duration-200"
            :class="{ 'rotate-180': isCollapsed }"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
          </svg>
          <button
            type="button"
            class="flex items-center justify-center w-5 h-5 rounded hover:bg-neutral-700/50 transition-colors"
            @click.stop="handleClose"
            title="Close dashboard"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5 text-slate-400 hover:text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </button>
      
      <div v-show="!isCollapsed" class="panel-content">
        <div class="flex flex-col lg:flex-row">
          <div class="lg:w-[320px] border-b lg:border-b-0 lg:border-r border-primary/15 p-4 space-y-4">
            <div class="hud-frame-sm border border-primary/15 bg-black/40">
              <div class="grid grid-cols-2 gap-px bg-primary/10">
                <div class="hud-stat">
                  <div class="hud-stat__label">Total Calls</div>
                  <div class="hud-stat__value tabular-nums">{{ sessionStatus?.total_calls || 0 }}</div>
                  <div class="hud-stat__bar"></div>
                </div>
                <div class="hud-stat">
                  <div class="hud-stat__label">Calls / Second</div>
                  <div class="hud-stat__value tabular-nums text-primary">{{ sessionStatus?.calls_per_second || 0 }}</div>
                  <div class="hud-stat__bar hud-stat__bar--accent"></div>
                </div>
                <div class="hud-stat">
                  <div class="hud-stat__label">Active Hooks</div>
                  <div class="hud-stat__value tabular-nums">
                    {{ sessionStatus?.active_hooks || 0 }}
                    <span class="text-slate-400 font-medium">/ {{ sessionStatus?.hooks_count || 0 }}</span>
                  </div>
                  <div class="hud-stat__bar hud-stat__bar--secondary"></div>
                </div>
                <div class="hud-stat">
                  <div class="hud-stat__label">Errors</div>
                  <div
                    class="hud-stat__value tabular-nums"
                    :class="sessionStatus && sessionStatus.total_errors > 0 ? 'text-error' : 'text-white'"
                  >
                    {{ sessionStatus?.total_errors || 0 }}
                  </div>
                  <div class="hud-stat__bar hud-stat__bar--error"></div>
                </div>
              </div>
            </div>

            <div class="space-y-2">
              <div class="text-[0.65rem] uppercase tracking-wider text-slate-400/80 px-1">Actions</div>
              <div class="space-y-1.5">
                <button
                  type="button"
                  class="w-full flex items-center gap-2 px-3 py-2 rounded bg-black/60 border border-primary/10 hover:border-primary/30 hover:bg-black/80 transition-all duration-150 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                  :disabled="isSaving"
                  @click="handleSaveScript"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-primary/90" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" />
                  </svg>
                  <span class="text-sm font-medium text-white">{{ isSaving ? 'Saving...' : 'Save Script' }}</span>
                </button>
              </div>
            </div>
          </div>
        
          <div class="flex-1 p-4 flex flex-col">
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-3">
              <div class="text-sm text-base-content/70">
                Showing <span class="text-base-content font-medium">{{ paginatedHooks.length }}</span> of
                <span class="text-base-content font-medium">{{ sortedHooks.length }}</span> hooks
              </div>

              <div class="controls-bar px-3 py-2 bg-black/60 border border-primary/10 flex items-center gap-3 flex-wrap">
                <div class="flex items-center gap-2">
                  <span class="text-[0.65rem] uppercase tracking-wider text-slate-400/80">Sort</span>
                  <div class="join">
                  <button
                    type="button"
                    class="btn btn-xs join-item"
                    :class="localSortBy === 'top_activity' ? 'btn-primary' : 'btn-ghost'"
                    @click="setSort('top_activity')"
                  >
                    Top
                  </button>
                  <button
                    type="button"
                    class="btn btn-xs join-item"
                    :class="localSortBy === 'most_calls' ? 'btn-primary' : 'btn-ghost'"
                    @click="setSort('most_calls')"
                  >
                    Calls
                  </button>
                  <button
                    type="button"
                    class="btn btn-xs join-item"
                    :class="localSortBy === 'most_errors' ? 'btn-primary' : 'btn-ghost'"
                    @click="setSort('most_errors')"
                  >
                    Errors
                  </button>
                  <button
                    type="button"
                    class="btn btn-xs join-item"
                    :class="localSortBy === 'alphabetical' ? 'btn-primary' : 'btn-ghost'"
                    @click="setSort('alphabetical')"
                  >
                    A–Z
                  </button>
                </div>
                </div>

                <div class="flex items-center gap-2">
                  <span class="text-[0.65rem] uppercase tracking-wider text-slate-400/80">Filter</span>
                  <div class="join">
                  <button
                    type="button"
                    class="btn btn-xs join-item"
                    :class="localFilterBy === 'all' ? 'btn-secondary' : 'btn-ghost'"
                    @click="setFilter('all')"
                  >
                    All
                  </button>
                  <button
                    type="button"
                    class="btn btn-xs join-item"
                    :class="localFilterBy === 'active_only' ? 'btn-secondary' : 'btn-ghost'"
                    @click="setFilter('active_only')"
                  >
                    Active
                  </button>
                  <button
                    type="button"
                    class="btn btn-xs join-item"
                    :class="localFilterBy === 'with_errors' ? 'btn-secondary' : 'btn-ghost'"
                    @click="setFilter('with_errors')"
                  >
                    Errors
                  </button>
                </div>
                </div>
              </div>
            </div>
          
            <div v-if="sortedHooks.length === 0" class="flex-1 flex items-center justify-center text-base-content/60 text-sm">
              No hooks to display
            </div>
          
            <div v-else class="flex-1 overflow-hidden">
              <div class="hook-grid max-h-[260px] overflow-y-auto pr-1 custom-scrollbar">
                <HookCard
                  v-for="hook in paginatedHooks"
                  :key="hook.hook_id"
                  :hook="hook"
                  :maxCallRate="maxCallRate"
                />
              </div>
            </div>
          
            <div v-if="totalPages > 1" class="flex items-center justify-center gap-2 mt-3 pt-3 border-t border-base-300/80">
              <button
                type="button"
                class="btn btn-xs btn-ghost"
                :disabled="currentPage === 1"
                @click="previousPage"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                </svg>
              </button>
              
              <span class="text-xs text-slate-300/80 tabular-nums">
                Page <span class="text-white font-medium">{{ currentPage }}</span> of
                <span class="text-white font-medium">{{ totalPages }}</span>
              </span>
              
              <button
                type="button"
                class="btn btn-xs btn-ghost"
                :disabled="currentPage === totalPages"
                @click="nextPage"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import HookCard from './HookCard.vue'
import { useObserverStats } from '../../../../../composables/useObserverStats'
import { useToast } from '../../../../../../../../composables/useToast'

export default {
  name: 'ObserverStatsPanel',
  components: {
    HookCard
  },
  props: {
    deviceSerial: {
      type: String,
      required: true
    },
    isObserving: {
      type: Boolean,
      default: false
    },
    clientId: {
      type: String,
      required: true
    },
    showDashboard: {
      type: Boolean,
      default: false
    }
  },
  emits: ['close'],
  setup(props, { emit }) {
    const toast = useToast()
    const isCollapsed = ref(false)
    const localSortBy = ref('top_activity')
    const localFilterBy = ref('all')
    const itemsPerPage = ref(10)
    const currentPage = ref(1)
    const isSaving = ref(false)
    
    const {
      isConnected,
      sessionStatus,
      sortedHooks,
      maxCallRate,
      connectWebSocket,
      disconnectWebSocket,
      setSortBy,
      setFilterBy
    } = useObserverStats(props.deviceSerial)
    
    const totalPages = computed(() => {
      return Math.ceil(sortedHooks.value.length / itemsPerPage.value)
    })
    
    const paginatedHooks = computed(() => {
      const start = (currentPage.value - 1) * itemsPerPage.value
      const end = start + itemsPerPage.value
      return sortedHooks.value.slice(start, end)
    })
    
    const formattedElapsed = computed(() => {
      if (!sessionStatus.value || !sessionStatus.value.elapsed) {
        return '0s'
      }
      const elapsed = Math.floor(sessionStatus.value.elapsed)
      const minutes = Math.floor(elapsed / 60)
      const seconds = elapsed % 60
      if (minutes > 0) {
        return `${minutes}m ${seconds}s`
      }
      return `${seconds}s`
    })
    
    const toggleCollapse = () => {
      isCollapsed.value = !isCollapsed.value
    }
    
    const handleSortChange = () => {
      setSortBy(localSortBy.value)
      currentPage.value = 1
    }
    
    const handleFilterChange = () => {
      setFilterBy(localFilterBy.value)
      currentPage.value = 1
    }

    const setSort = (value) => {
      if (localSortBy.value === value) return
      localSortBy.value = value
      handleSortChange()
    }

    const setFilter = (value) => {
      if (localFilterBy.value === value) return
      localFilterBy.value = value
      handleFilterChange()
    }
    
    const handlePerPageChange = () => {
      currentPage.value = 1
    }
    
    const previousPage = () => {
      if (currentPage.value > 1) {
        currentPage.value--
      }
    }
    
    const nextPage = () => {
      if (currentPage.value < totalPages.value) {
        currentPage.value++
      }
    }
    
    const handleSaveScript = async () => {
      if (isSaving.value) return
      
      isSaving.value = true
      try {
        const response = await axios.post(
          `http://localhost:8000/api/devices/${props.deviceSerial}/observer/save_script`,
          { client_id: props.clientId }
        )
        
        if (response.data.success) {
          const scriptPath = response.data.path
          toast.success(`Script saved to: ${scriptPath}`, 'Observer')
          
          axios.post(
            'http://localhost:8000/api/devices/open_folder',
            { path: scriptPath }
          ).catch(err => {
            console.error('[ObserverStatsPanel] Failed to open folder:', err)
          })
        } else {
          throw new Error(response.data.message || 'Failed to save script')
        }
      } catch (err) {
        console.error('[ObserverStatsPanel] Save script failed:', err)
        toast.error(err.response?.data?.detail || 'Failed to save script', 'Observer')
      } finally {
        isSaving.value = false
      }
    }
    
    const handleClose = () => {
      emit('close')
    }
    
    watch(() => props.isObserving, (newValue) => {
      if (newValue) {
        connectWebSocket()
        isCollapsed.value = false
        currentPage.value = 1
      } else {
        disconnectWebSocket()
      }
    })
    
    onMounted(() => {
      if (props.isObserving) {
        connectWebSocket()
      }
    })
    
    onUnmounted(() => {
      disconnectWebSocket()
    })
    
    return {
      isCollapsed,
      localSortBy,
      localFilterBy,
      itemsPerPage,
      currentPage,
      totalPages,
      isConnected,
      sessionStatus,
      sortedHooks,
      paginatedHooks,
      maxCallRate,
      formattedElapsed,
      isSaving,
      toggleCollapse,
      handleSortChange,
      handleFilterChange,
      setSort,
      setFilter,
      previousPage,
      nextPage,
      handleSaveScript,
      handleClose
    }
  }
}
</script>

<style scoped>
.hud-frame {
  clip-path: polygon(
    12px 0,
    calc(100% - 12px) 0,
    100% 12px,
    100% calc(100% - 12px),
    calc(100% - 12px) 100%,
    12px 100%,
    0 calc(100% - 12px),
    0 12px
  );
}

.hud-frame-sm {
  clip-path: polygon(
    10px 0,
    calc(100% - 10px) 0,
    100% 10px,
    100% calc(100% - 10px),
    calc(100% - 10px) 100%,
    10px 100%,
    0 calc(100% - 10px),
    0 10px
  );
}

.pulse-dot {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.panel-content {
  min-height: 320px;
  max-height: 420px;
}

.hook-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(145px, 1fr));
  gap: 0.6rem;
}

.hud-stat {
  background: rgba(0, 0, 0, 0.55);
  padding: 0.75rem 0.75rem 0.6rem;
  border: 1px solid rgba(255, 255, 255, 0.03);
}

.hud-stat__label {
  font-size: 0.7rem;
  color: rgba(148, 163, 184, 0.9);
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.hud-stat__value {
  margin-top: 0.25rem;
  font-size: 1.35rem;
  font-weight: 700;
  color: white;
  line-height: 1.1;
}

.hud-stat__bar {
  margin-top: 0.55rem;
  height: 2px;
  background: linear-gradient(90deg, rgba(113, 0, 208, 0.8), rgba(113, 0, 208, 0.1));
}

.hud-stat__bar--accent {
  background: linear-gradient(90deg, rgba(34, 211, 238, 0.85), rgba(34, 211, 238, 0.08));
}

.hud-stat__bar--secondary {
  background: linear-gradient(90deg, rgba(139, 92, 246, 0.85), rgba(139, 92, 246, 0.1));
}

.hud-stat__bar--error {
  background: linear-gradient(90deg, rgba(239, 68, 68, 0.85), rgba(239, 68, 68, 0.1));
}

.controls-bar {
  clip-path: polygon(
    8px 0,
    calc(100% - 8px) 0,
    100% 8px,
    100% calc(100% - 8px),
    calc(100% - 8px) 100%,
    8px 100%,
    0 calc(100% - 8px),
    0 8px
  );
}

.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: rgba(113, 0, 208, 0.35) rgba(17, 17, 17, 0.2);
}

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: rgba(17, 17, 17, 0.2);
  border-radius: 3px;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(113, 0, 208, 0.35);
  border-radius: 3px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(113, 0, 208, 0.5);
}
</style>
