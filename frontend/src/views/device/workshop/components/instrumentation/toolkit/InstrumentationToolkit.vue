<template>
  <div class="border border-primary/20 rounded-lg bg-black/30 overflow-hidden">
    <button
      type="button"
      class="w-full px-3 py-2.5 flex items-center justify-between cursor-pointer hover:bg-neutral-900/40 transition-colors duration-150 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-primary/40"
      @click="isToolkitExpanded = !isToolkitExpanded"
      :aria-expanded="isToolkitExpanded ? 'true' : 'false'"
      :title="isToolkitExpanded ? 'Collapse toolkit' : 'Expand toolkit'"
    >
      <div class="flex items-center gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-primary/90" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
        </svg>
        <h3 class="text-sm font-semibold text-white">Instrumentation Toolkit</h3>
      </div>

      <svg
        xmlns="http://www.w3.org/2000/svg"
        class="h-4 w-4 text-slate-500 transition-transform duration-200"
        :class="{ 'rotate-180': isToolkitExpanded }"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </button>

    <div v-show="isToolkitExpanded" class="px-3 pb-3 space-y-3">
      <ToolkitCategory title="Tools" icon="tools" :defaultExpanded="true">
        <div v-for="tool in toolsFeatures" :key="tool.id" class="space-y-1">
          <ToolkitItem
            :id="tool.id"
            :label="tool.label"
            :description="tool.description"
            :status="tool.status"
            :selected="selectedItem?.id === tool.id"
            :expandable="tool.id === 'observer'"
            :expanded="tool.id === 'observer' && observerDropdownOpen"
            @select="handleSelect"
            @preview="handlePreview"
            @clearPreview="clearPreview"
          />

          <ObserverControls
            v-if="tool.id === 'observer' && selectedItem?.id === 'observer' && observerDropdownOpen"
            :selectedMethodCount="selectedMethodCount"
            :fridaAttached="fridaAttached"
            :isObserving="isObserving"
            :sessionName="sessionName"
            :timeLimit="timeLimit"
            :logPath="logPath"
            :methodSelectionEnabled="methodSelectionEnabled"
            @start="$emit('observer-start')"
            @stop="$emit('observer-stop')"
            @update:timeLimit="$emit('update:timeLimit', $event)"
            @update:logPath="$emit('update:logPath', $event)"
            @toggle-method-selection="$emit('toggle-method-selection')"
            @open-dashboard="$emit('open-dashboard')"
          />
        </div>
      </ToolkitCategory>
      
      <ToolkitCategory title="Resources" icon="resources" :defaultExpanded="false">
        <ToolkitItem
          v-for="resource in resourcesFeatures"
          :key="resource.id"
          :id="resource.id"
          :label="resource.label"
          :description="resource.description"
          :status="resource.status"
          :selected="selectedItem?.id === resource.id"
          @select="handleSelect"
          @preview="handlePreview"
          @clearPreview="clearPreview"
        />
      </ToolkitCategory>
      
      <ToolkitCategory title="General" icon="general" :defaultExpanded="false">
        <ToolkitItem
          v-for="general in generalFeatures"
          :key="general.id"
          :id="general.id"
          :label="general.label"
          :description="general.description"
          :status="general.status"
          :selected="selectedItem?.id === general.id"
          @select="handleSelect"
          @preview="handlePreview"
          @clearPreview="clearPreview"
        />
      </ToolkitCategory>

      <div v-if="detailsItem && detailsItem.description" class="pt-2 border-t border-primary/10 text-xs text-slate-400">
        <span class="text-slate-300 font-medium">{{ detailsItem.label }}:</span>
        {{ detailsItem.description }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import ToolkitCategory from './ToolkitCategory.vue'
import ToolkitItem from './ToolkitItem.vue'
import ObserverControls from './tools/observer/ObserverControls.vue'

const props = defineProps({
  selectedMethodCount: {
    type: Number,
    default: 0
  },
  fridaAttached: {
    type: Boolean,
    default: false
  },
  isObserving: {
    type: Boolean,
    default: false
  },
  sessionName: {
    type: String,
    default: ''
  },
  timeLimit: {
    type: Number,
    default: null
  },
  logPath: {
    type: String,
    default: ''
  },
  methodSelectionEnabled: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits([
  'tool-selected',
  'observer-start',
  'observer-stop',
  'update:timeLimit',
  'update:logPath',
  'toggle-method-selection',
  'open-dashboard'
])

const isToolkitExpanded = ref(true)
const hoveredItem = ref(null)
const selectedItem = ref(null)
const observerDropdownOpen = ref(false)

const detailsItem = computed(() => hoveredItem.value || selectedItem.value)

const toolsFeatures = ref([
  {
    id: 'observer',
    label: 'Observer',
    description: 'Monitor method calls',
    status: 'development',
    icon: 'eye'
  },
  {
    id: 'interceptor',
    label: 'Interceptor',
    description: 'Modify behavior',
    status: 'placeholder',
    icon: 'filter'
  },
  {
    id: 'tracer',
    label: 'Tracer',
    description: 'Trace execution flow',
    status: 'placeholder',
    icon: 'git-branch'
  },
  {
    id: 'profiler',
    label: 'Basic Profiler',
    description: 'Performance metrics',
    status: 'placeholder',
    icon: 'activity'
  }
])

const resourcesFeatures = ref([
  {
    id: 'plugins',
    label: 'Plugins',
    description: 'Manage custom scripts',
    status: 'placeholder',
    icon: 'package'
  },
  {
    id: 'scripts',
    label: 'Scripts',
    description: 'Script library',
    status: 'placeholder',
    icon: 'code'
  }
])

const generalFeatures = ref([
  {
    id: 'settings',
    label: 'Settings',
    description: 'General configuration',
    status: 'placeholder',
    icon: 'settings'
  }
])

selectedItem.value = {
  id: toolsFeatures.value[0].id,
  label: toolsFeatures.value[0].label,
  description: toolsFeatures.value[0].description,
  status: toolsFeatures.value[0].status
}

emit('tool-selected', toolsFeatures.value[0].id)
observerDropdownOpen.value = toolsFeatures.value[0].id === 'observer'

const handleSelect = (item) => {
  if (item.id === 'observer') {
    observerDropdownOpen.value = selectedItem.value?.id === 'observer' ? !observerDropdownOpen.value : true
  } else {
    observerDropdownOpen.value = false
  }
  selectedItem.value = item
  emit('tool-selected', item.id)
}

const handlePreview = (item) => {
  hoveredItem.value = item
}

const clearPreview = () => {
  hoveredItem.value = null
}
</script>
