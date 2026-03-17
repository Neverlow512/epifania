<template>
  <div class="path-browser">
    <div class="mb-2">
      <label class="label">
        <span class="label-text text-slate-400">{{ label }}</span>
      </label>
    </div>

    <div class="bg-black/30 border border-primary/20 rounded-lg overflow-hidden">
      <div class="flex items-center px-3 py-2 border-b border-primary/20 bg-neutral-900/40">
        <button 
          v-if="currentPath.length > 0"
          @click="navigateUp"
          class="btn btn-xs btn-ghost mr-2"
          title="Go up one level"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        
        <div class="flex-1 flex items-center gap-1 text-sm font-mono text-slate-300 overflow-x-auto whitespace-nowrap">
          <button 
            @click="navigateToRoot"
            class="hover:text-primary transition-colors text-slate-500"
            title="Go to root"
          >
            saved_discoveries
          </button>
          <template v-for="(segment, index) in currentPath" :key="index">
            <span class="text-slate-600">/</span>
            <button 
              @click="navigateToIndex(index)"
              class="hover:text-primary transition-colors"
              :class="{ 'text-primary': index === currentPath.length - 1 }"
            >
              {{ segment }}
            </button>
          </template>
          <span v-if="currentPath.length === 0" class="text-slate-600">/</span>
        </div>

        <button 
          @click="showNewFolderInput = true"
          class="btn btn-xs btn-primary ml-2"
          title="Create new folder"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
        </button>
      </div>

      <div v-if="showNewFolderInput" class="px-3 py-2 bg-primary/5 border-b border-primary/20">
        <div class="flex items-center gap-2">
          <input 
            ref="newFolderInput"
            v-model="newFolderName"
            @keyup.enter="createFolder"
            @keyup.esc="cancelNewFolder"
            type="text"
            placeholder="New folder name"
            class="input input-xs input-bordered bg-black border-primary/30 flex-1 text-white"
          />
          <button @click="createFolder" class="btn btn-xs btn-success">Create</button>
          <button @click="cancelNewFolder" class="btn btn-xs btn-ghost">Cancel</button>
        </div>
      </div>

      <div class="max-h-64 overflow-y-auto">
        <div v-if="loading" class="p-4 text-center">
          <span class="loading loading-spinner loading-sm text-primary"></span>
        </div>

        <div v-else-if="items.length === 0 && folders.length === 0" class="p-4 text-center text-slate-500 text-sm">
          Empty folder. Click + to create a subfolder.
        </div>

        <div v-else>
          <button
            v-for="folder in folders"
            :key="'folder-' + folder"
            @click="navigateInto(folder)"
            class="w-full flex items-center gap-2 px-3 py-2 hover:bg-primary/10 transition-colors text-left border-b border-primary/10 last:border-b-0"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-yellow-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
            </svg>
            <span class="text-slate-300 text-sm flex-1">{{ folder }}</span>
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-slate-600 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </button>

          <div
            v-for="discovery in discoveries"
            :key="'discovery-' + discovery.folder"
            class="flex items-center gap-2 px-3 py-2 text-left border-b border-primary/10 last:border-b-0 opacity-60"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-green-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <span class="text-slate-400 text-sm flex-1">{{ discovery.folder }}</span>
            <span class="text-xs text-slate-600">discovery</span>
          </div>
        </div>
      </div>

      <div class="px-3 py-2 bg-neutral-900/60 border-t border-primary/20">
        <div class="text-xs text-slate-400">
          Save to: <span class="font-mono text-primary">{{ displayPath }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, nextTick, onMounted } from 'vue'
import axios from 'axios'

export default {
  name: 'PathBrowser',
  props: {
    label: {
      type: String,
      default: 'Save Location'
    },
    apiEndpoint: {
      type: String,
      required: true
    },
    modelValue: {
      type: String,
      default: ''
    },
    defaultPath: {
      type: String,
      default: ''
    }
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    const currentPath = ref([])
    const folders = ref([])
    const discoveries = ref([])
    const items = ref([])
    const loading = ref(false)
    const showNewFolderInput = ref(false)
    const newFolderName = ref('')
    const newFolderInput = ref(null)

    const fullPath = computed(() => {
      return currentPath.value.join('/')
    })

    const displayPath = computed(() => {
      if (currentPath.value.length === 0) {
        return 'saved_discoveries/'
      }
      return 'saved_discoveries/' + fullPath.value + '/'
    })

    const loadFolders = async () => {
      try {
        loading.value = true
        const path = fullPath.value
        const response = await axios.get(props.apiEndpoint, {
          params: { path }
        })
        folders.value = response.data.folders || []
        discoveries.value = response.data.discoveries || []
        items.value = [...folders.value, ...discoveries.value.map(d => d.folder)]
      } catch (err) {
        console.error('Failed to load folders:', err)
        folders.value = []
        discoveries.value = []
        items.value = []
      } finally {
        loading.value = false
      }
    }

    const navigateUp = () => {
      if (currentPath.value.length > 0) {
        currentPath.value = currentPath.value.slice(0, -1)
        emit('update:modelValue', fullPath.value)
        loadFolders()
      }
    }

    const navigateToRoot = () => {
      currentPath.value = []
      emit('update:modelValue', '')
      loadFolders()
    }

    const navigateToIndex = (index) => {
      currentPath.value = currentPath.value.slice(0, index + 1)
      emit('update:modelValue', fullPath.value)
      loadFolders()
    }

    const navigateInto = (folder) => {
      currentPath.value = [...currentPath.value, folder]
      emit('update:modelValue', fullPath.value)
      loadFolders()
    }

    const createFolder = async () => {
      const folderName = newFolderName.value.trim()
      if (!folderName) {
        cancelNewFolder()
        return
      }

      const safeName = folderName.replace(/[/\\]/g, '_')
      
      if (folders.value.includes(safeName)) {
        alert('A folder with this name already exists')
        return
      }

      folders.value.push(safeName)
      folders.value.sort()
      items.value = [...folders.value, ...discoveries.value.map(d => d.folder)]
      
      cancelNewFolder()
    }

    const cancelNewFolder = () => {
      showNewFolderInput.value = false
      newFolderName.value = ''
    }

    watch(() => props.modelValue, (newValue) => {
      if (newValue !== undefined && newValue !== fullPath.value) {
        const parts = newValue.split('/').filter(p => p)
        currentPath.value = parts
        loadFolders()
      }
    }, { immediate: false })

    watch(showNewFolderInput, async (show) => {
      if (show) {
        await nextTick()
        newFolderInput.value?.focus()
      }
    })

    onMounted(() => {
      if (props.defaultPath) {
        const parts = props.defaultPath.split('/').filter(p => p)
        currentPath.value = parts
        emit('update:modelValue', props.defaultPath)
      }
      loadFolders()
    })

    return {
      currentPath,
      folders,
      discoveries,
      items,
      loading,
      showNewFolderInput,
      newFolderName,
      newFolderInput,
      fullPath,
      displayPath,
      navigateUp,
      navigateToRoot,
      navigateToIndex,
      navigateInto,
      createFolder,
      cancelNewFolder
    }
  }
}
</script>

<style scoped>
.path-browser {
  user-select: none;
}
</style>

