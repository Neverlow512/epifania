<template>
  <tr 
    class="hover:bg-neutral-800/50 cursor-pointer border-b border-neutral-700"
    :class="{ 'bg-primary/5': selected }"
    @click="$emit('toggle-expand')"
  >
    <td v-if="showSelection" class="w-10" @click.stop>
      <input 
        type="checkbox"
        :checked="selected"
        @change="$emit('toggle-select')"
        class="checkbox checkbox-xs checkbox-primary"
      />
    </td>
    <td class="w-8">
      <svg 
        xmlns="http://www.w3.org/2000/svg" 
        class="h-4 w-4 text-slate-400 transition-transform"
        :class="{ 'rotate-90': expanded }"
        fill="none" 
        viewBox="0 0 24 24" 
        stroke="currentColor"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
      </svg>
    </td>
    <td class="min-w-0">
      <div class="w-full">
        <div class="flex items-center gap-2 min-w-0">
          <span class="badge badge-xs badge-primary flex-shrink-0">Class</span>
          <code 
            class="text-xs font-mono cursor-pointer inline-block min-w-0 flex-1 max-w-[520px] align-top" 
            :class="[
              methodsExtracted ? 'text-white' : 'text-slate-400',
              nameExpanded ? 'whitespace-normal break-all' : 'truncate'
            ]"
            :title="classData.name"
            @click.stop="toggleNameExpanded"
          >{{ displayName }}</code>
          <span v-if="classData.is_obfuscated" class="badge badge-xs bg-yellow-600 text-white flex-shrink-0">Obf</span>
          <span v-if="isFromApk" class="badge badge-xs bg-blue-600 text-white flex-shrink-0" title="Loaded from APK">APK</span>
          <span v-else-if="isScanned && !isFromApk" class="badge badge-xs bg-slate-600 text-white flex-shrink-0" title="System/Framework class">Sys</span>
          <span 
            v-if="extractionBadge.show" 
            class="badge badge-xs text-white flex-shrink-0"
            :class="extractionBadge.color"
            :title="extractionBadge.tooltip"
          >{{ extractionBadge.label }}</span>
        </div>
        <div v-if="expanded" class="mt-1 text-[10px] text-slate-500 font-mono break-all max-w-md">
          {{ classData.name }}
          <span v-if="loaderType" class="ml-2 text-slate-600">[{{ loaderType }}]</span>
        </div>
        
        <div v-if="hasModifiers" class="mt-1.5 flex flex-wrap gap-1 w-full">
          <span 
            v-for="modifier in activeModifiers" 
            :key="modifier.id"
            class="badge badge-xs text-white font-medium px-1.5 py-0.5 flex-shrink-0"
            :style="{ backgroundColor: modifier.color }"
            :title="modifier.label"
          >
            {{ modifier.label }}
          </span>
        </div>
      </div>
    </td>
    <td>
      <CategoryBadge :category="classData.class_category || 'Unknown'" />
    </td>
    <td>
      <SourceBadge :source="classData.source" />
    </td>
    <td class="text-right whitespace-nowrap w-20">
      <span 
        class="text-xs"
        :class="methodsExtracted ? 'text-slate-400' : 'text-slate-600'"
        :title="methodsExtracted ? `${methodCount} methods extracted` : 'Methods not yet extracted'"
      >
        {{ methodCount }}
        <span v-if="!methodsExtracted" class="text-slate-500 text-[10px]">?</span>
      </span>
    </td>
    <td class="w-20" @click.stop>
      <div v-if="workshopMode === 'analysis'" class="flex gap-1 justify-end">
        <button
          v-if="!isScanned && showScanButton"
          class="btn btn-xs btn-ghost text-emerald-500 hover:bg-emerald-600/20 px-1"
          @click="$emit('scan-class', classData.name)"
          title="Scan ClassLoader"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </button>
        <button
          v-if="!methodsExtracted"
          class="btn btn-xs btn-ghost text-blue-500 hover:bg-blue-600/20 px-1"
          @click="$emit('extract-class', classData.name)"
          title="Extract Methods"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
        </button>
      </div>
    </td>
  </tr>
</template>

<script>
import CategoryBadge from '../../shared/CategoryBadge.vue'
import SourceBadge from '../../shared/SourceBadge.vue'

