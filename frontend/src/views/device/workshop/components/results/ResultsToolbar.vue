<template>
  <div class="space-y-3">
    <div class="flex flex-wrap gap-2 items-center">
      <!-- Search -->
      <input 
        type="text"
        :value="searchQuery"
        @input="$emit('update:searchQuery', $event.target.value)"
        placeholder="Search classes or methods..."
        class="input input-sm input-bordered bg-black border-primary/30 focus:border-primary text-white flex-1 min-w-[200px]"
      />
      
      <!-- Category Filter -->
      <select 
        :value="categoryFilter"
        @change="$emit('update:categoryFilter', $event.target.value)"
        class="select select-sm select-bordered bg-black border-primary/30 text-white"
      >
        <option value="all">All Categories</option>
        <option value="Network">Network</option>
        <option value="Crypto">Crypto</option>
        <option value="Storage">Storage</option>
        <option value="Security">Security</option>
        <option value="UI">UI</option>
        <option value="Reflection">Reflection</option>
        <option value="Native">Native</option>
        <option value="Obfuscated">Obfuscated</option>
        <option value="Unknown">Unknown</option>
      </select>
      
      <!-- Source Filter -->
      <div class="flex gap-2">
        <label class="label cursor-pointer gap-1">
          <input 
            type="radio" 
            name="source" 
            class="radio radio-xs radio-primary" 
            value="all"
            :checked="sourceFilter === 'all'"
            @change="$emit('update:sourceFilter', 'all')"
          />
          <span class="label-text text-xs text-white">All</span>
        </label>
        <label class="label cursor-pointer gap-1">
          <input 
            type="radio" 
            name="source" 
            class="radio radio-xs radio-primary" 
            value="app"
            :checked="sourceFilter === 'app'"
            @change="$emit('update:sourceFilter', 'app')"
          />
          <span class="label-text text-xs text-white">App</span>
        </label>
        <label class="label cursor-pointer gap-1">
          <input 
            type="radio" 
            name="source" 
            class="radio radio-xs radio-primary" 
            value="bundled"
            :checked="sourceFilter === 'bundled'"
            @change="$emit('update:sourceFilter', 'bundled')"
          />
          <span class="label-text text-xs text-white">Bundled</span>
        </label>
      </div>
      
      <!-- Items Per Page -->
      <div class="flex items-center gap-1">
        <span class="text-xs text-slate-400">Per page:</span>
        <div class="join">
          <button 
            type="button"
            class="btn btn-xs join-item bg-neutral-800 border-primary/30 hover:bg-neutral-700"
            @mousedown="startDecrement"
            @mouseup="stopAdjust"
            @mouseleave="stopAdjust"
            @touchstart.prevent="startDecrement"
            @touchend="stopAdjust"
            :disabled="itemsPerPage <= MIN_ITEMS"
          >
            -
          </button>
          <input 
            type="text"
            inputmode="numeric"
            pattern="[0-9]*"
            :value="itemsPerPage"
            @input="handleInputChange"
            @blur="handleInputBlur"
            class="input input-xs join-item bg-black border-primary/30 text-white text-center w-16 no-spinner"
          />
          <button 
            type="button"
            class="btn btn-xs join-item bg-neutral-800 border-primary/30 hover:bg-neutral-700"
            @mousedown="startIncrement"
            @mouseup="stopAdjust"
            @mouseleave="stopAdjust"
            @touchstart.prevent="startIncrement"
            @touchend="stopAdjust"
            :disabled="itemsPerPage >= MAX_ITEMS"
          >
            +
          </button>
        </div>
      </div>
    </div>
    
    <!-- Selection and Actions Row -->
    <div class="flex flex-wrap gap-2 items-center justify-between">
      <!-- Selection Controls (left side) -->
      <div class="flex items-center gap-2">
        <!-- Selected count -->
        <span v-if="selectedCount > 0" class="text-xs text-primary font-medium">
          {{ selectedCount }} selected
        </span>
        
        <!-- Inline selection buttons with clear labels and colors -->
        <div class="flex items-center gap-1">
          <span class="text-xs text-slate-500">Select:</span>
          <QuestionTooltip text="Page selects all classes on the current page.\nAll Visible selects all classes in the current filtered view (across all pages)." />
        </div>
        <button 
          type="button"
          class="btn btn-xs bg-violet-700 hover:bg-violet-600 border-none text-white"
          @click="$emit('select-page')"
          title="Select all classes on current page"
        >
          Page
        </button>
        <button 
          type="button"
          class="btn btn-xs bg-indigo-700 hover:bg-indigo-600 border-none text-white"
          @click="$emit('select-all')"
          title="Select all visible/filtered classes"
        >
          All Visible
        </button>
        <button 
          v-if="hasSelection"
          type="button"
          class="btn btn-xs bg-red-700 hover:bg-red-600 border-none text-white"
          @click="$emit('deselect-all')"
          title="Clear all selections"
        >
          Clear
        </button>
      </div>
      
      <!-- Action Buttons (right side) - Only show in Analysis mode -->
      <div v-if="workshopMode === 'analysis'" class="flex items-center gap-2">
        <QuestionTooltip 
          text="Scan ClassLoader: Determines whether selected classes are from APK or Android system. Adds APK/Sys badges and enables Package mode filtering. Select classes first, then click to scan.

          Choose Modifiers: Opens modal to select class modifier types (public, private, static, final, interface, abstract, protected). Select which properties to scan for, then execute.

          Extract Methods: Retrieves all methods from selected classes including signatures, parameters, return types, and method modifiers. Required to view and hook methods. Changes method count from 0? to actual number." 
        />
        <!-- Scan ClassLoader Button - only in Focused/All modes -->
        <button 
          v-if="filterMode !== 'package'"
          class="btn btn-xs bg-emerald-600 hover:bg-emerald-500 border-none text-white"
          :disabled="selectedCount === 0"
          @click="$emit('scan-classloader')"
          title="Scan ClassLoader for selected classes"
        >
          Scan ClassLoader ({{ selectedCount }})
        </button>
        
        <!-- Choose Modifiers Button - Opens modal to select scan types -->
        <button 
          class="btn btn-xs bg-indigo-600 hover:bg-indigo-500 border-none text-white"
          :disabled="selectedCount === 0"
          @click="$emit('open-scan-modal')"
          title="Choose which class modifiers to scan"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          Choose Modifiers
        </button>
        
        <!-- Extract Methods Button - all modes -->
        <button 
          class="btn btn-xs bg-blue-600 hover:bg-blue-500 border-none text-white"
          :disabled="selectedCount === 0"
          @click="$emit('extract-methods')"
          title="Extract methods for selected classes"
        >
          Extract Methods ({{ selectedCount }})
        </button>
      </div>
    </div>
    
    <!-- Selected Scan Types Display with Execute Button - Only show in Analysis mode -->
    <div v-if="workshopMode === 'analysis' && selectedScanTypes.length > 0" class="flex items-center gap-2 p-2 bg-neutral-800 rounded-lg border border-indigo-500/40">
      <span class="text-xs text-slate-400 font-medium">Selected scans:</span>
      <div class="flex flex-wrap gap-1">
        <span 
          v-for="scanType in selectedScanTypes" 
          :key="scanType.id"
          class="badge badge-sm text-white font-medium px-2 py-1 flex items-center gap-1"
          :style="{ backgroundColor: scanType.color }"
        >
          {{ scanType.label }}
          <button
            type="button"
            class="hover:opacity-70 ml-0.5"
            @click="$emit('remove-scan-type', scanType.id)"
            title="Remove this scan type"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </span>
      </div>
      <div class="flex items-center gap-1 ml-auto">
        <button
          type="button"
          class="btn btn-xs bg-indigo-700 hover:bg-indigo-600 border-none text-white"
          :disabled="selectedCount === 0"
          @click="$emit('scan-modifiers')"
          title="Execute modifier scan for selected classes"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          Execute ({{ selectedCount }})
        </button>
        <button
          type="button"
          class="btn btn-xs bg-red-700 hover:bg-red-600 border-none text-white"
          @click="$emit('clear-scan-types')"
          title="Clear all scan types"
        >
          Clear
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onUnmounted } from 'vue'
import QuestionTooltip from '../shared/QuestionTooltip.vue'

