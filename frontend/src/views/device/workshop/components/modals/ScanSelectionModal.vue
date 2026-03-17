<template>
  <div v-if="show" class="modal modal-open">
    <div class="modal-box bg-neutral-900 border border-primary/30 max-w-2xl">
      <h3 class="font-bold text-xl text-white mb-4">Select Modifier Scans</h3>
      
      <div class="mb-4">
        <p class="text-sm text-slate-400 mb-3">
          Choose which class modifiers to scan for the selected classes.
          Multiple scans can be combined in a single operation.
        </p>
        
        <div class="flex gap-2 mb-4">
          <button 
            type="button"
            class="btn btn-xs bg-violet-700 hover:bg-violet-600 border-none text-white"
            @click="selectAll"
          >
            Select All
          </button>
          <button 
            type="button"
            class="btn btn-xs bg-red-700 hover:bg-red-600 border-none text-white"
            @click="deselectAll"
          >
            Deselect All
          </button>
        </div>
        
        <div class="space-y-2 max-h-[400px] overflow-y-auto">
          <label 
            v-for="scanType in availableScanTypes" 
            :key="scanType.id"
            class="flex items-center gap-3 p-3 bg-neutral-800 rounded-lg hover:bg-neutral-750 cursor-pointer border border-transparent hover:border-primary/30 transition-all"
          >
            <input 
              type="checkbox"
              :checked="localSelectedTypes.includes(scanType.id)"
              @change="toggleScanType(scanType.id)"
              class="checkbox checkbox-sm checkbox-primary"
            />
            <div class="flex-1">
              <div class="flex items-center gap-2">
                <span 
                  class="badge badge-xs text-white font-medium px-2 py-1"
                  :style="{ backgroundColor: scanType.color }"
                >
                  {{ scanType.label }}
                </span>
                <span class="text-xs text-slate-500">{{ scanType.description }}</span>
              </div>
            </div>
          </label>
        </div>
      </div>
      
      <div v-if="localSelectedTypes.length > 0" class="mb-4 p-3 bg-neutral-800 rounded-lg border border-primary/30">
        <p class="text-xs text-slate-400 mb-2">Selected scans ({{ localSelectedTypes.length }}):</p>
        <div class="flex flex-wrap gap-1">
          <span 
            v-for="typeId in localSelectedTypes" 
            :key="typeId"
            class="badge badge-sm text-white font-medium px-2 py-1"
            :style="{ backgroundColor: getScanTypeColor(typeId) }"
          >
            {{ getScanTypeLabel(typeId) }}
          </span>
        </div>
      </div>
      
      <div class="modal-action">
        <button 
          type="button"
          class="btn btn-sm bg-neutral-700 hover:bg-neutral-600 border-none text-white"
          @click="$emit('close')"
        >
          Cancel
        </button>
        <button 
          type="button"
          class="btn btn-sm bg-primary hover:bg-primary/80 border-none text-white"
          :disabled="localSelectedTypes.length === 0"
          @click="confirmSelection"
        >
          Confirm ({{ localSelectedTypes.length }})
        </button>
      </div>
    </div>
    <div class="modal-backdrop bg-black/70" @click="$emit('close')"></div>
  </div>
</template>

<script>
import { ref, watch } from 'vue'

const SCAN_TYPES = [
  { id: 'is_public', label: 'Public', color: '#10b981', description: 'Public access modifier' },
  { id: 'is_private', label: 'Private', color: '#ef4444', description: 'Private access modifier' },
  { id: 'is_protected', label: 'Protected', color: '#eab308', description: 'Protected access modifier' },
  { id: 'is_static', label: 'Static', color: '#a855f7', description: 'Static class modifier' },
  { id: 'is_final', label: 'Final', color: '#f97316', description: 'Final (cannot be extended)' },
  { id: 'is_interface', label: 'Interface', color: '#06b6d4', description: 'Interface type' },
  { id: 'is_abstract', label: 'Abstract', color: '#ec4899', description: 'Abstract class' }
]

export default {
  name: 'ScanSelectionModal',
  props: {
    show: {
      type: Boolean,
      required: true
    },
    selectedTypes: {
      type: Array,
      default: () => []
    }
  },
  emits: ['close', 'confirm'],
  setup(props, { emit }) {
    const localSelectedTypes = ref([...props.selectedTypes])
    const availableScanTypes = SCAN_TYPES
    
    watch(() => props.show, (newVal) => {
      if (newVal) {
        localSelectedTypes.value = [...props.selectedTypes]
      }
    })
    
    const toggleScanType = (typeId) => {
      const index = localSelectedTypes.value.indexOf(typeId)
      if (index > -1) {
        localSelectedTypes.value.splice(index, 1)
      } else {
        localSelectedTypes.value.push(typeId)
      }
    }
    
    const selectAll = () => {
      localSelectedTypes.value = SCAN_TYPES.map(t => t.id)
    }
    
    const deselectAll = () => {
      localSelectedTypes.value = []
    }
    
    const confirmSelection = () => {
      emit('confirm', [...localSelectedTypes.value])
      emit('close')
    }
    
    const getScanTypeColor = (typeId) => {
      const scanType = SCAN_TYPES.find(t => t.id === typeId)
      return scanType ? scanType.color : '#6b7280'
    }
    
    const getScanTypeLabel = (typeId) => {
      const scanType = SCAN_TYPES.find(t => t.id === typeId)
      return scanType ? scanType.label : typeId
    }
    
    return {
      localSelectedTypes,
      availableScanTypes,
      toggleScanType,
      selectAll,
      deselectAll,
      confirmSelection,
      getScanTypeColor,
      getScanTypeLabel
    }
  }
}
</script>
