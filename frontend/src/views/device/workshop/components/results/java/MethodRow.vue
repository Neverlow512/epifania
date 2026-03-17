<template>
  <tr 
    class="bg-neutral-900/30 hover:bg-neutral-800/50 border-b border-neutral-700/50 cursor-pointer"
    @click="handleRowClick"
  >
    <td v-if="showSelection" class="w-10" @click.stop>
      <input
        v-if="workshopMode === 'instrumentation' && methodSelectionEnabled"
        type="checkbox"
        :checked="isSelected"
        @change="$emit('toggle-select-method', { className, method })"
        class="checkbox checkbox-xs checkbox-primary"
      />
    </td>
    <td class="w-12"></td>
    <td class="pl-8">
      <div class="flex items-center gap-2 flex-wrap">
        <span class="badge badge-xs badge-secondary">Method</span>
        <code 
          class="text-slate-300 text-xs font-mono" 
          :title="method.signature || method.name"
        >{{ method.name }}</code>
        <div class="flex gap-1">
          <span v-if="method.is_public" class="badge badge-xs bg-green-700 text-white">public</span>
          <span v-if="method.is_private" class="badge badge-xs bg-red-700 text-white">private</span>
          <span v-if="method.is_protected" class="badge badge-xs bg-yellow-700 text-white">protected</span>
          <span v-if="method.is_static" class="badge badge-xs badge-ghost">static</span>
          <span v-if="method.is_final" class="badge badge-xs badge-ghost">final</span>
          <span v-if="method.is_native" class="badge badge-xs badge-warning">native</span>
          <span v-if="method.is_synchronized" class="badge badge-xs bg-cyan-700 text-white">sync</span>
          <span v-if="method.is_abstract" class="badge badge-xs bg-pink-700 text-white">abstract</span>
          <ObserverSessionBadge :observationHistory="method.observation_history" />
        </div>
        <svg 
          xmlns="http://www.w3.org/2000/svg" 
          class="h-3 w-3 text-slate-500 ml-auto"
          fill="none" 
          viewBox="0 0 24 24" 
          stroke="currentColor"
          title="Click for details"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      <div v-if="method.signature" class="mt-1 text-[10px] text-slate-500 font-mono break-all max-w-lg truncate" :title="method.signature">
        {{ method.signature }}
      </div>
      <div v-if="method.return_type" class="text-[10px] text-slate-600 font-mono">
        Returns: {{ method.return_type }}
      </div>
    </td>
    <td>
      <CategoryBadge :category="method.method_category || 'Unknown'" />
    </td>
    <td></td>
    <td class="text-right">
      <span v-if="method.parameters && method.parameters.length > 0" class="text-slate-500 text-[10px]">
        {{ method.parameters.length }} params
      </span>
    </td>
  </tr>
</template>

<script>
import CategoryBadge from '../../shared/CategoryBadge.vue'
import ObserverSessionBadge from '../../instrumentation/toolkit/tools/observer/ObserverSessionBadge.vue'

export default {
  name: 'MethodRow',
  components: {
    CategoryBadge,
    ObserverSessionBadge
  },
  props: {
    method: {
      type: Object,
      required: true
    },
    className: {
      type: String,
      default: ''
    },
    showSelection: {
      type: Boolean,
      default: true
    },
    workshopMode: {
      type: String,
      default: 'analysis'
    },
    methodSelectionEnabled: {
      type: Boolean,
      default: false
    },
    isSelected: {
      type: Boolean,
      default: false
    }
  },
  emits: ['method-click', 'toggle-select-method'],
  methods: {
    handleRowClick() {
      this.$emit('method-click', this.method)
    }
  }
}
</script>