const MIN_ITEMS = 10
const MAX_ITEMS = 500
const INITIAL_DELAY = 400
const MIN_DELAY = 50
const ACCELERATION_FACTOR = 0.85

export default {
  name: 'ResultsToolbar',
  components: {
    QuestionTooltip
  },
  props: {
    searchQuery: {
      type: String,
      required: true
    },
    categoryFilter: {
      type: String,
      required: true
    },
    sourceFilter: {
      type: String,
      required: true
    },
    itemsPerPage: {
      type: Number,
      required: true
    },
    selectedCount: {
      type: Number,
      default: 0
    },
    filterMode: {
      type: String,
      default: 'focused'
    },
    workshopMode: {
      type: String,
      default: 'analysis'
    },
    hasSelection: {
      type: Boolean,
      default: false
    },
    selectedScanTypes: {
      type: Array,
      default: () => []
    }
  },
  emits: [
    'update:searchQuery',
    'update:categoryFilter',
    'update:sourceFilter',
    'update:itemsPerPage',
    'select-page',
    'select-all',
    'deselect-all',
    'scan-classloader',
    'open-scan-modal',
    'remove-scan-type',
    'clear-scan-types',
    'extract-methods'
  ],
  setup(props, { emit }) {
    let adjustTimer = null
    let currentDelay = INITIAL_DELAY
    let holdCount = ref(0)
    
    const clampValue = (value) => {
      return Math.max(MIN_ITEMS, Math.min(MAX_ITEMS, value))
    }
    
    const getStep = () => {
      if (holdCount.value < 5) return 1
      if (holdCount.value < 15) return 5
      if (holdCount.value < 30) return 10
      if (holdCount.value < 50) return 25
      return 50
    }
    
    const increment = () => {
      const step = getStep()
      const newValue = clampValue(props.itemsPerPage + step)
      if (newValue !== props.itemsPerPage) {
        emit('update:itemsPerPage', newValue)
      }
      holdCount.value++
      
      currentDelay = Math.max(MIN_DELAY, currentDelay * ACCELERATION_FACTOR)
      adjustTimer = setTimeout(increment, currentDelay)
    }
    
    const decrement = () => {
      const step = getStep()
      const newValue = clampValue(props.itemsPerPage - step)
      if (newValue !== props.itemsPerPage) {
        emit('update:itemsPerPage', newValue)
      }
      holdCount.value++
      
      currentDelay = Math.max(MIN_DELAY, currentDelay * ACCELERATION_FACTOR)
      adjustTimer = setTimeout(decrement, currentDelay)
    }
    
    const startIncrement = () => {
      holdCount.value = 0
      currentDelay = INITIAL_DELAY
      increment()
    }
    
    const startDecrement = () => {
      holdCount.value = 0
      currentDelay = INITIAL_DELAY
      decrement()
    }
    
    const stopAdjust = () => {
      if (adjustTimer) {
        clearTimeout(adjustTimer)
        adjustTimer = null
      }
      holdCount.value = 0
      currentDelay = INITIAL_DELAY
    }
    
    const handleInputChange = (event) => {
      const value = parseInt(event.target.value, 10)
      if (!isNaN(value)) {
        emit('update:itemsPerPage', clampValue(value))
      }
    }
    
    const handleInputBlur = (event) => {
      let value = parseInt(event.target.value, 10)
      if (isNaN(value) || value < MIN_ITEMS) {
        value = MIN_ITEMS
      } else if (value > MAX_ITEMS) {
        value = MAX_ITEMS
      }
      emit('update:itemsPerPage', value)
      event.target.value = value
    }
    
    onUnmounted(() => {
      stopAdjust()
    })
    
    return {
      MIN_ITEMS,
      MAX_ITEMS,
      startIncrement,
      startDecrement,
      stopAdjust,
      handleInputChange,
      handleInputBlur
    }
  }
}
</script>

<style scoped>
.no-spinner::-webkit-outer-spin-button,
.no-spinner::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.no-spinner[type=number] {
  appearance: textfield;
  -moz-appearance: textfield;
}
</style>