export default {
  name: 'ClassRow',
  components: {
    CategoryBadge,
    SourceBadge
  },
  props: {
    classData: {
      type: Object,
      required: true
    },
    expanded: {
      type: Boolean,
      required: true
    },
    selected: {
      type: Boolean,
      default: false
    },
    showSelection: {
      type: Boolean,
      default: true
    },
    workshopMode: {
      type: String,
      default: 'analysis'
    },
    classState: {
      type: Object,
      default: null
    },
    showScanButton: {
      type: Boolean,
      default: true
    }
  },
  emits: ['toggle-expand', 'toggle-select', 'scan-class', 'extract-class'],
  data() {
    return {
      nameExpanded: false
    }
  },
  computed: {
    shouldTruncateName() {
      const name = this.classData.name
      return name.length > 90
    },
    displayName() {
      const name = this.classData.name
      if (this.nameExpanded || !this.shouldTruncateName) return name
      return name.substring(0, 87) + '...'
    },
    isScanned() {
      return this.classState?.scanned || this.classData.scanned || false
    },
    isFromApk() {
      return this.classState?.is_from_apk || this.classData.is_from_apk || false
    },
    loaderType() {
      return this.classState?.loader_type || this.classData.loader_type || null
    },
    methodsExtracted() {
      if (this.classState?.extracted) return true
      if (this.classData.methods && this.classData.methods.length > 0) return true
      return false
    },
    methodCount() {
      if (this.classState?.methods) {
        return this.classState.methods.length
      }
      return this.classData.method_count || this.classData.methods?.length || 0
    },
    isAttempted() {
      return this.classState?.attempted || false
    },
    extractionBadge() {
      const status = this.classState?.extraction_status || this.classData.extraction_status
      
      if (status === 'completed') {
        return {
          show: true,
          type: 'completed',
          label: 'Completed',
          color: 'bg-green-600',
          tooltip: 'Methods successfully extracted'
        }
      }
      
      if (status === 'attempted') {
        return {
          show: true,
          type: 'attempted',
          label: 'Attempted',
          color: 'bg-orange-500',
          tooltip: 'Class loaded but method extraction failed - retry recommended'
        }
      }
      
      if (status === 'unable_to_load') {
        return {
          show: true,
          type: 'unable_to_load',
          label: 'Unable to Load',
          color: 'bg-amber-500',
          tooltip: 'Class could not be loaded - may be a classloader or timing issue'
        }
      }
      
      if (status === 'failed') {
        return {
          show: true,
          type: 'failed',
          label: 'Failed',
          color: 'bg-red-600',
          tooltip: 'Complete extraction failure - check session status'
        }
      }
      
      // Legacy fallback: check if already extracted based on old logic
      if (this.isAttempted) {
        return {
          show: true,
          type: 'attempted',
          label: 'Attempted',
          color: 'bg-orange-500',
          tooltip: 'Session crashed while processing this class'
        }
      }
      
      if (this.methodsExtracted) {
        return {
          show: true,
          type: 'extracted',
          label: 'Completed',
          color: 'bg-green-600',
          tooltip: 'Methods successfully extracted'
        }
      }
      
      return { show: false }
    },
    hasModifiers() {
      return this.activeModifiers.length > 0
    },
    activeModifiers() {
      const MODIFIER_MAP = [
        { id: 'is_public', label: 'Public', color: '#10b981' },
        { id: 'is_private', label: 'Private', color: '#ef4444' },
        { id: 'is_protected', label: 'Protected', color: '#eab308' },
        { id: 'is_static', label: 'Static', color: '#a855f7' },
        { id: 'is_final', label: 'Final', color: '#f97316' },
        { id: 'is_interface', label: 'Interface', color: '#06b6d4' },
        { id: 'is_abstract', label: 'Abstract', color: '#ec4899' }
      ]
      
      const modifiers = []
      const state = this.classState || this.classData
      
      for (const modifier of MODIFIER_MAP) {
        if (state && state[modifier.id] === true) {
          modifiers.push(modifier)
        }
      }
      
      return modifiers
    }
  },
  methods: {
    toggleNameExpanded() {
      if (!this.shouldTruncateName) return
      this.nameExpanded = !this.nameExpanded
    }
  }
}
</script>
