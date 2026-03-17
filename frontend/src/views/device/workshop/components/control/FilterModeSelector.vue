<template>
  <div class="form-control">
    <label class="label">
      <span class="label-text text-white font-semibold">Filter Mode</span>
    </label>
    <div class="flex flex-col gap-2">
      <!-- Focused -->
      <div class="flex items-start gap-2">
        <label class="label cursor-pointer justify-start items-start gap-3 p-2 rounded hover:bg-neutral-800/50 min-w-0 flex-1">
          <input 
            type="radio" 
            name="filter-mode" 
            class="radio radio-sm radio-primary" 
            value="focused"
            :checked="filterMode === 'focused'"
            @change="$emit('update:filterMode', 'focused')"
          />
          <div class="min-w-0 flex-1">
            <div class="flex items-center gap-1">
              <span class="label-text text-white block break-words">Focused</span>
              <div class="tooltip tooltip-right z-[9999]" data-tip="Shows classes matching your configured patterns. By default, only those matching the app's package ID.">
                <svg class="w-3.5 h-3.5 text-blue-400 hover:text-primary cursor-help drop-shadow-[0_0_2px_rgba(96,165,250,0.5)]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
            <p class="text-xs text-slate-400 whitespace-normal break-words leading-snug">Include classes matching configured patterns</p>
          </div>
        </label>
        <button
          v-if="filterMode === 'focused'"
          type="button"
          class="btn btn-xs btn-outline btn-primary mt-2"
          @click="$emit('open-config')"
        >
          Configure
        </button>
      </div>
      
      <!-- Package -->
      <label class="label cursor-pointer justify-start items-start gap-3 p-2 rounded hover:bg-neutral-800/50 min-w-0">
        <input 
          type="radio" 
          name="filter-mode" 
          class="radio radio-sm radio-primary" 
          value="package"
          :checked="filterMode === 'package'"
          @change="$emit('update:filterMode', 'package')"
        />
        <div class="min-w-0 flex-1">
          <div class="flex items-center gap-1">
            <span class="label-text text-white block break-words">Package</span>
            <div class="tooltip tooltip-right z-[9999]" data-tip="Shows everything bundled in the APK that's loaded at runtime. Includes app code, libraries, and any obfuscated code.">
              <svg class="w-3.5 h-3.5 text-blue-400 hover:text-primary cursor-help drop-shadow-[0_0_2px_rgba(96,165,250,0.5)]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
          <p class="text-xs text-slate-400 whitespace-normal break-words leading-snug">Include app code and bundled libraries</p>
        </div>
      </label>
      
      <!-- All -->
      <label class="label cursor-pointer justify-start items-start gap-3 p-2 rounded hover:bg-neutral-800/50 min-w-0">
        <input 
          type="radio" 
          name="filter-mode" 
          class="radio radio-sm radio-primary" 
          value="all"
          :checked="filterMode === 'all'"
          @change="$emit('update:filterMode', 'all')"
        />
        <div class="min-w-0 flex-1">
          <div class="flex items-center gap-1">
            <span class="label-text text-white block break-words">All</span>
            <div class="tooltip tooltip-right z-[9999]" data-tip="Shows all classes loaded in the app's process, including Android system classes.">
              <svg class="w-3.5 h-3.5 text-blue-400 hover:text-primary cursor-help drop-shadow-[0_0_2px_rgba(96,165,250,0.5)]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
          <p class="text-xs text-slate-400 whitespace-normal break-words leading-snug">Include everything (app, bundled, system)</p>
        </div>
      </label>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FilterModeSelector',
  props: {
    filterMode: {
      type: String,
      required: true
    }
  },
  emits: ['update:filterMode', 'open-config']
}
</script>

<style>
/* Force tooltips to appear on top of everything */
.tooltip:before,
.tooltip:after {
  z-index: 99999 !important;
}
</style>
