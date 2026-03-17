<template>
  <div v-if="show" class="modal modal-open">
    <div class="modal-box bg-neutral-900 border border-primary/30 max-w-2xl">
      <h3 class="font-bold text-lg text-white mb-4">App Focused Configuration</h3>
      
      <div v-if="loading" class="flex justify-center py-8">
        <span class="loading loading-spinner loading-lg text-primary"></span>
      </div>
      
      <div v-else class="space-y-4">
        <!-- Package Info -->
        <div class="text-sm text-slate-400">
          Package: <span class="text-white font-mono">{{ packageId }}</span>
        </div>
        
        <!-- Patterns Textarea -->
        <div class="form-control">
          <label class="label">
            <span class="label-text text-white">Include Patterns (one per line)</span>
          </label>
          <textarea
            v-model="patternsText"
            class="textarea textarea-bordered bg-black border-primary/30 text-white font-mono h-40"
            placeholder="com.example.app.*"
          ></textarea>
          <label class="label">
            <span class="label-text-alt text-slate-500">
              Patterns are additive - they include more classes, never exclude.
            </span>
          </label>
        </div>
        
        <!-- Quick Add Buttons -->
        <div class="flex flex-wrap gap-2">
          <button
            type="button"
            class="btn btn-sm btn-outline btn-secondary"
            @click="addStandardObfuscationPatterns"
          >
            + Standard Obfuscation
          </button>
          <button
            type="button"
            class="btn btn-sm btn-outline btn-secondary"
            @click="addSingleLetterPatterns"
          >
            + Single-Letter Classes
          </button>
        </div>
        
        <!-- Templates Section -->
        <div class="divider text-slate-500">Templates</div>
        
        <div class="flex flex-wrap gap-2 items-center">
          <select
            v-model="selectedTemplate"
            class="select select-sm select-bordered bg-black border-primary/30 text-white flex-1 min-w-[150px]"
            :disabled="templates.length === 0"
          >
            <option value="">{{ templates.length === 0 ? 'No saved templates' : 'Load template...' }}</option>
            <option v-for="t in templates" :key="t.name" :value="t.name">
              {{ t.name }} ({{ t.pattern_count }} patterns)
            </option>
          </select>
          
          <button
            type="button"
            class="btn btn-sm btn-outline btn-primary"
            :disabled="!selectedTemplate"
            @click="handleLoadTemplate"
          >
            Load
          </button>
          
          <button
            v-if="selectedTemplate"
            type="button"
            class="btn btn-sm btn-outline btn-error"
            @click="handleDeleteTemplate"
          >
            Delete
          </button>
        </div>
        
        <!-- Save as Template -->
        <div class="flex gap-2 items-center">
          <input
            v-model="newTemplateName"
            type="text"
            placeholder="Template name..."
            class="input input-sm input-bordered bg-black border-primary/30 text-white flex-1"
          />
          <button
            type="button"
            class="btn btn-sm btn-outline btn-accent"
            :disabled="!newTemplateName.trim() || saving"
            @click="handleSaveTemplate"
          >
            Save as Template
          </button>
        </div>
        
        <!-- Error Message -->
        <div v-if="error" class="alert alert-error">
          <span>{{ error }}</span>
        </div>
      </div>
      
      <!-- Actions -->
      <div class="modal-action">
        <button
          type="button"
          class="btn btn-ghost"
          @click="handleReset"
          :disabled="saving"
        >
          Reset to Default
        </button>
        <button
          type="button"
          class="btn btn-ghost"
          @click="$emit('close')"
        >
          Cancel
        </button>
        <button
          type="button"
          class="btn btn-primary"
          @click="handleSave"
          :disabled="saving"
        >
          <span v-if="saving" class="loading loading-spinner loading-xs"></span>
          Save
        </button>
      </div>
    </div>
    <div class="modal-backdrop bg-black/60" @click="$emit('close')"></div>
  </div>
</template>

<script>
import { ref, watch, onMounted } from 'vue'
import { useAppFocusedConfig } from '../../composables/useAppFocusedConfig'

export default {
  name: 'AppFocusedConfigModal',
  props: {
    show: {
      type: Boolean,
      required: true
    },
    packageId: {
      type: String,
      default: ''
    }
  },
  emits: ['close', 'saved'],
  setup(props, { emit }) {
    const {
      config,
      patternsText,
      templates,
      loading,
      saving,
      error,
      loadConfig,
      saveConfig,
      resetConfig,
      loadTemplates,
      loadTemplate,
      saveTemplate,
      deleteTemplate,
      addStandardObfuscationPatterns,
      addSingleLetterPatterns
    } = useAppFocusedConfig()
    
    const selectedTemplate = ref('')
    const newTemplateName = ref('')
    
    watch(() => props.show, async (newVal) => {
      if (newVal && props.packageId) {
        await loadConfig(props.packageId)
        await loadTemplates(props.packageId)
        selectedTemplate.value = ''
        newTemplateName.value = ''
      }
    }, { immediate: true })
    
    async function handleSave() {
      const success = await saveConfig(props.packageId)
      if (success) {
        emit('saved')
        emit('close')
      }
    }
    
    async function handleReset() {
      await resetConfig(props.packageId)
    }
    
    async function handleLoadTemplate() {
      if (selectedTemplate.value) {
        await loadTemplate(props.packageId, selectedTemplate.value)
      }
    }
    
    async function handleSaveTemplate() {
      if (newTemplateName.value.trim()) {
        const success = await saveTemplate(props.packageId, newTemplateName.value.trim())
        if (success) {
          newTemplateName.value = ''
        }
      }
    }
    
    async function handleDeleteTemplate() {
      if (selectedTemplate.value && confirm(`Delete template "${selectedTemplate.value}"?`)) {
        await deleteTemplate(props.packageId, selectedTemplate.value)
        selectedTemplate.value = ''
      }
    }
    
    return {
      config,
      patternsText,
      templates,
      loading,
      saving,
      error,
      selectedTemplate,
      newTemplateName,
      handleSave,
      handleReset,
      handleLoadTemplate,
      handleSaveTemplate,
      handleDeleteTemplate,
      addStandardObfuscationPatterns,
      addSingleLetterPatterns
    }
  }
}
</script>

