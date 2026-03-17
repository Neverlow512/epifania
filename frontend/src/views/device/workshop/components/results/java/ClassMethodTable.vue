<template>
  <div class="overflow-x-auto">
    <table class="table table-sm w-full">
      <thead>
        <tr class="border-b border-primary/20">
          <th v-if="showSelection" class="text-slate-400 font-semibold w-10"></th>
          <th class="text-slate-400 font-semibold w-8"></th>
          <th class="text-slate-400 font-semibold">Class / Method</th>
          <th class="text-slate-400 font-semibold">Category</th>
          <th class="text-slate-400 font-semibold">Source</th>
          <th class="text-slate-400 font-semibold text-right w-20">Methods</th>
          <th class="text-slate-400 font-semibold w-20">Actions</th>
        </tr>
      </thead>
      <tbody>
        <template v-for="classData in classes" :key="classData.name">
          <ClassRow
            :classData="classData"
            :expanded="expandedClasses.has(classData.name)"
            :selected="selectedClasses.has(classData.name)"
            :showSelection="showSelection"
            :workshopMode="workshopMode"
            :showScanButton="showScanButton"
            :classState="classStates.get(classData.name)"
            @toggle-expand="$emit('toggle-expand', classData.name)"
            @toggle-select="$emit('toggle-select', classData.name)"
            @scan-class="$emit('scan-class', $event)"
            @extract-class="$emit('extract-class', $event)"
          />
          <MethodRow
            v-if="expandedClasses.has(classData.name)"
            v-for="method in getClassMethods(classData)"
            :key="`${classData.name}.${method.name}`"
            :method="method"
            :className="classData.name"
            :showSelection="showSelection"
            :workshopMode="workshopMode"
            :methodSelectionEnabled="methodSelectionEnabled"
            :isSelected="isMethodSelected(classData.name, method.name, method.signature)"
            @method-click="$emit('method-click', { method: $event, className: classData.name })"
            @toggle-select-method="$emit('toggle-select-method', $event)"
          />
        </template>
      </tbody>
    </table>
  </div>
</template>

<script>
import ClassRow from './ClassRow.vue'
import MethodRow from './MethodRow.vue'

export default {
  name: 'ClassMethodTable',
  components: {
    ClassRow,
    MethodRow
  },
  props: {
    classes: {
      type: Array,
      required: true
    },
    expandedClasses: {
      type: Set,
      required: true
    },
    selectedClasses: {
      type: Set,
      default: () => new Set()
    },
    classStates: {
      type: Map,
      default: () => new Map()
    },
    showSelection: {
      type: Boolean,
      default: true
    },
    workshopMode: {
      type: String,
      default: 'analysis'
    },
    showScanButton: {
      type: Boolean,
      default: true
    },
    selectedMethods: {
      type: Map,
      default: () => new Map()
    },
    methodSelectionEnabled: {
      type: Boolean,
      default: false
    }
  },
  emits: ['toggle-expand', 'toggle-select', 'method-click', 'scan-class', 'extract-class', 'toggle-select-method'],
  setup(props) {
    const getClassMethods = (classData) => {
      const state = props.classStates.get(classData.name)
      if (state?.methods) {
        return state.methods
      }
      return classData.methods || []
    }
    
    const generateMethodId = (className, methodName, signature) => {
      return `${className}::${methodName}::${signature || ''}`
    }
    
    const isMethodSelected = (className, methodName, signature) => {
      const methodId = generateMethodId(className, methodName, signature)
      return props.selectedMethods.has(methodId)
    }
    
    return {
      getClassMethods,
      isMethodSelected
    }
  }
}
</script>
